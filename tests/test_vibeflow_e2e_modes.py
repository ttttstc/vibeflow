#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def run_python(script: Path, *args: object) -> str:
    result = subprocess.run(
        [sys.executable, str(script), *[str(arg) for arg in args]],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"{script.name} failed with code {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
    return result.stdout


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


def detect_phase(project_root: Path) -> dict:
    output = run_python(ROOT / "scripts" / "get-vibeflow-phase.py", "--project-root", project_root, "--json")
    return json.loads(output)


class TestVibeFlowModeE2E:
    def test_detect_phase_syncs_runtime_into_state(self, tmp_path):
        project_root = tmp_path / "sync-project"
        run_python(ROOT / "scripts" / "init_project.py", "sync-project", "--path", project_root, "--lang", "python")
        result = detect_phase(project_root)
        assert result["phase"] == "spark"
        state = read_json(project_root / ".vibeflow" / "state.json")
        assert state["runtime"]["current_phase"] == "spark"
        assert state["runtime"]["invariant"]["reason_code"]

    def test_full_mode_end_to_end_flow(self, tmp_path):
        project_root = tmp_path / "full-mode-project"
        run_python(ROOT / "scripts" / "init_project.py", "full-mode-project", "--path", project_root, "--lang", "python")

        phases = [detect_phase(project_root)["phase"]]
        assert phases[-1] == "spark"

        state = update_state(project_root, lambda data: data["checkpoints"].__setitem__("spark", True))
        write_text(project_root / state["artifacts"]["spark"], "# Brief\n")
        phases.append(detect_phase(project_root)["phase"])
        assert phases[-1] == "design"

        state = update_state(project_root, lambda data: data["checkpoints"].__setitem__("design", True))
        write_text(project_root / state["artifacts"]["design"], "# Design\n\n## Review Summary\n\nApproved.\n")
        phases.append(detect_phase(project_root)["phase"])
        assert phases[-1] == "tasks"

        state = update_state(project_root, lambda data: data["checkpoints"].__setitem__("tasks", True))
        write_text(project_root / state["artifacts"]["tasks"], "# Tasks\n")
        phases.append(detect_phase(project_root)["phase"])
        assert phases[-1] == "build"

        write_json(project_root / "feature-list.json", {"features": [{"id": 1, "title": "Primary flow", "status": "passing", "deprecated": False}]})
        phases.append(detect_phase(project_root)["phase"])
        assert phases[-1] == "review"

        state = update_state(project_root, lambda data: data["checkpoints"].__setitem__("review", True))
        write_text(project_root / state["artifacts"]["review"], "# Review\n\nLooks good.\n")
        phases.append(detect_phase(project_root)["phase"])
        assert phases[-1] == "test"

        state = update_state(project_root, lambda data: data["checkpoints"].__setitem__("test", True))
        write_text(project_root / state["artifacts"]["system_test"], "# System Test\n\nPassed.\n")
        phases.append(detect_phase(project_root)["phase"])
        assert phases[-1] == "done"

    def test_quick_mode_enters_build_directly(self, tmp_path):
        project_root = tmp_path / "quick-mode-project"
        run_python(ROOT / "scripts" / "init_project.py", "quick-mode-project", "--path", project_root, "--lang", "python")

        state = update_state(
            project_root,
            lambda data: (
                data.__setitem__("mode", "quick"),
                data["quick_meta"].update(
                    {
                        "decision": "approved",
                        "category": "bugfix",
                        "scope": "Fix a small bounded issue.",
                        "touchpoints": ["src/quick_mode_project.py"],
                        "validation_plan": "Run the targeted quick-mode checks.",
                        "rollback_plan": "Revert the single quick-mode commit.",
                    }
                ),
                data["checkpoints"].__setitem__("quick_ready", True),
            ),
        )
        write_text(project_root / state["artifacts"]["design"], "# Quick Design\n")
        write_text(project_root / state["artifacts"]["tasks"], "# Tasks\n")
        assert detect_phase(project_root)["phase"] == "build"
