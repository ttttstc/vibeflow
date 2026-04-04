# -*- coding: utf-8 -*-
"""Shared utilities for spec analyzer."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


IGNORED_DIRS = {
    ".git", ".venv", "venv", "node_modules", "dist", "build",
    "coverage", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "__pycache__", ".next", "target", ".idea", ".vscode", ".tmp",
}

TEXT_SUFFIXES = {".py", ".pyw", ".ts", ".tsx", ".js", ".jsx"}

MAX_FILE_SIZE = 128 * 1024  # 128KB

TEST_FILE_PATTERNS = {"*_test.py", "*_tests.py", "conftest.py"}


def should_skip(path: Path, project_root: Path, include_tests: bool = False) -> bool:
    """Check if a file/directory should be skipped."""
    parts = path.relative_to(project_root).parts
    if any(part in IGNORED_DIRS for part in parts):
        return True
    if not include_tests:
        name = path.name
        if name.endswith("_test.py") or name.endswith("_tests.py") or name == "conftest.py":
            return True
    return False


def iter_code_files(project_root: Path, include_tests: bool = False) -> list[Path]:
    """Iterate all code files respecting skip rules."""
    files = []
    for path in project_root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if should_skip(path, project_root, include_tests):
            continue
        if path.stat().st_size > MAX_FILE_SIZE:
            continue
        files.append(path)
    return files


def write_json(path: Path, data: Any) -> Path:
    """Write JSON data to path, creating parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def read_json(path: Path, default=None):
    """Read JSON from path, return default if not exists."""
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))
