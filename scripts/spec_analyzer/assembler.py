# -*- coding: utf-8 -*-
"""Assemble deep architecture analysis for docs/overview/ARCHITECTURE.md."""
from __future__ import annotations

import argparse
import difflib
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from spec_analyzer._utils import read_json
from spec_analyzer.inference import build_inference_template_from_facts
from spec_analyzer.runner import run_analysis


def render_module_responsibilities(inferences: dict, modules: list[dict]) -> list[str]:
    rows = []
    responsibilities = inferences.get("module_responsibilities", {})
    has_real_data = (
        responsibilities
        and "__PLACEHOLDER__" not in responsibilities
        and not (len(responsibilities) == 1 and "__PLACEHOLDER__" in responsibilities)
    )

    if not has_real_data:
        for mod in modules:
            name = mod.get("name", "unknown")
            kind = mod.get("kind", "module")
            rows.append(f"| `{name}` | 静态事实不足，待补充更高置信度说明 | {kind} |")
    else:
        for mod in modules:
            name = mod.get("name", "unknown")
            kind = mod.get("kind", "module")
            desc = responsibilities.get(name, "静态事实不足，待补充更高置信度说明")
            rows.append(f"| `{name}` | {desc} | {kind} |")

    return rows


def render_runtime_flows(inferences: dict) -> list[str]:
    flows = inferences.get("runtime_flows", [])
    if not flows:
        return ["- 暂无运行流推断；可通过 reverse-spec skill 注入更高保真推断。"]

    lines = []
    for i, flow in enumerate(flows, 1):
        title = flow.get("title") or flow.get("name") or f"Flow {i}"
        description = flow.get("description")
        mermaid = flow.get("mermaid")
        steps = flow.get("steps", [])
        lines.append(f"#### 6.1.{i} {title}")
        lines.append("")
        if description:
            lines.append(f"- {description}")
            lines.append("")
        if mermaid:
            lines.append(mermaid)
        else:
            lines.append("```mermaid")
            lines.append("sequenceDiagram")
            for step in steps:
                participant = step.get("participant", "Actor")
                action = step.get("action", "")
                next_step = step.get("next", None)
                if next_step:
                    lines.append(f"    {participant}->>+{next_step}: {action}")
                else:
                    lines.append(f"    {participant}->>+{participant}: {action}")
            lines.append("```")
        lines.append("")
    return lines


def render_tech_stack(facts: dict) -> list[str]:
    tech_stack = facts.get("tech_stack", [])
    if not tech_stack:
        return ["- 未从项目文件中稳定识别到技术栈。"]

    lines = []
    for item in tech_stack:
        name = item.get("name", "unknown")
        version = item.get("version", "")
        purpose = item.get("purpose", "")
        chunk = f"- **{name}**"
        if version:
            chunk += f" {version}"
        if purpose:
            chunk += f": {purpose}"
        lines.append(chunk)
    return lines


def render_data_model(facts: dict) -> list[str]:
    entities = facts.get("entities", [])
    er_diagram = facts.get("diagrams", {}).get("er_diagram_mermaid", "")
    if not entities:
        return ["- 未从项目文件中识别到稳定的数据模型实体。"]
    if er_diagram:
        return [er_diagram]

    lines = ["```mermaid", "erDiagram"]
    for entity in entities:
        name = entity.get("name", "Unknown")
        lines.append(f"    {name} {{")
        for field in entity.get("fields", []):
            f_type = field.get("type", "string")
            f_name = field.get("name", "field")
            lines.append(f"        {f_type} {f_name}")
        lines.append("    }")
    lines.append("```")
    return lines


def load_custom_standards(project_root: Path) -> dict[str, list[str]]:
    standards_dir = project_root / "docs" / "standards"
    if not standards_dir.exists() or not standards_dir.is_dir():
        return {}

    section_mapping = {
        "coding-standards.md": "8.3 编码规范",
        "naming-conventions.md": "8.4 命名约定",
        "architecture-rules.md": "8.5 架构规则",
        "testing-standards.md": "8.6 测试规范",
        "deployment-standards.md": "8.7 部署规范",
    }

    result: dict[str, list[str]] = {}
    for md_file in sorted(standards_dir.glob("*.md")):
        section_name = section_mapping.get(md_file.name, f"8.X {md_file.stem.replace('-', ' ').title()}")
        content = md_file.read_text(encoding="utf-8").strip()
        if not content:
            continue
        result[section_name] = [
            line for line in content.split("\n")
            if not line.strip().startswith("#")
        ]
    return result


def render_api_surface(facts: dict) -> list[str]:
    api_surface = facts.get("api_surface", {})
    if not api_surface:
        return ["- 未从项目文件中识别到稳定的公开 API。"]

    lines = []
    for module_name, exports in sorted(api_surface.items()):
        if not exports:
            continue
        lines.append(f"##### `{module_name}`")
        for export in exports:
            lines.append(f"- `{export}`")
        lines.append("")
    return lines


def render_module_graph(facts: dict) -> str:
    module_graph = facts.get("diagrams", {}).get("module_graph_mermaid", "")
    if module_graph:
        return module_graph

    modules = facts.get("modules", [])
    lines = ["```mermaid", "flowchart TD"]
    for mod in modules:
        name = mod.get("name", "unknown").replace(".", "_")
        lines.append(f"    {name}[{mod.get('name', 'unknown')}]")
    lines.append("```")
    return "\n".join(lines)


def render_c4_views(facts: dict) -> list[str]:
    diagrams = facts.get("diagrams", {})
    return [
        "#### 3.2 C4 分层结构",
        "",
        "##### 3.2.1 System Context",
        "",
        diagrams.get("c4_context_mermaid", "```mermaid\nflowchart LR\n    empty[No system context]\n```"),
        "",
        "##### 3.2.2 Container View",
        "",
        diagrams.get("c4_container_mermaid", "```mermaid\nflowchart TB\n    empty[No containers]\n```"),
        "",
        "##### 3.2.3 Component View",
        "",
        diagrams.get("c4_component_mermaid") or render_module_graph(facts),
        "",
    ]


def assemble_full_spec(facts: dict, inferences: dict, project_name: str, project_root: Path | None = None) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    custom_standards = load_custom_standards(project_root) if project_root else {}
    modules = facts.get("modules", [])
    entities = facts.get("entities", [])
    tech_stack = facts.get("tech_stack", [])

    responsibilities = inferences.get("module_responsibilities", {})
    has_responsibilities = (
        responsibilities
        and "__PLACEHOLDER__" not in responsibilities
        and not (len(responsibilities) == 1 and "__PLACEHOLDER__" in responsibilities)
    )
    has_runtime_flows = bool(inferences.get("runtime_flows"))

    lines = [
        f"> reverse-spec 生成时间：{now}",
        "> 输出定位：docs/overview/ARCHITECTURE.md 内的生成区块",
        "> 状态：基于静态事实生成；如有人工或 LLM 推断，应以更高置信度信息补充",
        "",
        "### 1. 引言与目标",
        "",
        "#### 1.1 质量目标",
        "- 待补充：记录可用性、性能、可维护性和可观测性目标。",
        "",
        "#### 1.2 相关方",
        "- 开发与维护团队",
        "- 架构评审者",
        "- 未来接手该仓库的协作者 / AI 代理",
        "",
        "### 2. 架构约束",
        "",
        "#### 2.1 技术约束",
    ]

    if tech_stack:
        for item in tech_stack:
            constraint = item.get("constraint", "")
            if constraint:
                lines.append(f"- {constraint}")
    if not any(line.startswith("- ") for line in lines[-len(tech_stack or []):]):
        lines.append("- 主要约束来自当前仓库可见的代码、目录和配置文件。")

    lines.extend([
        "",
        "#### 2.2 协作约束",
        "- 该文档需要与 docs/overview 下其他正式文档保持一致。",
        "- 生成区块允许自动刷新，人工正文不应被覆盖。",
        "",
        "### 3. 系统上下文与范围",
        "",
        "#### 3.1 范围说明",
        f"- 项目名：{project_name}",
        f"- 扫描文件数：{facts.get('source_files_count', len(modules))}",
        f"- 识别语言：{', '.join(l.get('name', '') for l in facts.get('languages', [])) or 'Python'}",
        "",
    ])
    lines.extend(render_c4_views(facts))
    lines.extend([
        "### 4. 解决方案策略",
        "",
        "#### 4.1 技术选型",
    ])
    lines.extend(render_tech_stack(facts))
    lines.append("")
    lines.extend([
        "#### 4.2 架构模式",
        "- 以模块/包为中心组织代码结构。",
        "- 通过静态分析抽取模块、API、实体和依赖关系。",
        "- 允许在静态事实之上叠加人工或 LLM 推断，补足职责与运行流说明。",
        "",
        "### 5. Building Block View",
        "",
        "#### 5.1 模块总览",
        "",
    ])
    lines.append(render_module_graph(facts))
    lines.append("")
    lines.append("#### 5.2 模块职责")
    lines.append("")
    lines.append("| 模块 | 职责推断 | 类型 |")
    lines.append("|------|----------|------|")
    lines.extend(render_module_responsibilities(inferences, modules))
    lines.append("")
    if has_responsibilities:
        lines.append("<!-- LLM-INFERRED: module_responsibilities -->")
    lines.append("")
    lines.append("### 6. Runtime View")
    lines.append("")
    lines.append("#### 6.1 关键运行流")
    lines.append("")
    lines.extend(render_runtime_flows(inferences))
    lines.append("")
    if has_runtime_flows:
        lines.append("<!-- LLM-INFERRED: runtime_flows -->")
    lines.append("")
    lines.extend([
        "### 7. Deployment View",
        "",
        "- 执行模型：依据仓库内可见入口运行脚本、服务或前端构建产物。",
        "- 配置来源：项目配置文件、环境变量、状态文件或框架默认约定。",
        "- 持久化线索：以代码中显式声明的数据模型、实体和文件契约为准。",
        "",
        "### 8. Concepts",
        "",
        "#### 8.1 数据模型",
        "",
    ])
    lines.extend(render_data_model(facts))
    lines.append("")
    if entities:
        lines.append("<!-- LLM-INFERRED: data_model_entities -->")
    lines.append("")
    lines.extend([
        "#### 8.2 API Surface",
        "",
    ])
    lines.extend(render_api_surface(facts))
    lines.append("")

    for section_name, section_lines in sorted(custom_standards.items()):
        lines.append(f"#### {section_name}")
        lines.append("")
        lines.extend(section_lines)
        lines.append("")

    lines.extend([
        "### 9. Architecture Decisions",
        "",
        "- 待补充：记录已确认且长期生效的架构决策或 ADR 链接。",
        "",
        "### 10. Quality Requirements",
        "",
        "- 待补充：将性能、可靠性、安全性等要求补成项目级约束。",
        "",
        "### 11. Risks and Technical Debt",
        "",
        "| 风险 | 影响 | 缓解思路 |",
        "|------|------|----------|",
        "| 基于装饰器或运行时动态注册的字段/依赖，静态分析可能无法完整识别 | 中 | 结合人工审阅或更高保真推断补充 |",
        "| 运行流来自静态依赖和保守推断，无法完全覆盖真实时序 | 中 | 用 reverse-spec skill 注入 LLM 推断并人工确认 |",
        "",
        "### 12. Glossary",
        "",
        "| 术语 | 说明 |",
        "|------|------|",
    ])

    seen_terms = set()
    for mod in modules:
        name = mod.get("name", "").split(".")[-1].replace("_", " ").title()
        if name and name not in seen_terms:
            lines.append(f"| {name} | {project_name} 中识别出的模块/概念名 |")
            seen_terms.add(name)

    lines.append("")
    lines.append("*Generated by VibeFlow spec_analyzer*")
    return "\n".join(lines)


def build_architecture_analysis(
    project_root: Path,
    *,
    include_tests: bool = False,
    inferences: dict | None = None,
) -> dict:
    """Build facts, inferences, and rendered Arc42 markdown in-memory."""
    facts = run_analysis(project_root, include_tests=include_tests, output_path=None)
    effective_inferences = inferences or build_inference_template_from_facts(facts)
    markdown = assemble_full_spec(facts, effective_inferences, project_root.name, project_root)
    return {
        "facts": facts,
        "inferences": effective_inferences,
        "markdown": markdown,
        "signature": {
            "facts": {
                key: value
                for key, value in facts.items()
                if key != "generated_at"
            },
            "inferences": {
                key: value
                for key, value in effective_inferences.items()
                if key not in {"generated_at", "llm_raw_response"}
            },
        },
    }


def generate_spec_delta(old_spec_path: Path, new_spec_path: Path, change_id: str) -> str:
    old_content = old_spec_path.read_text(encoding="utf-8") if old_spec_path.exists() else ""
    new_content = new_spec_path.read_text(encoding="utf-8") if new_spec_path.exists() else ""
    return generate_spec_delta_from_content(
        old_content,
        new_content,
        change_id=change_id,
        old_label=str(old_spec_path),
        new_label=str(new_spec_path),
    )


def generate_spec_delta_from_content(
    old_content: str,
    new_content: str,
    *,
    change_id: str,
    old_label: str,
    new_label: str,
) -> str:
    diff = difflib.unified_diff(
        old_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=old_label,
        tofile=new_label,
        lineterm="",
    )
    diff_text = "".join(diff)

    old_lines = len(old_content.splitlines())
    new_lines = len(new_content.splitlines())
    line_diff = new_lines - old_lines

    old_modules = set()
    new_modules = set()
    for line in old_content.splitlines():
        if line.startswith("| `") and "| " in line:
            parts = line.split("|")
            if len(parts) >= 2:
                old_modules.add(parts[1].strip().strip("`"))
    for line in new_content.splitlines():
        if line.startswith("| `") and "| " in line:
            parts = line.split("|")
            if len(parts) >= 2:
                new_modules.add(parts[1].strip().strip("`"))

    added_modules = new_modules - old_modules
    removed_modules = old_modules - new_modules

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    delta_lines = [
        f"# Spec Delta: {change_id}",
        "",
        f"**Generated**: {now}",
        f"**Change ID**: {change_id}",
        "",
        "## Change Summary",
        "",
        f"- **Lines**: {old_lines} -> {new_lines} ({'+' if line_diff >= 0 else ''}{line_diff})",
        f"- **Modules Added**: {len(added_modules)}",
        f"- **Modules Removed**: {len(removed_modules)}",
        "",
    ]

    if added_modules:
        delta_lines.append("### Added Modules")
        for module_name in sorted(added_modules):
            delta_lines.append(f"- `{module_name}`")
        delta_lines.append("")

    if removed_modules:
        delta_lines.append("### Removed Modules")
        for module_name in sorted(removed_modules):
            delta_lines.append(f"- `{module_name}`")
        delta_lines.append("")

    delta_lines.extend([
        "## Full Diff",
        "",
        "```diff",
        diff_text if diff_text else "(No changes detected)",
        "```",
    ])
    return "\n".join(delta_lines)


def assemble(project_root: Path, facts_path: Path, inferences_path: Path, output_path: Path) -> None:
    facts = read_json(facts_path, default={})
    inferences = read_json(inferences_path, default={})
    project_name = project_root.name

    old_spec_content = output_path.read_text(encoding="utf-8") if output_path.exists() else None
    new_spec_content = assemble_full_spec(facts, inferences, project_name, project_root)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(new_spec_content, encoding="utf-8")
    print(f"Architecture analysis written to: {output_path}")

    if old_spec_content is not None:
        change_id = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        delta_dir = project_root / "docs" / "changes" / change_id
        delta_dir.mkdir(parents=True, exist_ok=True)
        delta_content = generate_spec_delta_from_content(
            old_spec_content,
            new_spec_content,
            change_id=change_id,
            old_label=f"{output_path} (previous)",
            new_label=str(output_path),
        )
        delta_path = delta_dir / "spec-delta.md"
        delta_path.write_text(delta_content, encoding="utf-8")
        print(f"Spec delta written to: {delta_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Assemble docs/overview/ARCHITECTURE.md-ready analysis from spec facts and inferences"
    )
    parser.add_argument("--project-root", type=Path, default=Path("."), help="Root directory of the project")
    parser.add_argument("--facts", type=Path, default=None, help="Path to spec-facts.json")
    parser.add_argument("--inferences", type=Path, default=None, help="Path to spec-inferences.json")
    parser.add_argument("--output", type=Path, default=None, help="Output path for architecture markdown")
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    output_path = args.output or (project_root / "docs" / "overview" / "ARCHITECTURE.md")

    if args.facts and args.inferences:
        facts_path = args.facts.resolve()
        inferences_path = args.inferences.resolve()
        print(f"Project root: {project_root}")
        print(f"Facts: {facts_path}")
        print(f"Inferences: {inferences_path}")
        print(f"Output: {output_path}")
        try:
            assemble(project_root, facts_path, inferences_path, output_path)
            return 0
        except Exception as e:
            print(f"Error during assembly: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1

    try:
        analysis = build_architecture_analysis(project_root)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(analysis["markdown"], encoding="utf-8")
        print(f"Architecture analysis written to: {output_path}")
        print(f"Modules found: {len(analysis['facts'].get('modules', []))}")
        print(f"Runtime flows: {len(analysis['inferences'].get('runtime_flows', []))}")
        return 0
    except Exception as e:
        print(f"Error during assembly: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
