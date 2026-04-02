#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import inspect
import os
import sys
import traceback
import uuid
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
TESTS_ROOT = ROOT / "tests"
SUPPORTED_FIXTURES = {"tmp_path", "monkeypatch"}


def discover_test_files(selected: list[str]) -> list[Path]:
    if selected:
        return [Path(item).resolve() if Path(item).is_absolute() else (ROOT / item).resolve() for item in selected]
    return sorted(TESTS_ROOT.glob("test_*.py"))


def load_module(path: Path, index: int):
    module_name = f"repo_test_runner_{index}_{path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, str(path))
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def supported_signature(callable_obj) -> bool:
    signature = inspect.signature(callable_obj)
    for name in signature.parameters:
        if name == "self":
            continue
        if name not in SUPPORTED_FIXTURES:
            return False
    return True


def iter_test_callables(module):
    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj) and name.startswith("test_") and supported_signature(obj):
            yield f"{module.__name__}.{name}", obj
        elif inspect.isclass(obj) and name.startswith("Test"):
            for method_name, method in inspect.getmembers(obj, predicate=inspect.isfunction):
                if method_name.startswith("test_") and supported_signature(method):
                    instance = obj()
                    yield f"{module.__name__}.{name}.{method_name}", getattr(instance, method_name)


def run_test(callable_obj, *, temp_root: Path) -> tuple[bool, str]:
    signature = inspect.signature(callable_obj)
    kwargs = {}
    monkeypatch = None
    tmp_dir_path: Path | None = None
    try:
        for name in signature.parameters:
            if name == "self":
                continue
            if name == "tmp_path":
                tmp_dir_path = temp_root / f"case-{uuid.uuid4().hex}"
                tmp_dir_path.mkdir(parents=True, exist_ok=False)
                kwargs[name] = tmp_dir_path
            elif name == "monkeypatch":
                monkeypatch = pytest.MonkeyPatch()
                kwargs[name] = monkeypatch
        callable_obj(**kwargs)
        return True, ""
    except Exception:
        return False, traceback.format_exc()
    finally:
        if monkeypatch is not None:
            monkeypatch.undo()
        if tmp_dir_path is not None:
            os.environ["VIBEFLOW_LAST_TEST_TMP"] = str(tmp_dir_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the VibeFlow repository test suite without pytest tmpdir fixtures.")
    parser.add_argument("paths", nargs="*", help="Optional test file paths to run.")
    parser.add_argument("--temp-root", default=str(ROOT / "pytest-runner-temp" / "repo-tests"))
    args = parser.parse_args()

    temp_root = Path(args.temp_root).resolve()
    temp_root.mkdir(parents=True, exist_ok=True)

    test_files = discover_test_files(args.paths)
    if not test_files:
        print("No test files found.")
        return 1

    failures: list[tuple[str, str]] = []
    total = 0

    for index, path in enumerate(test_files, start=1):
        module = load_module(path, index)
        for test_name, callable_obj in iter_test_callables(module):
            total += 1
            ok, detail = run_test(callable_obj, temp_root=temp_root)
            if ok:
                print(f"PASS {test_name}")
            else:
                print(f"FAIL {test_name}")
                failures.append((test_name, detail))

    print(f"\nRan {total} test(s).")
    if failures:
        print(f"{len(failures)} failure(s):")
        for test_name, detail in failures:
            print(f"\n=== {test_name} ===")
            print(detail.rstrip())
        return 1

    print("All tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
