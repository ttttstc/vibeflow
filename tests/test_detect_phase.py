#!/usr/bin/env python3
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


phase_module = load_module(ROOT / "scripts" / "get-vibeflow-phase.py")
paths_module = load_module(ROOT / "scripts" / "vibeflow_paths.py")

detect_phase = phase_module.detect_phase
ui_required = phase_module.ui_required
reflect_required = phase_module.reflect_required
all_features_passing = phase_module.all_features_passing


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, data: object) -> None:
    write(path, json.dumps(data, indent=2, ensure_ascii=False))


def make_stateful_project(project_root: Path) -> dict:
    state = paths_module.default_state(project_root, topic="demo")
    paths_module.save_state(project_root, state)
    write(project_root / ".vibeflow" / "workflow.yaml", 'template: "api-standard"\nship:\n  required: true\nreflect:\n  required: true\n')
    return state


class TestDetectPhase:
    def test_increment_queue_wins(self, tmp_path):
        state = make_stateful_project(tmp_path)
        write_json(tmp_path / ".vibeflow" / "increments" / "queue.json", {"items": [{"id": "inc-1"}]})
        result = detect_phase(tmp_path)
        assert result["phase"] == "increment"
        assert result["resume_mode"] == "manual"

    def test_full_flow_transitions(self, tmp_path):
        state = make_stateful_project(tmp_path)
        assert detect_phase(tmp_path)["phase"] == "spark"

        state["checkpoints"]["spark"] = True
        write(tmp_path / state["artifacts"]["spark"], "# Brief\n")
        paths_module.save_state(tmp_path, state)
        assert detect_phase(tmp_path)["phase"] == "design"

        state["checkpoints"]["design"] = True
        write(tmp_path / state["artifacts"]["design"], "# Design\n\n## Review Summary\n\nApproved.\n")
        paths_module.save_state(tmp_path, state)
        assert detect_phase(tmp_path)["phase"] == "tasks"

        state["checkpoints"]["tasks"] = True
        write(tmp_path / state["artifacts"]["tasks"], "# Tasks\n")
        paths_module.save_state(tmp_path, state)
        assert detect_phase(tmp_path)["phase"] == "build"

        write_json(
            tmp_path / "feature-list.json",
            {"features": [{"id": 1, "title": "A", "status": "passing", "deprecated": False}]},
        )
        assert detect_phase(tmp_path)["phase"] == "review"

        state["checkpoints"]["review"] = True
        write(tmp_path / state["artifacts"]["review"], "# Review\n")
        paths_module.save_state(tmp_path, state)
        assert detect_phase(tmp_path)["phase"] == "test"

        state["checkpoints"]["test"] = True
        write(tmp_path / state["artifacts"]["system_test"], "# System Test\n")
        paths_module.save_state(tmp_path, state)
        assert detect_phase(tmp_path)["phase"] == "ship"

        state["checkpoints"]["ship"] = True
        write(tmp_path / "RELEASE_NOTES.md", "# Release Notes\n")
        paths_module.save_state(tmp_path, state)
        assert detect_phase(tmp_path)["phase"] == "reflect"

        state["checkpoints"]["reflect"] = True
        write(tmp_path / ".vibeflow" / "logs" / "retro-2026-04-04.md", "# Retro\n")
        paths_module.save_state(tmp_path, state)
        assert detect_phase(tmp_path)["phase"] == "done"

    def test_ui_test_phase_requires_qa_artifact(self, tmp_path):
        state = make_stateful_project(tmp_path)
        write(tmp_path / ".vibeflow" / "workflow.yaml", 'template: "web-standard"\nqa:\n  required: true\n')
        for checkpoint, artifact in (("spark", "spark"), ("design", "design"), ("tasks", "tasks"), ("review", "review")):
            state["checkpoints"][checkpoint] = True
            write(tmp_path / state["artifacts"][artifact], f"# {artifact}\n")
        write_json(
            tmp_path / "feature-list.json",
            {"features": [{"id": 1, "title": "A", "status": "passing", "deprecated": False}]},
        )
        state["checkpoints"]["test"] = True
        write(tmp_path / state["artifacts"]["system_test"], "# System Test\n")
        paths_module.save_state(tmp_path, state)
        result = detect_phase(tmp_path)
        assert result["phase"] == "test"
        assert result["blocking_item"] == "qa"

    def test_quick_mode_goes_directly_to_build(self, tmp_path):
        state = make_stateful_project(tmp_path)
        state["mode"] = "quick"
        state["quick_meta"].update(
            {
                "decision": "approved",
                "category": "bugfix",
                "scope": "Small bounded fix",
                "touchpoints": ["src/app.py"],
                "validation_plan": "Run quick checks",
                "rollback_plan": "Revert change",
            }
        )
        state["checkpoints"]["quick_ready"] = True
        write(tmp_path / state["artifacts"]["design"], "# Design\n")
        write(tmp_path / state["artifacts"]["tasks"], "# Tasks\n")
        paths_module.save_state(tmp_path, state)
        assert detect_phase(tmp_path)["phase"] == "build"

    def test_verbose_includes_checks_and_guidance(self, tmp_path):
        make_stateful_project(tmp_path)
        result = detect_phase(tmp_path, verbose=True)
        assert result["phase"] == "spark"
        assert len(result["checks"]) > 0
        assert result["next_action"]
        assert result["open_files"]

    def test_missing_overview_docs_returns_generation_suggestion(self, tmp_path):
        make_stateful_project(tmp_path)
        result = detect_phase(tmp_path, verbose=True)
        assert result["overview_missing"] is True
        assert "PROJECT.md" in result["overview_missing_files"]
        assert "map-codebase.py" in result["overview_suggestion"]
        assert "map-change-impact.py" in result["overview_suggestion"]

    def test_spark_guidance_mentions_office_hours_and_design_confirmation(self, tmp_path):
        make_stateful_project(tmp_path)
        result = detect_phase(tmp_path, verbose=True)
        assert "vibeflow-office-hours" in result["next_action"]
        assert "验收标准" in result["next_action"]
        assert "是否进入 design" in result["next_action"]

    def test_existing_overview_docs_clear_generation_suggestion(self, tmp_path):
        state = make_stateful_project(tmp_path)
        overview_root = tmp_path / "docs" / "overview"
        write(overview_root / "PROJECT.md", "# 项目总览\n")
        write(overview_root / "ARCHITECTURE.md", "# 架构总览\n")
        write(overview_root / "CURRENT-STATE.md", "# 当前状态\n")
        paths_module.save_state(tmp_path, state)
        result = detect_phase(tmp_path, verbose=True)
        assert result["overview_missing"] is False
        assert result["overview_missing_files"] == []
        assert result["overview_suggestion"] == ""

    def test_design_guidance_mentions_confirmation_before_tasks(self, tmp_path):
        state = make_stateful_project(tmp_path)
        state["checkpoints"]["spark"] = True
        write(tmp_path / state["artifacts"]["spark"], "# Brief\n")
        paths_module.save_state(tmp_path, state)
        result = detect_phase(tmp_path, verbose=True)
        assert result["phase"] == "design"
        assert "eng/design review" in result["next_action"]
        assert "用户确认后" in result["next_action"]
        assert "进入 tasks" in result["next_action"]


class TestHelpers:
    def test_ui_required(self, tmp_path):
        wf = tmp_path / "workflow.yaml"
        wf.write_text("qa:\n  required: true", encoding="utf-8")
        assert ui_required(wf) is True

    def test_reflect_required(self, tmp_path):
        wf = tmp_path / "workflow.yaml"
        wf.write_text("reflect:\n  required: true", encoding="utf-8")
        assert reflect_required(wf) is True

    def test_all_features_passing(self, tmp_path):
        feature_list = tmp_path / "feature-list.json"
        write_json(feature_list, {"features": [{"id": 1, "status": "passing", "deprecated": False}]})
        assert all_features_passing(feature_list) is True
