# -*- coding: utf-8 -*-
"""Python static analyzer using standard library ast."""
from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any


def parse_python_file(path: Path) -> dict:
    """Parse a single .py file and extract structure.

    Returns:
        dict with keys: imports, classes, functions, all_list
    """
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, ValueError):
        return {"imports": [], "classes": [], "functions": [], "all_list": []}

    imports = []
    classes = []
    functions = []

    # Extract __all__ if present
    all_list = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        if isinstance(node.value, ast.Tuple):
                            elts = node.value.elts
                        else:
                            elts = node.value.elts
                        all_list = [e.value if isinstance(e, ast.Constant) else None for e in elts]
                        all_list = [x for x in all_list if x is not None]

    # Extract imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({
                    "type": "import",
                    "name": alias.name,
                    "alias": alias.asname,
                })
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imports.append({
                    "type": "from_import",
                    "module": node.module,
                    "name": alias.name,
                    "alias": alias.asname,
                })

    # Extract class and function definitions (top-level only)
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            bases = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    bases.append(base.id)
                elif isinstance(base, ast.Attribute):
                    bases.append(_get_attr_name(base))

            methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
                    methods.append(item.name)

            classes.append({
                "name": node.name,
                "bases": bases,
                "methods": methods,
            })
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_") or node.name == "__all__":
                args = [arg.arg for arg in node.args.args]
                functions.append({
                    "name": node.name,
                    "args": args,
                })

    return {
        "imports": imports,
        "classes": classes,
        "functions": functions,
        "all_list": all_list,
    }


def _get_attr_name(node: ast.Attribute) -> str:
    """Get the full name of an attribute node."""
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def build_module_graph(files: list[Path], project_root: Path) -> list[dict]:
    """Build module dependency graph.

    Returns list of dicts with name, path, deps, kind.
    """
    modules = []
    module_data = {}

    # First pass: parse all files
    for path in files:
        rel_path = path.relative_to(project_root)
        module_name = str(rel_path.with_suffix("")).replace("/", ".").replace("\\", ".")
        parsed = parse_python_file(path)
        module_data[path] = {
            "name": module_name,
            "path": str(rel_path),
            "deps": [],
            "parsed": parsed,
        }

    # Second pass: resolve dependencies
    for path, data in module_data.items():
        parsed = data["parsed"]
        deps = set()
        for imp in parsed["imports"]:
            if imp["type"] == "import":
                dep_name = imp["name"]
            elif imp["type"] == "from_import" and imp["module"]:
                dep_name = imp["module"]
            else:
                continue

            # Find matching modules
            dep_base = dep_name.split(".")[0]
            for other_path, other_data in module_data.items():
                other_name = other_data["name"]
                if other_name == dep_name or other_name.startswith(dep_name + "."):
                    deps.add(other_name)
                elif other_name.split(".")[0] == dep_base:
                    deps.add(other_name)

        data["deps"] = sorted(deps)

    # Build final module list
    for path, data in module_data.items():
        kind = "module"
        if path.name == "__init__.py":
            kind = "package"
        modules.append({
            "name": data["name"],
            "path": data["path"],
            "deps": data["deps"],
            "kind": kind,
        })

    return modules


def extract_api_surface(files: list[Path], project_root: Path) -> dict:
    """Extract public API for each module.

    Returns dict mapping module_path to list of public names.
    """
    surface = {}

    for path in files:
        rel_path = path.relative_to(project_root)
        module_name = str(rel_path.with_suffix("")).replace("/", ".").replace("\\", ".")

        try:
            parsed = parse_python_file(path)
        except Exception:
            continue

        public_names = []

        # Use __all__ if present
        if parsed["all_list"]:
            public_names = parsed["all_list"]
        else:
            # Otherwise, use non-underscore names
            for cls in parsed["classes"]:
                if not cls["name"].startswith("_"):
                    public_names.append(cls["name"])
            for func in parsed["functions"]:
                if not func["name"].startswith("_"):
                    public_names.append(func["name"])

        if public_names:
            surface[module_name] = public_names

    return surface


def extract_data_models(files: list[Path], project_root: Path) -> list[dict]:
    """Extract class definitions as data models.

    Returns list of dicts with module, name, bases, fields, methods.
    """
    entities = []

    for path in files:
        try:
            rel_path = path.relative_to(project_root)
        except ValueError:
            rel_path = path

        module_name = str(rel_path.with_suffix("")).replace("/", ".").replace("\\", ".")

        try:
            parsed = parse_python_file(path)
        except Exception:
            continue

        for cls in parsed["classes"]:
            if cls["name"].startswith("_"):
                continue

            entities.append({
                "module": module_name,
                "name": cls["name"],
                "bases": cls["bases"],
                "fields": [],  # AST doesn't capture instance variables easily
                "methods": cls["methods"],
            })

    return entities


def detect_python_tech_stack(project_root: Path) -> list[dict]:
    """Detect Python tech stack from pyproject.toml and setup.py.

    Returns list of dicts with name, version, source.
    """
    tech_stack = []

    # Parse pyproject.toml
    pyproject_path = project_root / "pyproject.toml"
    if pyproject_path.exists():
        try:
            import tomllib
            with open(pyproject_path, "rb") as f:
                pyproject = tomllib.load(f)

            # Project dependencies
            if "project" in pyproject:
                deps = pyproject["project"].get("dependencies", [])
                for dep in deps:
                    name, version = _parse_dependency(dep)
                    if name:
                        tech_stack.append({
                            "name": name,
                            "version": version,
                            "source": "pyproject.toml",
                        })

            # Optional dependencies
            if "project" in pyproject:
                optional_deps = pyproject["project"].get("optional-dependencies", {})
                for opt_name, deps in optional_deps.items():
                    for dep in deps:
                        name, version = _parse_dependency(dep)
                        if name:
                            tech_stack.append({
                                "name": f"{name} ({opt_name})",
                                "version": version,
                                "source": "pyproject.toml",
                            })

            # Tool sections (e.g., ruff, mypy)
            if "tool" in pyproject:
                for tool_name in pyproject["tool"]:
                    if isinstance(pyproject["tool"][tool_name], dict):
                        tech_stack.append({
                            "name": tool_name,
                            "version": "",
                            "source": "pyproject.toml",
                        })
        except Exception:
            pass

    # Parse setup.py if exists
    setup_path = project_root / "setup.py"
    if setup_path.exists():
        try:
            content = setup_path.read_text(encoding="utf-8")
            # Simple regex extraction for setup() call
            requires_match = re.search(r'install_requires\s*=\s*\[(.*?)\]', content, re.DOTALL)
            if requires_match:
                reqs = requires_match.group(1)
                for dep in re.findall(r'["\']([^"\']+)["\']', reqs):
                    name, version = _parse_dependency(dep)
                    if name:
                        tech_stack.append({
                            "name": name,
                            "version": version,
                            "source": "setup.py",
                        })
        except Exception:
            pass

    return tech_stack


def _parse_dependency(dep: str) -> tuple[str, str]:
    """Parse dependency string into name and version.

    Examples:
        "requests>=2.28" -> ("requests", ">=2.28")
        "pytest" -> ("pytest", "")
    """
    dep = dep.strip()
    match = re.match(r"([a-zA-Z0-9_-]+)([<>=!~]+.*)", dep)
    if match:
        return match.group(1), match.group(2)
    return dep, ""


def analyze_python(project_root: Path, include_tests: bool = False) -> dict:
    """Main Python analysis function.

    Returns dict with languages, modules, api_surface, entities, tech_stack.
    """
    from ._utils import iter_code_files

    # Get all Python files
    all_files = iter_code_files(project_root, include_tests)
    python_files = [f for f in all_files if f.suffix in {".py", ".pyw"}]

    if not python_files:
        return {
            "languages": [],
            "modules": [],
            "api_surface": {},
            "entities": [],
            "tech_stack": [],
            "source_files_count": 0,
        }

    # Run analyses
    modules = build_module_graph(python_files, project_root)
    api_surface = extract_api_surface(python_files, project_root)
    entities = extract_data_models(python_files, project_root)
    tech_stack = detect_python_tech_stack(project_root)

    return {
        "languages": [{"name": "python", "file_count": len(python_files)}],
        "modules": modules,
        "api_surface": api_surface,
        "entities": entities,
        "tech_stack": tech_stack,
        "source_files_count": len(python_files),
    }
