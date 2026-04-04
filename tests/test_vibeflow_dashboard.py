#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


dashboard_module = load_module(ROOT / "scripts" / "vibeflow_dashboard.py")
paths_module = load_module(ROOT / "scripts" / "vibeflow_paths.py")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, data: object) -> None:
    write(path, json.dumps(data, indent=2, ensure_ascii=False))


class TestVibeFlowDashboard:
    def test_dashboard_snapshot_describes_current_workflow(self, tmp_path):
        state = paths_module.default_state(tmp_path, topic="demo")
        for checkpoint in ("spark", "design", "tasks", "build", "review", "test"):
            state["checkpoints"][checkpoint] = True
        paths_module.save_state(tmp_path, state)
        for artifact in ("spark", "design", "tasks", "review", "system_test"):
            write(tmp_path / state["artifacts"][artifact], f"# {artifact}\n")
        write_json(tmp_path / "feature-list.json", {"features": [{"id": 1, "status": "passing", "deprecated": False}]})
        snapshot = dashboard_module.build_dashboard_snapshot(tmp_path)
        assert snapshot["current_phase"] == "done"
        assert any(card["key"] == "build" for card in snapshot["workflow"])

    def test_dashboard_token_changes_when_state_changes(self, tmp_path):
        state = paths_module.default_state(tmp_path, topic="demo")
        paths_module.save_state(tmp_path, state)
        snapshot_before = dashboard_module.build_dashboard_snapshot(tmp_path)
        state["checkpoints"]["spark"] = True
        paths_module.save_state(tmp_path, state)
        snapshot_after = dashboard_module.build_dashboard_snapshot(tmp_path)
        assert snapshot_before["token"] != snapshot_after["token"]

    def test_dashboard_surfaces_invariant_stop_reason(self, tmp_path):
        state = paths_module.default_state(tmp_path, topic="demo")
        paths_module.save_state(tmp_path, state)
        runtime = paths_module.default_runtime()
        runtime["status"] = "blocked"
        runtime["current_phase"] = "spark"
        runtime["stop_reason"] = "Waiting for brief."
        runtime["invariant"] = {
            "phase": "spark",
            "reason": "Waiting for brief.",
            "reason_code": "missing_artifact",
            "status": "blocked",
            "updated_at": "2026-04-04T00:00:00+08:00",
        }
        paths_module.save_runtime(tmp_path, runtime)
        snapshot = dashboard_module.build_dashboard_snapshot(tmp_path)
        assert snapshot["reason"]
        assert snapshot["status"] in {"blocked", "pending"}
