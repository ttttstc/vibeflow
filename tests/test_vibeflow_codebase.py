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
    def test_map_codebase_refreshes_overview_without_persisting_process_files(self, tmp_path):
        project_root = copy_sample_project(tmp_path, "sample-codebase-map")

        result = run_python(
            ROOT / "scripts" / "map-codebase.py",
            "--project-root",
            project_root,
            "--refresh",
            "force",
            "--json",
        )
        payload = json.loads(result.stdout)
        assert payload["status"] == "built"
        assert payload["overview"]["project"].endswith("docs\\overview\\PROJECT.md")
        assert payload["overview"]["architecture"].endswith("docs\\overview\\ARCHITECTURE.md")
        assert not (project_root / ".vibeflow" / "codebase-map.json").exists()
        assert not (project_root / ".vibeflow" / "codebase-map.md").exists()
        assert not (project_root / ".vibeflow" / "analysis").exists()

        project_doc = (project_root / "docs" / "overview" / "PROJECT.md").read_text(encoding="utf-8")
        architecture_doc = (project_root / "docs" / "overview" / "ARCHITECTURE.md").read_text(encoding="utf-8")
        assert "sample_priority_api" in project_doc
        assert "src" in architecture_doc
        assert "tests" in architecture_doc
        assert "C4 分层结构" in architecture_doc
        assert "Arc42 深度架构视图" in architecture_doc

    def test_map_change_impact_refreshes_current_state_without_writing_change_scoped_process_files(self, tmp_path):
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
        assert not impact_md_path.exists()
        assert not (project_root / ".vibeflow" / "analysis").exists()
        assert payload["matched_terms"]
        assert payload["relevant_modules"] >= 1

        current_state = (project_root / "docs" / "overview" / "CURRENT-STATE.md").read_text(encoding="utf-8")
        assert "## 当前变更关注点" in current_state
        assert "重点模块" in current_state
        assert "建议先读" in current_state
        assert "sample_priority_api" in current_state
