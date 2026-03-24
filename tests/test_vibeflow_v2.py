#!/usr/bin/env python3
"""Tests for the VibeFlow v2 state/artifact layout."""

import json
import importlib.util
from pathlib import Path


ROOT = Path(__file__).parent.parent


def load_module(filename: str, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, str(ROOT / "scripts" / filename))
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


phase_module = load_module("get-vibeflow-phase.py", "get_vibeflow_phase_v2")
paths_module = load_module("vibeflow_paths.py", "vibeflow_paths_v2")
st_module = load_module("check_st_readiness.py", "check_st_readiness_v2")


detect_phase = phase_module.detect_phase
default_state = paths_module.default_state
save_state = paths_module.save_state
path_contract = paths_module.path_contract
check_st_readiness = st_module.check_st_readiness


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class TestVibeFlowV2:
    def test_v2_requirements_missing(self, tmp_path):
        state = default_state(tmp_path, topic="sample")
        save_state(tmp_path, state)
        contract = path_contract(tmp_path, state)

        write(contract["workflow"], 'template: "prototype"\n')
        write(contract["artifacts"]["think"], "# Context\n")
        write(contract["artifacts"]["plan"], "# Proposal\n")

        state["checkpoints"]["think"] = True
        state["checkpoints"]["plan"] = True
        save_state(tmp_path, state)

        result = detect_phase(tmp_path)
        assert result["phase"] == "requirements"

    def test_v2_quick_mode_goes_straight_to_build_work(self, tmp_path):
        state = default_state(tmp_path, topic="quick-fix")
        state["mode"] = "quick"
        state["checkpoints"]["quick_ready"] = True
        save_state(tmp_path, state)

        contract = path_contract(tmp_path, state)
        write(contract["workflow"], 'template: "prototype"\n')

        result = detect_phase(tmp_path)
        assert result["phase"] == "build-work"

    def test_v2_increment_queue_json_triggers_increment(self, tmp_path):
        state = default_state(tmp_path, topic="increment")
        save_state(tmp_path, state)
        contract = path_contract(tmp_path, state)
        write(contract["workflow"], 'template: "prototype"\n')
        contract["increment_queue"].parent.mkdir(parents=True, exist_ok=True)
        contract["increment_queue"].write_text(
            json.dumps({"items": [{"id": "inc-1"}]}, ensure_ascii=False),
            encoding="utf-8",
        )

        result = detect_phase(tmp_path)
        assert result["phase"] == "increment"

    def test_check_st_readiness_under_v2_layout(self, tmp_path):
        state = default_state(tmp_path, topic="ui-app")
        save_state(tmp_path, state)
        contract = path_contract(tmp_path, state)

        write(
            tmp_path / "feature-list.json",
            json.dumps(
                {
                    "features": [
                        {"id": 1, "title": "UI flow", "status": "passing", "ui": True, "st_case_path": "docs/test-cases/feature-1.md"}
                    ]
                },
                ensure_ascii=False,
            ),
        )
        write(contract["artifacts"]["requirements"], "# Requirements\n")
        write(contract["artifacts"]["design"], "# Design\n")
        write(contract["artifacts"]["ucd"], "# UCD\n")
        (tmp_path / "docs" / "test-cases").mkdir(parents=True, exist_ok=True)

        result = check_st_readiness(tmp_path / "feature-list.json")
        assert result["ready"] is True
        assert result["srs_found"] is True
        assert result["design_found"] is True
        assert result["ucd_found"] is True
