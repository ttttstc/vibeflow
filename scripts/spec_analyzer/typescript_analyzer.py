# -*- coding: utf-8 -*-
"""TypeScript/JS static analyzer with an optional ts-morph fast path."""
from __future__ import annotations

import json
import re
from pathlib import Path

try:
    from ts_morph import Project as TsProject, SyntaxKind
    TS_MORPH_AVAILABLE = True
except ImportError:
    TS_MORPH_AVAILABLE = False


def analyze_typescript(project_root: Path) -> dict:
    """Main TypeScript analysis function."""
    ts_files = discover_typescript_files(project_root)
    if not ts_files:
        return empty_analysis()

    tech_stack = detect_tech_stack(project_root)
    if TS_MORPH_AVAILABLE:
        try:
            return analyze_typescript_with_ts_morph(project_root, ts_files, tech_stack)
        except Exception:
            pass

    return analyze_typescript_with_fallback(project_root, ts_files, tech_stack)


def empty_analysis() -> dict:
    return {
        "languages": [],
        "modules": [],
        "api_surface": {},
        "entities": [],
        "tech_stack": [],
        "source_files_count": 0,
    }


def discover_typescript_files(project_root: Path) -> list[Path]:
    text_suffixes = {".ts", ".tsx", ".js", ".jsx"}
    all_files = list(project_root.rglob("*"))
    return [
        f for f in all_files
        if f.is_file() and f.suffix.lower() in text_suffixes
        and not _should_skip(f, project_root)
    ]


def analyze_typescript_with_ts_morph(project_root: Path, ts_files: list[Path], tech_stack: list[dict]) -> dict:
    project = TsProject()
    for f in ts_files:
        try:
            project.addSourceFile(f)
        except Exception:
            pass

    source_files = project.getSourceFiles()
    return {
        "languages": [{"name": "typescript", "file_count": len(ts_files)}],
        "modules": build_dependency_graph(source_files, project_root),
        "api_surface": extract_api_surface(source_files),
        "entities": extract_data_models(source_files),
        "tech_stack": tech_stack,
        "source_files_count": len(ts_files),
    }


def analyze_typescript_with_fallback(project_root: Path, ts_files: list[Path], tech_stack: list[dict]) -> dict:
    modules = []
    api_surface: dict[str, list[str]] = {}
    entities: list[dict] = []

    for path in ts_files:
        content = read_text(path)
        if content is None:
            continue

        module_name = module_name_for_path(path, project_root)
        deps = extract_relative_dependencies(path, project_root, content)
        modules.append({
            "name": module_name,
            "path": str(path.relative_to(project_root)),
            "deps": deps,
            "kind": "module",
        })

        exports = extract_exports_from_text(content)
        if exports:
            api_surface[module_name] = exports

        entities.extend(extract_entities_from_text(content, module_name))

    return {
        "languages": [{"name": "typescript", "file_count": len(ts_files)}],
        "modules": modules,
        "api_surface": api_surface,
        "entities": entities,
        "tech_stack": tech_stack,
        "source_files_count": len(ts_files),
    }


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def module_name_for_path(path: Path, project_root: Path) -> str:
    rel_path = path.relative_to(project_root)
    return str(rel_path.with_suffix("")).replace("/", ".").replace("\\", ".")


def resolve_relative_module(source_path: Path, project_root: Path, dep_text: str) -> str | None:
    try:
        candidate = (source_path.parent / dep_text).resolve()
        if candidate.is_dir():
            candidate = candidate / "index.ts"
        if candidate.suffix == "":
            for suffix in (".ts", ".tsx", ".js", ".jsx"):
                resolved = candidate.with_suffix(suffix)
                if resolved.exists():
                    candidate = resolved
                    break
        rel_path = candidate.relative_to(project_root)
        return str(rel_path.with_suffix("")).replace("/", ".").replace("\\", ".")
    except Exception:
        return None


def extract_relative_dependencies(path: Path, project_root: Path, content: str) -> list[str]:
    deps = set()
    patterns = [
        r"""(?:import|export)\s+[^'"\n]+?\s+from\s+['"]([^'"]+)['"]""",
        r"""require\(\s*['"]([^'"]+)['"]\s*\)""",
    ]
    for pattern in patterns:
        for dep_text in re.findall(pattern, content):
            if not dep_text.startswith("."):
                continue
            dep_name = resolve_relative_module(path, project_root, dep_text)
            if dep_name:
                deps.add(dep_name)
    return sorted(deps)


def extract_exports_from_text(content: str) -> list[str]:
    exports = set()
    patterns = [
        r"""export\s+(?:async\s+)?function\s+([A-Za-z_]\w*)""",
        r"""export\s+(?:default\s+)?class\s+([A-Za-z_]\w*)""",
        r"""export\s+interface\s+([A-Za-z_]\w*)""",
        r"""export\s+type\s+([A-Za-z_]\w*)""",
        r"""export\s+(?:const|let|var)\s+([A-Za-z_]\w*)""",
    ]
    for pattern in patterns:
        exports.update(re.findall(pattern, content))

    for group in re.findall(r"""export\s*\{\s*([^}]+)\}""", content):
        for item in group.split(","):
            name = item.strip().split(" as ", 1)[0].strip()
            if name:
                exports.add(name)

    return sorted(exports)


def extract_entities_from_text(content: str, module_name: str) -> list[dict]:
    entities: list[dict] = []
    entities.extend(extract_interfaces_from_text(content, module_name))
    entities.extend(extract_type_aliases_from_text(content, module_name))
    entities.extend(extract_classes_from_text(content, module_name))
    return entities


def extract_interfaces_from_text(content: str, module_name: str) -> list[dict]:
    entities = []
    pattern = re.compile(
        r"""(?:export\s+)?interface\s+([A-Za-z_]\w*)\s*\{(?P<body>.*?)\}""",
        re.DOTALL,
    )
    for match in pattern.finditer(content):
        fields = []
        for line in match.group("body").splitlines():
            field_match = re.match(r"""\s*([A-Za-z_]\w*)\??:\s*([^;]+);?""", line.strip())
            if field_match:
                fields.append({
                    "name": field_match.group(1),
                    "type": field_match.group(2).strip(),
                })
        entities.append({
            "module": module_name,
            "name": match.group(1),
            "bases": [],
            "fields": fields,
            "methods": [],
        })
    return entities


def extract_type_aliases_from_text(content: str, module_name: str) -> list[dict]:
    entities = []
    pattern = re.compile(r"""(?:export\s+)?type\s+([A-Za-z_]\w*)\s*=\s*([^;]+);""")
    for match in pattern.finditer(content):
        entities.append({
            "module": module_name,
            "name": match.group(1),
            "bases": [],
            "fields": [{"name": "value", "type": match.group(2).strip()}],
            "methods": [],
        })
    return entities


def extract_classes_from_text(content: str, module_name: str) -> list[dict]:
    entities = []
    pattern = re.compile(
        r"""(?:export\s+)?(?:default\s+)?class\s+([A-Za-z_]\w*)(?:\s+extends\s+([A-Za-z_][\w.]*))?[^{]*\{(?P<body>.*?)\}""",
        re.DOTALL,
    )
    method_pattern = re.compile(
        r"""^\s*(?:public|private|protected|static|async|\s)*([A-Za-z_]\w*)\s*\(""",
        re.MULTILINE,
    )
    for match in pattern.finditer(content):
        methods = sorted({
            name
            for name in method_pattern.findall(match.group("body"))
            if name != "constructor" and not name.startswith("_")
        })
        bases = [match.group(2)] if match.group(2) else []
        entities.append({
            "module": module_name,
            "name": match.group(1),
            "bases": bases,
            "fields": [],
            "methods": methods,
        })
    return entities


def _should_skip(path: Path, project_root: Path) -> bool:
    ignored_dirs = {
        ".git", ".venv", "venv", "node_modules", "dist", "build",
        "coverage", ".pytest_cache", ".mypy_cache", ".ruff_cache",
        "__pycache__", ".next", "target", ".idea", ".vscode",
    }
    parts = path.relative_to(project_root).parts
    return any(part in ignored_dirs for part in parts)


def parse_tsconfig(project_root: Path) -> dict | None:
    tsconfig_path = project_root / "tsconfig.json"
    if not tsconfig_path.exists():
        return None

    try:
        return json.loads(tsconfig_path.read_text(encoding="utf-8"))
    except Exception:
        return None


def build_dependency_graph(source_files: list, project_root: Path) -> list[dict]:
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
                if hasattr(module_ref, "getText"):
                    dep_text = module_ref.getText().strip('"').strip("'")
                    if not dep_text.startswith("."):
                        continue
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
    surface = {}
    for sf in source_files:
        try:
            file_path = Path(sf.getFilePath())
            module_name = str(file_path.with_suffix("")).replace("/", ".").replace("\\", ".")
            exports = []
            for exp in sf.getExportedDeclarations():
                exports.append(exp.getName())
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
    entities = []
    for sf in source_files:
        try:
            file_path = Path(sf.getFilePath())
            module_name = str(file_path.with_suffix("")).replace("/", ".").replace("\\", ".")

            for iface in sf.getInterfaces():
                iface_name = iface.getName()
                if not iface_name or iface_name.startswith("_"):
                    continue

                properties = []
                for prop in iface.getProperties():
                    type_str = prop.getType().getText()
                    properties.append({"name": prop.getName(), "type": type_str})

                entities.append({
                    "module": module_name,
                    "name": iface_name,
                    "bases": [],
                    "fields": properties,
                    "methods": [],
                })

            for type_alias in sf.getTypeAliases():
                alias_name = type_alias.getName()
                if not alias_name or alias_name.startswith("_"):
                    continue

                type_str = type_alias.getTypeNode().getText() if type_alias.getTypeNode() else ""
                entities.append({
                    "module": module_name,
                    "name": alias_name,
                    "bases": [],
                    "fields": [{"name": "value", "type": type_str}],
                    "methods": [],
                })

            for cls in sf.getClasses():
                class_name = cls.getName()
                if not class_name or class_name.startswith("_"):
                    continue

                methods = []
                for method in cls.getMethods():
                    method_name = method.getName()
                    if not method_name.startswith("_"):
                        methods.append(method_name)

                base_expr = cls.getBaseClass()
                bases = [base_expr.getName()] if base_expr else []
                entities.append({
                    "module": module_name,
                    "name": class_name,
                    "bases": bases,
                    "fields": [],
                    "methods": methods,
                })
        except Exception:
            pass
    return entities


def detect_tech_stack(project_root: Path) -> list[dict]:
    tech_stack = []
    package_json_path = project_root / "package.json"
    if not package_json_path.exists():
        return tech_stack

    try:
        package_json = json.loads(package_json_path.read_text(encoding="utf-8"))
        deps = package_json.get("dependencies", {})
        for name, version in deps.items():
            tech_stack.append({"name": name, "version": version, "source": "package.json"})

        dev_deps = package_json.get("devDependencies", {})
        for name, version in dev_deps.items():
            tech_stack.append({"name": name, "version": version, "source": "package.json"})
    except Exception:
        pass

    return tech_stack
