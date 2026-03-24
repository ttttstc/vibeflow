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


QUICK_ALLOWED_CATEGORIES = {
    "bugfix",
    "hotfix",
    "small-change",
    "config",
    "docs",
    "tests",
    "dependency",
}

QUICK_BLOCKING_RISK_FLAGS = {
    "core-logic",
    "payment",
    "auth",
    "data",
    "external-api",
    "security",
    "multi-service",
    "multi-database",
    "ui-redesign",
    "migration",
    "new-feature",
    "architecture",
}

DEFAULT_QUICK_PROMOTION_RULES = [
    "scope grows beyond a small bounded change",
    "risk touches auth, payment, security, or data migration",
    "work spans multiple services, databases, or ownership boundaries",
    "design decisions are no longer obvious",
]


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
        "quick_meta": {
            "decision": "pending",
            "category": "",
            "scope": "",
            "touchpoints": [],
            "risk_flags": [],
            "validation_plan": "",
            "rollback_plan": "",
            "promote_to_full_if": list(DEFAULT_QUICK_PROMOTION_RULES),
            "rejected_reasons": [],
            "promoted_from_quick": False,
            "promotion_reason": "",
        },
        "autopilot": {
            "enabled": False,
            "max_steps": 20,
            "max_retries_per_phase": 0,
            "parallel_build": True,
            "parallel_build_workers": 2,
            "manual_only": [
                "increment",
                "think",
                "template-selection",
                "plan",
                "requirements",
                "design",
                "quick",
            ],
            "auto_runnable": [
                "build-init",
                "build-config",
                "build-work",
                "review",
                "test-system",
                "test-qa",
                "ship",
                "reflect",
            ],
            "retryable": [
                "build-work",
                "review",
                "test-system",
                "test-qa",
            ],
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


def runtime_path(project_root: Path) -> Path:
    return project_root / ".vibeflow" / "runtime.json"


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
        "runtime": runtime_path(project_root),
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
    merged.update(
        {
            k: v
            for k, v in data.items()
            if k not in {"active_change", "artifacts", "checkpoints", "quick_meta", "autopilot"}
        }
    )
    for key in ("active_change", "artifacts", "checkpoints", "quick_meta", "autopilot"):
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


def default_runtime() -> dict:
    return {
        "run_id": "",
        "status": "idle",
        "current_phase": "",
        "current_action": "",
        "friendly_message": "准备就绪，随时可以继续。",
        "last_heartbeat_at": "",
        "stop_reason": "",
        "step_count": 0,
        "attempts": {},
        "events": [],
        "phase_runs": [],
        "feature_runs": [],
    }


def load_runtime(project_root: Path) -> dict:
    path = runtime_path(project_root)
    if not path.exists():
        return default_runtime()
    data = json.loads(path.read_text(encoding="utf-8"))
    merged = default_runtime()
    merged.update({k: v for k, v in data.items() if k not in {"attempts", "events", "phase_runs", "feature_runs"}})
    for key in ("attempts", "events", "phase_runs", "feature_runs"):
        loaded = data.get(key)
        if isinstance(loaded, dict) and isinstance(merged.get(key), dict):
            merged[key].update(loaded)
        elif isinstance(loaded, list):
            merged[key] = loaded
    return merged


def save_runtime(project_root: Path, runtime: dict) -> Path:
    path = runtime_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(runtime, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def ensure_runtime(project_root: Path) -> dict:
    path = runtime_path(project_root)
    if path.exists():
        return load_runtime(project_root)
    runtime = default_runtime()
    save_runtime(project_root, runtime)
    return runtime


def checkpoint_done(state: dict, key: str) -> bool:
    return bool((state.get("checkpoints") or {}).get(key))


def set_checkpoint(state: dict, key: str, done: bool = True, phase: str | None = None) -> None:
    state.setdefault("checkpoints", {})[key] = done
    if phase is not None:
        state["current_phase"] = phase


def quick_meta(state: dict) -> dict:
    meta = deepcopy(default_state(Path("."))["quick_meta"])
    loaded = state.get("quick_meta") or {}
    if isinstance(loaded, dict):
        meta.update(loaded)
    return meta


def quick_eligibility_issues(state: dict) -> list[str]:
    meta = quick_meta(state)
    issues: list[str] = []

    category = str(meta.get("category") or "").strip().lower()
    if not category:
        issues.append("quick_meta.category is required.")
    elif category not in QUICK_ALLOWED_CATEGORIES:
        issues.append(f"category '{category}' is not eligible for Quick Mode.")

    scope = str(meta.get("scope") or "").strip()
    if not scope:
        issues.append("quick_meta.scope is required.")

    touchpoints = meta.get("touchpoints") or []
    if not isinstance(touchpoints, list) or not [item for item in touchpoints if str(item).strip()]:
        issues.append("quick_meta.touchpoints must list the affected files or modules.")

    validation_plan = str(meta.get("validation_plan") or "").strip()
    if not validation_plan:
        issues.append("quick_meta.validation_plan is required.")

    rollback_plan = str(meta.get("rollback_plan") or "").strip()
    if not rollback_plan:
        issues.append("quick_meta.rollback_plan is required.")

    risk_flags = meta.get("risk_flags") or []
    normalized_flags = {str(flag).strip().lower() for flag in risk_flags if str(flag).strip()}
    blocked_flags = sorted(normalized_flags & QUICK_BLOCKING_RISK_FLAGS)
    if blocked_flags:
        issues.append(f"risk flags require Full Mode: {', '.join(blocked_flags)}.")

    decision = str(meta.get("decision") or "pending").strip().lower()
    if decision == "rejected":
        rejected = meta.get("rejected_reasons") or []
        suffix = f" Reasons: {'; '.join(str(item) for item in rejected if str(item).strip())}" if rejected else ""
        issues.append(f"Quick Mode was rejected.{suffix}".strip())

    return issues


def quick_required_artifacts(project_root: Path, state: dict) -> dict[str, Path]:
    contract = path_contract(project_root, state)
    return {
        "design": contract["artifacts"]["design"],
        "tasks": contract["artifacts"]["tasks"],
    }


def quick_readiness_issues(project_root: Path, state: dict) -> list[str]:
    issues = quick_eligibility_issues(state)
    if not checkpoint_done(state, "quick_ready"):
        issues.append("quick_ready checkpoint is not set.")

    meta = quick_meta(state)
    if str(meta.get("decision") or "pending").strip().lower() != "approved":
        issues.append("quick_meta.decision must be 'approved' before Quick Mode can build.")

    for artifact_name, artifact_path in quick_required_artifacts(project_root, state).items():
        if not artifact_path.exists():
            issues.append(f"Quick Mode requires {artifact_name} artifact: {artifact_path}.")

    return issues


def mark_quick_approved(
    state: dict,
    *,
    category: str,
    scope: str,
    touchpoints: list[str],
    validation_plan: str,
    rollback_plan: str,
    risk_flags: list[str] | None = None,
    promote_to_full_if: list[str] | None = None,
) -> None:
    meta = quick_meta(state)
    meta.update(
        {
            "decision": "approved",
            "category": category,
            "scope": scope,
            "touchpoints": touchpoints,
            "risk_flags": risk_flags or [],
            "validation_plan": validation_plan,
            "rollback_plan": rollback_plan,
            "promote_to_full_if": promote_to_full_if or list(DEFAULT_QUICK_PROMOTION_RULES),
            "rejected_reasons": [],
        }
    )
    state["quick_meta"] = meta


def promote_quick_to_full(state: dict, reason: str = "", project_root: Path | None = None) -> None:
    state["mode"] = "full"
    state["current_phase"] = "think"
    set_checkpoint(state, "quick_ready", False)

    meta = quick_meta(state)
    meta["decision"] = "promoted"
    meta["promoted_from_quick"] = True
    meta["promotion_reason"] = reason
    state["quick_meta"] = meta

    for checkpoint in (
        "think",
        "plan",
        "requirements",
        "design",
        "build_init",
        "build_config",
        "build_work",
        "review",
        "test_system",
        "test_qa",
        "ship",
        "reflect",
    ):
        set_checkpoint(state, checkpoint, False)

    if project_root is not None:
        for artifact in (feature_list_path(project_root), work_config_path(project_root)):
            if artifact.exists():
                artifact.unlink()


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
