#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from vibeflow_automation import run_autopilot  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Run VibeFlow autopilot from the current phase.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--max-steps", type=int, default=None)
    parser.add_argument("--max-workers", type=int, default=None)
    parser.add_argument("--stop-at", action="append", default=[])
    parser.add_argument("--serial-build", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    result = run_autopilot(
        Path(args.project_root),
        max_steps=args.max_steps,
        stop_at={item for item in args.stop_at if item},
        parallel_build=not args.serial_build,
        max_workers=args.max_workers,
    )

    if args.as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(result["status"])
        print(f"final_phase={result['final_phase']}")
        for item in result.get("executed", []):
            status = "ok" if item["ok"] else "failed"
            print(f"- {item['phase']}: {status} — {item['detail']}")

    raise SystemExit(0 if result["status"] in {"completed", "waiting_manual", "stopped"} else 1)


if __name__ == "__main__":
    main()
