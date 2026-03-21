#!/usr/bin/env python3
"""
Read tech_stack and quality_gates from feature-list.json, output the exact
shell commands for test, coverage, and mutation tooling.

Eliminates the need for the LLM to look up per-language command syntax.

When --bindings is provided, outputs MCP tool call specifications instead of
CLI commands, for projects using enterprise CI/CD MCP servers.

Usage:
    python get_tool_commands.py feature-list.json
    python get_tool_commands.py feature-list.json --json
    python get_tool_commands.py feature-list.json --bindings tool-bindings.json
    python get_tool_commands.py feature-list.json --bindings tool-bindings.json --json
"""

import argparse
import json
import sys

# ---------------------------------------------------------------------------
# Command templates per tool
# Keys = lowercase tool names as they appear in tech_stack
# Values = dict of command templates
#   {changed_files}  — placeholder the LLM fills with actual paths
#   {changed_classes} — placeholder for Java class patterns
# ---------------------------------------------------------------------------

TEST_COMMANDS = {
    "pytest":  "pytest",
    "junit":   "mvn test",
    "jest":    "npx jest",
    "vitest":  "npx vitest run",
    "ctest":   "ctest --test-dir build",
    "gtest":   "ctest --test-dir build",
}

COVERAGE_COMMANDS = {
    "pytest-cov": "pytest --cov=src --cov-branch --cov-report=term-missing",
    "jacoco":     "mvn test jacoco:report",
    "c8":         "npx vitest run --coverage",
    "c8-jest":    "npx c8 --branches 80 --lines 90 --reporter=text npx jest",
    "gcov":       "make CFLAGS=\"--coverage\" test && gcov -b src/*.c && lcov --capture -d . -o coverage.info && lcov --summary coverage.info",
}

MUTATION_COMMANDS = {
    "mutmut": {
        "incremental": "mutmut run --paths-to-mutate={changed_files}",
        "full":        "mutmut run",
        "results":     "mutmut results",
        "show":        "mutmut show <mutant-id>",
    },
    "pitest": {
        "incremental": "mvn pitest:mutationCoverage -DtargetClasses={changed_classes}",
        "full":        "mvn pitest:mutationCoverage",
        "results":     "cat target/pit-reports/*/mutations.xml",
        "show":        "open target/pit-reports/*/index.html",
    },
    "stryker": {
        "incremental": "npx stryker run --mutate='{changed_files}'",
        "full":        "npx stryker run",
        "results":     "cat reports/mutation/mutation.json",
        "show":        "open reports/mutation/html/index.html",
    },
    "mull": {
        "incremental": "mull-runner ./test-binary --filters={changed_files}",
        "full":        "mull-runner ./test-binary",
        "results":     "cat mull-report.json",
        "show":        "cat mull-report.json",
    },
}


def get_commands(feature_list: dict) -> dict:
    """Extract tool commands from feature-list.json structure.

    Returns a dict with keys: test, coverage, mutation_incremental,
    mutation_full, mutation_results, mutation_show, thresholds, tech_stack.
    Values are concrete command strings (or 'UNKNOWN: <tool>' if unmapped).
    """
    ts = feature_list.get("tech_stack", {})
    qg = feature_list.get("quality_gates", {})

    test_fw = ts.get("test_framework", "TODO")
    cov_tool = ts.get("coverage_tool", "TODO")
    mut_tool = ts.get("mutation_tool", "TODO")

    test_cmd = TEST_COMMANDS.get(test_fw, f"UNKNOWN: {test_fw}")
    cov_cmd = COVERAGE_COMMANDS.get(cov_tool, f"UNKNOWN: {cov_tool}")

    mut_cmds = MUTATION_COMMANDS.get(mut_tool, {})
    mut_inc = mut_cmds.get("incremental", f"UNKNOWN: {mut_tool}")
    mut_full = mut_cmds.get("full", f"UNKNOWN: {mut_tool}")
    mut_results = mut_cmds.get("results", f"UNKNOWN: {mut_tool}")
    mut_show = mut_cmds.get("show", f"UNKNOWN: {mut_tool}")

    return {
        "test": test_cmd,
        "coverage": cov_cmd,
        "mutation_incremental": mut_inc,
        "mutation_full": mut_full,
        "mutation_results": mut_results,
        "mutation_show": mut_show,
        "thresholds": {
            "line_coverage_min": qg.get("line_coverage_min", 90),
            "branch_coverage_min": qg.get("branch_coverage_min", 80),
            "mutation_score_min": qg.get("mutation_score_min", 80),
        },
        "tech_stack": {
            "language": ts.get("language", "TODO"),
            "test_framework": test_fw,
            "coverage_tool": cov_tool,
            "mutation_tool": mut_tool,
        },
    }


def get_mcp_commands(feature_list: dict, bindings: dict) -> dict:
    """
    Extract MCP tool specifications from tool-bindings.json.

    Returns a dict with keys: mode, test, coverage, mutation_incremental,
    mutation_full, mutation_results, thresholds, tech_stack.
    Values describe MCP tool calls instead of CLI commands.
    """
    qg = feature_list.get("quality_gates", {})
    ts = feature_list.get("tech_stack", {})
    caps = bindings.get("capability_bindings", {})

    def _mcp_spec(cap_key: str) -> dict:
        cap = caps.get(cap_key, {})
        if cap.get("type") == "mcp":
            return {
                "tool": cap.get("tool", f"UNKNOWN:{cap_key}"),
                "input_template": cap.get("input_template", {}),
                "result_fields": cap.get("result_fields", {}),
            }
        return {"tool": f"NOT_CONFIGURED:{cap_key}"}

    return {
        "mode": "mcp",
        "test": _mcp_spec("test"),
        "coverage": _mcp_spec("coverage"),
        "mutation_incremental": _mcp_spec("mutation"),
        "mutation_full": _mcp_spec("mutation"),
        "mutation_results": {"note": "see result_fields in test/mutation spec"},
        "thresholds": {
            "line_coverage_min": qg.get("line_coverage_min", 90),
            "branch_coverage_min": qg.get("branch_coverage_min", 80),
            "mutation_score_min": qg.get("mutation_score_min", 80),
        },
        "tech_stack": {
            "language": ts.get("language", "TODO"),
            "test_framework": ts.get("test_framework", "TODO"),
            "coverage_tool": ts.get("coverage_tool", "TODO"),
            "mutation_tool": ts.get("mutation_tool", "TODO"),
        },
    }


def format_mcp_text(cmds: dict) -> str:
    """Format MCP commands as human-readable text output."""
    ts = cmds["tech_stack"]
    th = cmds["thresholds"]

    def _fmt_spec(spec: dict) -> str:
        if "tool" not in spec:
            return "(not configured)"
        tool = spec["tool"]
        inp = json.dumps(spec.get("input_template", {}), ensure_ascii=False)
        res = json.dumps(spec.get("result_fields", {}), ensure_ascii=False)
        return f"tool={tool}  input={inp}  result_fields={res}"

    lines = [
        "mode: mcp",
        f"Language: {ts['language']}",
        "",
        "[test]",
        f"  {_fmt_spec(cmds['test'])}",
        "",
        "[coverage]",
        f"  {_fmt_spec(cmds['coverage'])}",
        "",
        "[mutation (incremental / full — same tool)]",
        f"  {_fmt_spec(cmds['mutation_incremental'])}",
        "",
        "[thresholds]",
        f"  line_coverage  >= {th['line_coverage_min']}%",
        f"  branch_coverage >= {th['branch_coverage_min']}%",
        f"  mutation_score  >= {th['mutation_score_min']}%",
        "",
        "Usage: call each MCP tool with the input_template fields resolved,",
        "then read results via result_fields JSON paths.",
    ]
    return "\n".join(lines)


def format_text(cmds: dict) -> str:
    """Format commands as human-readable text output."""
    ts = cmds["tech_stack"]
    th = cmds["thresholds"]
    lines = [
        f"Language: {ts['language']}",
        f"Test framework: {ts['test_framework']}",
        f"Coverage tool: {ts['coverage_tool']}",
        f"Mutation tool: {ts['mutation_tool']}",
        "",
        f"[test]",
        f"  {cmds['test']}",
        "",
        f"[coverage]",
        f"  {cmds['coverage']}",
        "",
        f"[mutation-incremental]",
        f"  {cmds['mutation_incremental']}",
        "",
        f"[mutation-full]",
        f"  {cmds['mutation_full']}",
        "",
        f"[mutation-results]",
        f"  {cmds['mutation_results']}",
        "",
        f"[mutation-show]",
        f"  {cmds['mutation_show']}",
        "",
        f"[thresholds]",
        f"  line_coverage  >= {th['line_coverage_min']}%",
        f"  branch_coverage >= {th['branch_coverage_min']}%",
        f"  mutation_score  >= {th['mutation_score_min']}%",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Output exact tool commands for a vibeflow project"
    )
    parser.add_argument("feature_list", help="Path to feature-list.json")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON instead of text")
    parser.add_argument(
        "--bindings", default=None, metavar="TOOL_BINDINGS",
        help="Path to tool-bindings.json for enterprise MCP mode"
    )
    args = parser.parse_args()

    try:
        with open(args.feature_list, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading {args.feature_list}: {e}", file=sys.stderr)
        sys.exit(1)

    # MCP mode when --bindings is provided
    if args.bindings:
        try:
            with open(args.bindings, "r", encoding="utf-8") as f:
                bindings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading {args.bindings}: {e}", file=sys.stderr)
            sys.exit(1)
        cmds = get_mcp_commands(data, bindings)
        if args.json:
            print(json.dumps(cmds, indent=2))
        else:
            print(format_mcp_text(cmds))
        return

    # CLI mode (default)
    cmds = get_commands(data)

    if args.json:
        print(json.dumps(cmds, indent=2))
    else:
        print(format_text(cmds))


if __name__ == "__main__":
    main()
