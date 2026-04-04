#!/usr/bin/env python3
"""
Shared path and state helpers for the VibeFlow v2 layout.

The refactor keeps VibeFlow file-driven, but separates:
- internal state under .vibeflow/
- change artifacts under docs/changes/<change-id>/
- build execution state in feature-list.json
- architecture specs under docs/architecture/

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

POLICY_PHASE_FIELDS = (
    "required_artifacts",
    "required_checkpoints",
    "required_approvals",
    "completion_evidence",
    "blocking_conditions",
)


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
        "current_phase": "spark",
        "active_change": {
            "id": change_id,
            "root": change_root,
        },
        "artifacts": {
            "spark": f"{change_root}/brief.md",
            "requirements": f"{change_root}/brief.md",
            "ucd": f"{change_root}/ucd.md",
            "design": f"{change_root}/design.md",
            "design_review": f"{change_root}/design.md",
            "tasks": f"{change_root}/tasks.md",
            "review": f"{change_root}/verification/review.md",
            "system_test": f"{change_root}/verification/system-test.md",
            "qa": f"{change_root}/verification/qa.md",
        },
        "phase_history": [],
        "checkpoints": {
            "quick_ready": False,
            "spark": False,
            "design": False,
            "tasks": False,
            "build": False,
            "build_init": False,
            "build_config": False,
            "build_work": False,
            "review": False,
            "test": False,
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
            "enabled": True,
            "max_steps": 20,
            "max_retries_per_phase": 0,
            "parallel_build": True,
            "parallel_build_workers": 2,
            "manual_only": [
                "increment",
                "spark",
                "design",
                "tasks",
                "quick",
            ],
            "auto_runnable": [
                "build",
                "review",
                "test",
                "ship",
                "reflect",
            ],
            "retryable": [
                "build",
                "review",
                "test",
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


def policy_path(project_root: Path) -> Path:
    return project_root / ".vibeflow" / "policy.yaml"


def feature_list_path(project_root: Path) -> Path:
    return project_root / "feature-list.json"


def release_notes_path(project_root: Path) -> Path:
    return project_root / "RELEASE_NOTES.md"


def overview_root(project_root: Path) -> Path:
    return project_root / "docs" / "overview"


def overview_readme_path(project_root: Path) -> Path:
    return overview_root(project_root) / "README.md"


def overview_project_path(project_root: Path) -> Path:
    return overview_root(project_root) / "PROJECT.md"


def overview_architecture_path(project_root: Path) -> Path:
    return overview_root(project_root) / "ARCHITECTURE.md"


def overview_current_state_path(project_root: Path) -> Path:
    return overview_root(project_root) / "CURRENT-STATE.md"


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


def project_rules_dir(project_root: Path) -> Path:
    return project_root / "rules"


def build_reports_dir(project_root: Path) -> Path:
    return project_root / ".vibeflow" / "build-reports"


def codebase_map_json_path(project_root: Path) -> Path:
    return project_root / ".vibeflow" / "codebase-map.json"


def codebase_map_md_path(project_root: Path) -> Path:
    return project_root / ".vibeflow" / "codebase-map.md"


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
    if key == "spark":
        return change_root(project_root, state) / "brief.md"
    return change_root(project_root, state) / f"{key}.md"


def codebase_impact_json_path(project_root: Path, state: dict) -> Path:
    return change_root(project_root, state) / "codebase-impact.json"


def codebase_impact_md_path(project_root: Path, state: dict) -> Path:
    return change_root(project_root, state) / "codebase-impact.md"


def path_contract(project_root: Path, state: dict | None = None) -> dict:
    loaded_state = state or load_state(project_root)
    return {
        "state": state_path(project_root),
        "policy": policy_path(project_root),
        "workflow": workflow_path(project_root),
        "feature_list": feature_list_path(project_root),
        "release_notes": release_notes_path(project_root),
        "overview_root": overview_root(project_root),
        "overview": {
            "readme": overview_readme_path(project_root),
            "project": overview_project_path(project_root),
            "architecture": overview_architecture_path(project_root),
            "current_state": overview_current_state_path(project_root),
        },
        "increment_queue": increment_queue_path(project_root),
        "increment_history": increment_history_path(project_root),
        "increment_requests_dir": increment_requests_dir(project_root),
        "session_log": session_log_path(project_root),
        "build_guide": build_guide_path(project_root),
        "services_guide": services_guide_path(project_root),
        "build_reports_dir": build_reports_dir(project_root),
        "rules_dir": project_rules_dir(project_root),
        "change_root": change_root(project_root, loaded_state),
        "codebase_map_json": codebase_map_json_path(project_root),
        "codebase_map_md": codebase_map_md_path(project_root),
        "spec_facts": project_root / "docs" / "architecture" / ".spec-facts.json",
        "spec_inferences": project_root / "docs" / "architecture" / ".spec-inferences.json",
        "spec_architecture": project_root / "docs" / "architecture" / "full-spec.md",
        "codebase_impact_json": codebase_impact_json_path(project_root, loaded_state),
        "codebase_impact_md": codebase_impact_md_path(project_root, loaded_state),
        "artifacts": {
            key: resolve_artifact_path(project_root, loaded_state, key)
            for key in [
                "spark",
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


def mode_selection_required(project_root: Path) -> bool:
    return not state_path(project_root).exists()


def selected_mode(project_root: Path) -> str | None:
    path = state_path(project_root)
    if not path.exists():
        return None
    mode = str(load_state(project_root).get("mode") or "").strip()
    return mode or None


def default_policy() -> dict:
    return {
        "version": 1,
        "phases": {
            "spark": {
                "required_artifacts": ["spark"],
                "required_checkpoints": [],
                "required_approvals": ["spark"],
                "completion_evidence": ["artifact:spark"],
                "blocking_conditions": [],
            },
            "design": {
                "required_artifacts": ["design"],
                "required_checkpoints": [],
                "required_approvals": ["design"],
                "completion_evidence": ["artifact:design"],
                "blocking_conditions": [],
            },
            "tasks": {
                "required_artifacts": ["tasks"],
                "required_checkpoints": [],
                "required_approvals": ["tasks"],
                "completion_evidence": ["artifact:tasks"],
                "blocking_conditions": [],
            },
            "build": {
                "required_artifacts": ["tasks"],
                "required_checkpoints": ["tasks"],
                "required_approvals": [],
                "completion_evidence": [],
                "blocking_conditions": [],
            },
            "review": {
                "required_artifacts": ["review"],
                "required_checkpoints": [],
                "required_approvals": ["review"],
                "completion_evidence": ["artifact:review"],
                "blocking_conditions": [],
            },
            "test": {
                "required_artifacts": ["system_test"],
                "required_checkpoints": [],
                "required_approvals": ["test"],
                "completion_evidence": ["artifact:system_test"],
                "blocking_conditions": [],
            },
            "ship": {
                "required_artifacts": ["release_notes"],
                "required_checkpoints": [],
                "required_approvals": ["ship"],
                "completion_evidence": ["release_notes_exists"],
                "blocking_conditions": [],
            },
            "reflect": {
                "required_artifacts": [],
                "required_checkpoints": [],
                "required_approvals": ["reflect"],
                "completion_evidence": [],
                "blocking_conditions": [],
            },
            "done": {
                "required_artifacts": [],
                "required_checkpoints": [],
                "required_approvals": [],
                "completion_evidence": ["all_phases_complete"],
                "blocking_conditions": [],
            },
        },
    }


def _parse_policy_scalar(value: str):
    if value == "":
        return ""
    if value.startswith("[") or value.startswith("{"):
        return json.loads(value)
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if value.startswith('"') and value.endswith('"'):
        return json.loads(value)
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        return value


def _parse_policy_text(text: str) -> dict:
    data: dict = {}
    current_phase: str | None = None
    in_phases = False

    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        if indent == 0:
            current_phase = None
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()
            if key == "phases":
                data["phases"] = {}
                in_phases = True
                continue
            in_phases = False
            data[key] = _parse_policy_scalar(value)
            continue

        if indent == 2 and in_phases and stripped.endswith(":"):
            current_phase = stripped[:-1].strip()
            data.setdefault("phases", {})[current_phase] = {}
            continue

        if indent == 4 and in_phases and current_phase:
            key, _, value = stripped.partition(":")
            data["phases"][current_phase][key.strip()] = _parse_policy_scalar(value.strip())
            continue

        raise ValueError(f"Unsupported policy syntax: {raw_line}")

    return data


def _normalize_policy_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def load_policy(project_root: Path) -> dict:
    merged = deepcopy(default_policy())
    path = policy_path(project_root)
    if not path.exists():
        return merged

    loaded = _parse_policy_text(path.read_text(encoding="utf-8"))
    version = loaded.get("version")
    if isinstance(version, int):
        merged["version"] = version

    phases = loaded.get("phases") or {}
    if not isinstance(phases, dict):
        return merged

    for phase_name, config in phases.items():
        if not isinstance(config, dict):
            continue
        target = merged["phases"].setdefault(
            phase_name,
            {field: [] for field in POLICY_PHASE_FIELDS},
        )
        for field in POLICY_PHASE_FIELDS:
            if field in config:
                target[field] = _normalize_policy_list(config.get(field))

    return merged


def default_runtime_invariant() -> dict:
    return {
        "phase": "",
        "reason": "",
        "reason_code": "",
        "status": "clear",
        "updated_at": "",
    }


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
        "invariant": default_runtime_invariant(),
    }


def load_runtime(project_root: Path) -> dict:
    state = load_state(project_root)
    data = state.get("runtime") or {}
    merged = default_runtime()
    merged.update(
        {
            k: v
            for k, v in data.items()
            if k not in {"attempts", "events", "phase_runs", "feature_runs", "invariant"}
        }
    )
    for key in ("attempts", "events", "phase_runs", "feature_runs", "invariant"):
        loaded = data.get(key)
        if isinstance(loaded, dict) and isinstance(merged.get(key), dict):
            merged[key].update(loaded)
        elif isinstance(loaded, list):
            merged[key] = loaded
    return merged


def save_runtime(project_root: Path, runtime: dict) -> Path:
    state = ensure_state(project_root)
    state["runtime"] = deepcopy(runtime)
    return save_state(project_root, state)


def ensure_runtime(project_root: Path) -> dict:
    state = ensure_state(project_root)
    if isinstance(state.get("runtime"), dict):
        return load_runtime(project_root)
    runtime = default_runtime()
    save_runtime(project_root, runtime)
    return runtime


def set_runtime_invariant(
    runtime: dict,
    *,
    phase: str = "",
    reason: str = "",
    reason_code: str = "",
    status: str = "clear",
    updated_at: str | None = None,
) -> dict:
    invariant = deepcopy(default_runtime_invariant())
    loaded = runtime.get("invariant")
    if isinstance(loaded, dict):
        invariant.update(loaded)
    invariant.update(
        {
            "phase": phase,
            "reason": reason,
            "reason_code": reason_code,
            "status": status,
            "updated_at": updated_at or datetime.now().astimezone().isoformat(timespec="seconds"),
        }
    )
    runtime["invariant"] = invariant
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
    state["current_phase"] = "spark"
    set_checkpoint(state, "quick_ready", False)

    meta = quick_meta(state)
    meta["decision"] = "promoted"
    meta["promoted_from_quick"] = True
    meta["promotion_reason"] = reason
    state["quick_meta"] = meta

    for checkpoint in (
        "spark",
        "design",
        "tasks",
        "build",
        "review",
        "test",
        "ship",
        "reflect",
    ):
        set_checkpoint(state, checkpoint, False)

    if project_root is not None:
        for artifact in (feature_list_path(project_root),):
            if artifact.exists():
                artifact.unlink()


def update_active_change(state: dict, change_id: str) -> None:
    root = f"docs/changes/{change_id}"
    state["active_change"] = {"id": change_id, "root": root}
    state["artifacts"] = {
        "spark": f"{root}/brief.md",
        "requirements": f"{root}/brief.md",
        "ucd": f"{root}/ucd.md",
        "design": f"{root}/design.md",
        "design_review": f"{root}/design.md",
        "tasks": f"{root}/tasks.md",
        "review": f"{root}/verification/review.md",
        "system_test": f"{root}/verification/system-test.md",
        "qa": f"{root}/verification/qa.md",
    }


def append_phase_history(project_root: Path, entry: dict) -> Path:
    state = load_state(project_root)
    history = state.setdefault("phase_history", [])
    if not isinstance(history, list):
        history = []
        state["phase_history"] = history
    history.append(deepcopy(entry))
    save_state(project_root, state)
    return state_path(project_root)
