#!/usr/bin/env python3
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from vibeflow_paths import (
    build_packet_path,
    build_packet_result_path,
    path_contract,
)


PACKET_VERSION = 1
SUMMARY_CHAR_LIMIT = 480
SOURCE_REF_KEYS = ("think", "plan", "requirements", "design", "tasks", "build_guide", "services_guide")


def normalize_string_list(value) -> list[str]:
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    if isinstance(value, list):
        normalized: list[str] = []
        for item in value:
            text = str(item).strip()
            if text:
                normalized.append(text)
        return normalized
    return []


def feature_execution_config(feature: dict) -> tuple[list[str], str, int]:
    autopilot = feature.get("autopilot") if isinstance(feature.get("autopilot"), dict) else {}
    commands = normalize_string_list(autopilot.get("commands"))
    if not commands:
        commands = normalize_string_list(feature.get("autopilot_commands"))
    if not commands and feature.get("command"):
        commands = normalize_string_list(feature.get("command"))

    workdir = str(autopilot.get("workdir") or feature.get("autopilot_workdir") or ".").strip() or "."
    timeout = int(autopilot.get("timeout_sec") or feature.get("autopilot_timeout_sec") or 300)
    return commands, workdir, timeout


def _task_anchor(feature_id: int | str) -> str:
    return f"feature-{feature_id}"


def _default_source_refs(contract: dict, feature_id: int | str) -> dict[str, list[str]]:
    default_refs = {
        "think": [str(contract["artifacts"]["think"])],
        "plan": [str(contract["artifacts"]["plan"])],
        "requirements": [str(contract["artifacts"]["requirements"])],
        "design": [str(contract["artifacts"]["design"])],
        "tasks": [f"{contract['artifacts']['tasks']}#{_task_anchor(feature_id)}"],
        "build_guide": [str(contract["build_guide"])],
        "services_guide": [str(contract["services_guide"])],
    }
    return default_refs


def _normalize_source_refs(raw_source_refs, contract: dict, feature_id: int | str) -> dict[str, list[str]]:
    normalized = _default_source_refs(contract, feature_id)
    if not isinstance(raw_source_refs, dict):
        return normalized

    for key, value in raw_source_refs.items():
        if key not in SOURCE_REF_KEYS:
            continue
        refs = normalize_string_list(value)
        if refs:
            normalized[key] = refs
    return normalized


def summarize_markdown(path: Path, *, limit: int = SUMMARY_CHAR_LIMIT) -> str:
    if not path.exists():
        return ""

    lines: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if not stripped:
            continue
        lines.append(stripped)
        if len(" ".join(lines)) >= limit:
            break

    summary = " ".join(lines)
    if len(summary) <= limit:
        return summary
    return summary[: limit - 3].rstrip() + "..."


def ensure_feature_contract(feature: dict, project_root: Path, state: dict) -> dict:
    contract = path_contract(project_root, state)
    normalized = deepcopy(feature)

    feature_id = normalized.get("id")
    title = str(normalized.get("title") or f"Feature {feature_id}").strip()
    description = str(normalized.get("description") or title).strip()
    commands, workdir, timeout = feature_execution_config(normalized)

    normalized["title"] = title
    normalized["description"] = description
    normalized.setdefault("category", "delivery")
    normalized.setdefault("priority", "medium")
    normalized.setdefault("status", "failing")

    normalized["objective"] = str(normalized.get("objective") or description or title).strip()
    normalized["business_intent"] = str(normalized.get("business_intent") or description or title).strip()
    normalized["out_of_scope"] = normalize_string_list(normalized.get("out_of_scope"))
    normalized["file_scope"] = normalize_string_list(normalized.get("file_scope"))
    normalized["verification_commands"] = normalize_string_list(normalized.get("verification_commands")) or commands
    normalized["verification_steps"] = normalize_string_list(normalized.get("verification_steps"))
    normalized["done_criteria"] = normalize_string_list(normalized.get("done_criteria")) or normalize_string_list(
        normalized.get("verification_steps")
    )
    if not normalized["done_criteria"]:
        normalized["done_criteria"] = [f"Complete {title} and verify the expected behavior."]

    normalized["risk_notes"] = normalize_string_list(normalized.get("risk_notes"))
    normalized["required_configs"] = normalize_string_list(normalized.get("required_configs"))
    normalized["source_refs"] = _normalize_source_refs(normalized.get("source_refs"), contract, feature_id)

    if commands and not normalize_string_list(normalized.get("autopilot_commands")):
        normalized["autopilot_commands"] = commands

    if not isinstance(normalized.get("dependencies"), list):
        normalized["dependencies"] = []

    normalized["autopilot"] = {
        "commands": commands,
        "workdir": workdir,
        "timeout_sec": timeout,
    }
    return normalized


def build_feature_packet(project_root: Path, state: dict, feature: dict) -> dict:
    normalized = ensure_feature_contract(feature, project_root, state)
    contract = path_contract(project_root, state)
    commands, workdir, timeout = feature_execution_config(normalized)

    snippets = {
        "think_summary": summarize_markdown(contract["artifacts"]["think"]),
        "plan_summary": summarize_markdown(contract["artifacts"]["plan"]),
        "requirements_summary": summarize_markdown(contract["artifacts"]["requirements"]),
        "design_summary": summarize_markdown(contract["artifacts"]["design"]),
        "tasks_summary": summarize_markdown(contract["artifacts"]["tasks"]),
    }

    return {
        "version": PACKET_VERSION,
        "change_id": str((state.get("active_change") or {}).get("id") or project_root.name),
        "feature": {
            "id": normalized.get("id"),
            "title": normalized.get("title"),
            "category": normalized.get("category"),
            "priority": normalized.get("priority"),
        },
        "objective": normalized.get("objective"),
        "business_intent": normalized.get("business_intent"),
        "out_of_scope": normalized.get("out_of_scope"),
        "dependencies": normalized.get("dependencies") or [],
        "file_scope": normalized.get("file_scope") or [],
        "verification_commands": normalized.get("verification_commands") or [],
        "verification_steps": normalized.get("verification_steps") or [],
        "done_criteria": normalized.get("done_criteria") or [],
        "risk_notes": normalized.get("risk_notes") or [],
        "required_configs": normalized.get("required_configs") or [],
        "source_refs": normalized.get("source_refs") or {},
        "source_snippets": snippets,
        "execution": {
            "commands": commands,
            "workdir": workdir,
            "timeout_sec": timeout,
        },
    }


def packet_validation_issues(packet: dict) -> list[str]:
    issues: list[str] = []

    feature = packet.get("feature") if isinstance(packet.get("feature"), dict) else {}
    if feature.get("id") in (None, ""):
        issues.append("feature.id is required.")
    if not str(feature.get("title") or "").strip():
        issues.append("feature.title is required.")
    if not str(packet.get("objective") or "").strip():
        issues.append("objective is required.")

    if not normalize_string_list(packet.get("done_criteria")):
        issues.append("done_criteria must contain at least one item.")

    if not normalize_string_list(packet.get("verification_commands")) and not normalize_string_list(packet.get("verification_steps")):
        issues.append("verification_commands or verification_steps must contain at least one item.")

    source_refs = packet.get("source_refs") if isinstance(packet.get("source_refs"), dict) else {}
    for key in ("requirements", "design", "tasks"):
        if not normalize_string_list(source_refs.get(key)):
            issues.append(f"source_refs.{key} is required.")

    return issues


def write_feature_packet(project_root: Path, state: dict, feature: dict) -> Path:
    packet = build_feature_packet(project_root, state, feature)
    path = build_packet_path(project_root, state, feature.get("id"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def load_feature_packet(project_root: Path, state: dict, feature_id: int | str) -> dict | None:
    path = build_packet_path(project_root, state, feature_id)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def sync_feature_packets(project_root: Path, state: dict, payload: dict) -> dict:
    normalized_features = [ensure_feature_contract(feature, project_root, state) for feature in payload.get("features", [])]
    payload["features"] = normalized_features

    packet_dir = path_contract(project_root, state)["packets_dir"]
    packet_dir.mkdir(parents=True, exist_ok=True)
    active_paths: set[Path] = set()
    for feature in normalized_features:
        packet_path = write_feature_packet(project_root, state, feature)
        active_paths.add(packet_path.resolve())

    for stale in packet_dir.glob("feature-*.json"):
        if stale.resolve() not in active_paths:
            stale.unlink()

    return payload


def write_feature_result(project_root: Path, state: dict, result: dict, packet: dict | None = None) -> Path:
    feature_id = result.get("feature_id")
    path = build_packet_result_path(project_root, state, feature_id)
    path.parent.mkdir(parents=True, exist_ok=True)

    packet_data = packet or {}
    feature_info = packet_data.get("feature") if isinstance(packet_data.get("feature"), dict) else {}
    output = {
        "version": PACKET_VERSION,
        "change_id": str((state.get("active_change") or {}).get("id") or project_root.name),
        "feature_id": feature_id,
        "status": "passing" if result.get("ok") else "failing",
        "feature_title": result.get("title") or feature_info.get("title") or "Untitled",
        "implemented_files": normalize_string_list(packet_data.get("file_scope")),
        "verification": {
            "commands": normalize_string_list((packet_data.get("execution") or {}).get("commands")),
            "passed": bool(result.get("ok")),
        },
        "summary": result.get("detail") or "",
        "needs_clarification": False,
        "error": "" if result.get("ok") else result.get("detail") or "",
    }
    path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
