#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path


SUPPORTED_RULE_SUFFIXES = {".md", ".markdown", ".txt", ".json", ".yaml", ".yml"}
RULE_CONTENT_CHAR_LIMIT = 4000
RULE_SUMMARY_CHAR_LIMIT = 320
GUIDANCE_FILENAMES = {"claude.md", "agent.md", "agents.md"}


def rules_dir_path(project_root: Path) -> Path:
    return project_root / "rules"


def guidance_file_paths(project_root: Path) -> list[Path]:
    if not project_root.exists():
        return []
    return sorted(
        [
            path
            for path in project_root.iterdir()
            if path.is_file() and path.name.lower() in GUIDANCE_FILENAMES
        ],
        key=lambda path: path.name.lower(),
    )


def _relative_posix(path: Path, project_root: Path) -> str:
    return path.relative_to(project_root).as_posix()


def _truncate(value: str, limit: int) -> str:
    text = value.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _slugify(value: str) -> str:
    text = value.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "rule"


def _first_meaningful_line(content: str) -> str:
    for raw in content.splitlines():
        line = raw.strip()
        if not line or line.startswith("<!--"):
            continue
        return line
    return ""


def _extract_structured_value(content: str, keys: tuple[str, ...]) -> str:
    for raw in content.splitlines():
        line = raw.strip()
        for key in keys:
            match = re.match(rf"{re.escape(key)}\s*:\s*(.+)$", line, re.IGNORECASE)
            if not match:
                continue
            value = match.group(1).strip().strip("\"'")
            if value:
                return value
    return ""


def _parse_json_metadata(content: str) -> tuple[str, str]:
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return "", ""
    if not isinstance(data, dict):
        return "", ""
    rule_id = str(data.get("rule_id") or data.get("id") or data.get("name") or "").strip()
    title = str(data.get("title") or data.get("name") or data.get("id") or "").strip()
    return rule_id, title


def _extract_rule_id(path: Path, content: str, relative_path: str) -> str:
    if path.suffix.lower() == ".json":
        rule_id, _ = _parse_json_metadata(content)
        if rule_id:
            return _slugify(rule_id)
    if path.suffix.lower() in {".yaml", ".yml"}:
        rule_id = _extract_structured_value(content, ("rule_id", "id", "name"))
        if rule_id:
            return _slugify(rule_id)
    return _slugify(relative_path.rsplit(".", 1)[0].replace("/", "-"))


def _extract_title(path: Path, content: str) -> str:
    suffix = path.suffix.lower()
    if suffix == ".json":
        _, title = _parse_json_metadata(content)
        if title:
            return title
    if suffix in {".yaml", ".yml"}:
        title = _extract_structured_value(content, ("title", "name", "id"))
        if title:
            return title
    for raw in content.splitlines():
        line = raw.strip()
        if line.startswith("#"):
            title = line.lstrip("#").strip()
            if title:
                return title
    first_line = _first_meaningful_line(content)
    if first_line:
        return first_line.strip("\"'")
    return path.stem.replace("-", " ").replace("_", " ").strip() or path.name


def _summarize_content(content: str) -> str:
    lines: list[str] = []
    for raw in content.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            line = line.lstrip("#").strip()
        lines.append(line)
        if len(" ".join(lines)) >= RULE_SUMMARY_CHAR_LIMIT:
            break
    return _truncate(" ".join(lines), RULE_SUMMARY_CHAR_LIMIT)


def load_project_rules(project_root: Path) -> dict:
    rules_dir = rules_dir_path(project_root)
    rule_files: list[dict] = []
    guidance_files = [_relative_posix(path, project_root) for path in guidance_file_paths(project_root)]

    if rules_dir.exists():
        for path in sorted(rules_dir.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in SUPPORTED_RULE_SUFFIXES:
                continue
            content = path.read_text(encoding="utf-8")
            relative_path = _relative_posix(path, project_root)
            rule_files.append(
                {
                    "id": _extract_rule_id(path, content, relative_path),
                    "title": _extract_title(path, content),
                    "path": relative_path,
                    "format": path.suffix.lower().lstrip("."),
                    "summary": _summarize_content(content),
                    "content": _truncate(content, RULE_CONTENT_CHAR_LIMIT),
                }
            )

    precedence_targets = ", ".join(guidance_files) if guidance_files else "root agent guidance files"
    return {
        "enabled": bool(rule_files),
        "rules_dir": _relative_posix(rules_dir, project_root),
        "agent_guidance_files": guidance_files,
        "precedence_note": (
            f"Project rules under rules/ override {precedence_targets} when they conflict."
        ),
        "files": rule_files,
    }
