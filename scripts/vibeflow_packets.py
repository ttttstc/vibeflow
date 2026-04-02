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
from vibeflow_rules import load_project_rules, select_applicable_rules


PACKET_VERSION = 1
SUMMARY_CHAR_LIMIT = 480
SOURCE_REF_KEYS = (
    "spark",
    "requirements",
    "design",
    "build_contract",
    "tasks",
    "build_guide",
    "services_guide",
    "rules",
)


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


def _section_ref(path: Path, section: str) -> str:
    normalized = str(section).strip().replace(".", "-")
    return f"{path}#section-{normalized}" if normalized else str(path)


def _default_source_refs(contract: dict, feature: dict, rules_refs: list[str] | None = None) -> dict[str, list[str]]:
    feature_id = feature.get("id")
    design_section = str(feature.get("design_section") or "").strip()
    requirement_refs = normalize_string_list(feature.get("requirements_refs"))
    default_refs = {
        "spark": [str(contract["artifacts"]["spark"])],
        "requirements": (
            [f"{contract['artifacts']['requirements']}#{ref}" for ref in requirement_refs]
            if requirement_refs
            else [str(contract["artifacts"]["requirements"])]
        ),
        "design": [_section_ref(contract["artifacts"]["design"], design_section)],
        "build_contract": [f"{contract['artifacts']['design']}#build-contract"],
        "tasks": [f"{contract['artifacts']['tasks']}#{_task_anchor(feature_id)}"],
        "build_guide": [str(contract["build_guide"])],
        "services_guide": [str(contract["services_guide"])],
    }
    if rules_refs:
        default_refs["rules"] = list(rules_refs)
    return default_refs


def _normalize_source_refs(
    raw_source_refs,
    contract: dict,
    feature: dict,
    *,
    rules_refs: list[str] | None = None,
) -> dict[str, list[str]]:
    normalized = _default_source_refs(contract, feature, rules_refs=rules_refs)
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


def _normalize_custom_rules(rules_context: dict) -> dict:
    files: list[dict] = []
    for rule in rules_context.get("files") or []:
        if not isinstance(rule, dict):
            continue
        files.append(
            {
                "id": str(rule.get("id") or "").strip(),
                "title": str(rule.get("title") or "").strip(),
                "path": str(rule.get("path") or "").strip(),
                "format": str(rule.get("format") or "").strip(),
                "summary": str(rule.get("summary") or "").strip(),
                "content": str(rule.get("content") or "").strip(),
                "applies_to": rule.get("applies_to") if isinstance(rule.get("applies_to"), dict) else {},
                "checks": normalize_string_list(rule.get("checks")),
            }
        )
    return {
        "enabled": bool(rules_context.get("enabled") and files),
        "precedence_note": str(rules_context.get("precedence_note") or "").strip(),
        "agent_guidance_files": normalize_string_list(rules_context.get("agent_guidance_files")),
        "files": files,
    }


def _rules_summary(custom_rules: dict) -> str:
    if not custom_rules.get("enabled"):
        return ""
    lines: list[str] = []
    for rule in custom_rules.get("files") or []:
        if not isinstance(rule, dict):
            continue
        title = str(rule.get("title") or rule.get("id") or "").strip()
        summary = str(rule.get("summary") or "").strip()
        if title and summary:
            lines.append(f"{title}: {summary}")
        elif title:
            lines.append(title)
        if len(" ".join(lines)) >= SUMMARY_CHAR_LIMIT:
            break
    summary = " ".join(lines).strip()
    if len(summary) <= SUMMARY_CHAR_LIMIT:
        return summary
    return summary[: SUMMARY_CHAR_LIMIT - 3].rstrip() + "..."


def ensure_feature_contract(
    feature: dict,
    project_root: Path,
    state: dict,
    *,
    rules_context: dict | None = None,
    project_language: str = "",
) -> dict:
    contract = path_contract(project_root, state)
    loaded_rules = rules_context or load_project_rules(project_root)
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
    normalized["requirements_refs"] = normalize_string_list(normalized.get("requirements_refs") or normalized.get("requirements"))
    normalized["design_section"] = str(normalized.get("design_section") or "").strip()
    normalized["integration_points"] = normalize_string_list(normalized.get("integration_points"))
    normalized["layers"] = normalize_string_list(normalized.get("layers") or normalized.get("layer"))
    normalized["build_contract_ref"] = (
        str(normalized.get("build_contract_ref") or "").strip() or f"{contract['artifacts']['design']}#build-contract"
    )
    selected_rules = select_applicable_rules(
        project_root,
        rules_context=loaded_rules,
        project_language=project_language,
        file_scope=normalized.get("file_scope") or [],
        layers=normalized.get("layers") or [],
        stage="build",
    )
    rules_refs = [
        str(rule.get("path") or "").strip()
        for rule in selected_rules.get("files") or []
        if str(rule.get("path") or "").strip()
    ]
    normalized["source_refs"] = _normalize_source_refs(
        normalized.get("source_refs"),
        contract,
        normalized,
        rules_refs=rules_refs,
    )
    normalized["custom_rules"] = _normalize_custom_rules(selected_rules)

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


def build_feature_packet(
    project_root: Path,
    state: dict,
    feature: dict,
    *,
    rules_context: dict | None = None,
    project_language: str = "",
) -> dict:
    loaded_rules = rules_context or load_project_rules(project_root)
    normalized = ensure_feature_contract(
        feature,
        project_root,
        state,
        rules_context=loaded_rules,
        project_language=project_language,
    )
    contract = path_contract(project_root, state)
    commands, workdir, timeout = feature_execution_config(normalized)
    rules_summary = _rules_summary(normalized.get("custom_rules") or {})

    snippets = {
        "spark_summary": summarize_markdown(contract["artifacts"]["spark"]),
        "requirements_summary": summarize_markdown(contract["artifacts"]["requirements"]),
        "design_summary": summarize_markdown(contract["artifacts"]["design"]),
        "tasks_summary": summarize_markdown(contract["artifacts"]["tasks"]),
        "rules_summary": rules_summary,
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
        "design_contract": {
            "build_contract_ref": normalized.get("build_contract_ref") or "",
            "design_section": normalized.get("design_section") or "",
            "requirements_refs": normalized.get("requirements_refs") or [],
            "integration_points": normalized.get("integration_points") or [],
        },
        "custom_rules": normalized.get("custom_rules") or {},
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
    for key in ("requirements", "design", "build_contract", "tasks"):
        if not normalize_string_list(source_refs.get(key)):
            issues.append(f"source_refs.{key} is required.")

    custom_rules = packet.get("custom_rules") if isinstance(packet.get("custom_rules"), dict) else {}
    if custom_rules.get("enabled"):
        if not normalize_string_list(source_refs.get("rules")):
            issues.append("source_refs.rules is required when custom_rules are enabled.")
        if not str(custom_rules.get("precedence_note") or "").strip():
            issues.append("custom_rules.precedence_note is required when custom_rules are enabled.")
        files = custom_rules.get("files")
        if not isinstance(files, list) or not files:
            issues.append("custom_rules.files must contain at least one rule when custom_rules are enabled.")

    return issues


def write_feature_packet(
    project_root: Path,
    state: dict,
    feature: dict,
    *,
    rules_context: dict | None = None,
    project_language: str = "",
) -> Path:
    packet = build_feature_packet(project_root, state, feature, rules_context=rules_context, project_language=project_language)
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
    rules_context = load_project_rules(project_root)
    project_language = str(((payload.get("tech_stack") or {}).get("language") or "")).strip()
    normalized_features = [
        ensure_feature_contract(
            feature,
            project_root,
            state,
            rules_context=rules_context,
            project_language=project_language,
        )
        for feature in payload.get("features", [])
    ]
    payload["features"] = normalized_features

    packet_dir = path_contract(project_root, state)["packets_dir"]
    packet_dir.mkdir(parents=True, exist_ok=True)
    active_paths: set[Path] = set()
    for feature in normalized_features:
        packet_path = write_feature_packet(
            project_root,
            state,
            feature,
            rules_context=rules_context,
            project_language=project_language,
        )
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
        "applied_rule_ids": [
            str(rule.get("id") or "").strip()
            for rule in ((packet_data.get("custom_rules") or {}).get("files") or [])
            if str(rule.get("id") or "").strip()
        ],
        "summary": result.get("detail") or "",
        "needs_clarification": False,
        "error": "" if result.get("ok") else result.get("detail") or "",
    }
    path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
