#!/usr/bin/env python3
"""
Shared path and state helpers for the VibeFlow v2 layout.

The refactor keeps VibeFlow file-driven, but separates:
- internal state under .vibeflow/
- change artifacts under docs/changes/<change-id>/
- build execution state in feature-list.json

This module is intentionally lightweight so both scripts and tests can import it.
"""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path


def slugify(value: str) -> str:
    cleaned = []
    previous_dash = False
    for ch in value.lower():
        if ch.isalnum():
            cleaned.append(ch)
            previous_dash = False
        else:
            if not previous_dash:
                cleaned.append("-")
            previous_dash = True
    slug = "".join(cleaned).strip("-")
    return slug or "work-package"


def default_change_id(topic: str | None = None, now: datetime | None = None) -> str:
    current = now or datetime.now()
    suffix = slugify(topic or "work-package")
    return f"{current.strftime('%Y-%m-%d')}-{suffix}"


def default_state(project_root: Path, topic: str | None = None) -> dict:
    change_id = default_change_id(topic)
    change_root = f"docs/changes/{change_id}"
    return {
        "version": 2,
        "mode": "full",
        "context": "greenfield",
        "current_phase": "think",
        "active_change": {
            "id": change_id,
            "root": change_root,
        },
        "artifacts": {
            "think": f"{change_root}/context.md",
            "plan": f"{change_root}/proposal.md",
            "requirements": f"{change_root}/requirements.md",
            "ucd": f"{change_root}/ucd.md",
            "design": f"{change_root}/design.md",
            "design_review": f"{change_root}/design-review.md",
            "tasks": f"{change_root}/tasks.md",
            "review": f"{change_root}/verification/review.md",
            "system_test": f"{change_root}/verification/system-test.md",
            "qa": f"{change_root}/verification/qa.md",
        },
        "checkpoints": {
            "quick_ready": False,
            "think": False,
            "plan": False,
            "requirements": False,
            "design": False,
            "build_init": False,
            "build_config": False,
            "build_work": False,
            "review": False,
            "test_system": False,
            "test_qa": False,
            "ship": False,
            "reflect": False,
        },
    }


def state_path(project_root: Path) -> Path:
    return project_root / ".vibeflow" / "state.json"


def workflow_path(project_root: Path) -> Path:
    state_root = project_root / ".vibeflow"
    for ext in (".yaml", ".yml"):
        candidate = state_root / f"workflow{ext}"
        if candidate.exists():
            return candidate
    return state_root / "workflow.yaml"


def work_config_path(project_root: Path) -> Path:
    return project_root / ".vibeflow" / "work-config.json"


def feature_list_path(project_root: Path) -> Path:
    return project_root / "feature-list.json"


def release_notes_path(project_root: Path) -> Path:
    return project_root / "RELEASE_NOTES.md"


def phase_history_path(project_root: Path) -> Path:
    return project_root / ".vibeflow" / "phase-history.json"


def increments_dir(project_root: Path) -> Path:
    return project_root / ".vibeflow" / "increments"


def increment_queue_path(project_root: Path) -> Path:
    return increments_dir(project_root) / "queue.json"


def increment_history_path(project_root: Path) -> Path:
    return increments_dir(project_root) / "history.json"


def increment_requests_dir(project_root: Path) -> Path:
    return increments_dir(project_root) / "requests"


def session_log_path(project_root: Path) -> Path:
    return project_root / ".vibeflow" / "logs" / "session-log.md"


def guides_dir(project_root: Path) -> Path:
    return project_root / ".vibeflow" / "guides"


def build_guide_path(project_root: Path) -> Path:
    return guides_dir(project_root) / "build.md"


def services_guide_path(project_root: Path) -> Path:
    return guides_dir(project_root) / "services.md"


def change_root(project_root: Path, state: dict) -> Path:
    active = state.get("active_change") or {}
    rel = active.get("root")
    if rel:
        return project_root / Path(rel)
    change_id = default_change_id()
    return project_root / "docs" / "changes" / change_id


def resolve_artifact_path(project_root: Path, state: dict, key: str) -> Path:
    artifacts = state.get("artifacts") or {}
    rel = artifacts.get(key)
    if rel:
        return project_root / Path(rel)
    return change_root(project_root, state) / f"{key}.md"


def path_contract(project_root: Path, state: dict | None = None) -> dict:
    loaded_state = state or load_state(project_root)
    return {
        "state": state_path(project_root),
        "workflow": workflow_path(project_root),
        "work_config": work_config_path(project_root),
        "feature_list": feature_list_path(project_root),
        "release_notes": release_notes_path(project_root),
        "phase_history": phase_history_path(project_root),
        "increment_queue": increment_queue_path(project_root),
        "increment_history": increment_history_path(project_root),
        "increment_requests_dir": increment_requests_dir(project_root),
        "session_log": session_log_path(project_root),
        "build_guide": build_guide_path(project_root),
        "services_guide": services_guide_path(project_root),
        "change_root": change_root(project_root, loaded_state),
        "artifacts": {
            key: resolve_artifact_path(project_root, loaded_state, key)
            for key in [
                "think",
                "plan",
                "requirements",
                "ucd",
                "design",
                "design_review",
                "tasks",
                "review",
                "system_test",
                "qa",
            ]
        },
    }


def load_state(project_root: Path) -> dict:
    path = state_path(project_root)
    if not path.exists():
        return default_state(project_root)
    data = json.loads(path.read_text(encoding="utf-8"))
    merged = default_state(project_root)
    merged.update({k: v for k, v in data.items() if k not in {"active_change", "artifacts", "checkpoints"}})
    for key in ("active_change", "artifacts", "checkpoints"):
        if key in data and isinstance(data[key], dict):
            merged[key].update(data[key])
    return merged


def save_state(project_root: Path, state: dict) -> Path:
    path = state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def ensure_state(project_root: Path, topic: str | None = None) -> dict:
    path = state_path(project_root)
    if path.exists():
        return load_state(project_root)
    state = default_state(project_root, topic=topic)
    save_state(project_root, state)
    return state


def checkpoint_done(state: dict, key: str) -> bool:
    return bool((state.get("checkpoints") or {}).get(key))


def set_checkpoint(state: dict, key: str, done: bool = True, phase: str | None = None) -> None:
    state.setdefault("checkpoints", {})[key] = done
    if phase is not None:
        state["current_phase"] = phase


def update_active_change(state: dict, change_id: str) -> None:
    root = f"docs/changes/{change_id}"
    state["active_change"] = {"id": change_id, "root": root}
    state["artifacts"] = {
        "think": f"{root}/context.md",
        "plan": f"{root}/proposal.md",
        "requirements": f"{root}/requirements.md",
        "ucd": f"{root}/ucd.md",
        "design": f"{root}/design.md",
        "design_review": f"{root}/design-review.md",
        "tasks": f"{root}/tasks.md",
        "review": f"{root}/verification/review.md",
        "system_test": f"{root}/verification/system-test.md",
        "qa": f"{root}/verification/qa.md",
    }


def append_phase_history(project_root: Path, entry: dict) -> Path:
    path = phase_history_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        history = json.loads(path.read_text(encoding="utf-8"))
    else:
        history = []
    history.append(deepcopy(entry))
    path.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
