#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

from spec_analyzer.assembler import build_architecture_analysis
from vibeflow_codebase import build_change_impact, build_codebase_map, change_focus_summary
from vibeflow_paths import feature_list_path, load_state, path_contract


PROJECT_DOC = "PROJECT.md"
ARCHITECTURE_DOC = "ARCHITECTURE.md"
CURRENT_STATE_DOC = "CURRENT-STATE.md"
PROJECT_BLOCK = "代码面速览"
ARCHITECTURE_BLOCK = "技术快照"
ARCHITECTURE_ANALYSIS_BLOCK = "Arc42 架构视图"
LEGACY_PROJECT_MARKERS = ("# Project - ", "## Summary", "## Current Capabilities")
LEGACY_ARCHITECTURE_MARKERS = ("# Architecture", "## Technical Snapshot", "## Major Modules")
GENERATED_BLOCK_MARKER_TEMPLATE = "<!-- 生成区块:{name} {edge} -->"


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def today_text() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d")


def now_display() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def read_project_summary(project_root: Path) -> str:
    readme = project_root / "README.md"
    if not readme.exists():
        return ""
    paragraphs: list[str] = []
    current: list[str] = []
    for raw_line in readme.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        if line.startswith("#") or line.startswith("- ") or line.startswith("* ") or line.startswith("```"):
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        current.append(line)
    if current:
        paragraphs.append(" ".join(current))
    for paragraph in paragraphs:
        if paragraph and "managed with VibeFlow" not in paragraph:
            return paragraph
    return ""


def contains_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def project_name(project_root: Path) -> str:
    payload = read_json(feature_list_path(project_root), {})
    name = str(payload.get("project") or "").strip()
    return name or project_root.name


def active_change_rel(state: dict) -> str:
    return str((state.get("active_change") or {}).get("root") or "docs/changes")


def active_change_link(state: dict) -> str:
    return "../" + active_change_rel(state).split("docs/", 1)[-1].replace("\\", "/")


def current_feature_payload(project_root: Path) -> dict:
    return read_json(feature_list_path(project_root), {"features": []})


def feature_status_summary(project_root: Path) -> dict:
    payload = current_feature_payload(project_root)
    features = payload.get("features") or []
    counts = {"total": len(features), "passing": 0, "failing": 0, "pending": 0, "other": 0}
    for feature in features:
        status = str(feature.get("status") or "").strip().lower()
        if status == "passing":
            counts["passing"] += 1
        elif status == "failing":
            counts["failing"] += 1
        elif status in {"pending", "todo", "queued", "ready"} or not status:
            counts["pending"] += 1
        else:
            counts["other"] += 1
    counts["titles"] = [str(feature.get("title") or f"功能 {idx + 1}") for idx, feature in enumerate(features[:6])]
    return counts


def rules_snapshot(project_root: Path) -> dict:
    rules_dir = project_root / "rules"
    if not rules_dir.exists():
        return {"count": 0, "files": []}
    files = sorted(
        path.relative_to(project_root).as_posix()
        for path in rules_dir.rglob("*")
        if path.is_file()
    )
    return {"count": len(files), "files": files[:20]}


def codebase_snapshot(project_root: Path, contract: dict, codebase_map: dict | None = None) -> dict:
    del contract
    data = codebase_map or build_codebase_map(project_root)
    return {
        "source": "live-repo-scan",
        "languages": [item.get("name") for item in data.get("languages", []) if item.get("name")][:5],
        "modules": [item.get("name") for item in data.get("modules", []) if item.get("name")][:10],
        "frameworks": [item.get("name") for item in data.get("frameworks", []) if item.get("name")][:5],
        "roots": data.get("roots") or {},
        "entrypoints": [item.get("path") for item in data.get("entrypoints", []) if item.get("path")][:6],
    }


def change_focus_snapshot(project_root: Path, state: dict, codebase_map: dict | None = None) -> dict:
    impact = build_change_impact(project_root, state, codebase_map or build_codebase_map(project_root))
    return {
        "change_id": impact.get("change_id", ""),
        "matched_terms": [item for item in impact.get("matched_terms", []) if item][:8],
        **change_focus_summary(impact),
    }


def latest_release_heading(contract: dict) -> str:
    path = contract["release_notes"]
    if not path.exists():
        return ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            return line.removeprefix("## ").strip()
    return ""


def checkpoint_summary(state: dict) -> tuple[list[str], list[str]]:
    completed = []
    pending = []
    for key, value in (state.get("checkpoints") or {}).items():
        label = key.replace("_", " ")
        if value:
            completed.append(label)
        else:
            pending.append(label)
    return completed, pending


def stable_hash(payload: object) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_wiki_status(path: Path) -> dict:
    data = read_json(path, None)
    if not isinstance(data, dict):
        return {"version": 1, "docs": {}}
    docs = data.get("docs")
    if not isinstance(docs, dict):
        data["docs"] = {}
    data.setdefault("version", 1)
    return data


def save_wiki_status(path: Path, data: dict) -> Path:
    return write_json(path, data)


def cleanup_legacy_process_files(project_root: Path, contract: dict) -> None:
    legacy_paths = [
        project_root / ".vibeflow" / "codebase-map.json",
        project_root / ".vibeflow" / "codebase-map.md",
        project_root / ".vibeflow" / "analysis" / "spec-facts.json",
        project_root / ".vibeflow" / "analysis" / "spec-inferences.json",
        project_root / ".vibeflow" / "analysis" / "inference-prompt.md",
        project_root / ".vibeflow" / "analysis" / "architecture-analysis.md",
        project_root / "docs" / "architecture" / ".spec-facts.json",
        project_root / "docs" / "architecture" / ".spec-inferences.json",
        project_root / "docs" / "architecture" / ".inference-prompt.md",
        project_root / "docs" / "architecture" / "full-spec.md",
        contract["change_root"] / "codebase-impact.json",
        contract["change_root"] / "codebase-impact.md",
    ]
    for path in legacy_paths:
        if path.exists():
            path.unlink()
    analysis_dir = project_root / ".vibeflow" / "analysis"
    if analysis_dir.exists() and not any(analysis_dir.iterdir()):
        analysis_dir.rmdir()


def update_doc_status(status: dict, name: str, *, source_hash: str, generated_blocks: dict[str, dict]) -> None:
    docs = status.setdefault("docs", {})
    doc_status = docs.setdefault(name, {})
    doc_status.update(
        {
            "last_refreshed_at": now_iso(),
            "last_checked_at": now_iso(),
            "stale": False,
            "stale_reasons": [],
            "source_hash": source_hash,
            "generated_blocks": generated_blocks,
        }
    )


def update_doc_check_status(status: dict, name: str, *, stale: bool, reasons: list[str]) -> None:
    docs = status.setdefault("docs", {})
    doc_status = docs.setdefault(name, {})
    doc_status["last_checked_at"] = now_iso()
    doc_status["stale"] = stale
    doc_status["stale_reasons"] = reasons


def generated_block_marker(name: str, edge: str) -> str:
    return GENERATED_BLOCK_MARKER_TEMPLATE.format(name=name, edge=edge)


def generated_block_pattern(name: str) -> re.Pattern[str]:
    start = re.escape(generated_block_marker(name, "开始"))
    end = re.escape(generated_block_marker(name, "结束"))
    return re.compile(rf"{start}\n(?P<body>.*?)(?:\n{end})", re.DOTALL)


def normalize_generated_block_content(content: str) -> str:
    return content.rstrip()


def generated_block_state(content: str) -> dict[str, str]:
    return {"content_hash": stable_hash(normalize_generated_block_content(content))}


def stored_generated_block_hash(payload: dict) -> str:
    return str(payload.get("content_hash") or payload.get("source_hash") or "")


def read_generated_block_content(doc_path: Path, block_name: str) -> str | None:
    if not doc_path.exists():
        return None
    match = generated_block_pattern(block_name).search(doc_path.read_text(encoding="utf-8"))
    if not match:
        return None
    return normalize_generated_block_content(match.group("body"))


def doc_stale_status(status: dict, name: str, current_source_hash: str, *, doc_path: Path | None = None) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    doc_status = (status.get("docs") or {}).get(name) or {}
    previous_hash = str(doc_status.get("source_hash") or "")
    if not previous_hash:
        reasons.append("尚未建立同步记录")
    elif previous_hash != current_source_hash:
        reasons.append("源输入已变化，尚未重新同步")

    generated_blocks = doc_status.get("generated_blocks") or {}
    if doc_path is not None:
        if not doc_path.exists():
            reasons.append("文档文件缺失")
        for block_name, block_payload in generated_blocks.items():
            expected_hash = stored_generated_block_hash(block_payload)
            if not expected_hash:
                continue
            actual_content = read_generated_block_content(doc_path, block_name)
            if actual_content is None:
                reasons.append(f"生成区块“{block_name}”缺失或格式无效")
                continue
            if stable_hash(actual_content) != expected_hash:
                reasons.append(f"生成区块“{block_name}”内容已漂移")

    normalized = list(dict.fromkeys(reasons))
    return bool(normalized), normalized


def metadata_block(doc_type: str, maintenance: str, status_label: str, review_label: str, sources: str) -> str:
    return "\n".join(
        [
            f"> 文档类型：{doc_type}",
            f"> 维护方式：{maintenance}",
            f"> 状态：{status_label}",
            f"> {review_label}：{today_text()}",
            f"> 主要输入：{sources}",
        ]
    )


def render_overview_readme(project_root: Path, state: dict) -> str:
    change_link = active_change_link(state)
    return "\n".join(
        [
            "# 总览入口",
            "",
            "首次进入仓库时，建议按下面的顺序阅读：",
            "",
            "## 阅读顺序",
            "",
            "1. [CURRENT-STATE.md](CURRENT-STATE.md) - 当前项目状态、阻塞与下一步建议",
            "2. [PROJECT.md](PROJECT.md) - 项目底座、目标边界与核心概念",
            "3. [ARCHITECTURE.md](ARCHITECTURE.md) - 模块结构、依赖规则与运行流",
            f"4. [当前变更包]({change_link}/) - 本次交付的 brief / design / tasks / verification",
            "",
            "## 快速链接",
            "",
            "- [项目 README](../../README.md)",
            f"- [当前变更包]({change_link}/)",
            "- [feature-list.json](../../feature-list.json)",
            "- [RELEASE_NOTES.md](../../RELEASE_NOTES.md)",
            "",
        ]
    ) + "\n"


def render_generated_block(name: str, content: str) -> str:
    body = normalize_generated_block_content(content)
    if body:
        return f"{generated_block_marker(name, '开始')}\n{body}\n{generated_block_marker(name, '结束')}"
    return f"{generated_block_marker(name, '开始')}\n{generated_block_marker(name, '结束')}"


def replace_generated_block(content: str, name: str, block_content: str, anchor_heading: str) -> str:
    block = render_generated_block(name, block_content)
    pattern = re.compile(
        rf"{re.escape(generated_block_marker(name, '开始'))}.*?{re.escape(generated_block_marker(name, '结束'))}",
        re.DOTALL,
    )
    if pattern.search(content):
        return pattern.sub(block, content)

    anchor = f"## {anchor_heading}"
    if anchor in content:
        marker = f"{anchor}\n"
        return content.replace(marker, f"{marker}\n{block}\n", 1)

    suffix = f"\n\n## {anchor_heading}\n\n{block}\n"
    return content.rstrip() + suffix


def looks_like_legacy_doc(content: str, markers: tuple[str, ...]) -> bool:
    return all(marker in content for marker in markers)


def sync_hybrid_doc(
    path: Path,
    template: str,
    *,
    blocks: list[tuple[str, str, str]],
    force: bool,
    legacy_markers: tuple[str, ...],
) -> Path:
    if not path.exists():
        return write_text(path, template)

    current = path.read_text(encoding="utf-8")
    if force or looks_like_legacy_doc(current, legacy_markers):
        return write_text(path, template)

    updated = current
    for block_name, block_content, anchor_heading in blocks:
        updated = replace_generated_block(updated, block_name, block_content, anchor_heading)
    if updated != current:
        return write_text(path, updated)
    return path


def render_project_block(snapshot: dict, rules_info: dict) -> str:
    languages = "、".join(snapshot.get("languages") or []) or "未知"
    modules = "、".join(snapshot.get("modules") or []) or "待补充"
    entrypoints = "、".join(snapshot.get("entrypoints") or []) or "待补充"
    rule_files = "、".join(rules_info.get("files") or []) or "无"
    return "\n".join(
        [
            f"- 代码面来源：`{snapshot.get('source', 'none')}`",
            f"- 主要语言：{languages}",
            f"- 主要模块：{modules}",
            f"- 关键入口：{entrypoints}",
            f"- 规则文件数：{rules_info.get('count', 0)}",
            f"- 规则文件示例：{rule_files}",
        ]
    )


def render_architecture_block(snapshot: dict) -> str:
    languages = "、".join(snapshot.get("languages") or []) or "未知"
    frameworks = "、".join(snapshot.get("frameworks") or []) or "待补充"
    roots = snapshot.get("roots") or {}
    source_roots = "、".join(roots.get("source") or []) or "待补充"
    test_roots = "、".join(roots.get("tests") or []) or "待补充"
    modules = "、".join(snapshot.get("modules") or []) or "待补充"
    entrypoints = "、".join(snapshot.get("entrypoints") or []) or "待补充"
    return "\n".join(
        [
            f"- 代码事实来源：`{snapshot.get('source', 'none')}`",
            f"- 主要语言：{languages}",
            f"- 框架线索：{frameworks}",
            f"- 源码根目录：{source_roots}",
            f"- 测试根目录：{test_roots}",
            f"- 主要模块：{modules}",
            f"- 关键入口：{entrypoints}",
            "- 深度架构分析：见下方 Arc42 架构视图生成区块",
        ]
    )


def project_summary_text(project_root: Path) -> str:
    summary = read_project_summary(project_root)
    if summary and contains_cjk(summary):
        return summary
    return f"{project_name(project_root)} 由 VibeFlow 管理。这份文档用于沉淀项目长期有效的上下文和边界。"


def project_doc_source_inputs(project_root: Path, state: dict, contract: dict, snapshot: dict | None = None) -> dict:
    return {
        "summary": project_summary_text(project_root),
        "features": feature_status_summary(project_root),
        "rules": rules_snapshot(project_root),
        "snapshot": snapshot or codebase_snapshot(project_root, contract),
        "context": state.get("context"),
    }


def architecture_doc_source_inputs(
    project_root: Path,
    contract: dict,
    snapshot: dict | None = None,
    analysis: dict | None = None,
) -> dict:
    return {
        "snapshot": snapshot or codebase_snapshot(project_root, contract),
        "rules": rules_snapshot(project_root),
        "arc42": (analysis or build_architecture_analysis(project_root)).get("signature", {}),
    }


def compute_overview_sync_status(
    project_root: Path,
    state: dict,
    contract: dict,
    wiki_status: dict,
    snapshot: dict | None = None,
) -> dict[str, dict]:
    current_snapshot = snapshot or codebase_snapshot(project_root, contract)
    project_source_hash = stable_hash(project_doc_source_inputs(project_root, state, contract, current_snapshot))
    architecture_source_hash = stable_hash(architecture_doc_source_inputs(project_root, contract, current_snapshot))
    project_stale, project_reasons = doc_stale_status(
        wiki_status,
        PROJECT_DOC,
        project_source_hash,
        doc_path=contract["overview"]["project"],
    )
    architecture_stale, architecture_reasons = doc_stale_status(
        wiki_status,
        ARCHITECTURE_DOC,
        architecture_source_hash,
        doc_path=contract["overview"]["architecture"],
    )
    return {
        PROJECT_DOC: {
            "stale": project_stale,
            "reasons": project_reasons,
            "current_source_hash": project_source_hash,
        },
        ARCHITECTURE_DOC: {
            "stale": architecture_stale,
            "reasons": architecture_reasons,
            "current_source_hash": architecture_source_hash,
        },
    }


def render_project_template(project_root: Path, state: dict, contract: dict, snapshot: dict | None = None) -> tuple[str, str, str]:
    name = project_name(project_root)
    summary = read_project_summary(project_root)
    if not summary or not contains_cjk(summary):
        summary = f"{name} 由 VibeFlow 管理。这份文档用于沉淀项目长期有效的上下文和边界。"
    current_snapshot = snapshot or codebase_snapshot(project_root, contract)
    rules_info = rules_snapshot(project_root)
    block_content = render_project_block(current_snapshot, rules_info)
    content = "\n".join(
        [
            f"# 项目总览 - {name}",
            "",
            metadata_block(
                "项目底座",
                "人工正文 + 生成区块",
                "正式",
                "最近审阅",
                "README.md、feature-list.json、rules/、docs/changes/",
            ),
            "",
            "## 项目摘要",
            "",
            summary,
            "",
            "## 项目目标",
            "",
            "- 待补充：用 2 到 5 条描述项目长期要达成的目标。",
            "",
            "## 非目标",
            "",
            "- 待补充：明确项目当前不解决的问题，帮助后续设计收边界。",
            "",
            "## 核心概念",
            "",
            "- 待补充：列出项目领域概念、关键术语和内部对象。",
            "",
            "## 能力地图",
            "",
            "- 待补充：只写长期稳定能力，不写一次性变更任务。",
            "",
            "## 主流程",
            "",
            "- 待补充：描述最关键的业务链路或交付链路。",
            "",
            "## 外部依赖",
            "",
            "- 待补充：记录外部系统、外部平台、重要文件契约。",
            "",
            "## 关键决策",
            "",
            "- 待补充：记录当前已经生效、应长期遵守的关键设计决策。",
            "",
            "## 开放问题",
            "",
            "- 待补充：记录下一步设计仍需回答的问题。",
            "",
            "## 代码面速览",
            "",
            render_generated_block(PROJECT_BLOCK, block_content),
            "",
            "## 更新规则",
            "",
            "- 当项目目标、能力边界、关键决策或外部依赖变化时，必须回写本文件。",
            "- 自动化只允许修改生成区块，其他正文由人工维护。",
            "",
        ]
    )
    source_hash = stable_hash(project_doc_source_inputs(project_root, state, contract, current_snapshot))
    return content.rstrip() + "\n", block_content, source_hash


def render_architecture_template(
    project_root: Path,
    contract: dict,
    snapshot: dict | None = None,
    analysis: dict | None = None,
) -> tuple[str, dict[str, str], str]:
    current_snapshot = snapshot or codebase_snapshot(project_root, contract)
    block_content = render_architecture_block(current_snapshot)
    current_analysis = analysis or build_architecture_analysis(project_root)
    analysis_block = current_analysis["markdown"]
    content = "\n".join(
        [
            "# 架构总览",
            "",
            metadata_block(
                "工程结构",
                "人工正文 + 生成区块",
                "正式",
                "最近审阅",
                "源码目录、rules/、feature-list.json",
            ),
            "",
            "## 架构摘要",
            "",
            "- 待补充：用一句话概括当前系统如何组织。",
            "",
            "## 技术快照",
            "",
            render_generated_block(ARCHITECTURE_BLOCK, block_content),
            "",
            "## Arc42 深度架构视图",
            "",
            render_generated_block(ARCHITECTURE_ANALYSIS_BLOCK, analysis_block),
            "",
            "## 人工补充",
            "",
            "- 待补充：记录业务边界、静态分析无法看出的外部系统契约，以及已确认的长期设计决策。",
            "",
            "## 更新规则",
            "",
            "- 当目录结构、主要模块、入口点、依赖方向或关键状态模型变化时，必须回写本文件。",
            "- reverse-spec / spec_analyzer 的深度结果统一刷新到 Arc42 生成区块，不再额外维护过程文件。",
            "- 自动化只允许修改生成区块，其他正文由人工维护。",
            "",
        ]
    )
    source_hash = stable_hash(architecture_doc_source_inputs(project_root, contract, current_snapshot, current_analysis))
    return content.rstrip() + "\n", {
        ARCHITECTURE_BLOCK: block_content,
        ARCHITECTURE_ANALYSIS_BLOCK: analysis_block,
    }, source_hash


def render_change_focus_lines(change_focus: dict) -> list[str]:
    relevant_modules = "、".join(change_focus.get("relevant_modules") or []) or "暂无明确热点"
    integration_points = "、".join(change_focus.get("integration_points") or []) or "暂无明显入口"
    affected_tests = "、".join(change_focus.get("affected_tests") or []) or "暂无明确测试影响"
    read_order = "、".join(change_focus.get("suggested_read_order") or []) or "先看 CURRENT-STATE.md / PROJECT.md / ARCHITECTURE.md"
    lines = [
        f"- 重点模块：{relevant_modules}",
        f"- 关键入口：{integration_points}",
        f"- 受影响测试：{affected_tests}",
        f"- 建议先读：{read_order}",
    ]
    for note in change_focus.get("risk_notes") or []:
        lines.append(f"- 风险提示：{note}")
    return lines


def render_current_state_doc(
    project_root: Path,
    state: dict,
    contract: dict,
    overview_sync_status: dict[str, dict],
    snapshot: dict | None = None,
    change_focus: dict | None = None,
) -> tuple[str, str]:
    active_change = state.get("active_change") or {}
    change_rel = active_change_rel(state)
    change_link = active_change_link(state)
    summary = feature_status_summary(project_root)
    completed, pending = checkpoint_summary(state)
    completed_preview = "、".join(completed[:8]) or "无"
    pending_preview = "、".join(pending[:8]) or "无"
    release_heading = latest_release_heading(contract) or "暂无发布记录"
    current_snapshot = snapshot or codebase_snapshot(project_root, contract)
    current_change_focus = change_focus or change_focus_snapshot(project_root, state)
    module_preview = "、".join(current_snapshot.get("modules") or []) or "暂无"
    languages = "、".join(current_snapshot.get("languages") or []) or "未知"
    project_status = overview_sync_status[PROJECT_DOC]
    architecture_status = overview_sync_status[ARCHITECTURE_DOC]
    project_stale = bool(project_status["stale"])
    project_reasons = list(project_status["reasons"])
    architecture_stale = bool(architecture_status["stale"])
    architecture_reasons = list(architecture_status["reasons"])
    risks: list[str] = []
    if summary["failing"] > 0:
        risks.append("存在失败功能，需要先回看 review / test 产物。")
    if pending:
        risks.append(f"仍有未完成 checkpoint：{pending_preview}")
    if project_stale:
        risks.append("项目底座文档可能过期，需要检查 PROJECT.md。")
    if architecture_stale:
        risks.append("架构文档可能过期，需要检查 ARCHITECTURE.md。")
    if not risks:
        risks.append("当前没有明显阻塞，但仍建议检查 active change 的设计与验证产物。")

    content = "\n".join(
        [
            "# 当前状态",
            "",
            f"> 文档类型：运行态快照",
            f"> 维护方式：自动生成",
            f"> 状态：派生",
            f"> 最近刷新：{now_display()}",
            f"> 主要输入：.vibeflow/state.json、feature-list.json、RELEASE_NOTES.md、active change",
            "",
            "## 快照",
            "",
            f"- 模式：`{state.get('mode', 'full')}`",
            f"- 上下文：`{state.get('context', 'greenfield')}`",
            f"- 当前阶段：`{state.get('current_phase', '') or 'unknown'}`",
            f"- 当前活跃变更：`{active_change.get('id', '') or 'unknown'}`",
            "",
            "## 当前变更",
            "",
            f"- 变更目录：`{change_rel}`",
            f"- 关键文件：`{change_rel}/brief.md`、`{change_rel}/design.md`、`{change_rel}/tasks.md`",
            f"- 验证目录：`{change_rel}/verification/`",
            f"- 关注关键词：{'、'.join(current_change_focus.get('matched_terms') or []) or '待从变更文档继续补充'}",
            "",
            "## 交付状态",
            "",
            f"- 功能状态：{summary['passing']}/{summary['total']} 通过，{summary['failing']} 失败，{summary['pending']} 待处理",
            f"- 已完成 checkpoint：{completed_preview}",
            f"- 待完成 checkpoint：{pending_preview}",
            "",
            "## 当前变更关注点",
            "",
            *render_change_focus_lines(current_change_focus),
            "",
            "## 最新信号",
            "",
            f"- 最新发布记录：{release_heading}",
            f"- 主要语言：{languages}",
            f"- 模块快照：{module_preview}",
            "",
            "## 当前风险与未知项",
            "",
            *[f"- {item}" for item in risks],
            "",
            "## 建议阅读顺序",
            "",
            "- [项目总览](PROJECT.md)",
            "- [架构总览](ARCHITECTURE.md)",
            f"- [当前变更包]({change_link}/)",
            f"- [feature-list.json](../../feature-list.json)",
            "",
            "## 文档同步状态",
            "",
            f"- `PROJECT.md`：{'待同步' if project_stale else '已同步'}" + (
                f"（{'；'.join(project_reasons)}）" if project_reasons else ""
            ),
            f"- `ARCHITECTURE.md`：{'待同步' if architecture_stale else '已同步'}" + (
                f"（{'；'.join(architecture_reasons)}）" if architecture_reasons else ""
            ),
            "",
        ]
    )
    source_hash = stable_hash(
        {
            "state": state,
            "features": summary,
            "release": release_heading,
            "project_hash": project_status["current_source_hash"],
            "architecture_hash": architecture_status["current_source_hash"],
            "change_focus": current_change_focus,
        }
    )
    return content.rstrip() + "\n", source_hash


def ensure_overview_docs(project_root: Path, state: dict | None = None, *, force: bool = False) -> dict:
    loaded_state = state or load_state(project_root)
    contract = path_contract(project_root, loaded_state)
    contract["overview_root"].mkdir(parents=True, exist_ok=True)
    cleanup_legacy_process_files(project_root, contract)
    codebase_map = build_codebase_map(project_root)
    current_snapshot = codebase_snapshot(project_root, contract, codebase_map)

    project_doc, project_block, project_hash = render_project_template(
        project_root,
        loaded_state,
        contract,
        current_snapshot,
    )
    architecture_analysis = build_architecture_analysis(project_root)
    architecture_doc, architecture_blocks, architecture_hash = render_architecture_template(
        project_root,
        contract,
        current_snapshot,
        architecture_analysis,
    )

    sync_hybrid_doc(
        contract["overview"]["project"],
        project_doc,
        blocks=[(PROJECT_BLOCK, project_block, "代码面速览")],
        force=force,
        legacy_markers=LEGACY_PROJECT_MARKERS,
    )
    sync_hybrid_doc(
        contract["overview"]["architecture"],
        architecture_doc,
        blocks=[
            (ARCHITECTURE_BLOCK, architecture_blocks[ARCHITECTURE_BLOCK], "技术快照"),
            (ARCHITECTURE_ANALYSIS_BLOCK, architecture_blocks[ARCHITECTURE_ANALYSIS_BLOCK], "Arc42 深度架构视图"),
        ],
        force=force,
        legacy_markers=LEGACY_ARCHITECTURE_MARKERS,
    )
    if contract["overview"]["readme"].exists():
        write_text(contract["overview"]["readme"], render_overview_readme(project_root, loaded_state))

    status = load_wiki_status(contract["wiki_status"])
    update_doc_status(
        status,
        PROJECT_DOC,
        source_hash=project_hash,
        generated_blocks={PROJECT_BLOCK: generated_block_state(project_block)},
    )
    update_doc_status(
        status,
        ARCHITECTURE_DOC,
        source_hash=architecture_hash,
        generated_blocks={
            name: generated_block_state(content)
            for name, content in architecture_blocks.items()
        },
    )
    save_wiki_status(contract["wiki_status"], status)
    refresh_current_state(project_root, loaded_state, snapshot=current_snapshot, codebase_map=codebase_map)
    return contract["overview"]


def refresh_current_state(
    project_root: Path,
    state: dict | None = None,
    *,
    snapshot: dict | None = None,
    codebase_map: dict | None = None,
) -> Path:
    loaded_state = state or load_state(project_root)
    contract = path_contract(project_root, loaded_state)
    contract["overview_root"].mkdir(parents=True, exist_ok=True)
    cleanup_legacy_process_files(project_root, contract)
    status = load_wiki_status(contract["wiki_status"])
    live_codebase_map = codebase_map or build_codebase_map(project_root)
    current_snapshot = snapshot or codebase_snapshot(project_root, contract, live_codebase_map)
    current_change_focus = change_focus_snapshot(project_root, loaded_state, live_codebase_map)
    overview_sync_status = compute_overview_sync_status(
        project_root,
        loaded_state,
        contract,
        status,
        current_snapshot,
    )
    for name, sync_status in overview_sync_status.items():
        update_doc_check_status(
            status,
            name,
            stale=bool(sync_status["stale"]),
            reasons=list(sync_status["reasons"]),
        )
    content, source_hash = render_current_state_doc(
        project_root,
        loaded_state,
        contract,
        overview_sync_status,
        current_snapshot,
        current_change_focus,
    )
    path = write_text(contract["overview"]["current_state"], content)
    update_doc_status(status, CURRENT_STATE_DOC, source_hash=source_hash, generated_blocks={})
    save_wiki_status(contract["wiki_status"], status)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="生成或刷新项目 overview 文档。")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--refresh-current-only", action="store_true")
    parser.add_argument("--refresh-all", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    state = load_state(project_root)

    if args.refresh_current_only:
        path = refresh_current_state(project_root, state)
        result = {"updated": "current_state", "path": str(path)}
    else:
        overview = ensure_overview_docs(project_root, state, force=args.refresh_all)
        result = {"updated": "overview", "paths": {key: str(value) for key, value in overview.items()}}

    if args.as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if args.refresh_current_only:
            print(f"已更新当前状态文档：{result['path']}")
        else:
            print("Overview 文档已就绪：")
            for key, value in result["paths"].items():
                print(f"- {key}: {value}")


if __name__ == "__main__":
    main()
