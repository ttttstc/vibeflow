#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from vibeflow_paths import feature_list_path, load_state, path_contract


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def write_if_missing(path: Path, content: str) -> Path:
    if not path.exists():
        write_text(path, content)
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
    counts["titles"] = [str(feature.get("title") or f"Feature {idx + 1}") for idx, feature in enumerate(features[:6])]
    return counts


def codebase_snapshot(project_root: Path, contract: dict) -> dict:
    # First try the new spec-facts.json
    spec_facts_path = project_root / "docs" / "architecture" / ".spec-facts.json"
    if spec_facts_path.exists():
        data = read_json(spec_facts_path, {})
        return {
            "languages": data.get("languages", []),
            "modules": [m.get("name") for m in data.get("modules", [])],
            "frameworks": [],  # spec-facts does not have frameworks field
            "roots": {},
            "entrypoints": [],
        }
    # Fallback to old codebase-map.json (only for legacy projects)
    path = contract["codebase_map_json"]
    if not path.exists():
        return {}
    data = read_json(path, {})
    return {
        "languages": [item.get("name") for item in data.get("languages", []) if item.get("name")][:3],
        "modules": [item.get("name") for item in data.get("modules", []) if item.get("name")][:6],
        "frameworks": [item.get("name") for item in data.get("frameworks", []) if item.get("name")][:5],
        "roots": data.get("roots") or {},
        "entrypoints": [item.get("path") for item in data.get("entrypoints", []) if item.get("path")][:4],
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


def render_overview_readme(project_root: Path, state: dict) -> str:
    change_link = active_change_link(state)
    return "\n".join(
        [
            "# Project Overview",
            "",
            "Start here when you are new to this repository.",
            "",
            "## Read in this order",
            "",
            f"1. [PROJECT.md](PROJECT.md) - What this project is and why it exists",
            f"2. [CURRENT-STATE.md](CURRENT-STATE.md) - Where the project stands right now",
            f"3. [PRODUCT.md](PRODUCT.md) - User-facing capabilities and product boundaries",
            f"4. [ARCHITECTURE.md](ARCHITECTURE.md) - System structure and technical flow",
            f"5. [Current Change Package]({change_link}/) - The active delivery package",
            "",
            "## Quick links",
            "",
            "- [Project README](../../README.md)",
            f"- [Current Change Package]({change_link}/)",
            "- [feature-list.json](../../feature-list.json)",
            "- [RELEASE_NOTES.md](../../RELEASE_NOTES.md)",
            "",
        ]
    ) + "\n"


def render_project_doc(project_root: Path, state: dict) -> str:
    name = project_name(project_root)
    change_link = active_change_link(state)
    summary = read_project_summary(project_root) or f"`{name}` is managed with VibeFlow. This document is the long-lived project brief for new contributors."
    context = str(state.get("context") or "greenfield")
    return "\n".join(
        [
            f"# Project - {name}",
            "",
            "## Summary",
            "",
            summary,
            "",
            "## Current Project Context",
            "",
            f"- Delivery context: `{context}`",
            f"- Active change package: [Current Change]({change_link}/)",
            "- Long-lived project context lives under `docs/overview/`.",
            "- Per-change decisions live under `docs/changes/<change-id>/...`.",
            "",
            "## Where To Start",
            "",
            f"- Project overview: [README.md](../../README.md)",
            f"- Current state snapshot: [CURRENT-STATE.md](CURRENT-STATE.md)",
            f"- Active change package: [Current Change]({change_link}/)",
            "",
            "## Key Directories",
            "",
            "- `src/` or the main source root: implementation code",
            "- `tests/`: verification and regression coverage",
            "- `docs/overview/`: long-lived project context",
            "- `docs/changes/`: change-by-change delivery records",
            "",
        ]
    ) + "\n"


def render_product_doc(project_root: Path, state: dict) -> str:
    summary = feature_status_summary(project_root)
    change_link = active_change_link(state)
    feature_lines = [f"- {title}" for title in summary["titles"]] or ["- Add the current user-facing capabilities here."]
    project_summary = read_project_summary(project_root)
    return "\n".join(
        [
            "# Product",
            "",
            "## Summary",
            "",
            project_summary or "This file tracks the stable, user-facing shape of the project.",
            "",
            "## Current Product Shape",
            "",
            f"- Active change package: [Current Change]({change_link}/)",
            f"- Tracked feature count: {summary['total']}",
            "",
            "## Current Capabilities",
            "",
            *feature_lines,
            "",
            "## Core User Flows",
            "",
            "- Capture the main user-facing flow here when the product surface stabilizes.",
            "- Keep this section stable across individual code changes.",
            "",
            "## Non-Goals",
            "",
            "- Record what this project intentionally does not do when boundaries become explicit.",
            "",
            "## Update Policy",
            "",
            "- Update this file when user-facing capabilities or product boundaries change.",
            "- Do not rewrite it for every small implementation detail.",
            "",
        ]
    ) + "\n"


def render_architecture_doc(project_root: Path, state: dict, contract: dict) -> str:
    snapshot = codebase_snapshot(project_root, contract)
    roots = snapshot.get("roots") or {}
    source_roots = ", ".join(roots.get("source") or []) or "TBD"
    test_roots = ", ".join(roots.get("tests") or []) or "TBD"
    languages = ", ".join(snapshot.get("languages") or []) or "TBD"
    frameworks = ", ".join(snapshot.get("frameworks") or []) or "TBD"
    modules = snapshot.get("modules") or []
    entrypoints = snapshot.get("entrypoints") or []
    module_lines = [f"- `{module}`" for module in modules] or ["- Add major modules once they stabilize."]
    entrypoint_lines = [f"- `{path}`" for path in entrypoints] or ["- Add the main runtime entrypoints here."]
    return "\n".join(
        [
            "# Architecture",
            "",
            "## Technical Snapshot",
            "",
            f"- Languages: {languages}",
            f"- Frameworks: {frameworks}",
            f"- Source roots: {source_roots}",
            f"- Test roots: {test_roots}",
            "",
            "## Major Modules",
            "",
            *module_lines,
            "",
            "## Entrypoints",
            "",
            *entrypoint_lines,
            "",
            "## Delivery Files",
            "",
            "- `docs/overview/`: long-lived project context",
            "- `docs/changes/<change-id>/`: per-change requirements, design, tasks, and verification",
            "- `feature-list.json`: feature execution state",
            "- `.vibeflow/`: workflow state and internal execution files",
            "",
            "## Update Policy",
            "",
            "- Update this file when architecture, module boundaries, or runtime flow changes.",
            "- Avoid rewriting it for minor implementation details.",
            "",
        ]
    ) + "\n"


def render_current_state_doc(project_root: Path, state: dict, contract: dict) -> str:
    active_change = state.get("active_change") or {}
    change_rel = active_change_rel(state)
    change_link = active_change_link(state)
    summary = feature_status_summary(project_root)
    completed, pending = checkpoint_summary(state)
    completed_preview = ", ".join(completed[:8]) or "none"
    pending_preview = ", ".join(pending[:8]) or "none"
    release_heading = latest_release_heading(contract) or "No release entries yet."
    snapshot = codebase_snapshot(project_root, contract)
    module_preview = ", ".join(snapshot.get("modules") or []) or "No codebase map yet."
    languages = ", ".join(snapshot.get("languages") or []) or "Unknown"

    return "\n".join(
        [
            "# Current State",
            "",
            f"- Last updated: {now_iso()}",
            f"- Mode: `{state.get('mode', 'full')}`",
            f"- Context: `{state.get('context', 'greenfield')}`",
            f"- Current phase: `{state.get('current_phase', '') or 'unknown'}`",
            f"- Active change: `{active_change.get('id', '') or 'unknown'}`",
            "",
            "## Recommended Reading",
            "",
            "- [Project brief](PROJECT.md)",
            "- [Product](PRODUCT.md)",
            "- [Architecture](ARCHITECTURE.md)",
            f"- [Active change package]({change_link}/)",
            f"- [feature-list.json](../../feature-list.json)",
            "",
            "## Delivery Snapshot",
            "",
            f"- Active change root: `{change_rel}`",
            f"- Feature status: {summary['passing']}/{summary['total']} passing, {summary['failing']} failing, {summary['pending']} pending",
            f"- Completed checkpoints: {completed_preview}",
            f"- Pending checkpoints: {pending_preview}",
            f"- Latest release note heading: {release_heading}",
            "",
            "## Current Implementation Surface",
            "",
            f"- Languages: {languages}",
            f"- Module snapshot: {module_preview}",
            f"- Codebase map: {'available' if contract['codebase_map_json'].exists() else 'not generated yet'}",
            "",
            "## Key Files To Open Next",
            "",
            f"- [Requirements]({change_link}/requirements.md)",
            f"- [Design]({change_link}/design.md)",
            f"- [Tasks]({change_link}/tasks.md)",
            f"- [Verification]({change_link}/verification/)",
            "",
            "## Notes",
            "",
            "- This file is refreshed automatically to summarize the latest project state.",
            "- Stable project positioning belongs in PROJECT.md and PRODUCT.md.",
            "",
        ]
    ) + "\n"


def ensure_overview_docs(project_root: Path, state: dict | None = None, *, force: bool = False) -> dict:
    loaded_state = state or load_state(project_root)
    contract = path_contract(project_root, loaded_state)
    contract["overview_root"].mkdir(parents=True, exist_ok=True)
    writer = write_text if force else write_if_missing
    writer(contract["overview"]["readme"], render_overview_readme(project_root, loaded_state))
    writer(contract["overview"]["project"], render_project_doc(project_root, loaded_state))
    writer(contract["overview"]["product"], render_product_doc(project_root, loaded_state))
    writer(contract["overview"]["architecture"], render_architecture_doc(project_root, loaded_state, contract))
    refresh_current_state(project_root, loaded_state)
    return contract["overview"]


def refresh_current_state(project_root: Path, state: dict | None = None) -> Path:
    loaded_state = state or load_state(project_root)
    contract = path_contract(project_root, loaded_state)
    contract["overview_root"].mkdir(parents=True, exist_ok=True)
    return write_text(contract["overview"]["current_state"], render_current_state_doc(project_root, loaded_state, contract))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate or refresh project overview docs.")
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
            print(f"Updated current state: {result['path']}")
        else:
            print("Overview docs ready:")
            for key, value in result["paths"].items():
                print(f"- {key}: {value}")


if __name__ == "__main__":
    main()
