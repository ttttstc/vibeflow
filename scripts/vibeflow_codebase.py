#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from vibeflow_paths import load_state, path_contract


MAP_VERSION = 1
IMPACT_VERSION = 1
MAX_SCAN_FILE_SIZE = 128 * 1024
MAX_RELEVANT_FILES = 12
IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".next",
    "target",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
}
TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".rs",
    ".java",
    ".kt",
    ".go",
    ".sh",
    ".ps1",
    ".env",
}
SOURCE_ROOT_CANDIDATES = ("src", "app", "lib", "server", "client", "frontend", "backend", "packages")
TEST_ROOT_CANDIDATES = ("tests", "test", "spec", "__tests__")
DOC_ROOT_CANDIDATES = ("docs",)
CONFIG_ROOT_CANDIDATES = ("config", "configs")
KEY_FILES = (
    "pyproject.toml",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "Cargo.toml",
    "pom.xml",
    "build.gradle",
    "docker-compose.yml",
    "docker-compose.yaml",
    ".env.example",
    "README.md",
)
ENTRYPOINT_NAMES = {
    "main.py",
    "app.py",
    "server.py",
    "index.ts",
    "index.js",
    "main.ts",
    "main.js",
    "main.tsx",
    "main.jsx",
    "cli.py",
    "__main__.py",
}
STOPWORDS = {
    "this",
    "that",
    "with",
    "from",
    "into",
    "then",
    "when",
    "must",
    "should",
    "have",
    "will",
    "were",
    "been",
    "being",
    "than",
    "also",
    "only",
    "used",
    "using",
    "user",
    "users",
    "need",
    "needs",
    "page",
    "pages",
    "flow",
    "work",
    "change",
    "feature",
    "features",
    "system",
    "project",
    "requirements",
    "design",
    "proposal",
    "tasks",
    "context",
}
LANGUAGE_BY_SUFFIX = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".rs": "rust",
    ".java": "java",
    ".kt": "kotlin",
    ".go": "go",
    ".c": "c",
    ".cc": "cpp",
    ".cpp": "cpp",
    ".cxx": "cpp",
}
FRAMEWORK_RULES = (
    ("fastapi", ("fastapi",)),
    ("flask", ("flask",)),
    ("django", ("django",)),
    ("pytest", ("pytest",)),
    ("react", ("react",)),
    ("nextjs", ("next", "nextjs")),
    ("vite", ("vite",)),
    ("vue", ("vue",)),
    ("express", ("express",)),
    ("tailwindcss", ("tailwindcss", "tailwind")),
    ("axum", ("axum",)),
)


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def safe_read_text(path: Path) -> str:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return ""
    try:
        if path.stat().st_size > MAX_SCAN_FILE_SIZE:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def should_skip(path: Path, project_root: Path) -> bool:
    parts = path.relative_to(project_root).parts
    return any(part in IGNORED_DIRS for part in parts)


def iter_repo_files(project_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in project_root.rglob("*"):
        if not path.is_file():
            continue
        if should_skip(path, project_root):
            continue
        files.append(path)
    return files


def find_roots(project_root: Path, candidates: tuple[str, ...]) -> list[str]:
    roots = []
    for name in candidates:
        candidate = project_root / name
        if candidate.exists():
            roots.append(name)
    return roots


def repo_fingerprint(project_root: Path) -> dict:
    top_level_dirs = sorted(
        item.name for item in project_root.iterdir() if item.is_dir() and item.name not in IGNORED_DIRS
    )
    key_files = sorted(item.name for item in project_root.iterdir() if item.is_file() and item.name in KEY_FILES)
    source_roots = find_roots(project_root, SOURCE_ROOT_CANDIDATES)
    test_roots = find_roots(project_root, TEST_ROOT_CANDIDATES)
    return {
        "top_level_dirs": top_level_dirs,
        "key_files": key_files,
        "source_roots": source_roots,
        "test_roots": test_roots,
    }


def detect_languages(files: list[Path], project_root: Path) -> list[dict]:
    counts: Counter[str] = Counter()
    for path in files:
        language = LANGUAGE_BY_SUFFIX.get(path.suffix.lower())
        if language:
            counts[language] += 1
    return [{"name": name, "file_count": count} for name, count in counts.most_common()]


def detect_frameworks(project_root: Path) -> list[dict]:
    evidence_text = "\n".join(
        safe_read_text(project_root / name)
        for name in ("pyproject.toml", "package.json", "Cargo.toml", "pom.xml", "README.md")
        if (project_root / name).exists()
    ).lower()
    frameworks = []
    for name, patterns in FRAMEWORK_RULES:
        if any(pattern in evidence_text for pattern in patterns):
            frameworks.append({"name": name, "confidence": "high", "evidence": list(patterns)})
    return frameworks


def guess_kind(path_text: str) -> str:
    lowered = path_text.lower()
    if "test" in lowered or "spec" in lowered:
        return "test"
    if any(token in lowered for token in ("api", "route", "endpoint")):
        return "api"
    if any(token in lowered for token in ("ui", "view", "page", "component", "frontend")):
        return "ui"
    if any(token in lowered for token in ("model", "schema", "db", "data", "repository")):
        return "data"
    if any(token in lowered for token in ("infra", "deploy", "docker", "ops")):
        return "infra"
    return "module"


def detect_modules(project_root: Path, source_roots: list[str]) -> list[dict]:
    modules: list[dict] = []
    for root_name in source_roots:
        root = project_root / root_name
        for child in sorted(root.iterdir(), key=lambda item: item.name):
            if child.name in IGNORED_DIRS:
                continue
            relative = child.relative_to(project_root).as_posix()
            if child.is_dir():
                modules.append({"name": child.name, "path": relative, "kind": guess_kind(relative)})
            elif child.is_file() and child.suffix.lower() in TEXT_SUFFIXES:
                modules.append({"name": child.stem, "path": relative, "kind": guess_kind(relative)})
    return modules


def detect_entrypoints(project_root: Path, files: list[Path]) -> list[dict]:
    entrypoints = []
    for path in files:
        if path.name not in ENTRYPOINT_NAMES:
            continue
        entrypoints.append(
            {
                "name": path.stem,
                "path": path.relative_to(project_root).as_posix(),
            }
        )
    return entrypoints[:10]


def build_surfaces(modules: list[dict], entrypoints: list[dict]) -> dict:
    grouped = defaultdict(list)
    for item in modules:
        grouped[item["kind"]].append(item["path"])
    for entrypoint in entrypoints:
        kind = guess_kind(entrypoint["path"])
        grouped[kind].append(entrypoint["path"])
    return {
        "ui": sorted(dict.fromkeys(grouped.get("ui", []))),
        "api": sorted(dict.fromkeys(grouped.get("api", []))),
        "data": sorted(dict.fromkeys(grouped.get("data", []))),
        "infra": sorted(dict.fromkeys(grouped.get("infra", []))),
    }


def collect_configs(project_root: Path, files: list[Path]) -> list[str]:
    configs = []
    for path in files:
        if path.name in KEY_FILES or path.suffix.lower() in {".toml", ".yaml", ".yml", ".json", ".env"}:
            relative = path.relative_to(project_root).as_posix()
            if relative.startswith("docs/"):
                continue
            configs.append(relative)
    return sorted(dict.fromkeys(configs))[:40]


def detect_hotspots(project_root: Path, files: list[Path], entrypoints: list[dict]) -> list[str]:
    hotspots = [entry["path"] for entry in entrypoints]
    parent_counts: Counter[str] = Counter()
    for path in files:
        relative = path.relative_to(project_root).as_posix()
        parent = str(Path(relative).parent).replace("\\", "/")
        if parent not in {".", ""}:
            parent_counts[parent] += 1
    for parent, _count in parent_counts.most_common(5):
        if parent not in hotspots:
            hotspots.append(parent)
    return hotspots[:8]


def build_codebase_map(project_root: Path) -> dict:
    files = iter_repo_files(project_root)
    fingerprint = repo_fingerprint(project_root)
    source_roots = fingerprint["source_roots"]
    test_roots = fingerprint["test_roots"]
    modules = detect_modules(project_root, source_roots)
    entrypoints = detect_entrypoints(project_root, files)
    surfaces = build_surfaces(modules, entrypoints)
    warnings = []
    if not source_roots:
        warnings.append("No conventional source root detected; scanned the repository heuristically.")
    if not test_roots:
        warnings.append("No conventional test root detected.")

    return {
        "version": MAP_VERSION,
        "generated_at": now_iso(),
        "scan_scope": "full",
        "repo_fingerprint": fingerprint,
        "languages": detect_languages(files, project_root),
        "frameworks": detect_frameworks(project_root),
        "roots": {
            "source": source_roots,
            "tests": test_roots,
            "docs": find_roots(project_root, DOC_ROOT_CANDIDATES),
            "config": find_roots(project_root, CONFIG_ROOT_CANDIDATES),
        },
        "modules": modules,
        "entrypoints": entrypoints,
        "surfaces": surfaces,
        "configs": collect_configs(project_root, files),
        "generated_or_ignored": sorted(IGNORED_DIRS),
        "hotspots": detect_hotspots(project_root, files, entrypoints),
        "warnings": warnings,
    }


def render_codebase_map_markdown(data: dict) -> str:
    language_summary = ", ".join(
        f"{item['name']} ({item['file_count']})" for item in data.get("languages", [])
    ) or "[none]"
    framework_summary = ", ".join(item["name"] for item in data.get("frameworks", [])) or "[none]"
    lines = [
        "# Codebase Map",
        "",
        f"- Generated: {data.get('generated_at', '')}",
        f"- Scan scope: {data.get('scan_scope', 'full')}",
        "",
        "## Summary",
        "",
        f"- Source roots: {', '.join(data.get('roots', {}).get('source', [])) or '[none]'}",
        f"- Test roots: {', '.join(data.get('roots', {}).get('tests', [])) or '[none]'}",
        f"- Entrypoints: {len(data.get('entrypoints', []))}",
        f"- Modules: {len(data.get('modules', []))}",
        "",
        "## Languages and Frameworks",
        "",
        f"- Languages: {language_summary}",
        f"- Frameworks: {framework_summary}",
        "",
        "## Major Modules",
        "",
    ]
    if data.get("modules"):
        for module in data["modules"][:12]:
            lines.append(f"- `{module['path']}` ({module['kind']})")
    else:
        lines.append("- [none]")

    lines.extend(["", "## Entrypoints and Runtime Surfaces", ""])
    if data.get("entrypoints"):
        for item in data["entrypoints"]:
            lines.append(f"- `{item['path']}`")
    else:
        lines.append("- [none]")

    lines.extend(["", "## Configs and Hotspots", ""])
    lines.append(f"- Configs: {', '.join(data.get('configs', [])) or '[none]'}")
    lines.append(f"- Hotspots: {', '.join(data.get('hotspots', [])) or '[none]'}")

    warnings = data.get("warnings") or []
    lines.extend(["", "## Warnings", ""])
    if warnings:
        lines.extend([f"- {warning}" for warning in warnings])
    else:
        lines.append("- None.")
    return "\n".join(lines).rstrip() + "\n"


def ensure_codebase_map(
    project_root: Path,
    *,
    refresh: str = "auto",
    include_markdown: bool = False,
) -> tuple[dict, str]:
    del refresh
    del include_markdown
    return build_codebase_map(project_root), "built"


def read_change_sources(project_root: Path, change_root: Path) -> tuple[dict[str, str], str]:
    files = {
        "brief": change_root / "brief.md",
        "proposal": change_root / "proposal.md",
        "requirements": change_root / "requirements.md",
        "design": change_root / "design.md",
        "tasks": change_root / "tasks.md",
    }
    docs = {name: safe_read_text(path) for name, path in files.items() if path.exists()}
    combined = "\n".join(text for text in docs.values() if text)
    return docs, combined


def extract_terms(change_id: str, combined_text: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", f"{change_id} {combined_text}".lower())
    counts: Counter[str] = Counter()
    for token in tokens:
        normalized = token.replace("_", "-")
        if normalized in STOPWORDS or normalized.isdigit():
            continue
        counts[normalized] += 1
    return [term for term, _count in counts.most_common(20)]


def searchable_files(project_root: Path, codebase_map: dict) -> list[Path]:
    roots = set()
    for bucket in ("source", "tests", "config"):
        for root_name in codebase_map.get("roots", {}).get(bucket, []):
            roots.add(project_root / root_name)
    if not roots:
        roots = {project_root}

    files: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        if root.is_file():
            if not should_skip(root, project_root):
                files.append(root)
            continue
        for path in root.rglob("*"):
            if path.is_file() and not should_skip(path, project_root):
                files.append(path)
    return files


def score_files(project_root: Path, files: list[Path], terms: list[str]) -> list[tuple[int, str]]:
    scored: list[tuple[int, str]] = []
    for path in files:
        relative = path.relative_to(project_root).as_posix()
        haystack = relative.lower()
        text = safe_read_text(path).lower()
        score = 0
        for term in terms:
            if term in haystack:
                score += 3
            elif text and term in text:
                score += 1
        if score > 0:
            scored.append((score, relative))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return scored[:MAX_RELEVANT_FILES]


def collect_relevant_modules(codebase_map: dict, relevant_paths: list[str], terms: list[str]) -> list[dict]:
    modules = []
    for module in codebase_map.get("modules", []):
        path_text = str(module.get("path", "")).lower()
        if any(path_text == path or path.startswith(path_text + "/") for path in relevant_paths):
            modules.append({"name": module.get("name"), "path": module.get("path")})
            continue
        if any(term in path_text for term in terms):
            modules.append({"name": module.get("name"), "path": module.get("path")})
    deduped = []
    seen = set()
    for module in modules:
        key = (module["name"], module["path"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(module)
    return deduped[:10]


def build_risk_notes(terms: list[str], relevant_paths: list[str]) -> list[str]:
    risk_notes = []
    haystack = " ".join(terms + relevant_paths).lower()
    if any(token in haystack for token in ("auth", "login", "session", "permission")):
        risk_notes.append("涉及认证、登录或会话相关路径，实施前要重点确认兼容性。")
    if any(token in haystack for token in ("payment", "billing", "invoice")):
        risk_notes.append("涉及支付或计费相关路径，应按高风险改动处理。")
    if any(token in haystack for token in ("data", "model", "schema", "migration", "db")):
        risk_notes.append("涉及数据模型、Schema 或迁移面，实施前要确认向后兼容。")
    if not risk_notes:
        risk_notes.append("当前轻量扫描未发现明显高风险点；如果范围继续扩大，仍需人工复核。")
    return risk_notes


def build_change_impact(project_root: Path, state: dict, codebase_map: dict, *, change_root: Path | None = None) -> dict:
    contract = path_contract(project_root, state)
    active_change = state.get("active_change") or {}
    resolved_change_root = change_root or contract["change_root"]
    docs, combined = read_change_sources(project_root, resolved_change_root)
    terms = extract_terms(str(active_change.get("id") or project_root.name), combined)
    scored_files = score_files(project_root, searchable_files(project_root, codebase_map), terms)
    relevant_paths = [path for _score, path in scored_files]

    relevant_modules = collect_relevant_modules(codebase_map, relevant_paths, terms)
    affected_tests = [path for path in relevant_paths if "/tests/" in f"/{path}/" or path.startswith("tests/")]
    integration_points = []
    for item in codebase_map.get("entrypoints", []):
        path_text = str(item.get("path", ""))
        lowered = path_text.lower()
        if path_text in relevant_paths or any(term in lowered for term in terms):
            integration_points.append(path_text)
    if not integration_points:
        integration_points = [item.get("path") for item in codebase_map.get("entrypoints", [])[:3]]

    config_surfaces = []
    for config in codebase_map.get("configs", []):
        lowered = config.lower()
        if any(term in lowered for term in terms):
            config_surfaces.append(config)

    suggested_read_order = []
    for item in integration_points + [module["path"] for module in relevant_modules] + affected_tests:
        if item and item not in suggested_read_order:
            suggested_read_order.append(item)
    for path in relevant_paths:
        if path not in suggested_read_order:
            suggested_read_order.append(path)

    return {
        "version": IMPACT_VERSION,
        "change_id": str(active_change.get("id") or project_root.name),
        "generated_at": now_iso(),
        "source_docs": [str(path) for path in (resolved_change_root / name for name in ("brief.md", "proposal.md", "requirements.md", "design.md", "tasks.md")) if path.exists()],
        "matched_terms": terms,
        "relevant_modules": relevant_modules,
        "integration_points": integration_points[:8],
        "affected_tests": affected_tests[:8],
        "config_surfaces": config_surfaces[:8],
        "risk_notes": build_risk_notes(terms, relevant_paths),
        "suggested_read_order": suggested_read_order[:12],
        "unknowns": [] if docs else ["未找到当前变更文档，本次判断仅基于仓库结构推断。"],
        "current_structure_summary": {
            "languages": [item["name"] for item in codebase_map.get("languages", [])[:3]],
            "source_roots": codebase_map.get("roots", {}).get("source", []),
            "test_roots": codebase_map.get("roots", {}).get("tests", []),
        },
    }


def render_change_impact_markdown(data: dict) -> str:
    lines = [
        "# Codebase Impact",
        "",
        f"- Generated: {data.get('generated_at', '')}",
        f"- Change ID: {data.get('change_id', '')}",
        "",
        "## Current Structure",
        "",
        f"- Languages: {', '.join(data.get('current_structure_summary', {}).get('languages', [])) or '[unknown]'}",
        f"- Source roots: {', '.join(data.get('current_structure_summary', {}).get('source_roots', [])) or '[none]'}",
        f"- Test roots: {', '.join(data.get('current_structure_summary', {}).get('test_roots', [])) or '[none]'}",
        "",
        "## Relevant Modules",
        "",
    ]
    if data.get("relevant_modules"):
        for module in data["relevant_modules"]:
            lines.append(f"- `{module['path']}`")
    else:
        lines.append("- [none]")

    lines.extend(["", "## Integration Points", ""])
    if data.get("integration_points"):
        for item in data["integration_points"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("- [none]")

    lines.extend(["", "## Affected Tests", ""])
    if data.get("affected_tests"):
        for item in data["affected_tests"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("- [none]")

    lines.extend(["", "## Config and Runtime Surfaces", ""])
    if data.get("config_surfaces"):
        for item in data["config_surfaces"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("- [none]")

    lines.extend(["", "## Risk Notes", ""])
    lines.extend([f"- {item}" for item in data.get("risk_notes", [])] or ["- None."])

    lines.extend(["", "## Suggested Read Order", ""])
    lines.extend([f"- `{item}`" for item in data.get("suggested_read_order", [])] or ["- [none]"])

    lines.extend(["", "## Unknowns", ""])
    lines.extend([f"- {item}" for item in data.get("unknowns", [])] or ["- None."])
    return "\n".join(lines).rstrip() + "\n"


def change_focus_summary(data: dict) -> dict:
    return {
        "relevant_modules": [item.get("path") for item in data.get("relevant_modules", []) if item.get("path")][:6],
        "integration_points": [item for item in data.get("integration_points", []) if item][:6],
        "affected_tests": [item for item in data.get("affected_tests", []) if item][:6],
        "risk_notes": [item for item in data.get("risk_notes", []) if item][:4],
        "suggested_read_order": [item for item in data.get("suggested_read_order", []) if item][:8],
    }
