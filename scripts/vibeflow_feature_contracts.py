#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from vibeflow_paths import path_contract
from vibeflow_rules import load_project_rules, select_applicable_rules


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


def sync_feature_contracts(project_root: Path, state: dict, payload: dict) -> dict:
    rules_context = load_project_rules(project_root)
    project_language = str(((payload.get("tech_stack") or {}).get("language") or "")).strip()
    payload["features"] = [
        ensure_feature_contract(
            feature,
            project_root,
            state,
            rules_context=rules_context,
            project_language=project_language,
        )
        for feature in payload.get("features", [])
    ]
    return payload
