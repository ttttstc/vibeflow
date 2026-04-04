#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from vibeflow_automation import execute_phase  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Execute the VibeFlow build phase.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--max-workers", type=int, default=2)
    parser.add_argument("--serial", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    result = execute_phase(
        Path(args.project_root),
        "build",
        parallel_build=not args.serial,
        max_workers=args.max_workers,
    )

    if args.as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("ok" if result["ok"] else "failed")
        print(result["detail"])

    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
