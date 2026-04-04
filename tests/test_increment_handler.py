"""Tests for increment-handler legacy-to-spark routing behavior."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).parent.parent


def load_module(filename: str, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, str(ROOT / "scripts" / filename))
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


increment_module = load_module("increment-handler.py", "increment_handler")
paths_module = load_module("vibeflow_paths.py", "vibeflow_paths_for_increment")

default_state = paths_module.default_state
load_state = paths_module.load_state
path_contract = paths_module.path_contract
save_state = paths_module.save_state
resolve_doc_target = increment_module.resolve_doc_target
update_state_after_increment = increment_module.update_state_after_increment


class TestIncrementHandler:
    def test_resolve_doc_target_maps_plan_docs_to_spark_artifact(self, tmp_path):
        state = default_state(tmp_path, topic="increment-doc-target")
        save_state(tmp_path, state)
        contract = path_contract(tmp_path, state)

        assert resolve_doc_target(tmp_path, "proposal") == contract["artifacts"]["spark"]
        assert resolve_doc_target(tmp_path, "plan") == contract["artifacts"]["spark"]

    def test_update_state_after_increment_routes_plan_updates_to_spark(self, tmp_path):
        state = default_state(tmp_path, topic="increment-state-route")
        state["current_phase"] = "build-work"
        state["checkpoints"]["spark"] = True
        state["checkpoints"]["design"] = True
        state["checkpoints"]["tasks"] = True
        state["checkpoints"]["build_init"] = True
        save_state(tmp_path, state)

        update_state_after_increment(
            tmp_path,
            {"type": "update_doc", "doc_type": "plan"},
            "updated plan document",
        )

        updated = load_state(tmp_path)
        assert updated["current_phase"] == "spark"
        assert updated["checkpoints"]["spark"] is False
        assert updated["checkpoints"]["design"] is False
        assert updated["checkpoints"]["tasks"] is False
        assert updated["checkpoints"]["build_init"] is False
