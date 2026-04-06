"""Tests for internal architecture analysis assembly and TypeScript fallback analysis."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).parent.parent


def load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, str(path))
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


assembler_module = load_module(ROOT / "scripts" / "spec_analyzer" / "assembler.py", "spec_assembler")
typescript_module = load_module(ROOT / "scripts" / "spec_analyzer" / "typescript_analyzer.py", "spec_ts_analyzer")

assemble = assembler_module.assemble
build_architecture_analysis = assembler_module.build_architecture_analysis
analyze_typescript = typescript_module.analyze_typescript


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


class TestSpecAnalyzer:
    def test_assemble_first_run_does_not_create_delta(self, tmp_path):
        facts_path = tmp_path / "spec-facts.json"
        inferences_path = tmp_path / "spec-inferences.json"
        output_path = tmp_path / "docs" / "overview" / "ARCHITECTURE.md"
        write_json(facts_path, {"modules": [], "entities": [], "tech_stack": [], "api_surface": {}, "diagrams": {}})
        write_json(inferences_path, {})

        assemble(tmp_path, facts_path, inferences_path, output_path)

        assert output_path.exists()
        text = output_path.read_text(encoding="utf-8")
        assert "C4 分层结构" in text
        assert "### 6. Runtime View" in text
        delta_root = tmp_path / "docs" / "changes"
        assert not delta_root.exists()

    def test_assemble_existing_spec_creates_delta_against_previous_snapshot(self, tmp_path):
        facts_path = tmp_path / "spec-facts.json"
        inferences_path = tmp_path / "spec-inferences.json"
        output_path = tmp_path / "docs" / "overview" / "ARCHITECTURE.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("# Old Spec\n\nLegacy snapshot.\n", encoding="utf-8")
        write_json(
            facts_path,
            {
                "modules": [{"name": "app.core", "path": "src/app/core.py", "deps": [], "kind": "module"}],
                "entities": [],
                "tech_stack": [],
                "api_surface": {},
                "diagrams": {},
            },
        )
        write_json(inferences_path, {})

        assemble(tmp_path, facts_path, inferences_path, output_path)

        delta_files = list((tmp_path / "docs" / "changes").glob("*/spec-delta.md"))
        assert len(delta_files) == 1
        delta_text = delta_files[0].read_text(encoding="utf-8")
        assert "Full Diff" in delta_text
        assert "(No changes detected)" not in delta_text
        assert "previous" in delta_text

    def test_build_architecture_analysis_stays_in_memory_and_contains_arc42_sections(self, tmp_path):
        src_dir = tmp_path / "src" / "demo"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "__init__.py").write_text("from .service import run\n", encoding="utf-8")
        (src_dir / "service.py").write_text("def run():\n    return 'ok'\n", encoding="utf-8")

        result = build_architecture_analysis(tmp_path)

        assert "markdown" in result
        assert "#### 3.2 C4 分层结构" in result["markdown"]
        assert "#### 5.2 模块职责" in result["markdown"]
        assert not (tmp_path / ".vibeflow" / "analysis").exists()

    def test_typescript_analyzer_uses_fallback_when_ts_morph_is_unavailable(self, tmp_path, monkeypatch):
        src_dir = tmp_path / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "models.ts").write_text(
            "export interface User { id: string; name?: string; }\n"
            "export type UserId = string;\n"
            "export class UserService extends BaseService {\n"
            "  getUser(id: string) { return id; }\n"
            "}\n"
            "export function makeUser() { return null; }\n",
            encoding="utf-8",
        )
        (src_dir / "index.ts").write_text(
            "import { UserService } from './models';\n"
            "export { UserService };\n",
            encoding="utf-8",
        )
        (tmp_path / "package.json").write_text(
            json.dumps({"dependencies": {"react": "^19.0.0"}}),
            encoding="utf-8",
        )

        monkeypatch.setattr(typescript_module, "TS_MORPH_AVAILABLE", False)
        result = analyze_typescript(tmp_path)

        assert result["languages"] == [{"name": "typescript", "file_count": 2}]
        assert result["source_files_count"] == 2
        assert any(module["name"] == "src.index" and "src.models" in module["deps"] for module in result["modules"])
        assert "src.models" in result["api_surface"]
        assert "makeUser" in result["api_surface"]["src.models"]
        entity_names = {entity["name"] for entity in result["entities"]}
        assert {"User", "UserId", "UserService"} <= entity_names
        assert any(item["name"] == "react" for item in result["tech_stack"])
