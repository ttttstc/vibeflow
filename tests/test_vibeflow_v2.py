#!/usr/bin/env python3
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


paths_module = load_module(ROOT / "scripts" / "vibeflow_paths.py")
phase_module = load_module(ROOT / "scripts" / "get-vibeflow-phase.py")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, data: object) -> None:
    write(path, json.dumps(data, indent=2, ensure_ascii=False))


def run_python(script: Path, *args: object) -> str:
    result = subprocess.run(
        [sys.executable, str(script), *[str(arg) for arg in args]],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    return result.stdout


class TestVibeFlowV2:
    def test_default_state_uses_macro_phases(self, tmp_path):
        state = paths_module.default_state(tmp_path, topic="demo")
        assert state["current_phase"] == "spark"
        assert state["autopilot"]["auto_runnable"] == ["build", "review", "test", "ship", "reflect"]
        assert state["checkpoints"]["build"] is False
        assert state["checkpoints"]["test"] is False

    def test_path_contract_exposes_consolidated_paths(self, tmp_path):
        state = paths_module.default_state(tmp_path, topic="demo")
        contract = paths_module.path_contract(tmp_path, state)
        assert contract["build_reports_dir"].name == "build-reports"
        assert contract["overview"]["project"].name == "PROJECT.md"
        assert contract["artifacts"]["spark"].name == "brief.md"
        assert contract["artifacts"]["design_review"] == contract["artifacts"]["design"]

    def test_init_project_creates_new_surface(self, tmp_path):
        project_root = tmp_path / "demo"
        run_python(ROOT / "scripts" / "init_project.py", "demo", "--path", project_root, "--lang", "python")
        assert (project_root / ".vibeflow" / "state.json").exists()
        assert not (project_root / ".vibeflow" / "runtime.json").exists()
        assert not (project_root / ".vibeflow" / "work-config.json").exists()
        assert (project_root / "docs" / "overview" / "CURRENT-STATE.md").exists()
        assert (project_root / "docs" / "overview" / "PROJECT.md").exists()
        assert (project_root / "docs" / "overview" / "ARCHITECTURE.md").exists()
        assert not (project_root / "docs" / "overview" / "README.md").exists()

    def test_runtime_is_embedded_in_state(self, tmp_path):
        state = paths_module.default_state(tmp_path, topic="demo")
        paths_module.save_state(tmp_path, state)
        runtime = paths_module.default_runtime()
        runtime["current_phase"] = "build"
        runtime["friendly_message"] = "Resume build."
        paths_module.save_runtime(tmp_path, runtime)
        loaded_state = paths_module.load_state(tmp_path)
        assert loaded_state["runtime"]["current_phase"] == "build"
        assert paths_module.load_runtime(tmp_path)["friendly_message"] == "Resume build."

    def test_promote_quick_mode_back_to_full_resets_macro_checkpoints(self, tmp_path):
        state = paths_module.default_state(tmp_path, topic="demo")
        state["mode"] = "quick"
        state["checkpoints"]["quick_ready"] = True
        state["checkpoints"]["build"] = True
        write_json(tmp_path / "feature-list.json", {"features": []})
        paths_module.promote_quick_to_full(state, reason="scope expanded", project_root=tmp_path)
        assert state["mode"] == "full"
        assert state["current_phase"] == "spark"
        assert state["checkpoints"]["build"] is False
        assert not (tmp_path / "feature-list.json").exists()

    def test_check_st_readiness_accepts_brief_as_upstream_input(self, tmp_path):
        check_module = load_module(ROOT / "scripts" / "check_st_readiness.py")
        state = paths_module.default_state(tmp_path, topic="demo")
        paths_module.save_state(tmp_path, state)
        write(tmp_path / ".vibeflow" / "workflow.yaml", 'template: "api-standard"\n')
        write(tmp_path / state["artifacts"]["spark"], "# Brief\n")
        write(tmp_path / state["artifacts"]["design"], "# Design\n")
        write_json(tmp_path / "feature-list.json", {"features": [{"id": 1, "status": "passing", "deprecated": False}]})
        result = check_module.check_st_readiness(tmp_path / "feature-list.json")
        assert "brief.md" in (result.get("srs_path") or "")

    def test_detect_phase_after_tasks_enters_build(self, tmp_path):
        state = paths_module.default_state(tmp_path, topic="demo")
        state["checkpoints"]["spark"] = True
        state["checkpoints"]["design"] = True
        state["checkpoints"]["tasks"] = True
        paths_module.save_state(tmp_path, state)
        for key in ("spark", "design", "tasks"):
            write(tmp_path / state["artifacts"][key], f"# {key}\n")
        result = phase_module.detect_phase(tmp_path)
        assert result["phase"] == "build"
