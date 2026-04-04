#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from vibeflow_codebase import build_change_impact, ensure_codebase_map, write_change_impact
from vibeflow_paths import load_state, path_contract


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate change-scoped codebase impact analysis.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--source", choices=("spark", "design", "tasks", "requirements"), default="design")
    parser.add_argument("--refresh-map", choices=("auto", "force", "skip"), default="auto")
    parser.add_argument("--include-impact-json", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    state = load_state(project_root)

    if args.refresh_map == "skip":
        map_path = path_contract(project_root, state)["codebase_map_json"]
        if map_path.exists():
            codebase_map = json.loads(map_path.read_text(encoding="utf-8"))
            map_status = "reused"
        else:
            codebase_map, map_status = ensure_codebase_map(project_root, refresh="auto", include_markdown=False)
    else:
        codebase_map, map_status = ensure_codebase_map(
            project_root,
            refresh="force" if args.refresh_map == "force" else "auto",
            include_markdown=False,
        )

    impact = build_change_impact(project_root, state, codebase_map)
    json_path, md_path = write_change_impact(project_root, state, impact, include_json=args.include_impact_json)
    result = {
        "status": "built",
        "map_status": map_status,
        "source": args.source,
        "codebase_impact_json": str(json_path) if json_path else None,
        "codebase_impact_md": str(md_path),
        "matched_terms": impact.get("matched_terms", []),
        "relevant_modules": len(impact.get("relevant_modules", [])),
    }

    if args.as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("status: built")
        print(f"map_status: {map_status}")
        if json_path:
            print(f"codebase_impact_json: {json_path}")
        print(f"codebase_impact_md: {md_path}")
        print(f"matched_terms: {', '.join(impact.get('matched_terms', [])) or '[none]'}")
        print(f"relevant_modules: {len(impact.get('relevant_modules', []))}")


if __name__ == "__main__":
    main()
