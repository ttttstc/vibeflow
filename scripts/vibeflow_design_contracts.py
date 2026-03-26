#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from vibeflow_paths import load_state, path_contract


FEATURE_HEADING_RE = re.compile(r"^(?P<section>\d+(?:\.\d+)*)\s+Feature:\s+(?P<title>.+)$")
REQUIREMENT_REF_RE = re.compile(r"\b(?:FR|NFR|IFR)-\d+\b", re.IGNORECASE)
BUILD_CONTRACT_MARKERS = ("build contract", "execution readiness", "execution contract")
IMPLEMENTATION_CONTRACT_MARKER = "implementation contract"


def dedupe_preserve_order(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def normalize_string_list(value) -> list[str]:
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            text = str(item).strip()
            if text:
                result.append(text)
        return dedupe_preserve_order(result)
    return []


def normalize_int_list(value) -> list[int]:
    result: list[int] = []
    for item in value or []:
        if isinstance(item, bool):
            continue
        if isinstance(item, int):
            result.append(item)
            continue
        text = str(item).strip()
        if text.isdigit():
            result.append(int(text))
    return result


def normalize_required_configs(value) -> list[dict]:
    configs: list[dict] = []
    if not isinstance(value, list):
        return configs
    for item in value:
        if not isinstance(item, dict):
            continue
        normalized = {
            "name": str(item.get("name") or "").strip(),
            "type": str(item.get("type") or "").strip(),
            "description": str(item.get("description") or "").strip(),
            "required_by": normalize_int_list(item.get("required_by")),
        }
        for optional_key in ("key", "path", "check_hint", "default"):
            text = str(item.get(optional_key) or "").strip()
            if text:
                normalized[optional_key] = text
        configs.append(normalized)
    return configs


def build_contract_ref(design_path: Path) -> str:
    return f"{design_path}#build-contract"


def extract_toml_blocks(text: str) -> list[dict]:
    blocks: list[dict] = []
    heading_stack: list[dict] = []
    in_toml = False
    block_lines: list[str] = []
    block_headings: list[dict] = []

    for raw_line in text.splitlines():
        if not in_toml:
            heading_match = re.match(r"^(#{1,6})\s+(.*\S)\s*$", raw_line)
            if heading_match:
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()
                while heading_stack and heading_stack[-1]["level"] >= level:
                    heading_stack.pop()
                heading_stack.append({"level": level, "text": title})
                continue

            if raw_line.strip().lower() == "```toml":
                in_toml = True
                block_lines = []
                block_headings = [dict(item) for item in heading_stack]
                continue

        else:
            if raw_line.strip() == "```":
                blocks.append(
                    {
                        "headings": [dict(item) for item in block_headings],
                        "content": "\n".join(block_lines).strip(),
                    }
                )
                in_toml = False
                block_lines = []
                block_headings = []
                continue
            block_lines.append(raw_line)

    return blocks


def parse_feature_heading(text: str) -> dict | None:
    match = FEATURE_HEADING_RE.match(text.strip())
    if not match:
        return None

    section = match.group("section")
    raw_title = match.group("title").strip()
    requirement_refs = [ref.upper() for ref in REQUIREMENT_REF_RE.findall(raw_title)]
    title = re.sub(r"\s*\((?:FR|NFR|IFR)-\d+(?:\s*,\s*(?:FR|NFR|IFR)-\d+)*\)\s*$", "", raw_title, flags=re.IGNORECASE).strip()
    return {
        "section": section,
        "title": title or raw_title,
        "requirements_refs": dedupe_preserve_order(requirement_refs),
    }


def find_feature_context(headings: list[dict]) -> dict | None:
    for heading in reversed(headings):
        parsed = parse_feature_heading(str(heading.get("text") or ""))
        if parsed:
            return parsed
    return None


def is_build_contract_heading(text: str) -> bool:
    lowered = text.strip().lower()
    return any(marker in lowered for marker in BUILD_CONTRACT_MARKERS)


def is_implementation_contract_heading(text: str) -> bool:
    return IMPLEMENTATION_CONTRACT_MARKER in text.strip().lower()


def parse_build_contract(data: dict) -> dict:
    return {
        "project": str(data.get("project") or data.get("project_name") or "").strip(),
        "tech_stack": {
            "language": str(data.get("language") or data.get("tech_stack_language") or "").strip() or "TODO",
            "test_framework": str(data.get("test_framework") or "").strip() or "TODO",
            "coverage_tool": str(data.get("coverage_tool") or "").strip() or "TODO",
            "mutation_tool": str(data.get("mutation_tool") or "").strip() or "TODO",
        },
        "constraints": normalize_string_list(data.get("constraints")),
        "assumptions": normalize_string_list(data.get("assumptions")),
        "required_configs": normalize_required_configs(data.get("required_configs")),
    }


def parse_feature_contract(data: dict, *, feature_context: dict | None, design_path: Path) -> tuple[dict | None, list[str], list[str]]:
    issues: list[str] = []
    warnings: list[str] = []

    raw_id = data.get("feature_id", data.get("id"))
    if isinstance(raw_id, bool):
        raw_id = None
    if isinstance(raw_id, int):
        feature_id = raw_id
    else:
        text = str(raw_id or "").strip()
        feature_id = int(text) if text.isdigit() else None
    if feature_id is None:
        issues.append("feature_id is required and must be an integer.")

    feature_title = str(data.get("title") or (feature_context or {}).get("title") or "").strip()
    if not feature_title:
        issues.append("title is required.")

    design_section = str(data.get("design_section") or (feature_context or {}).get("section") or "").strip()
    if not design_section:
        warnings.append("design_section is missing; packets will reference the whole design document.")

    verification_commands = normalize_string_list(data.get("verification_commands"))
    verification_steps = normalize_string_list(data.get("verification_steps"))
    if not verification_commands and not verification_steps:
        issues.append("verification_commands or verification_steps must contain at least one item.")

    file_scope = normalize_string_list(data.get("file_scope"))
    if not file_scope:
        warnings.append("file_scope is empty; parallel build will fall back to sequential execution.")

    if issues:
        return None, issues, warnings

    objective = str(data.get("objective") or data.get("description") or feature_title).strip()
    description = str(data.get("description") or objective or feature_title).strip()
    done_criteria = normalize_string_list(data.get("done_criteria")) or list(verification_steps)
    if not done_criteria:
        done_criteria = [f"Complete {feature_title} and verify the expected behavior."]

    autopilot_commands = normalize_string_list(data.get("autopilot_commands") or data.get("execution_commands"))
    autopilot_workdir = str(data.get("autopilot_workdir") or data.get("workdir") or ".").strip() or "."
    raw_timeout = data.get("autopilot_timeout_sec", data.get("timeout_sec", 300))
    try:
        autopilot_timeout = int(raw_timeout)
    except (TypeError, ValueError):
        autopilot_timeout = 300

    requirements_refs = (
        normalize_string_list(data.get("requirements_refs"))
        or normalize_string_list(data.get("requirements"))
        or list((feature_context or {}).get("requirements_refs") or [])
    )
    requirements_refs = dedupe_preserve_order([ref.upper() for ref in requirements_refs])

    feature = {
        "id": feature_id,
        "title": feature_title,
        "category": str(data.get("category") or "delivery").strip() or "delivery",
        "description": description,
        "objective": objective,
        "business_intent": str(data.get("business_intent") or description or feature_title).strip(),
        "priority": str(data.get("priority") or "medium").strip() or "medium",
        "status": str(data.get("status") or "failing").strip() or "failing",
        "dependencies": normalize_int_list(data.get("dependencies")),
        "file_scope": file_scope,
        "verification_commands": verification_commands,
        "verification_steps": verification_steps,
        "done_criteria": done_criteria,
        "risk_notes": normalize_string_list(data.get("risk_notes")),
        "required_configs": normalize_string_list(data.get("required_configs")),
        "out_of_scope": normalize_string_list(data.get("out_of_scope")),
        "integration_points": normalize_string_list(data.get("integration_points")),
        "requirements_refs": requirements_refs,
        "design_section": design_section,
        "build_contract_ref": build_contract_ref(design_path),
        "ui": bool(data.get("ui")) if isinstance(data.get("ui"), bool) else False,
        "ui_entry": str(data.get("ui_entry") or "").strip(),
        "autopilot_commands": autopilot_commands,
        "autopilot_workdir": autopilot_workdir,
        "autopilot_timeout_sec": autopilot_timeout,
    }
    return feature, issues, warnings


def load_design_execution_contracts(project_root: Path, state: dict | None = None) -> dict:
    loaded_state = state or load_state(project_root)
    design_path = path_contract(project_root, loaded_state)["artifacts"]["design"]
    if not design_path.exists():
        return {
            "detected": False,
            "enabled": False,
            "design_path": str(design_path),
            "build_contract": {},
            "features": [],
            "issues": [],
            "warnings": [],
        }

    text = design_path.read_text(encoding="utf-8")
    blocks = extract_toml_blocks(text)
    detected = False
    build_contract: dict = {}
    features: list[dict] = []
    issues: list[str] = []
    warnings: list[str] = []

    for block in blocks:
        headings = block.get("headings") or []
        current_heading = str(headings[-1]["text"] if headings else "").strip()
        if not current_heading:
            continue

        try:
            parsed = tomllib.loads(block.get("content") or "")
        except tomllib.TOMLDecodeError as exc:
            if is_build_contract_heading(current_heading) or is_implementation_contract_heading(current_heading):
                detected = True
                issues.append(f"{current_heading}: invalid TOML ({exc}).")
            continue

        if is_build_contract_heading(current_heading):
            detected = True
            if build_contract:
                issues.append("Multiple Build Contract TOML blocks were found; keep exactly one.")
                continue
            build_contract = parse_build_contract(parsed)
            continue

        if is_implementation_contract_heading(current_heading):
            detected = True
            feature_context = find_feature_context(headings)
            if feature_context is None:
                issues.append(f"{current_heading}: could not find the parent feature heading.")
                continue
            feature, feature_issues, feature_warnings = parse_feature_contract(
                parsed,
                feature_context=feature_context,
                design_path=design_path,
            )
            issues.extend([f"{feature_context['title']}: {item}" for item in feature_issues])
            warnings.extend([f"{feature_context['title']}: {item}" for item in feature_warnings])
            if feature is not None:
                features.append(feature)

    if detected and not build_contract:
        issues.append("Design execution contracts require exactly one Build Contract TOML block.")

    if detected and not features:
        issues.append("Design execution contracts were detected, but no valid Implementation Contract blocks were parsed.")

    seen_ids: set[int] = set()
    for feature in features:
        feature_id = feature.get("id")
        if feature_id in seen_ids:
            issues.append(f"Duplicate feature_id found in design execution contracts: {feature_id}.")
        else:
            seen_ids.add(feature_id)

    features.sort(key=lambda item: int(item.get("id") or 0))
    enabled = detected and not issues and bool(features)
    return {
        "detected": detected,
        "enabled": enabled,
        "design_path": str(design_path),
        "build_contract": build_contract,
        "features": features,
        "issues": issues,
        "warnings": warnings,
    }
