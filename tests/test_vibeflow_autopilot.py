#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SAMPLE_ROOT = ROOT / "validation" / "sample-priority-api"


def run_python(script: Path, *args: object, cwd: Path | None = None, expect_ok: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, str(script), *[str(arg) for arg in args]],
        cwd=str(cwd or ROOT),
        capture_output=True,
        text=True,
    )
    if expect_ok:
        assert result.returncode == 0, (
            f"{script.name} failed with code {result.returncode}\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )
    return result


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def detect_phase(project_root: Path) -> dict:
    result = run_python(ROOT / "scripts" / "get-vibeflow-phase.py", "--project-root", project_root, "--json")
    return json.loads(result.stdout)


def run_autopilot(project_root: Path, *extra_args: object, expect_ok: bool = True) -> dict:
    result = run_python(
        ROOT / "scripts" / "run-vibeflow-autopilot.py",
        "--project-root",
        project_root,
        "--json",
        *extra_args,
        expect_ok=expect_ok,
    )
    return json.loads(result.stdout)


def run_build_work(project_root: Path, *extra_args: object, expect_ok: bool = True) -> dict:
    result = run_python(
        ROOT / "scripts" / "run-vibeflow-build-work.py",
        "--project-root",
        project_root,
        "--json",
        *extra_args,
        expect_ok=expect_ok,
    )
    return json.loads(result.stdout)


def copy_sample_project(tmp_path: Path, name: str) -> Path:
    target = tmp_path / name
    shutil.copytree(SAMPLE_ROOT, target)
    for pycache in target.rglob("__pycache__"):
        shutil.rmtree(pycache)
    return target


def prepare_sample_for_full_autopilot(project_root: Path) -> None:
    workflow_path = project_root / ".vibeflow" / "workflow.yaml"
    workflow = workflow_path.read_text(encoding="utf-8")
    if "ship:\n  required: true" not in workflow:
        workflow = workflow.replace(
            "ship:\n  version_strategy: \"semver\"",
            "ship:\n  required: true\n  version_strategy: \"semver\"",
        )
    if "reflect:\n  required: true" not in workflow:
        workflow = workflow.replace(
            "reflect:\n  required: false",
            "reflect:\n  required: true",
        )
    workflow_path.write_text(workflow, encoding="utf-8")

    state_path = project_root / ".vibeflow" / "state.json"
    state = read_json(state_path)
    state["mode"] = "full"
    state["current_phase"] = "design"
    state["checkpoints"]["build_init"] = True
    state["checkpoints"]["build_config"] = False
    state["checkpoints"]["build_work"] = False
    state["checkpoints"]["review"] = False
    state["checkpoints"]["test_system"] = False
    state["checkpoints"]["ship"] = False
    state["checkpoints"]["reflect"] = False
    write_json(state_path, state)

    feature_payload = read_json(project_root / "feature-list.json")
    for feature in feature_payload["features"]:
        feature["status"] = "failing"
    write_json(project_root / "feature-list.json", feature_payload)

    work_config = project_root / ".vibeflow" / "work-config.json"
    if work_config.exists():
        work_config.unlink()

    review_artifact = project_root / state["artifacts"]["review"]
    system_test_artifact = project_root / state["artifacts"]["system_test"]
    if review_artifact.exists():
        review_artifact.unlink()
    if system_test_artifact.exists():
        system_test_artifact.unlink()

    release_notes = project_root / "RELEASE_NOTES.md"
    if release_notes.exists():
        release_notes.unlink()

    for retro in (project_root / ".vibeflow" / "logs").glob("retro-*.md"):
        retro.unlink()
    legacy_retro = project_root / ".vibeflow" / "retro-2026-03-21.md"
    if legacy_retro.exists():
        legacy_retro.unlink()


def prepare_sample_for_quick_autopilot(project_root: Path) -> None:
    prepare_sample_for_full_autopilot(project_root)
    state_path = project_root / ".vibeflow" / "state.json"
    state = read_json(state_path)
    state["mode"] = "quick"
    state["current_phase"] = "quick"
    state["checkpoints"]["quick_ready"] = True
    state.setdefault("quick_meta", {})
    state["quick_meta"].update(
        {
            "decision": "approved",
            "category": "bugfix",
            "scope": "Run the bounded sample workflow end-to-end in Quick Mode.",
            "touchpoints": ["src/sample_priority_api/workflow.py", "tests/test_workflow.py"],
            "validation_plan": "Run the sample feature commands plus system tests.",
            "rollback_plan": "Revert the sample quick-mode change package.",
        }
    )
    write_json(state_path, state)
    write_text(project_root / state["artifacts"]["tasks"], "# Tasks\n\n- [ ] Run sample quick flow\n")


def create_parallel_project(tmp_path: Path) -> Path:
    project_root = tmp_path / "parallel-build-project"
    run_python(
        ROOT / "scripts" / "init_project.py",
        "parallel-build-project",
        "--path",
        project_root,
        "--lang",
        "python",
    )
    write_text(
        project_root / ".vibeflow" / "workflow.yaml",
        """name: "Parallel Build"
template: "api-standard"
created_at: "2026-03-25"

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
  required: false

reflect:
  required: false
""",
    )
    state = read_json(project_root / ".vibeflow" / "state.json")
    for checkpoint in ("think", "plan", "requirements", "design", "build_init", "build_config"):
        state["checkpoints"][checkpoint] = True
    state["current_phase"] = "build-work"
    write_json(project_root / ".vibeflow" / "state.json", state)
    write_text(project_root / state["artifacts"]["think"], "# Context\n\nParallel build context.\n")
    write_text(project_root / state["artifacts"]["plan"], "# Proposal\n\nParallel build proposal.\n")
    write_text(project_root / state["artifacts"]["requirements"], "# Requirements\n\nParallel build requirements.\n")
    write_text(project_root / state["artifacts"]["design"], "# Design\n\nParallel build design.\n")
    write_text(project_root / state["artifacts"]["design_review"], "# Design Review\n\nApproved.\n")
    run_python(ROOT / "scripts" / "new-vibeflow-work-config.py", "--project-root", project_root)

    write_text(
        project_root / "scripts" / "parallel_barrier.py",
        """from pathlib import Path
import sys
import time

root = Path(sys.argv[1])
name = sys.argv[2]
peer = sys.argv[3]

(root / f"{name}-start").write_text(name, encoding="utf-8")
deadline = time.time() + 5
while not (root / f"{peer}-start").exists():
    if time.time() >= deadline:
        raise SystemExit("peer did not start in time")
    time.sleep(0.05)
(root / f"{name}-done").write_text(name, encoding="utf-8")
""",
    )
    write_text(
        project_root / "scripts" / "parallel_verify.py",
        """from pathlib import Path
import sys

root = Path(sys.argv[1])
required = ["feature-a-done", "feature-b-done"]
missing = [name for name in required if not (root / name).exists()]
if missing:
    raise SystemExit(f"missing markers: {missing}")
(root / "feature-c-done").write_text("feature-c", encoding="utf-8")
""",
    )

    marker_root = project_root / ".tmp-markers"
    marker_root.mkdir(parents=True, exist_ok=True)
    feature_payload = read_json(project_root / "feature-list.json")
    feature_payload["features"] = [
        {
            "id": 1,
            "category": "build",
            "title": "Feature A",
            "description": "First independent feature lane.",
            "status": "failing",
            "priority": "high",
            "dependencies": [],
            "file_scope": ["src/feature-a"],
            "verification_steps": ["Run feature A barrier command"],
            "autopilot_commands": [
                f'python scripts/parallel_barrier.py "{marker_root}" feature-a feature-b'
            ],
        },
        {
            "id": 2,
            "category": "build",
            "title": "Feature B",
            "description": "Second independent feature lane.",
            "status": "failing",
            "priority": "high",
            "dependencies": [],
            "file_scope": ["src/feature-b"],
            "verification_steps": ["Run feature B barrier command"],
            "autopilot_commands": [
                f'python scripts/parallel_barrier.py "{marker_root}" feature-b feature-a'
            ],
        },
        {
            "id": 3,
            "category": "build",
            "title": "Feature C",
            "description": "Dependent feature that waits for A and B.",
            "status": "failing",
            "priority": "medium",
            "dependencies": [1, 2],
            "file_scope": ["src/feature-c"],
            "verification_steps": ["Verify dependency markers exist"],
            "autopilot_commands": [
                f'python scripts/parallel_verify.py "{marker_root}"'
            ],
        },
    ]
    write_json(project_root / "feature-list.json", feature_payload)
    return project_root


def create_conflicting_parallel_project(tmp_path: Path) -> Path:
    project_root = tmp_path / "conflicting-build-project"
    run_python(
        ROOT / "scripts" / "init_project.py",
        "conflicting-build-project",
        "--path",
        project_root,
        "--lang",
        "python",
    )
    write_text(
        project_root / ".vibeflow" / "workflow.yaml",
        """name: "Conflicting Build"
template: "api-standard"
created_at: "2026-03-25"

build:
  steps:
    - id: tdd
      required: true
""",
    )
    state = read_json(project_root / ".vibeflow" / "state.json")
    for checkpoint in ("think", "plan", "requirements", "design", "build_init", "build_config"):
        state["checkpoints"][checkpoint] = True
    state["current_phase"] = "build-work"
    write_json(project_root / ".vibeflow" / "state.json", state)
    write_text(project_root / state["artifacts"]["think"], "# Context\n\nConflicting build context.\n")
    write_text(project_root / state["artifacts"]["plan"], "# Proposal\n\nConflicting build proposal.\n")
    write_text(project_root / state["artifacts"]["requirements"], "# Requirements\n\nConflicting build requirements.\n")
    write_text(project_root / state["artifacts"]["design"], "# Design\n\nConflicting build design.\n")
    write_text(project_root / state["artifacts"]["design_review"], "# Design Review\n\nApproved.\n")
    run_python(ROOT / "scripts" / "new-vibeflow-work-config.py", "--project-root", project_root)

    write_text(
        project_root / "scripts" / "exclusive_lock.py",
        """from pathlib import Path
import sys
import time

lock_file = Path(sys.argv[1])
done_file = Path(sys.argv[2])
if lock_file.exists():
    raise SystemExit("lock already held")
lock_file.write_text("locked", encoding="utf-8")
time.sleep(0.15)
done_file.write_text("done", encoding="utf-8")
lock_file.unlink()
""",
    )

    marker_root = project_root / ".tmp-conflict"
    marker_root.mkdir(parents=True, exist_ok=True)
    shared_scope = ["src/shared"]
    shared_lock = marker_root / "shared.lock"
    feature_a_done = marker_root / "feature-a.done"
    feature_b_done = marker_root / "feature-b.done"
    feature_payload = read_json(project_root / "feature-list.json")
    feature_payload["features"] = [
        {
            "id": 1,
            "category": "build",
            "title": "Shared Feature A",
            "description": "Touches a shared implementation surface.",
            "status": "failing",
            "priority": "high",
            "dependencies": [],
            "file_scope": shared_scope,
            "verification_steps": ["Run shared feature A command"],
            "autopilot_commands": [
                f'python scripts/exclusive_lock.py "{shared_lock}" "{feature_a_done}"'
            ],
        },
        {
            "id": 2,
            "category": "build",
            "title": "Shared Feature B",
            "description": "Touches the same shared implementation surface.",
            "status": "failing",
            "priority": "high",
            "dependencies": [],
            "file_scope": shared_scope,
            "verification_steps": ["Run shared feature B command"],
            "autopilot_commands": [
                f'python scripts/exclusive_lock.py "{shared_lock}" "{feature_b_done}"'
            ],
        },
    ]
    write_json(project_root / "feature-list.json", feature_payload)
    return project_root


class TestVibeFlowAutopilot:
    def test_build_init_generates_feature_packets_and_normalized_feature_contracts(self, tmp_path):
        project_root = tmp_path / "packet-build-init"
        run_python(
            ROOT / "scripts" / "init_project.py",
            "packet-build-init",
            "--path",
            project_root,
            "--lang",
            "python",
        )

        state = read_json(project_root / ".vibeflow" / "state.json")
        for checkpoint in ("think", "plan", "requirements", "design"):
            state["checkpoints"][checkpoint] = True
        state["current_phase"] = "design"
        write_json(project_root / ".vibeflow" / "state.json", state)

        change_root = project_root / state["active_change"]["root"]
        write_text(change_root / "context.md", "# Context\n\nDeliver a small authenticated API workflow.\n")
        write_text(change_root / "proposal.md", "# Proposal\n\nImplement two bounded features.\n")
        write_text(change_root / "requirements.md", "# Requirements\n\n- FR-001 Auth flow\n- FR-002 Audit trail\n")
        write_text(change_root / "design.md", "# Design\n\n## 4.1 Auth\n\nImplement auth.\n\n## 4.2 Audit\n\nImplement audit.\n")
        write_text(change_root / "design-review.md", "# Design Review\n\nApproved.\n")
        write_text(
            project_root / ".vibeflow" / "workflow.yaml",
            'name: "Packet Build Init"\ntemplate: "api-standard"\n',
        )
        write_text(
            change_root / "tasks.md",
            "# Tasks\n\n- [ ] Implement auth flow\n- [ ] Implement audit trail\n",
        )

        result = run_autopilot(project_root, "--stop-at", "build-config")
        assert result["status"] == "stopped"
        assert result["final_phase"] == "build-config"

        feature_payload = read_json(project_root / "feature-list.json")
        assert len(feature_payload["features"]) == 2
        first = feature_payload["features"][0]
        assert first["objective"] == "Implement auth flow"
        assert "done_criteria" in first
        assert "source_refs" in first
        assert "requirements" in first["source_refs"]
        assert "design" in first["source_refs"]
        assert "tasks" in first["source_refs"]

        packet_dir = project_root / ".vibeflow" / "packets" / state["active_change"]["id"]
        packet_path = packet_dir / "feature-1.json"
        assert packet_path.exists()
        packet = read_json(packet_path)
        assert packet["feature"]["id"] == 1
        assert packet["objective"] == "Implement auth flow"
        assert packet["source_snippets"]["requirements_summary"]
        assert packet["source_snippets"]["design_summary"]

    def test_autopilot_waits_at_manual_phase(self, tmp_path):
        project_root = tmp_path / "manual-stop-project"
        run_python(
            ROOT / "scripts" / "init_project.py",
            "manual-stop-project",
            "--path",
            project_root,
            "--lang",
            "python",
        )
        result = run_autopilot(project_root)
        assert result["status"] == "waiting_manual"
        assert result["final_phase"] == "think"

        runtime = read_json(project_root / ".vibeflow" / "runtime.json")
        assert runtime["status"] == "waiting_manual"
        assert runtime["current_phase"] == "think"

    def test_full_mode_autopilot_runs_sample_project_to_done(self, tmp_path):
        project_root = copy_sample_project(tmp_path, "sample-full-autopilot")
        prepare_sample_for_full_autopilot(project_root)

        phase_before = detect_phase(project_root)
        assert phase_before["phase"] == "build-config"

        result = run_autopilot(project_root, "--max-workers", 2)
        assert result["status"] == "completed"
        assert result["final_phase"] == "done"

        phase_after = detect_phase(project_root)
        assert phase_after["phase"] == "done"

        state = read_json(project_root / ".vibeflow" / "state.json")
        assert state["checkpoints"]["build_config"] is True
        assert state["checkpoints"]["build_work"] is True
        assert state["checkpoints"]["review"] is True
        assert state["checkpoints"]["test_system"] is True
        assert state["checkpoints"]["ship"] is True
        assert state["checkpoints"]["reflect"] is True

        review_artifact = project_root / state["artifacts"]["review"]
        system_test_artifact = project_root / state["artifacts"]["system_test"]
        assert review_artifact.exists()
        assert system_test_artifact.exists()
        review_text = review_artifact.read_text(encoding="utf-8")
        assert "## Spec Compliance" in review_text
        assert "## Code Quality" in review_text
        assert "## Verdict" in review_text
        assert (project_root / "RELEASE_NOTES.md").exists()
        assert any((project_root / ".vibeflow" / "logs").glob("retro-*.md"))

    def test_quick_mode_autopilot_runs_sample_project_to_done(self, tmp_path):
        project_root = copy_sample_project(tmp_path, "sample-quick-autopilot")
        prepare_sample_for_quick_autopilot(project_root)

        phase_before = detect_phase(project_root)
        assert phase_before["phase"] == "build-work"

        result = run_autopilot(project_root, "--max-workers", 2)
        assert result["status"] == "completed"
        assert result["final_phase"] == "done"

        state = read_json(project_root / ".vibeflow" / "state.json")
        assert state["mode"] == "quick"
        assert state["checkpoints"]["build_work"] is True
        assert state["checkpoints"]["review"] is True
        assert state["checkpoints"]["test_system"] is True
        assert state["checkpoints"]["ship"] is True
        assert state["checkpoints"]["reflect"] is True

    def test_parallel_build_runs_ready_features_and_respects_dependencies(self, tmp_path):
        project_root = create_parallel_project(tmp_path)
        result = run_build_work(project_root, "--max-workers", 2)
        assert result["ok"] is True

        feature_payload = read_json(project_root / "feature-list.json")
        statuses = {feature["id"]: feature["status"] for feature in feature_payload["features"]}
        assert statuses == {1: "passing", 2: "passing", 3: "passing"}

        marker_root = project_root / ".tmp-markers"
        assert (marker_root / "feature-a-start").exists()
        assert (marker_root / "feature-b-start").exists()
        assert (marker_root / "feature-a-done").exists()
        assert (marker_root / "feature-b-done").exists()
        assert (marker_root / "feature-c-done").exists()

        state = read_json(project_root / ".vibeflow" / "state.json")
        packet_dir = project_root / ".vibeflow" / "packets" / state["active_change"]["id"]
        result_dir = project_root / ".vibeflow" / "subagent-results" / state["active_change"]["id"]
        assert (packet_dir / "feature-1.json").exists()
        assert (packet_dir / "feature-2.json").exists()
        assert (packet_dir / "feature-3.json").exists()
        assert (result_dir / "feature-1.json").exists()
        assert (result_dir / "feature-2.json").exists()
        assert (result_dir / "feature-3.json").exists()
        feature_result = read_json(result_dir / "feature-1.json")
        assert feature_result["status"] == "passing"
        assert feature_result["verification"]["passed"] is True

    def test_autopilot_blocks_on_failed_feature_command(self, tmp_path):
        project_root = create_parallel_project(tmp_path)
        feature_payload = read_json(project_root / "feature-list.json")
        feature_payload["features"][0]["autopilot_commands"] = ["python -c \"raise SystemExit(7)\""]
        write_json(project_root / "feature-list.json", feature_payload)

        result = run_autopilot(project_root, "--max-workers", 2, expect_ok=False)
        assert result["status"] == "blocked"
        assert result["final_phase"] == "build-work"

        runtime = read_json(project_root / ".vibeflow" / "runtime.json")
        assert runtime["status"] == "blocked"
        assert runtime["current_phase"] == "build-work"

    def test_review_blocks_when_feature_result_is_missing(self, tmp_path):
        project_root = create_parallel_project(tmp_path)

        build_result = run_build_work(project_root, "--max-workers", 2)
        assert build_result["ok"] is True

        state = read_json(project_root / ".vibeflow" / "state.json")
        result_dir = project_root / ".vibeflow" / "subagent-results" / state["active_change"]["id"]
        missing_result = result_dir / "feature-2.json"
        assert missing_result.exists()
        missing_result.unlink()

        state["current_phase"] = "review"
        state["checkpoints"]["build_work"] = True
        state["checkpoints"]["review"] = False
        write_json(project_root / ".vibeflow" / "state.json", state)

        result = run_autopilot(project_root, expect_ok=False)
        assert result["status"] == "blocked"
        assert result["final_phase"] == "review"

        runtime = read_json(project_root / ".vibeflow" / "runtime.json")
        assert runtime["status"] == "blocked"
        assert runtime["current_phase"] == "review"

        review_artifact = project_root / state["artifacts"]["review"]
        assert review_artifact.exists()
        review_text = review_artifact.read_text(encoding="utf-8")
        assert "Feature #2 (Feature B): implementation result file is missing." in review_text
        assert "FAIL — Fix review issues before system testing." in review_text

    def test_parallel_build_falls_back_to_serial_when_file_scope_overlaps(self, tmp_path):
        project_root = create_conflicting_parallel_project(tmp_path)

        result = run_build_work(project_root, "--max-workers", 2)
        assert result["ok"] is True

        feature_payload = read_json(project_root / "feature-list.json")
        statuses = {feature["id"]: feature["status"] for feature in feature_payload["features"]}
        assert statuses == {1: "passing", 2: "passing"}

        marker_root = project_root / ".tmp-conflict"
        assert (marker_root / "feature-a.done").exists()
        assert (marker_root / "feature-b.done").exists()
