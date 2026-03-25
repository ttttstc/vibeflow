#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from vibeflow_codebase import ensure_codebase_map
from vibeflow_paths import path_contract


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate or refresh the reusable codebase map.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--refresh", choices=("auto", "force"), default="auto")
    parser.add_argument("--include-markdown", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    data, status = ensure_codebase_map(project_root, refresh=args.refresh, include_markdown=args.include_markdown)
    contract = path_contract(project_root)
    result = {
        "status": status,
        "codebase_map_json": str(contract["codebase_map_json"]),
        "codebase_map_md": str(contract["codebase_map_md"]) if args.include_markdown else None,
        "modules": len(data.get("modules", [])),
        "entrypoints": len(data.get("entrypoints", [])),
        "languages": [item["name"] for item in data.get("languages", [])],
    }

    if args.as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"status: {status}")
        print(f"codebase_map_json: {contract['codebase_map_json']}")
        if args.include_markdown:
            print(f"codebase_map_md: {contract['codebase_map_md']}")
        print(f"modules: {result['modules']}")
        print(f"entrypoints: {result['entrypoints']}")
        print(f"languages: {', '.join(result['languages']) or '[none]'}")


if __name__ == "__main__":
    main()
