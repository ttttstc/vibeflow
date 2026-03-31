# -*- coding: utf-8 -*-
"""TypeScript/JS static analyzer using ts-morph."""
from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from ts_morph import Project as TsProject, SyntaxKind
    TS_MORPH_AVAILABLE = True
except ImportError:
    TS_MORPH_AVAILABLE = False


def analyze_typescript(project_root: Path) -> dict:
    """Main TypeScript analysis function.

    Returns dict with languages, modules, api_surface, entities, tech_stack.
    """
    if not TS_MORPH_AVAILABLE:
        return {
            "languages": [],
            "modules": [],
            "api_surface": {},
            "entities": [],
            "tech_stack": [],
            "source_files_count": 0,
        }

    # Get all TypeScript/JS files
    text_suffixes = {".ts", ".tsx", ".js", ".jsx"}
    all_files = list(project_root.rglob("*"))
    ts_files = [
        f for f in all_files
        if f.is_file() and f.suffix.lower() in text_suffixes
        and not _should_skip(f, project_root)
    ]

    if not ts_files:
        return {
            "languages": [],
            "modules": [],
            "api_surface": {},
            "entities": [],
            "tech_stack": [],
            "source_files_count": 0,
        }

    try:
        project = TsProject()
        for f in ts_files:
            try:
                project.addSourceFile(f)
            except Exception:
                pass

        source_files = project.getSourceFiles()

        modules = build_dependency_graph(source_files, project_root)
        api_surface = extract_api_surface(source_files)
        entities = extract_data_models(source_files)
        tech_stack = detect_tech_stack(project_root)

        return {
            "languages": [{"name": "typescript", "file_count": len(ts_files)}],
            "modules": modules,
            "api_surface": api_surface,
            "entities": entities,
            "tech_stack": tech_stack,
            "source_files_count": len(ts_files),
        }
    except Exception:
        return {
            "languages": [],
            "modules": [],
            "api_surface": {},
            "entities": [],
            "tech_stack": [],
            "source_files_count": 0,
        }


def _should_skip(path: Path, project_root: Path) -> bool:
    """Check if a file should be skipped."""
    ignored_dirs = {
        ".git", ".venv", "venv", "node_modules", "dist", "build",
        "coverage", ".pytest_cache", ".mypy_cache", ".ruff_cache",
        "__pycache__", ".next", "target", ".idea", ".vscode",
    }
    parts = path.relative_to(project_root).parts
    return any(part in ignored_dirs for part in parts)


def parse_tsconfig(project_root: Path) -> dict | None:
    """Find and parse tsconfig.json."""
    tsconfig_path = project_root / "tsconfig.json"
    if not tsconfig_path.exists():
        return None

    try:
        import json
        return json.loads(tsconfig_path.read_text(encoding="utf-8"))
    except Exception:
        return None


def build_dependency_graph(source_files: list, project_root: Path) -> list[dict]:
    """Build dependency graph from import/export statements."""
    modules = []
    seen = set()

    for sf in source_files:
        try:
            file_path = Path(sf.getFilePath())
            rel_path = file_path.relative_to(project_root)
            module_name = str(rel_path.with_suffix("")).replace("/", ".").replace("\\", ".")

            if module_name in seen:
                continue
            seen.add(module_name)

            deps = set()
            for imp in sf.getImportDeclarations():
                module_ref = imp.getModuleReference()
                if hasattr(module_ref, 'getText'):
                    dep_text = module_ref.getText().strip('"').strip("'")
                    if not dep_text.startswith("."):
                        continue
                    # Resolve relative import
                    try:
                        resolved = (file_path.parent / dep_text).resolve()
                        if resolved.suffix == "":
                            resolved = resolved.with_suffix(".ts")
                        resolved_rel = resolved.relative_to(project_root)
                        dep_name = str(resolved_rel.with_suffix("")).replace("/", ".").replace("\\", ".")
                        deps.add(dep_name)
                    except Exception:
                        pass

            modules.append({
                "name": module_name,
                "path": str(rel_path),
                "deps": sorted(deps),
                "kind": "module",
            })
        except Exception:
            pass

    return modules


def extract_api_surface(source_files: list) -> dict:
    """Extract exported functions, classes, interfaces."""
    surface = {}

    for sf in source_files:
        try:
            file_path = Path(sf.getFilePath())
            module_name = str(file_path.with_suffix("")).replace("/", ".").replace("\\", ".")

            exports = []

            # Export declarations
            for exp in sf.getExportedDeclarations():
                exports.append(exp.getName())

            # Named exports
            for named in sf.getExportedSymbols():
                name = named.getName()
                if not name.startswith("_"):
                    exports.append(name)

            if exports:
                surface[module_name] = exports
        except Exception:
            pass

    return surface


def extract_data_models(source_files: list) -> list[dict]:
    """Extract interface and type definitions."""
    entities = []

    for sf in source_files:
        try:
            file_path = Path(sf.getFilePath())
            module_name = str(file_path.with_suffix("")).replace("/", ".").replace("\\", ".")

            # Interfaces
            for iface in sf.getInterfaces():
                if iface.getName().startswith("_"):
                    continue

                properties = []
                for prop in iface.getProperties():
                    type_str = prop.getType().getText()
                    properties.append({
                        "name": prop.getName(),
                        "type": type_str,
                    })

                entities.append({
                    "module": module_name,
                    "name": iface.getName(),
                    "bases": [],
                    "fields": properties,
                    "methods": [],
                })

            # Type aliases
            for type_alias in sf.getTypeAliases():
                if type_alias.getName().startswith("_"):
                    continue

                type_str = type_alias.getTypeNode().getText() if type_alias.getTypeNode() else ""

                entities.append({
                    "module": module_name,
                    "name": type_alias.getName(),
                    "bases": [],
                    "fields": [{"name": "value", "type": type_str}],
                    "methods": [],
                })

            # Classes
            for cls in sf.getClasses():
                if cls.getName().startswith("_"):
                    continue

                methods = []
                for method in cls.getMethods():
                    if not method.getName().startswith("_"):
                        methods.append(method.getName())

                entities.append({
                    "module": module_name,
                    "name": cls.getName(),
                    "bases": [base.getText() for base in cls.getBaseClasses()],
                    "fields": [],
                    "methods": methods,
                })
        except Exception:
            pass

    return entities


def detect_tech_stack(project_root: Path) -> list[dict]:
    """Detect tech stack from package.json."""
    tech_stack = []

    package_json_path = project_root / "package.json"
    if not package_json_path.exists():
        return tech_stack

    try:
        import json
        package_json = json.loads(package_json_path.read_text(encoding="utf-8"))

        # Dependencies
        deps = package_json.get("dependencies", {})
        for name, version in deps.items():
            tech_stack.append({
                "name": name,
                "version": version,
                "source": "package.json",
            })

        # Dev dependencies
        dev_deps = package_json.get("devDependencies", {})
        for name, version in dev_deps.items():
            tech_stack.append({
                "name": name,
                "version": version,
                "source": "package.json",
            })
    except Exception:
        pass

    return tech_stack
