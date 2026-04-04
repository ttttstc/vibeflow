#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def run_python(script: Path, *args: object) -> tuple[int, str, str]:
    result = subprocess.run(
        [sys.executable, str(script), *[str(arg) for arg in args]],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


def run_autopilot(project_root: Path, *args: object) -> dict:
    code, stdout, stderr = run_python(
        ROOT / "scripts" / "run-vibeflow-autopilot.py",
        "--project-root",
        project_root,
        "--json",
        *args,
    )
    assert code in {0, 1}, stderr
    return json.loads(stdout)


def run_build(project_root: Path, *args: object) -> dict:
    code, stdout, stderr = run_python(
        ROOT / "scripts" / "run-vibeflow-build-work.py",
        "--project-root",
        project_root,
        "--json",
        *args,
    )
    assert code in {0, 1}, stderr
    return json.loads(stdout)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def update_state(project_root: Path, mutator) -> dict:
    state_path = project_root / ".vibeflow" / "state.json"
    state = read_json(state_path)
    mutator(state)
    write_json(state_path, state)
    return state


def init_project(project_root: Path, name: str = "autopilot-project") -> dict:
    code, stdout, stderr = run_python(ROOT / "scripts" / "init_project.py", name, "--path", project_root, "--lang", "python")
    assert code == 0, stderr or stdout
    return read_json(project_root / ".vibeflow" / "state.json")


def ready_for_build(project_root: Path, *, quick: bool = False, command: str = "python -c \"print('ok')\"", system_test_command: str = "python -c \"print('st')\"") -> dict:
    state = init_project(project_root, project_root.name)
    workflow = 'template: "api-standard"\nship:\n  required: false\nreflect:\n  required: false\n'
    write_text(project_root / ".vibeflow" / "workflow.yaml", workflow)
    if quick:
        state["mode"] = "quick"
        state["checkpoints"]["quick_ready"] = True
        state["quick_meta"].update(
            {
                "decision": "approved",
                "category": "bugfix",
                "scope": "Small bounded change",
                "touchpoints": ["src/demo.py"],
                "validation_plan": "Run quick checks",
                "rollback_plan": "Revert commit",
            }
        )
    else:
        state["checkpoints"]["spark"] = True
    write_text(project_root / state["artifacts"]["spark"], "# Brief\n")
    state["checkpoints"]["design"] = True
    write_text(project_root / state["artifacts"]["design"], "# Design\n\n## Review Summary\n\nApproved.\n")
    state["checkpoints"]["tasks"] = True
    write_text(project_root / state["artifacts"]["tasks"], "# Tasks\n")
    write_json(project_root / ".vibeflow" / "state.json", state)
    write_json(
        project_root / "feature-list.json",
        {
            "project": project_root.name,
            "tech_stack": {"language": "python"},
            "real_test": {
                "system_test_command": system_test_command,
                "marker_pattern": "test_*",
                "test_dir": "tests",
            },
            "features": [
                {
                    "id": 1,
                    "title": "Primary flow",
                    "status": "failing",
                    "priority": "high",
                    "deprecated": False,
                    "command": command,
                    "verification_steps": ["Run the primary feature command and confirm success."],
                }
            ],
        },
    )
    return state


class TestVibeFlowAutopilot:
    def test_autopilot_waits_at_manual_phase(self, tmp_path):
        project_root = tmp_path / "manual-stop-project"
        init_project(project_root, "manual-stop-project")
        result = run_autopilot(project_root)
        assert result["status"] == "waiting_manual"
        assert result["final_phase"] == "spark"
        state = read_json(project_root / ".vibeflow" / "state.json")
        assert state["runtime"]["current_phase"] == "spark"

    def test_build_phase_blocks_on_failed_feature_command(self, tmp_path):
        project_root = tmp_path / "failed-build-project"
        ready_for_build(project_root, command="python -c \"import sys; sys.exit(1)\"")
        result = run_autopilot(project_root)
        assert result["status"] == "blocked"
        assert result["final_phase"] == "build"

    def test_full_mode_autopilot_runs_to_done(self, tmp_path):
        project_root = tmp_path / "full-mode-project"
        ready_for_build(project_root)
        result = run_autopilot(project_root)
        assert result["status"] == "completed"
        assert result["final_phase"] == "done"
        state = read_json(project_root / ".vibeflow" / "state.json")
        runtime = state["runtime"]
        assert state["checkpoints"]["build"] is True
        assert state["checkpoints"]["review"] is True
        assert state["checkpoints"]["test"] is True
        assert "归档文档" in runtime["friendly_message"]
        assert "requirements:" in runtime["friendly_message"]
        assert "design:" in runtime["friendly_message"]
        assert "tasks:" in runtime["friendly_message"]
        assert "review:" in runtime["friendly_message"]

    def test_quick_mode_autopilot_runs_to_done(self, tmp_path):
        project_root = tmp_path / "quick-mode-project"
        ready_for_build(project_root, quick=True)
        result = run_autopilot(project_root)
        assert result["status"] == "completed"
        assert result["final_phase"] == "done"

    def test_build_wrapper_executes_build_phase(self, tmp_path):
        project_root = tmp_path / "build-wrapper-project"
        ready_for_build(project_root)
        result = run_build(project_root, "--serial")
        assert result["ok"] is True
        assert result["detail"]
