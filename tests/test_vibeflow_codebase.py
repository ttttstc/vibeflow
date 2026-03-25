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


def copy_sample_project(tmp_path: Path, name: str) -> Path:
    target = tmp_path / name
    shutil.copytree(SAMPLE_ROOT, target)
    for pycache in target.rglob("__pycache__"):
        shutil.rmtree(pycache)
    return target


class TestCodebaseArtifacts:
    def test_map_codebase_builds_and_then_reuses(self, tmp_path):
        project_root = copy_sample_project(tmp_path, "sample-codebase-map")

        first = run_python(
            ROOT / "scripts" / "map-codebase.py",
            "--project-root",
            project_root,
            "--refresh",
            "force",
            "--json",
        )
        second = run_python(ROOT / "scripts" / "map-codebase.py", "--project-root", project_root, "--json")

        first_payload = json.loads(first.stdout)
        second_payload = json.loads(second.stdout)
        assert first_payload["status"] == "built"
        assert second_payload["status"] == "reused"

        map_json = project_root / ".vibeflow" / "codebase-map.json"
        map_md = project_root / ".vibeflow" / "codebase-map.md"
        assert map_json.exists()
        assert not map_md.exists()

        data = read_json(map_json)
        assert data["roots"]["source"] == ["src"]
        assert data["roots"]["tests"] == ["tests"]
        assert any(module["path"] == "src/sample_priority_api" for module in data["modules"])

    def test_map_change_impact_writes_change_scoped_artifacts(self, tmp_path):
        project_root = copy_sample_project(tmp_path, "sample-codebase-impact")

        result = run_python(ROOT / "scripts" / "map-change-impact.py", "--project-root", project_root, "--json")
        payload = json.loads(result.stdout)
        assert payload["status"] == "built"

        impact_json = project_root / ".vibeflow" / "state.json"
        state = read_json(impact_json)
        change_root = project_root / state["active_change"]["root"]
        impact_json_path = change_root / "codebase-impact.json"
        impact_md_path = change_root / "codebase-impact.md"

        assert not impact_json_path.exists()
        assert impact_md_path.exists()
        assert payload["matched_terms"]
        assert payload["relevant_modules"] >= 1

        content = impact_md_path.read_text(encoding="utf-8")
        assert "## Relevant Modules" in content
        assert "## Integration Points" in content
        assert "## Suggested Read Order" in content
        assert "sample_priority_api" in content
