#!/usr/bin/env python3
"""Promote an in-flight Quick Mode work package back to Full Mode."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from vibeflow_paths import load_state, promote_quick_to_full, save_state  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    parser.add_argument(
        "--reason",
        default="Quick Mode exceeded its safe boundary and was promoted to Full Mode.",
        help="Reason recorded into quick_meta.promotion_reason",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    state = load_state(project_root)

    if state.get("mode") != "quick":
        raise SystemExit("Current mode is not quick; no promotion needed.")

    promote_quick_to_full(state, reason=args.reason)
    save_state(project_root, state)

    payload = {
        "mode": state.get("mode"),
        "current_phase": state.get("current_phase"),
        "active_change": state.get("active_change"),
        "promotion_reason": (state.get("quick_meta") or {}).get("promotion_reason", ""),
    }

    if args.as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("Quick Mode promoted to Full Mode.")
        print(f"Current phase: {payload['current_phase']}")
        print(f"Reason: {payload['promotion_reason']}")


if __name__ == "__main__":
    main()
