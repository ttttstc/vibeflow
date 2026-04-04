#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import PurePosixPath
from pathlib import Path


SUPPORTED_RULE_SUFFIXES = {".md", ".markdown", ".txt", ".json", ".yaml", ".yml"}
RULE_CONTENT_CHAR_LIMIT = 4000
RULE_SUMMARY_CHAR_LIMIT = 320
GUIDANCE_FILENAMES = {"claude.md", "agent.md", "agents.md"}
FRONT_MATTER_PATTERN = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|$)", re.DOTALL)
RULE_SECTION_HEADING = "## Project Rules And Constraints"
ALL_SCOPE_VALUES = {"", "*", "all", "any"}
EXTENSION_LANGUAGE_MAP = {
    ".py": "python",
    ".java": "java",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".go": "go",
    ".rs": "rust",
    ".cs": "csharp",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".php": "php",
    ".rb": "ruby",
    ".sql": "sql",
}
CHECK_DEFINITIONS = {
    "design-rules-documented": "Design must include a Project Rules And Constraints section.",
    "python-no-bare-except": "Python runtime code must not use bare except clauses.",
    "python-no-print-runtime": "Python runtime code should use logging instead of print.",
    "java-no-field-injection": "Java code should prefer constructor injection over field injection.",
    "ts-no-explicit-any": "TypeScript production code should avoid explicit any.",
    "js-no-throw-string": "JavaScript should throw Error objects, not raw strings.",
    "sql-no-select-star": "SQL should avoid SELECT * in checked-in queries.",
}


def rules_dir_path(project_root: Path) -> Path:
    return project_root / "rules"


def guidance_file_paths(project_root: Path) -> list[Path]:
    if not project_root.exists():
        return []
    return sorted(
        [
            path
            for path in project_root.iterdir()
            if path.is_file() and path.name.lower() in GUIDANCE_FILENAMES
        ],
        key=lambda path: path.name.lower(),
    )


def _relative_posix(path: Path, project_root: Path) -> str:
    return path.relative_to(project_root).as_posix()


def _truncate(value: str, limit: int) -> str:
    text = value.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _slugify(value: str) -> str:
    text = value.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "rule"


def _first_meaningful_line(content: str) -> str:
    for raw in content.splitlines():
        line = raw.strip()
        if not line or line.startswith("<!--"):
            continue
        return line
    return ""


def _extract_structured_value(content: str, keys: tuple[str, ...]) -> str:
    for raw in content.splitlines():
        line = raw.strip()
        for key in keys:
            match = re.match(rf"{re.escape(key)}\s*:\s*(.+)$", line, re.IGNORECASE)
            if not match:
                continue
            value = match.group(1).strip().strip("\"'")
            if value:
                return value
    return ""


def _parse_json_metadata(content: str) -> tuple[str, str]:
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return "", ""
    if not isinstance(data, dict):
        return "", ""
    rule_id = str(data.get("rule_id") or data.get("id") or data.get("name") or "").strip()
    title = str(data.get("title") or data.get("name") or data.get("id") or "").strip()
    return rule_id, title


def _strip_quotes(value: str) -> str:
    text = value.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {"'", '"'}:
        return text[1:-1]
    return text


def _parse_front_matter_value(value: str):
    text = value.strip()
    if not text:
        return ""
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        if not inner:
            return []
        parts = [item.strip() for item in inner.split(",")]
        return [_strip_quotes(item) for item in parts if _strip_quotes(item)]
    lowered = text.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    return _strip_quotes(text)


def _split_front_matter(content: str) -> tuple[dict, str]:
    normalized_content = content.lstrip("\ufeff")
    match = FRONT_MATTER_PATTERN.match(normalized_content)
    if not match:
        return {}, normalized_content

    metadata: dict[str, object] = {}
    lines = match.group(1).splitlines()
    index = 0
    while index < len(lines):
        raw = lines[index].rstrip()
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            index += 1
            continue
        key, remainder = line.split(":", 1)
        key = key.strip().lower().replace("-", "_")
        remainder = remainder.strip()
        if not remainder:
            items: list[str] = []
            cursor = index + 1
            while cursor < len(lines):
                candidate = lines[cursor].strip()
                if not candidate:
                    cursor += 1
                    continue
                if candidate.startswith("- "):
                    item = _strip_quotes(candidate[2:].strip())
                    if item:
                        items.append(item)
                    cursor += 1
                    continue
                break
            metadata[key] = items
            index = cursor
            continue
        metadata[key] = _parse_front_matter_value(remainder)
        index += 1

    return metadata, normalized_content[match.end():]


def _normalize_string_list(value) -> list[str]:
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    if isinstance(value, list):
        normalized: list[str] = []
        for item in value:
            text = str(item).strip()
            if text:
                normalized.append(text)
        return normalized
    return []


def _normalize_scope_values(values) -> list[str]:
    normalized: list[str] = []
    for item in _normalize_string_list(values):
        lowered = item.strip().lower()
        if lowered and lowered not in normalized:
            normalized.append(lowered)
    return normalized


def _normalize_path_list(values) -> list[str]:
    normalized: list[str] = []
    for item in _normalize_string_list(values):
        path = item.replace("\\", "/").strip().strip("/")
        if path.startswith("./"):
            path = path[2:]
        if path and path not in normalized:
            normalized.append(path)
    return normalized


def _metadata_list(metadata: dict, *keys: str) -> list[str]:
    for key in keys:
        if key in metadata:
            return _normalize_string_list(metadata.get(key))
    return []


def _rule_metadata(path: Path, content: str) -> tuple[dict, str]:
    metadata, body = _split_front_matter(content)
    applies_to = {
        "languages": _normalize_scope_values(_metadata_list(metadata, "languages", "language")),
        "globs": _normalize_path_list(_metadata_list(metadata, "globs", "glob")),
        "layers": _normalize_scope_values(_metadata_list(metadata, "layers", "layer")),
        "stages": _normalize_scope_values(_metadata_list(metadata, "stages", "stage")),
    }
    checks = _normalize_scope_values(_metadata_list(metadata, "checks", "check"))
    return {
        "id": str(metadata.get("id") or metadata.get("rule_id") or "").strip(),
        "title": str(metadata.get("title") or metadata.get("name") or "").strip(),
        "applies_to": applies_to,
        "checks": checks,
    }, body


def _language_aliases(language: str) -> list[str]:
    lowered = str(language or "").strip().lower()
    if not lowered:
        return []
    aliases = [lowered]
    if lowered == "ts":
        aliases.append("typescript")
    elif lowered == "typescript":
        aliases.append("ts")
    elif lowered == "js":
        aliases.append("javascript")
    elif lowered == "javascript":
        aliases.append("js")
    elif lowered in {"c#", "dotnet"}:
        aliases.append("csharp")
    elif lowered == "csharp":
        aliases.extend(["c#", "dotnet"])
    return [item for item in aliases if item]


def infer_scope_languages(project_root: Path, *, project_language: str = "", file_scope: list[str] | None = None) -> list[str]:
    languages: list[str] = []
    for value in _language_aliases(project_language):
        if value not in languages:
            languages.append(value)

    for raw in file_scope or []:
        suffix = Path(str(raw)).suffix.lower()
        mapped = EXTENSION_LANGUAGE_MAP.get(suffix)
        if not mapped:
            continue
        for value in _language_aliases(mapped):
            if value not in languages:
                languages.append(value)

    if not languages:
        if (project_root / "pyproject.toml").exists():
            languages.append("python")
        elif (project_root / "package.json").exists():
            languages.extend(["typescript", "javascript"])
        elif (project_root / "Cargo.toml").exists():
            languages.append("rust")
        elif (project_root / "pom.xml").exists():
            languages.append("java")

    return languages


def infer_scope_layers(file_scope: list[str] | None = None, explicit_layers=None) -> list[str]:
    layers = _normalize_scope_values(explicit_layers)
    for raw in file_scope or []:
        path = str(raw).replace("\\", "/").lower()
        inferred = None
        if any(token in path for token in ("/tests/", "/test/", "tests/", "test_")):
            inferred = "tests"
        elif any(token in path for token in ("/ui/", "/frontend/", "/components/", "/pages/", ".tsx", ".jsx")):
            inferred = "ui"
        elif any(token in path for token in ("/db/", "/sql/", "/migrations/", "/schema/")):
            inferred = "data"
        elif any(token in path for token in ("/scripts/", "/bin/", "/tools/")):
            inferred = "scripts"
        elif any(token in path for token in ("/api/", "/controllers/", "/routes/")):
            inferred = "api"
        elif any(token in path for token in ("/src/", "/app/", "/services/", "/domain/")):
            inferred = "runtime"
        if inferred and inferred not in layers:
            layers.append(inferred)
    return layers


def build_rule_scope(
    project_root: Path,
    *,
    project_language: str = "",
    file_scope: list[str] | None = None,
    layers=None,
    stage: str = "",
) -> dict:
    normalized_scope = _normalize_path_list(file_scope or [])
    return {
        "languages": infer_scope_languages(project_root, project_language=project_language, file_scope=normalized_scope),
        "file_scope": normalized_scope,
        "layers": infer_scope_layers(normalized_scope, layers),
        "stage": str(stage or "").strip().lower(),
    }


def _matches_scoped_values(rule_values: list[str], scope_values: list[str]) -> bool:
    if not rule_values:
        return True
    lowered_rule_values = {item.lower() for item in rule_values}
    if lowered_rule_values & ALL_SCOPE_VALUES:
        return True
    return bool(lowered_rule_values & {item.lower() for item in scope_values})


def _matches_globs(globs: list[str], file_scope: list[str]) -> bool:
    if not globs:
        return True
    if not file_scope:
        return True
    for glob in globs:
        normalized_glob = glob.replace("\\", "/").strip()
        if normalized_glob in {"", "*", "**", "**/*"}:
            return True
        for raw_path in file_scope:
            candidate = raw_path.replace("\\", "/").strip("/")
            pure = PurePosixPath(candidate)
            if pure.match(normalized_glob) or pure.match(normalized_glob.lstrip("./")):
                return True
            if normalized_glob.startswith("**/") and pure.match(normalized_glob[3:]):
                return True
    return False


def rule_matches_scope(rule: dict, scope: dict) -> bool:
    applies_to = rule.get("applies_to") if isinstance(rule.get("applies_to"), dict) else {}
    languages = _normalize_scope_values(applies_to.get("languages"))
    layers = _normalize_scope_values(applies_to.get("layers"))
    stages = _normalize_scope_values(applies_to.get("stages"))
    globs = _normalize_path_list(applies_to.get("globs"))

    if not _matches_scoped_values(languages, _normalize_scope_values(scope.get("languages"))):
        return False
    if not _matches_scoped_values(stages, _normalize_scope_values([scope.get("stage")])):
        return False
    scope_layers = _normalize_scope_values(scope.get("layers"))
    if layers and scope_layers and not _matches_scoped_values(layers, scope_layers):
        return False
    if not _matches_globs(globs, _normalize_path_list(scope.get("file_scope"))):
        return False
    return True


def _extract_rule_id(path: Path, content: str, relative_path: str) -> str:
    metadata, _ = _rule_metadata(path, content)
    if metadata.get("id"):
        return _slugify(str(metadata.get("id")))
    if path.suffix.lower() == ".json":
        rule_id, _ = _parse_json_metadata(content)
        if rule_id:
            return _slugify(rule_id)
    if path.suffix.lower() in {".yaml", ".yml"}:
        rule_id = _extract_structured_value(content, ("rule_id", "id", "name"))
        if rule_id:
            return _slugify(rule_id)
    return _slugify(relative_path.rsplit(".", 1)[0].replace("/", "-"))


def _extract_title(path: Path, content: str) -> str:
    metadata, body = _rule_metadata(path, content)
    if metadata.get("title"):
        return str(metadata.get("title"))
    suffix = path.suffix.lower()
    if suffix == ".json":
        _, title = _parse_json_metadata(content)
        if title:
            return title
    if suffix in {".yaml", ".yml"}:
        title = _extract_structured_value(content, ("title", "name", "id"))
        if title:
            return title
    for raw in body.splitlines():
        line = raw.strip()
        if line.startswith("#"):
            title = line.lstrip("#").strip()
            if title:
                return title
    first_line = _first_meaningful_line(body)
    if first_line:
        return first_line.strip("\"'")
    return path.stem.replace("-", " ").replace("_", " ").strip() or path.name


def _summarize_content(content: str) -> str:
    _, body = _rule_metadata(Path("rule.md"), content)
    lines: list[str] = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            line = line.lstrip("#").strip()
        lines.append(line)
        if len(" ".join(lines)) >= RULE_SUMMARY_CHAR_LIMIT:
            break
    return _truncate(" ".join(lines), RULE_SUMMARY_CHAR_LIMIT)


def load_project_rules(project_root: Path) -> dict:
    rules_dir = rules_dir_path(project_root)
    rule_files: list[dict] = []
    guidance_files = [_relative_posix(path, project_root) for path in guidance_file_paths(project_root)]

    if rules_dir.exists():
        for path in sorted(rules_dir.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in SUPPORTED_RULE_SUFFIXES:
                continue
            content = path.read_text(encoding="utf-8")
            relative_path = _relative_posix(path, project_root)
            metadata, body = _rule_metadata(path, content)
            rule_files.append(
                {
                    "id": _extract_rule_id(path, content, relative_path),
                    "title": _extract_title(path, content),
                    "path": relative_path,
                    "format": path.suffix.lower().lstrip("."),
                    "summary": _summarize_content(content),
                    "content": _truncate(body, RULE_CONTENT_CHAR_LIMIT),
                    "applies_to": metadata.get("applies_to") or {},
                    "checks": metadata.get("checks") or [],
                }
            )

    precedence_targets = ", ".join(guidance_files) if guidance_files else "root agent guidance files"
    return {
        "enabled": bool(rule_files),
        "rules_dir": _relative_posix(rules_dir, project_root),
        "agent_guidance_files": guidance_files,
        "precedence_note": (
            f"Project rules under rules/ override {precedence_targets} when they conflict."
        ),
        "files": rule_files,
    }


def select_applicable_rules(
    project_root: Path,
    *,
    rules_context: dict | None = None,
    project_language: str = "",
    file_scope: list[str] | None = None,
    layers=None,
    stage: str = "",
) -> dict:
    loaded = rules_context or load_project_rules(project_root)
    scope = build_rule_scope(
        project_root,
        project_language=project_language,
        file_scope=file_scope,
        layers=layers,
        stage=stage,
    )
    applicable = [
        rule
        for rule in loaded.get("files") or []
        if isinstance(rule, dict) and rule_matches_scope(rule, scope)
    ]
    return {
        "enabled": bool(applicable),
        "rules_dir": loaded.get("rules_dir", "rules"),
        "agent_guidance_files": _normalize_string_list(loaded.get("agent_guidance_files")),
        "precedence_note": str(loaded.get("precedence_note") or "").strip(),
        "selection_scope": scope,
        "files": applicable,
    }


def render_design_rules_section(rules_context: dict) -> str:
    lines = [RULE_SECTION_HEADING, ""]
    if not rules_context.get("enabled"):
        lines.extend(
            [
                "No applicable project rules were detected for the current design scope.",
                "",
                "Document any design constraints directly in the design sections below if they emerge later.",
            ]
        )
        return "\n".join(lines).rstrip() + "\n"

    precedence = str(rules_context.get("precedence_note") or "").strip()
    if precedence:
        lines.extend([precedence, ""])

    lines.extend(["Applicable rules for this design scope:", ""])
    for rule in rules_context.get("files") or []:
        title = str(rule.get("title") or rule.get("id") or "Untitled Rule").strip()
        path = str(rule.get("path") or "").strip()
        summary = str(rule.get("summary") or "").strip()
        checks = [check for check in _normalize_scope_values(rule.get("checks")) if check in CHECK_DEFINITIONS]
        bullet = f"- `{path}` — {title}"
        if summary:
            bullet += f": {summary}"
        lines.append(bullet)
        if checks:
            lines.append(f"  Executable checks: {', '.join(checks)}")

    lines.extend(
        [
            "",
            "Design implications:",
            "",
            "- The architecture, module boundaries, and delivery plan must remain compatible with every applicable rule above.",
            "- If a design choice needs an exception, record the exception and migration plan explicitly in this document before implementation starts.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def design_rules_documented(design_path: Path) -> bool:
    if not design_path.exists():
        return False
    content = design_path.read_text(encoding="utf-8")
    return RULE_SECTION_HEADING.lower() in content.lower()


def _is_runtime_path(path: str) -> bool:
    lowered = path.replace("\\", "/").lower()
    return not any(token in lowered for token in ("/tests/", "/test/", "/examples/", "/scripts/", "/docs/"))


def _scan_file_for_pattern(path: Path, pattern: re.Pattern[str]) -> bool:
    if not path.exists() or not path.is_file():
        return False
    return bool(pattern.search(path.read_text(encoding="utf-8")))


def evaluate_executable_rule_checks(
    project_root: Path,
    *,
    rules: list[dict],
    implemented_files: list[str] | None = None,
    design_path: Path | None = None,
) -> dict:
    issues: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []
    active_checks: list[str] = []
    seen_checks: set[str] = set()

    for rule in rules:
        if not isinstance(rule, dict):
            continue
        for check in _normalize_scope_values(rule.get("checks")):
            if check in seen_checks:
                continue
            seen_checks.add(check)
            active_checks.append(check)

    if not active_checks:
        return {"issues": issues, "warnings": warnings, "notes": notes, "active_checks": active_checks}

    normalized_files = _normalize_path_list(implemented_files or [])
    absolute_files = [project_root / rel_path for rel_path in normalized_files]

    for check in active_checks:
        notes.append(f"- {check}: {CHECK_DEFINITIONS.get(check, 'Custom executable rule check')}")
        if check == "design-rules-documented":
            if design_path and not design_rules_documented(design_path):
                issues.append(
                    f"Design artifact is missing the '{RULE_SECTION_HEADING}' section required by project rules."
                )
        elif check == "python-no-bare-except":
            pattern = re.compile(r"(?m)^\s*except\s*:\s*(?:#.*)?$")
            offenders = [
                rel_path
                for rel_path, abs_path in zip(normalized_files, absolute_files)
                if abs_path.suffix.lower() == ".py" and _is_runtime_path(rel_path) and _scan_file_for_pattern(abs_path, pattern)
            ]
            if offenders:
                issues.append("Bare except found in runtime Python files: " + ", ".join(offenders))
        elif check == "python-no-print-runtime":
            pattern = re.compile(r"\bprint\s*\(")
            offenders = [
                rel_path
                for rel_path, abs_path in zip(normalized_files, absolute_files)
                if abs_path.suffix.lower() == ".py" and _is_runtime_path(rel_path) and _scan_file_for_pattern(abs_path, pattern)
            ]
            if offenders:
                warnings.append("print() found in runtime Python files: " + ", ".join(offenders))
        elif check == "java-no-field-injection":
            pattern = re.compile(r"@(?:Autowired|Inject)\s*(?:\r?\n\s*)*(?:private|protected|public)\s+[^\n;]+;", re.MULTILINE)
            offenders = [
                rel_path
                for rel_path, abs_path in zip(normalized_files, absolute_files)
                if abs_path.suffix.lower() == ".java" and _scan_file_for_pattern(abs_path, pattern)
            ]
            if offenders:
                issues.append("Field injection annotation found in Java files: " + ", ".join(offenders))
        elif check == "ts-no-explicit-any":
            pattern = re.compile(r"(?<![A-Za-z0-9_])any(?![A-Za-z0-9_])")
            offenders = [
                rel_path
                for rel_path, abs_path in zip(normalized_files, absolute_files)
                if abs_path.suffix.lower() in {".ts", ".tsx"} and _is_runtime_path(rel_path) and _scan_file_for_pattern(abs_path, pattern)
            ]
            if offenders:
                warnings.append("Explicit any found in TypeScript runtime files: " + ", ".join(offenders))
        elif check == "js-no-throw-string":
            pattern = re.compile(r"throw\s+(?:'[^']*'|\"[^\"]*\"|`[^`]*`)")
            offenders = [
                rel_path
                for rel_path, abs_path in zip(normalized_files, absolute_files)
                if abs_path.suffix.lower() in {".js", ".jsx"} and _scan_file_for_pattern(abs_path, pattern)
            ]
            if offenders:
                issues.append("String throws found in JavaScript files: " + ", ".join(offenders))
        elif check == "sql-no-select-star":
            pattern = re.compile(r"(?is)\bselect\s+\*")
            offenders = [
                rel_path
                for rel_path, abs_path in zip(normalized_files, absolute_files)
                if abs_path.suffix.lower() == ".sql" and _scan_file_for_pattern(abs_path, pattern)
            ]
            if offenders:
                warnings.append("SELECT * found in SQL files: " + ", ".join(offenders))
        else:
            warnings.append(f"Executable rule check '{check}' is not implemented yet.")

    return {"issues": issues, "warnings": warnings, "notes": notes, "active_checks": active_checks}


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect and render VibeFlow project rules.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--stage", default="")
    parser.add_argument("--language", default="")
    parser.add_argument("--layer", action="append", default=[])
    parser.add_argument("--file-scope", action="append", default=[])
    parser.add_argument("--design-path", default="")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--design-section", action="store_true")
    parser.add_argument("--evaluate-checks", action="store_true")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    rules = select_applicable_rules(
        project_root,
        project_language=args.language,
        file_scope=args.file_scope,
        layers=args.layer,
        stage=args.stage,
    )

    if args.evaluate_checks:
        design_path = Path(args.design_path) if args.design_path else None
        result = evaluate_executable_rule_checks(
            project_root,
            rules=rules.get("files") or [],
            implemented_files=args.file_scope,
            design_path=design_path,
        )
        if args.format == "markdown":
            lines = ["# Rule Checks", ""]
            if result["active_checks"]:
                lines.extend(["Active checks:", *[f"- {item}" for item in result["active_checks"]], ""])
            if result["notes"]:
                lines.extend(["Notes:", *result["notes"], ""])
            if result["warnings"]:
                lines.extend(["Warnings:", *[f"- {item}" for item in result["warnings"]], ""])
            if result["issues"]:
                lines.extend(["Issues:", *[f"- {item}" for item in result["issues"]]])
            else:
                lines.extend(["Issues:", "- None."])
            print("\n".join(lines).rstrip())
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if not result["issues"] else 1

    if args.format == "markdown" or args.design_section:
        print(render_design_rules_section(rules).rstrip())
    else:
        print(json.dumps(rules, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
