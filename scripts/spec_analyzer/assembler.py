# -*- coding: utf-8 -*-
"""Document Assembly Layer — renders Arc42 full-spec.md from spec-facts.json and spec-inferences.json."""
from __future__ import annotations

import argparse
import difflib
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from spec_analyzer._utils import read_json


def render_module_responsibilities(inferences: dict, modules: list) -> list[str]:
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
            rows.append(f"| `{name}` | Insufficient data | {kind} |")
    else:
        for mod in modules:
            name = mod.get("name", "unknown")
            kind = mod.get("kind", "module")
            desc = responsibilities.get(name, "Insufficient data")
            rows.append(f"| `{name}` | {desc} | {kind} |")

    return rows


def render_runtime_flows(inferences: dict) -> list[str]:
    flows = inferences.get("runtime_flows", [])
    if not flows:
        return ["*No runtime flows recorded — run inference with an LLM to populate this section.*"]

    lines = []
    for i, flow in enumerate(flows, 1):
        title = flow.get("title", f"Flow {i}")
        steps = flow.get("steps", [])
        lines.append(f"### 6.1.{i} {title}")
        lines.append("")
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
        return ["*Tech stack not detected from project files.*"]

    lines = []
    for item in tech_stack:
        name = item.get("name", "unknown")
        version = item.get("version", "")
        purpose = item.get("purpose", "")
        lines.append(f"- **{name}** {version}: {purpose}".strip())
    return lines


def render_data_model(facts: dict) -> list[str]:
    entities = facts.get("entities", [])
    er_diagram = facts.get("diagrams", {}).get("er_diagram_mermaid", "")
    if not entities:
        return ["*No data model entities detected from project files.*"]
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
        "coding-standards.md": "8.3 Coding Standards",
        "naming-conventions.md": "8.4 Naming Conventions",
        "architecture-rules.md": "8.5 Architecture Rules",
        "testing-standards.md": "8.6 Testing Standards",
        "deployment-standards.md": "8.7 Deployment Standards",
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
        return ["*No API surface detected from project files.*"]

    lines = []
    for module_name, exports in sorted(api_surface.items()):
        if not exports:
            continue
        lines.append(f"### `{module_name}`")
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

    lines = [
        f"# {project_name} Architecture Specification",
        "",
        f"> Generated by VibeFlow reverse-spec on {now}",
        "> Status: DRAFT - Review Required",
        "",
        "## 1. Introduction and Goals",
        "",
        "### 1.1 Quality Goals",
        "- *To be defined through project requirements gathering*",
        "",
        "### 1.2 Stakeholders",
        "- *Project development team*",
        "- *Architecture reviewers*",
        "",
        "## 2. Architecture Constraints",
        "",
        "### Technical Constraints",
    ]

    if tech_stack:
        for item in tech_stack:
            constraint = item.get("constraint", "")
            if constraint:
                lines.append(f"- {constraint}")
    else:
        lines.append("- Python 3.10+ required")
        lines.append("- No external runtime dependencies required (pure Python project)")

    lines.extend([
        "",
        "### Organizational Constraints",
        "- Project follows VibeFlow 6-phase workflow methodology",
        "",
        "## 3. System Context and Scope",
        "",
        "### 3.1 Business Context",
        f"- Project: {project_name}",
        "- Type: CLI automation tool for AI-assisted development workflows",
        "- Core functionality: Coordinates AI agents through structured development phases",
        "",
        "### 3.2 Technical Boundary",
        f"- Source files analyzed: {facts.get('source_files_count', len(modules))}",
        f"- Languages: {', '.join(l.get('name', '') for l in facts.get('languages', [])) or 'Python'}",
        "- Runs as standalone Python scripts",
        "- No external API dependencies for core operation",
        "",
        "## 4. Solution Strategy",
        "",
        "### 4.1 Technology Choices",
    ])
    lines.extend(render_tech_stack(facts))
    lines.append("")
    lines.extend([
        "### 4.2 Architecture Patterns",
        "- Modular script-based architecture",
        "- State machine driven phase transitions",
        "- Feature-based code organization",
        "- Static analysis for codebase mapping",
        "",
        "## 5. Building Block View",
        "",
        "### 5.1 Overview",
        "",
    ])

    lines.append(render_module_graph(facts))
    lines.append("")
    lines.append("### 5.2 Module Catalog")
    lines.append("")
    lines.append("| Module | Responsibility | Kind |")
    lines.append("|--------|----------------|------|")
    lines.extend(render_module_responsibilities(inferences, modules))
    lines.append("")
    if has_responsibilities:
        lines.append("<!-- LLM-INFERRED: module_responsibilities -->")
    lines.append("")
    lines.append("## 6. Runtime View")
    lines.append("")
    lines.append("### 6.1 Key Runtime Flows")
    lines.append("")
    lines.extend(render_runtime_flows(inferences))
    lines.append("")
    if inferences.get("runtime_flows"):
        lines.append("<!-- LLM-INFERRED: runtime_flows -->")
    lines.append("")
    lines.extend([
        "## 7. Deployment View",
        "",
        "- **Execution Model**: Standalone Python scripts",
        "- **Installation**: Via package installation or direct script execution",
        "- **Configuration**: YAML-based workflow configuration files",
        "- **State Persistence**: JSON files for runtime state and feature tracking",
        "",
        "## 8. Concepts",
        "",
        "### 8.1 Data Model",
        "",
    ])
    lines.extend(render_data_model(facts))
    lines.append("")
    if entities:
        lines.append("<!-- LLM-INFERRED: data_model_entities -->")
    lines.append("")
    lines.extend([
        "### 8.2 API Surface",
        "",
    ])
    lines.extend(render_api_surface(facts))
    lines.append("")

    for section_name, section_lines in sorted(custom_standards.items()):
        lines.append(f"### {section_name}")
        lines.append("")
        lines.extend(section_lines)
        lines.append("")

    lines.extend([
        "## 9. Architecture Decisions",
        "",
        "*Architecture Decision Records (ADRs) deferred to future phase.*",
        "",
        "## 10. Quality Requirements",
        "",
        "*Quality requirements deferred to future phase.*",
        "",
        "## 11. Risks and Technical Debt",
        "",
        "| Risk | Impact | Mitigation |",
        "|------|--------|------------|",
        "| Known limitation: decorator-based entity fields (Pydantic, dataclasses) may not appear in entity list | Medium | Future enhancement to AST-based field extraction |",
        "| Static analysis cannot capture runtime behavior | Low | LLM inference for behavioral analysis |",
        "",
        "## 12. Glossary",
        "",
        "| Term | Definition |",
        "|------|------------|",
    ])

    seen_terms = set()
    for mod in modules:
        name = mod.get("name", "").split(".")[-1].replace("_", " ").title()
        if name not in seen_terms:
            lines.append(f"| {name} | Module in {project_name} |")
            seen_terms.add(name)

    lines.append("")
    lines.append("*Generated by VibeFlow spec_analyzer*")
    return "\n".join(lines)


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
        for m in sorted(added_modules):
            delta_lines.append(f"- `{m}`")
        delta_lines.append("")

    if removed_modules:
        delta_lines.append("### Removed Modules")
        for m in sorted(removed_modules):
            delta_lines.append(f"- `{m}`")
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
    print(f"Full spec written to: {output_path}")

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
        description="Assemble Arc42 full-spec.md from spec-facts.json and spec-inferences.json"
    )
    parser.add_argument("--project-root", type=Path, default=Path("."), help="Root directory of the project")
    parser.add_argument("--facts", type=Path, default=None, help="Path to .spec-facts.json")
    parser.add_argument("--inferences", type=Path, default=None, help="Path to .spec-inferences.json")
    parser.add_argument("--output", type=Path, default=None, help="Output path for full-spec.md")
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    facts_path = args.facts or (project_root / "docs" / "architecture" / ".spec-facts.json")
    inferences_path = args.inferences or (project_root / "docs" / "architecture" / ".spec-inferences.json")
    output_path = args.output or (project_root / "docs" / "architecture" / "full-spec.md")

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


if __name__ == "__main__":
    sys.exit(main())
