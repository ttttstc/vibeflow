#!/usr/bin/env python3
"""End-to-end mode flow tests for the VibeFlow v2 layout."""

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
        f"{script.name} failed with code {result.returncode}\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
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
    output = run_python(
        ROOT / "scripts" / "get-vibeflow-phase.py",
        "--project-root",
        project_root,
        "--json",
    )
    return json.loads(output)


def setup_report(project_root: Path) -> dict:
    output = run_python(
        ROOT / "scripts" / "test-vibeflow-setup.py",
        "--project-root",
        project_root,
        "--json",
    )
    return json.loads(output)


def create_workflow(project_root: Path) -> None:
    write_text(
        project_root / ".vibeflow" / "workflow.yaml",
        """name: "Mode E2E"
template: "api-standard"
created_at: "2026-03-24"

build:
  steps:
    - id: tdd
      required: true
    - id: quality
      required: true
    - id: review
      required: true

test:
  st:
    required: true
  qa:
    required: false

ship:
  required: true

reflect:
  required: true
""",
    )


def create_feature_list(project_root: Path, status: str) -> None:
    write_json(
        project_root / "feature-list.json",
        {
            "project": project_root.name,
            "features": [
                {
                    "id": 1,
                    "title": "Primary flow",
                    "status": status,
                    "priority": "high",
                    "ui": False,
                    "dependencies": [],
                }
            ],
        },
    )


class TestVibeFlowModeE2E:
    def test_detect_phase_cli_syncs_invariant_reason_to_runtime(self, tmp_path):
        project_root = tmp_path / "invariant-runtime-project"
        run_python(
            ROOT / "scripts" / "init_project.py",
            "invariant-runtime-project",
            "--path",
            project_root,
            "--lang",
            "python",
        )

        create_workflow(project_root)
        state = update_state(
            project_root,
            lambda data: data["checkpoints"].__setitem__("spark", True),
        )
        write_text(project_root / state["artifacts"]["spark"], "# Context\n\nInvariant runtime.\n")
        write_text(project_root / state["artifacts"]["requirements"], "# Requirements\n\nWaiting approval.\n")

        result = detect_phase(project_root)
        assert result["phase"] == "requirements"
        assert result["reason_code"] == "missing_approval"
        assert result["blocking_item"] == "requirements"

        runtime = read_json(project_root / ".vibeflow" / "runtime.json")
        assert runtime["invariant"]["phase"] == "requirements"
        assert runtime["invariant"]["reason_code"] == "missing_approval"
        assert "requirements checkpoint" in runtime["invariant"]["reason"]

    def test_full_mode_end_to_end_flow(self, tmp_path):
        project_root = tmp_path / "full-mode-project"
        run_python(
            ROOT / "scripts" / "init_project.py",
            "full-mode-project",
            "--path",
            project_root,
            "--lang",
            "python",
        )

        create_workflow(project_root)
        phases = [detect_phase(project_root)["phase"]]
        assert phases[-1] == "spark"

        state = update_state(
            project_root,
            lambda data: data["checkpoints"].__setitem__("spark", True),
        )
        write_text(project_root / state["artifacts"]["spark"], "# Context\n\nFull mode context.\n")
        phases.append(detect_phase(project_root)["phase"])
        assert phases[-1] == "requirements"

        state = update_state(
            project_root,
            lambda data: data["checkpoints"].__setitem__("requirements", True),
        )
        write_text(
            project_root / state["artifacts"]["requirements"],
            "# Requirements\n\nFull mode requirements.\n",
        )
        phases.append(detect_phase(project_root)["phase"])
        assert phases[-1] == "design"

        state = update_state(
            project_root,
            lambda data: data["checkpoints"].__setitem__("design", True),
        )
        write_text(project_root / state["artifacts"]["design"], "# Design\n\nFull mode design.\n")
        write_text(
            project_root / state["artifacts"]["design_review"],
            "# Design Review\n\nApproved.\n",
        )
        phases.append(detect_phase(project_root)["phase"])
        assert phases[-1] == "build-init"

        update_state(
            project_root,
            lambda data: data["checkpoints"].__setitem__("build_init", True),
        )
        create_feature_list(project_root, "todo")
        state = read_json(project_root / ".vibeflow" / "state.json")
        write_text(project_root / state["artifacts"]["tasks"], "# Tasks\n\n- [ ] Feature 1: Primary flow\n")
        phases.append(detect_phase(project_root)["phase"])
        assert phases[-1] == "tasks"

        update_state(
            project_root,
            lambda data: data["checkpoints"].__setitem__("tasks", True),
        )
        phases.append(detect_phase(project_root)["phase"])
        assert phases[-1] == "build-config"

        run_python(ROOT / "scripts" / "new-vibeflow-work-config.py", "--project-root", project_root)
        phases.append(detect_phase(project_root)["phase"])
        assert phases[-1] == "build-work"

        create_feature_list(project_root, "passing")
        phases.append(detect_phase(project_root)["phase"])
        assert phases[-1] == "review"

        state = update_state(
            project_root,
            lambda data: data["checkpoints"].__setitem__("review", True),
        )
        write_text(project_root / state["artifacts"]["review"], "# Review\n\nLooks good.\n")
        phases.append(detect_phase(project_root)["phase"])
        assert phases[-1] == "test-system"

        state = update_state(
            project_root,
            lambda data: data["checkpoints"].__setitem__("test_system", True),
        )
        write_text(
            project_root / state["artifacts"]["system_test"],
            "# System Test\n\nAll cases passed.\n",
        )
        phases.append(detect_phase(project_root)["phase"])
        assert phases[-1] == "ship"

        update_state(
            project_root,
            lambda data: data["checkpoints"].__setitem__("ship", True),
        )
        phases.append(detect_phase(project_root)["phase"])
        assert phases[-1] == "reflect"

        update_state(
            project_root,
            lambda data: data["checkpoints"].__setitem__("reflect", True),
        )
        write_text(
            project_root / ".vibeflow" / "logs" / "retro-2026-03-24.md",
            "# Retro\n\nShip complete.\n",
        )
        final_result = detect_phase(project_root)
        phases.append(final_result["phase"])
        assert final_result["phase"] == "done"

        assert phases == [
            "spark",
            "requirements",
            "design",
            "build-init",
            "tasks",
            "build-config",
            "build-work",
            "review",
            "test-system",
            "ship",
            "reflect",
            "done",
        ]

    def test_quick_mode_end_to_end_flow(self, tmp_path):
        project_root = tmp_path / "quick-mode-project"
        run_python(
            ROOT / "scripts" / "init_project.py",
            "quick-mode-project",
            "--path",
            project_root,
            "--lang",
            "python",
        )

        update_state(
            project_root,
            lambda data: data.__setitem__("mode", "quick"),
        )
        phases = [detect_phase(project_root)["phase"]]
        assert phases[-1] == "quick"

        create_workflow(project_root)
        run_python(ROOT / "scripts" / "new-vibeflow-work-config.py", "--project-root", project_root)

        state = update_state(
            project_root,
            lambda data: data["quick_meta"].update(
                {
                    "decision": "approved",
                    "category": "bugfix",
                    "scope": "Fix a small bounded issue.",
                    "touchpoints": ["src/quick_mode_project.py"],
                    "validation_plan": "Run the targeted quick-mode checks.",
                    "rollback_plan": "Revert the single quick-mode commit.",
                }
            ),
        )
        state["checkpoints"]["quick_ready"] = True
        write_json(project_root / ".vibeflow" / "state.json", state)
        write_text(project_root / state["artifacts"]["design"], "# Quick Design\n\nMinimal plan.\n")
        write_text(project_root / state["artifacts"]["tasks"], "# Tasks\n\n- Implement flow\n")
        create_feature_list(project_root, "todo")
        phases.append(detect_phase(project_root)["phase"])
        assert phases[-1] == "build-work"

        create_feature_list(project_root, "passing")
        phases.append(detect_phase(project_root)["phase"])
        assert phases[-1] == "review"

        state = update_state(
            project_root,
            lambda data: data["checkpoints"].__setitem__("review", True),
        )
        write_text(project_root / state["artifacts"]["review"], "# Review\n\nQuick review passed.\n")
        phases.append(detect_phase(project_root)["phase"])
        assert phases[-1] == "test-system"

        state = update_state(
            project_root,
            lambda data: data["checkpoints"].__setitem__("test_system", True),
        )
        write_text(
            project_root / state["artifacts"]["system_test"],
            "# System Test\n\nQuick mode checks passed.\n",
        )
        phases.append(detect_phase(project_root)["phase"])
        assert phases[-1] == "ship"

        update_state(
            project_root,
            lambda data: data["checkpoints"].__setitem__("ship", True),
        )
        phases.append(detect_phase(project_root)["phase"])
        assert phases[-1] == "reflect"

        update_state(
            project_root,
            lambda data: data["checkpoints"].__setitem__("reflect", True),
        )
        write_text(
            project_root / ".vibeflow" / "logs" / "retro-2026-03-24.md",
            "# Retro\n\nQuick mode ship complete.\n",
        )
        final_result = detect_phase(project_root)
        phases.append(final_result["phase"])
        assert final_result["phase"] == "done"

        assert phases == [
            "quick",
            "build-work",
            "review",
            "test-system",
            "ship",
            "reflect",
            "done",
        ]
