#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from vibeflow_paths import load_state, path_contract


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    state = load_state(project_root)
    contract = path_contract(project_root, state)

    result = {
        "state": str(contract["state"]),
        "workflow": str(contract["workflow"]),
        "feature_list": str(contract["feature_list"]),
        "release_notes": str(contract["release_notes"]),
        "overview_root": str(contract["overview_root"]),
        "overview": {k: str(v) for k, v in contract["overview"].items()},
        "increment_queue": str(contract["increment_queue"]),
        "increment_history": str(contract["increment_history"]),
        "increment_requests_dir": str(contract["increment_requests_dir"]),
        "session_log": str(contract["session_log"]),
        "build_guide": str(contract["build_guide"]),
        "services_guide": str(contract["services_guide"]),
        "build_reports_dir": str(contract["build_reports_dir"]),
        "rules_dir": str(contract["rules_dir"]),
        "change_root": str(contract["change_root"]),
        "codebase_map_json": str(contract["codebase_map_json"]),
        "codebase_map_md": str(contract["codebase_map_md"]),
        "codebase_impact_json": str(contract["codebase_impact_json"]),
        "codebase_impact_md": str(contract["codebase_impact_md"]),
        "artifacts": {k: str(v) for k, v in contract["artifacts"].items()},
    }

    if args.as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        for key, value in result.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for subkey, subvalue in value.items():
                    print(f"  {subkey}: {subvalue}")
            else:
                print(f"{key}: {value}")


if __name__ == "__main__":
    main()
