#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


overview_module = load_module(ROOT / "scripts" / "vibeflow_overview.py")
paths_module = load_module(ROOT / "scripts" / "vibeflow_paths.py")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, data: object) -> None:
    write(path, json.dumps(data, indent=2, ensure_ascii=False))


def seed_repo(tmp_path: Path, module_name: str) -> None:
    write(tmp_path / "src" / module_name / "__init__.py", "")
    write(tmp_path / "src" / "main.py", "from src import main\n")
    write(tmp_path / "tests" / f"test_{module_name}.py", "def test_smoke():\n    assert True\n")


class TestVibeFlowOverview:
    def test_ensure_overview_docs_generates_chinese_surface_and_wiki_status(self, tmp_path):
        state = paths_module.default_state(tmp_path, topic="demo")
        paths_module.save_state(tmp_path, state)
        write_json(tmp_path / "feature-list.json", {"project": "demo", "features": [{"title": "同步工作流"}]})
        seed_repo(tmp_path, "workflow")

        overview_module.ensure_overview_docs(tmp_path, state)

        project_doc = (tmp_path / "docs" / "overview" / "PROJECT.md").read_text(encoding="utf-8")
        architecture_doc = (tmp_path / "docs" / "overview" / "ARCHITECTURE.md").read_text(encoding="utf-8")
        current_state_doc = (tmp_path / "docs" / "overview" / "CURRENT-STATE.md").read_text(encoding="utf-8")
        wiki_status = json.loads((tmp_path / ".vibeflow" / "wiki-status.json").read_text(encoding="utf-8"))

        assert "# 项目总览 - demo" in project_doc
        assert "## 代码面速览" in project_doc
        assert "<!-- 生成区块:代码面速览 开始 -->" in project_doc
        assert "# 架构总览" in architecture_doc
        assert "## 技术快照" in architecture_doc
        assert "<!-- 生成区块:技术快照 开始 -->" in architecture_doc
        assert "## Arc42 深度架构视图" in architecture_doc
        assert "<!-- 生成区块:Arc42 架构视图 开始 -->" in architecture_doc
        assert "C4 分层结构" in architecture_doc
        assert "模块职责" in architecture_doc
        assert "Runtime View" in architecture_doc
        assert "# 当前状态" in current_state_doc
        assert "## 当前变更关注点" in current_state_doc
        assert "## 文档同步状态" in current_state_doc
        assert "`PROJECT.md`：已同步" in current_state_doc
        assert "`ARCHITECTURE.md`：已同步" in current_state_doc
        assert wiki_status["docs"]["PROJECT.md"]["stale"] is False
        assert wiki_status["docs"]["ARCHITECTURE.md"]["stale"] is False
        assert "content_hash" in wiki_status["docs"]["PROJECT.md"]["generated_blocks"]["代码面速览"]
        assert "content_hash" in wiki_status["docs"]["ARCHITECTURE.md"]["generated_blocks"]["技术快照"]
        assert "content_hash" in wiki_status["docs"]["ARCHITECTURE.md"]["generated_blocks"]["Arc42 架构视图"]
        assert "CURRENT-STATE.md" in wiki_status["docs"]

    def test_refresh_preserves_manual_sections_and_updates_generated_block(self, tmp_path):
        state = paths_module.default_state(tmp_path, topic="demo")
        paths_module.save_state(tmp_path, state)
        write_json(tmp_path / "feature-list.json", {"project": "demo", "features": []})
        seed_repo(tmp_path, "alpha")

        overview_module.ensure_overview_docs(tmp_path, state)

        project_path = tmp_path / "docs" / "overview" / "PROJECT.md"
        project_doc = project_path.read_text(encoding="utf-8")
        project_doc = project_doc.replace(
            "## 项目目标\n\n- 待补充：用 2 到 5 条描述项目长期要达成的目标。",
            "## 项目目标\n\n- 自定义目标：保持人工正文不被覆盖。",
        )
        write(project_path, project_doc)

        write(tmp_path / "src" / "beta" / "__init__.py", "")
        overview_module.ensure_overview_docs(tmp_path, state)

        refreshed = project_path.read_text(encoding="utf-8")
        assert "- 自定义目标：保持人工正文不被覆盖。" in refreshed
        assert "beta" in refreshed

    def test_refresh_current_state_surfaces_stale_overview_docs(self, tmp_path):
        state = paths_module.default_state(tmp_path, topic="demo")
        paths_module.save_state(tmp_path, state)
        write_json(tmp_path / "feature-list.json", {"project": "demo", "features": []})
        seed_repo(tmp_path, "alpha")

        overview_module.ensure_overview_docs(tmp_path, state)
        write(tmp_path / "src" / "beta" / "__init__.py", "")

        overview_module.refresh_current_state(tmp_path, state)

        current_state_doc = (tmp_path / "docs" / "overview" / "CURRENT-STATE.md").read_text(encoding="utf-8")
        wiki_status = json.loads((tmp_path / ".vibeflow" / "wiki-status.json").read_text(encoding="utf-8"))
        assert "`PROJECT.md`：待同步" in current_state_doc
        assert "`ARCHITECTURE.md`：待同步" in current_state_doc
        assert "源输入已变化" in current_state_doc
        assert wiki_status["docs"]["PROJECT.md"]["stale"] is True
        assert wiki_status["docs"]["ARCHITECTURE.md"]["stale"] is True
        assert "源输入已变化，尚未重新同步" in wiki_status["docs"]["PROJECT.md"]["stale_reasons"]

    def test_refresh_current_state_detects_generated_block_drift(self, tmp_path):
        state = paths_module.default_state(tmp_path, topic="demo")
        paths_module.save_state(tmp_path, state)
        write_json(tmp_path / "feature-list.json", {"project": "demo", "features": []})
        seed_repo(tmp_path, "alpha")

        overview_module.ensure_overview_docs(tmp_path, state)

        project_path = tmp_path / "docs" / "overview" / "PROJECT.md"
        project_doc = project_path.read_text(encoding="utf-8")
        assert "- 主要模块：alpha" in project_doc
        write(project_path, project_doc.replace("- 主要模块：alpha", "- 主要模块：manual-edit"))

        overview_module.refresh_current_state(tmp_path, state)

        current_state_doc = (tmp_path / "docs" / "overview" / "CURRENT-STATE.md").read_text(encoding="utf-8")
        wiki_status = json.loads((tmp_path / ".vibeflow" / "wiki-status.json").read_text(encoding="utf-8"))

        assert "`PROJECT.md`：待同步" in current_state_doc
        assert "生成区块“代码面速览”内容已漂移" in current_state_doc
        assert "`ARCHITECTURE.md`：已同步" in current_state_doc
        assert wiki_status["docs"]["PROJECT.md"]["stale"] is True
        assert "生成区块“代码面速览”内容已漂移" in wiki_status["docs"]["PROJECT.md"]["stale_reasons"]
        assert wiki_status["docs"]["ARCHITECTURE.md"]["stale"] is False
