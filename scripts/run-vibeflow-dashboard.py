#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from vibeflow_dashboard import build_dashboard_snapshot, run_dashboard_server  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Run the VibeFlow workflow dashboard.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4317)
    parser.add_argument("--snapshot-json", action="store_true")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()

    if args.snapshot_json:
        print(json.dumps(build_dashboard_snapshot(project_root), indent=2, ensure_ascii=False))
        return

    server = run_dashboard_server(project_root, host=args.host, port=args.port)
    actual_host, actual_port = server.server_address
    print(f"http://{actual_host}:{actual_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
