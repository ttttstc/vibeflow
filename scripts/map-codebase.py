#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from vibeflow_codebase import ensure_codebase_map
from vibeflow_overview import ensure_overview_docs


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan the repository and refresh docs/overview.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--refresh", choices=("auto", "force"), default="auto")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    data, status = ensure_codebase_map(project_root, refresh=args.refresh, include_markdown=False)
    overview = ensure_overview_docs(project_root, force=args.refresh == "force")
    result = {
        "status": status,
        "overview": {key: str(value) for key, value in overview.items()},
        "modules": len(data.get("modules", [])),
        "entrypoints": len(data.get("entrypoints", [])),
        "languages": [item["name"] for item in data.get("languages", [])],
    }

    if args.as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"status: {status}")
        print("overview:")
        for key, value in result["overview"].items():
            print(f"  {key}: {value}")
        print(f"modules: {result['modules']}")
        print(f"entrypoints: {result['entrypoints']}")
        print(f"languages: {', '.join(result['languages']) or '[none]'}")


if __name__ == "__main__":
    main()
