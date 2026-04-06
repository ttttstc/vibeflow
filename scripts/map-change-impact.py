#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from vibeflow_codebase import build_change_impact, change_focus_summary, ensure_codebase_map
from vibeflow_overview import ensure_overview_docs, refresh_current_state
from vibeflow_paths import load_state, path_contract


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh docs/overview with current change impact highlights.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--source", choices=("spark", "design", "tasks", "requirements"), default="design")
    parser.add_argument("--refresh-map", choices=("auto", "force", "skip"), default="auto")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    state = load_state(project_root)

    if args.refresh_map == "skip":
        codebase_map, map_status = ensure_codebase_map(project_root, refresh="auto", include_markdown=False)
    else:
        codebase_map, map_status = ensure_codebase_map(
            project_root,
            refresh="force" if args.refresh_map == "force" else "auto",
            include_markdown=False,
        )

    ensure_overview_docs(project_root, state, force=args.refresh_map == "force")
    current_state_path = refresh_current_state(project_root, state, codebase_map=codebase_map)
    impact = build_change_impact(project_root, state, codebase_map)
    contract = path_contract(project_root, state)
    result = {
        "status": "built",
        "map_status": map_status,
        "source": args.source,
        "current_state": str(current_state_path),
        "overview_project": str(contract["overview"]["project"]),
        "overview_architecture": str(contract["overview"]["architecture"]),
        "matched_terms": impact.get("matched_terms", []),
        "relevant_modules": len(impact.get("relevant_modules", [])),
        "change_focus": change_focus_summary(impact),
    }

    if args.as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("status: built")
        print(f"map_status: {map_status}")
        print(f"current_state: {current_state_path}")
        print(f"overview_project: {contract['overview']['project']}")
        print(f"overview_architecture: {contract['overview']['architecture']}")
        print(f"matched_terms: {', '.join(impact.get('matched_terms', [])) or '[none]'}")
        print(f"relevant_modules: {len(impact.get('relevant_modules', []))}")


if __name__ == "__main__":
    main()
