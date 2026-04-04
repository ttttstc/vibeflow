#!/usr/bin/env python3
"""
Check system testing readiness for a vibeflow project.

Verifies:
- feature-list.json exists and all active features are "passing"
- spark/context or legacy requirements, plus design artifacts, exist
- UI projects have either a dedicated UCD artifact or an inlined design artifact

The script understands both the legacy docs/plans layout and the v2
docs/changes/<change-id>/ layout.

Usage:
    python check_st_readiness.py <path/to/feature-list.json>
    python check_st_readiness.py --project-root <path/to/project>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from vibeflow_paths import load_state, path_contract, state_path  # noqa: E402


def latest_matching_file(base: Path, pattern: str) -> Path | None:
    if not base.exists():
        return None
    matches = sorted(base.glob(pattern), key=lambda item: item.stat().st_mtime, reverse=True)
    return matches[0] if matches else None


def resolve_paths(project_root: Path) -> dict:
    if state_path(project_root).exists():
        state = load_state(project_root)
        contract = path_contract(project_root, state)
        artifacts = contract["artifacts"]
        requirements = artifacts["requirements"] if artifacts["requirements"].exists() else artifacts["spark"]
        design = artifacts["design"]
        ucd = artifacts["ucd"] if artifacts["ucd"].exists() else design
        return {
            "requirements": requirements,
            "design": design,
            "ucd": ucd,
            "layout": "v2",
            "change_root": contract["change_root"],
        }

    plans_dir = project_root / "docs" / "plans"
    requirements = latest_matching_file(plans_dir, "*-srs.md")
    design = latest_matching_file(plans_dir, "*-design.md")
    ucd = latest_matching_file(plans_dir, "*-ucd.md")
    return {
        "requirements": requirements,
        "design": design,
        "ucd": ucd,
        "layout": "legacy",
        "change_root": plans_dir,
    }


def check_st_readiness(feature_list_path: Path) -> dict:
    result = {
        "ready": False,
        "total_features": 0,
        "passing_features": 0,
        "failing_features": 0,
        "deprecated_features": 0,
        "failing_ids": [],
        "srs_found": False,
        "srs_path": None,
        "design_found": False,
        "design_path": None,
        "ucd_found": False,
        "ucd_path": None,
        "has_ui_features": False,
        "issues": [],
    }

    if not feature_list_path.exists():
        raise FileNotFoundError(feature_list_path)

    data = json.loads(feature_list_path.read_text(encoding="utf-8"))
    features = data.get("features", [])
    active_features = []

    for feat in features:
        if feat.get("deprecated", False):
            result["deprecated_features"] += 1
        else:
            active_features.append(feat)

    result["total_features"] = len(active_features)
    if not active_features:
        result["issues"].append("No active features defined in feature-list.json")
        return result

    for feat in active_features:
        feat_id = feat.get("id", "?")
        if feat.get("status") == "passing":
            result["passing_features"] += 1
        else:
            result["failing_features"] += 1
            result["failing_ids"].append(feat_id)
        if feat.get("ui") is True:
            result["has_ui_features"] = True

    if result["failing_features"] > 0:
        result["issues"].append(
            f"{result['failing_features']} feature(s) still failing: {result['failing_ids']}"
        )

    project_root = feature_list_path.resolve().parent
    resolved = resolve_paths(project_root)
    requirements = resolved["requirements"]
    design = resolved["design"]
    ucd = resolved["ucd"]

    if requirements and requirements.exists():
        result["srs_found"] = True
        result["srs_path"] = str(requirements)
    else:
        if resolved["layout"] == "v2":
            expected = "docs/changes/<change-id>/brief.md or requirements.md"
            result["issues"].append(f"Spark brief artifact not found ({expected})")
        else:
            result["issues"].append("Requirements document not found (docs/plans/*-srs.md)")

    if design and design.exists():
        result["design_found"] = True
        result["design_path"] = str(design)
    else:
        expected = "docs/changes/<change-id>/design.md" if resolved["layout"] == "v2" else "docs/plans/*-design.md"
        result["issues"].append(f"Design document not found ({expected})")

    if ucd and ucd.exists():
        result["ucd_found"] = True
        result["ucd_path"] = str(ucd)
    elif result["has_ui_features"]:
        if resolved["layout"] == "v2" and design and design.exists():
            result["ucd_found"] = True
            result["ucd_path"] = str(design)
        else:
            expected = "docs/changes/<change-id>/ucd.md or inlined design.md" if resolved["layout"] == "v2" else "docs/plans/*-ucd.md"
            result["issues"].append(f"UI features exist but UCD document not found ({expected})")

    features_with_st_cases = 0
    features_without_st_cases = []
    for feat in active_features:
        if feat.get("st_case_path"):
            features_with_st_cases += 1
        else:
            features_without_st_cases.append(feat.get("id", "?"))
    result["st_case_coverage"] = features_with_st_cases
    result["st_case_missing"] = features_without_st_cases
    result["test_cases_dir_found"] = (project_root / "docs" / "test-cases").is_dir()

    result["ready"] = (
        result["failing_features"] == 0
        and result["srs_found"]
        and result["design_found"]
        and result["total_features"] > 0
        and (not result["has_ui_features"] or result["ucd_found"])
    )
    return result


def main():
    parser = argparse.ArgumentParser(description="Check system testing readiness")
    parser.add_argument("path", nargs="?", help="Path to feature-list.json")
    parser.add_argument("--project-root", default=None, help="Project root; feature-list.json will be resolved under it")
    args = parser.parse_args()

    if args.project_root:
        feature_list_path = Path(args.project_root).resolve() / "feature-list.json"
    elif args.path:
        feature_list_path = Path(args.path).resolve()
    else:
        parser.error("either <path> or --project-root is required")

    try:
        result = check_st_readiness(feature_list_path)
    except (json.JSONDecodeError, FileNotFoundError) as exc:
        print(f"ERROR: Cannot read feature-list.json: {exc}")
        sys.exit(1)

    print(f"Active features: {result['passing_features']}/{result['total_features']} passing")
    if result["deprecated_features"] > 0:
        print(f"Deprecated: {result['deprecated_features']} (excluded from checks)")
    if result["failing_features"] > 0:
        print(f"Failing: {result['failing_ids']}")
    print(f"Spark Brief/Requirements: {'found' if result['srs_found'] else 'MISSING'}")
    print(f"Design: {'found' if result['design_found'] else 'MISSING'}")
    if result["has_ui_features"]:
        print(f"UCD: {'found' if result['ucd_found'] else 'MISSING (UI features exist)'}")
    if "st_case_coverage" in result:
        if result["st_case_missing"]:
            print(f"ST test cases: {result['st_case_coverage']}/{result['total_features']} features covered")
            print(f"  Warning: features without ST test cases: {result['st_case_missing']}")
        else:
            print(f"ST test cases: {result['st_case_coverage']}/{result['total_features']} features covered")

    if result["ready"]:
        print("\nREADY for system testing.")
        sys.exit(0)

    print(f"\nNOT READY — {len(result['issues'])} issue(s):")
    for issue in result["issues"]:
        print(f"  - {issue}")
    sys.exit(1)


if __name__ == "__main__":
    main()
