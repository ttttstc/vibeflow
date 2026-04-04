#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run full static analysis and produce docs/architecture/.spec-facts.json"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from spec_analyzer._utils import iter_code_files, write_json
from spec_analyzer.python_analyzer import analyze_python
from spec_analyzer.typescript_analyzer import analyze_typescript
from spec_analyzer.diagrams import generate_module_graph_mermaid, generate_er_diagram_mermaid


def run_analysis(
    project_root: Path,
    include_tests: bool = False,
    output_path: Path | None = None,
) -> dict:
    """Run full static analysis.

    Args:
        project_root: Root directory of the project to analyze
        include_tests: Whether to include test files
        output_path: Output path for .spec-facts.json, defaults to docs/architecture/.spec-facts.json

    Returns:
        The complete spec_facts dict
    """
    if output_path is None:
        output_path = project_root / "docs" / "architecture" / ".spec-facts.json"

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Get all code files to detect languages
    all_files = iter_code_files(project_root, include_tests)

    python_files = [f for f in all_files if f.suffix in {".py", ".pyw"}]
    ts_files = [f for f in all_files if f.suffix in {".ts", ".tsx", ".js", ".jsx"}]

    # Initialize result structure
    spec_facts = {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scan_scope": "full" if include_tests else "excluding_tests",
        "languages": [],
        "modules": [],
        "api_surface": {},
        "entities": [],
        "tech_stack": [],
        "diagrams": {},
        "source_files_count": 0,
    }

    # Run Python analysis
    if python_files:
        python_result = analyze_python(project_root, include_tests)
        spec_facts["languages"].extend(python_result.get("languages", []))
        spec_facts["modules"].extend(python_result.get("modules", []))
        spec_facts["api_surface"].update(python_result.get("api_surface", {}))
        spec_facts["entities"].extend(python_result.get("entities", []))
        spec_facts["tech_stack"].extend(python_result.get("tech_stack", []))
        spec_facts["source_files_count"] += python_result.get("source_files_count", 0)

    # Run TypeScript analysis
    if ts_files:
        ts_result = analyze_typescript(project_root)
        spec_facts["languages"].extend(ts_result.get("languages", []))
        spec_facts["modules"].extend(ts_result.get("modules", []))
        spec_facts["api_surface"].update(ts_result.get("api_surface", {}))
        spec_facts["entities"].extend(ts_result.get("entities", []))
        spec_facts["tech_stack"].extend(ts_result.get("tech_stack", []))
        spec_facts["source_files_count"] += ts_result.get("source_files_count", 0)

    # Generate diagrams
    spec_facts["diagrams"] = {
        "module_graph_mermaid": generate_module_graph_mermaid(spec_facts["modules"]),
        "er_diagram_mermaid": generate_er_diagram_mermaid(spec_facts["entities"]),
    }

    # Write output
    write_json(output_path, spec_facts)

    return spec_facts


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run static analysis and produce .spec-facts.json"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path("."),
        help="Root directory of the project to analyze",
    )
    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Include test files in analysis",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path for .spec-facts.json",
    )

    args = parser.parse_args()

    # Resolve project root to absolute path
    project_root = args.project_root.resolve()

    print(f"Analyzing project at: {project_root}")
    print(f"Include tests: {args.include_tests}")

    try:
        result = run_analysis(
            project_root=project_root,
            include_tests=args.include_tests,
            output_path=args.output,
        )

        output_path = args.output or project_root / "docs" / "architecture" / ".spec-facts.json"
        print(f"\nAnalysis complete!")
        print(f"Output written to: {output_path}")
        print(f"Source files analyzed: {result['source_files_count']}")
        print(f"Languages detected: {[l['name'] for l in result['languages']]}")
        print(f"Modules found: {len(result['modules'])}")
        print(f"Entities found: {len(result['entities'])}")

        return 0
    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
