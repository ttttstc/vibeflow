#!/usr/bin/env python3
"""Tests for the VibeFlow v2 state/artifact layout."""

import json
import importlib.util
import subprocess
import sys
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
migrate_module = load_module("migrate-vibeflow-v2.py", "migrate_vibeflow_v2")


detect_phase = phase_module.detect_phase
default_state = paths_module.default_state
save_state = paths_module.save_state
path_contract = paths_module.path_contract
check_st_readiness = st_module.check_st_readiness


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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
        state["quick_meta"].update(
            {
                "decision": "approved",
                "category": "bugfix",
                "scope": "Fix a tiny bug in one module.",
                "touchpoints": ["src/module.py"],
                "validation_plan": "Run the targeted regression test.",
                "rollback_plan": "Revert the single commit.",
            }
        )
        state["checkpoints"]["quick_ready"] = True
        save_state(tmp_path, state)

        contract = path_contract(tmp_path, state)
        write(contract["workflow"], 'template: "prototype"\n')
        write(contract["artifacts"]["design"], "# Quick Design\n")
        write(contract["artifacts"]["tasks"], "# Tasks\n")

        result = detect_phase(tmp_path)
        assert result["phase"] == "build-work"

    def test_v2_quick_mode_rejects_high_risk_work(self, tmp_path):
        state = default_state(tmp_path, topic="risky-quick")
        state["mode"] = "quick"
        state["quick_meta"].update(
            {
                "decision": "approved",
                "category": "bugfix",
                "scope": "Touches authentication flow.",
                "touchpoints": ["src/auth.py"],
                "risk_flags": ["auth"],
                "validation_plan": "Run the auth regression suite.",
                "rollback_plan": "Revert the auth change.",
            }
        )
        state["checkpoints"]["quick_ready"] = True
        save_state(tmp_path, state)

        contract = path_contract(tmp_path, state)
        write(contract["workflow"], 'template: "prototype"\n')
        write(contract["artifacts"]["design"], "# Quick Design\n")
        write(contract["artifacts"]["tasks"], "# Tasks\n")

        result = detect_phase(tmp_path)
        assert result["phase"] == "quick"
        assert "Full Mode" in result["reason"]

    def test_v2_quick_mode_requires_design_and_tasks(self, tmp_path):
        state = default_state(tmp_path, topic="missing-quick-artifacts")
        state["mode"] = "quick"
        state["quick_meta"].update(
            {
                "decision": "approved",
                "category": "bugfix",
                "scope": "Fix a tiny regression.",
                "touchpoints": ["src/module.py"],
                "validation_plan": "Run the targeted regression test.",
                "rollback_plan": "Revert the single quick change.",
            }
        )
        state["checkpoints"]["quick_ready"] = True
        save_state(tmp_path, state)

        contract = path_contract(tmp_path, state)
        write(contract["workflow"], 'template: "prototype"\n')

        result = detect_phase(tmp_path)
        assert result["phase"] == "quick"
        assert "design artifact" in result["reason"] or "tasks artifact" in result["reason"]

    def test_promote_quick_mode_back_to_full(self, tmp_path):
        state = default_state(tmp_path, topic="promote-quick")
        state["mode"] = "quick"
        state["quick_meta"].update(
            {
                "decision": "approved",
                "category": "bugfix",
                "scope": "Started as a bugfix but kept expanding.",
                "touchpoints": ["src/module.py"],
                "validation_plan": "Run the targeted test.",
                "rollback_plan": "Revert the quick fix commit.",
            }
        )
        state["checkpoints"]["quick_ready"] = True
        save_state(tmp_path, state)
        contract = path_contract(tmp_path, state)
        write(contract["workflow"], 'template: "prototype"\n')
        write(contract["artifacts"]["design"], "# Quick Design\n")
        write(contract["artifacts"]["tasks"], "# Tasks\n")

        output = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "promote-vibeflow-quick.py"),
                "--project-root",
                str(tmp_path),
                "--reason",
                "Scope is no longer safe for Quick Mode.",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        assert output.returncode == 0, output.stderr

        promoted_state = read_json(tmp_path / ".vibeflow" / "state.json")
        assert promoted_state["mode"] == "full"
        assert promoted_state["quick_meta"]["promoted_from_quick"] is True
        assert promoted_state["quick_meta"]["promotion_reason"] == "Scope is no longer safe for Quick Mode."

        result = detect_phase(tmp_path)
        assert result["phase"] == "think"

    def test_migrate_legacy_quick_mode_populates_quick_meta(self, tmp_path):
        project_root = tmp_path / "legacy-quick"
        (project_root / ".vibeflow").mkdir(parents=True, exist_ok=True)
        (project_root / "docs").mkdir(parents=True, exist_ok=True)

        write(project_root / "docs" / "quick-design.md", "# Quick Design\n\nLegacy quick artifact.\n")

        original_argv = sys.argv[:]
        try:
            sys.argv = [
                "migrate-vibeflow-v2.py",
                "--project-root",
                str(project_root),
            ]
            migrate_module.main()
        finally:
            sys.argv = original_argv

        migrated_state = read_json(project_root / ".vibeflow" / "state.json")
        assert migrated_state["mode"] == "quick"
        assert migrated_state["checkpoints"]["quick_ready"] is True
        assert migrated_state["quick_meta"]["decision"] == "approved"
        assert migrated_state["quick_meta"]["category"] == "small-change"

        result = detect_phase(project_root)
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
