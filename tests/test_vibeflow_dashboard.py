#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import sys
import threading
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SAMPLE_ROOT = ROOT / "validation" / "sample-priority-api"
SCRIPT_DIR = ROOT / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from vibeflow_dashboard import build_dashboard_snapshot, serve_in_background  # noqa: E402


def copy_sample_project(tmp_path: Path, name: str) -> Path:
    target = tmp_path / name
    shutil.copytree(SAMPLE_ROOT, target)
    for pycache in target.rglob("__pycache__"):
        shutil.rmtree(pycache)
    return target


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def fetch_text(url: str) -> str:
    with urllib.request.urlopen(url) as response:
        return response.read().decode("utf-8")


class TestVibeFlowDashboard:
    def test_dashboard_snapshot_describes_current_workflow(self, tmp_path):
        project_root = copy_sample_project(tmp_path, "dashboard-sample")
        snapshot = build_dashboard_snapshot(project_root)

        assert snapshot["project"] == "dashboard-sample"
        assert snapshot["current_phase"] == "done"
        assert snapshot["workflow"]
        build_card = next(card for card in snapshot["workflow"] if card["key"] == "build")
        assert build_card["status"] == "completed"
        assert any(item["key"] == "review" for item in snapshot["artifacts"])
        assert snapshot["features"]["total"] >= 1

    def test_dashboard_server_serves_html_json_and_sse(self, tmp_path):
        project_root = copy_sample_project(tmp_path, "dashboard-server")
        server, thread = serve_in_background(project_root, port=0)
        host, port = server.server_address
        base = f"http://{host}:{port}"
        try:
            html = fetch_text(base + "/")
            assert "Editorial Ops Dashboard" in html
            assert "EventSource" in html

            snapshot = json.loads(fetch_text(base + "/api/snapshot"))
            assert snapshot["project"] == "dashboard-server"

            sse = fetch_text(base + "/api/events?once=1")
            assert "event: snapshot" in sse
            assert "\"current_phase\"" in sse
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_dashboard_token_changes_when_state_changes(self, tmp_path):
        project_root = copy_sample_project(tmp_path, "dashboard-token")
        snapshot_before = build_dashboard_snapshot(project_root)

        runtime_path = project_root / ".vibeflow" / "runtime.json"
        runtime = read_json(runtime_path)
        runtime["status"] = "running"
        runtime["friendly_message"] = "正在准备新的演示快照。"
        write_json(runtime_path, runtime)

        snapshot_after = build_dashboard_snapshot(project_root)
        assert snapshot_before["token"] != snapshot_after["token"]
        assert snapshot_after["friendly_message"] == "正在准备新的演示快照。"
