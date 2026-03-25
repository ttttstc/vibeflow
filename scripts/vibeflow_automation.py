#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from vibeflow_paths import (  # noqa: E402
    append_phase_history,
    ensure_runtime,
    ensure_state,
    feature_list_path,
    load_runtime,
    path_contract,
    save_runtime,
    save_state,
    set_checkpoint,
)


MANUAL_ONLY_PHASES = {
    "increment",
    "think",
    "template-selection",
    "plan",
    "requirements",
    "design",
    "quick",
}

AUTO_RUNNABLE_PHASES = {
    "build-init",
    "build-config",
    "build-work",
    "review",
    "test-system",
    "test-qa",
    "ship",
    "reflect",
}

RETRYABLE_PHASES = {
    "build-work",
    "review",
    "test-system",
    "test-qa",
}

FEATURE_REPORT_DIR = ".vibeflow/build-reports"

_PHASE_MODULE = None


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def load_phase_module():
    global _PHASE_MODULE
    if _PHASE_MODULE is None:
        module_path = SCRIPT_DIR / "get-vibeflow-phase.py"
        spec = importlib.util.spec_from_file_location("get_vibeflow_phase", module_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        _PHASE_MODULE = module
    return _PHASE_MODULE


def detect_phase(project_root: Path, verbose: bool = False) -> dict:
    return load_phase_module().detect_phase(project_root, verbose=verbose)


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def append_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(content)
    return path


def normalize_command_list(value) -> list[str]:
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def append_runtime_event(runtime: dict, *, kind: str, title: str, detail: str = "", phase: str = "", status: str = "info") -> None:
    events = runtime.setdefault("events", [])
    events.append(
        {
            "timestamp": now_iso(),
            "kind": kind,
            "title": title,
            "detail": detail,
            "phase": phase,
            "status": status,
        }
    )
    if len(events) > 200:
        del events[:-200]


def record_phase_run(runtime: dict, *, phase: str, status: str, detail: str = "") -> None:
    phase_runs = runtime.setdefault("phase_runs", [])
    phase_runs.append(
        {
            "phase": phase,
            "status": status,
            "detail": detail,
            "timestamp": now_iso(),
        }
    )
    if len(phase_runs) > 200:
        del phase_runs[:-200]


def record_feature_run(runtime: dict, *, feature_id: int | str, title: str, status: str, detail: str = "") -> None:
    feature_runs = runtime.setdefault("feature_runs", [])
    feature_runs.append(
        {
            "feature_id": feature_id,
            "title": title,
            "status": status,
            "detail": detail,
            "timestamp": now_iso(),
        }
    )
    if len(feature_runs) > 400:
        del feature_runs[:-400]


def persist_runtime(
    project_root: Path,
    runtime: dict,
    *,
    status: str | None = None,
    phase: str | None = None,
    action: str | None = None,
    message: str | None = None,
    stop_reason: str | None = None,
) -> dict:
    runtime["last_heartbeat_at"] = now_iso()
    if status is not None:
        runtime["status"] = status
    if phase is not None:
        runtime["current_phase"] = phase
    if action is not None:
        runtime["current_action"] = action
    if message is not None:
        runtime["friendly_message"] = message
    if stop_reason is not None:
        runtime["stop_reason"] = stop_reason
    save_runtime(project_root, runtime)
    return runtime


def friendly_message_for_phase(phase: str, *, status: str = "running", detail: str = "") -> str:
    base = {
        "build-init": "正在整理构建清单，准备进入实现。",
        "build-config": "正在生成构建配置，马上进入实现阶段。",
        "build-work": "正在推进功能实现和验证链路。",
        "review": "正在做整体审查，确认这轮改动站得住。",
        "test-system": "正在跑系统级测试，确认链路真的通。",
        "test-qa": "正在做界面层验证，盯着交互和体验。",
        "ship": "正在收口发布产物，快到终点了。",
        "reflect": "正在生成复盘，让这轮工作有个结尾。",
        "done": "这轮 workflow 已经收口完成。",
    }.get(phase, "正在推进 workflow。")

    if status == "waiting_manual":
        return detail or "这里需要人工确认，确认后才能继续往下跑。"
    if status in {"blocked", "failed"}:
        return detail or "这里卡住了，先解决阻塞项再继续。"
    return detail or base


def append_session_log(project_root: Path, line: str) -> None:
    contract = path_contract(project_root)
    append_text(contract["session_log"], f"- {now_iso()} {line}\n")


def infer_language(project_root: Path, feature_payload: dict) -> str:
    tech_stack = feature_payload.get("tech_stack") or {}
    language = str(tech_stack.get("language") or "").strip().lower()
    if language and language != "todo":
        return language
    if (project_root / "pyproject.toml").exists():
        return "python"
    if (project_root / "package.json").exists():
        return "typescript"
    if (project_root / "Cargo.toml").exists():
        return "rust"
    if (project_root / "pom.xml").exists():
        return "java"
    return "unknown"


def default_quality_gates() -> dict:
    return {
        "line_coverage_min": 90,
        "branch_coverage_min": 80,
        "mutation_score_min": 80,
    }


def read_quality_gates_from_workflow(project_root: Path) -> dict:
    workflow = path_contract(project_root)["workflow"]
    if not workflow.exists():
        return default_quality_gates()
    content = workflow.read_text(encoding="utf-8")
    gates = default_quality_gates()
    patterns = {
        "line_coverage_min": r"line_coverage:\s*(\d+)",
        "branch_coverage_min": r"branch_coverage:\s*(\d+)",
        "mutation_score_min": r"mutation_score:\s*(\d+)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            gates[key] = int(match.group(1))
    return gates


def extract_features_from_tasks(tasks_path: Path) -> list[dict]:
    if not tasks_path.exists():
        return []

    titles = []
    for raw in tasks_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("- [ ] "):
            titles.append(line[6:].strip())
        elif line.startswith("- "):
            titles.append(line[2:].strip())

    deduped = []
    seen = set()
    for title in titles:
        normalized = title.lower()
        if title and normalized not in seen:
            seen.add(normalized)
            deduped.append(title)

    features = []
    for index, title in enumerate(deduped, start=1):
        features.append(
            {
                "id": index,
                "title": title,
                "category": "delivery",
                "description": title,
                "priority": "medium",
                "status": "failing",
                "dependencies": [],
                "verification_steps": [f"Verify {title}"],
            }
        )
    return features


def create_default_feature_payload(project_root: Path, state: dict) -> dict:
    contract = path_contract(project_root, state)
    features = extract_features_from_tasks(contract["artifacts"]["tasks"])
    if not features:
        features = [
            {
                "id": 1,
                "title": f"Implement {state.get('active_change', {}).get('id', project_root.name)}",
                "category": "delivery",
                "description": "Autogenerated default feature for the active change.",
                "priority": "high",
                "status": "failing",
                "dependencies": [],
                "verification_steps": ["Run the project verification commands."],
            }
        ]
    return {
        "project": project_root.name,
        "created": datetime.now().strftime("%Y-%m-%d"),
        "tech_stack": {
            "language": infer_language(project_root, {}),
            "test_framework": "TODO",
            "coverage_tool": "TODO",
            "mutation_tool": "TODO",
        },
        "quality_gates": read_quality_gates_from_workflow(project_root),
        "constraints": [],
        "assumptions": [],
        "required_configs": [],
        "features": features,
    }


def load_feature_payload(project_root: Path) -> dict:
    path = feature_list_path(project_root)
    if not path.exists():
        return {}
    return read_json(path, {})


def save_feature_payload(project_root: Path, payload: dict) -> Path:
    return write_json(feature_list_path(project_root), payload)


def active_features(payload: dict) -> list[dict]:
    return [feature for feature in payload.get("features", []) if not feature.get("deprecated")]


def dependencies_satisfied(feature: dict, features_by_id: dict[int, dict]) -> bool:
    for dependency_id in feature.get("dependencies") or []:
        dependency = features_by_id.get(dependency_id)
        if not dependency or dependency.get("status") != "passing":
            return False
    return True


def find_ready_features(payload: dict) -> list[dict]:
    features = active_features(payload)
    features_by_id = {int(feature.get("id")): feature for feature in features if feature.get("id") is not None}
    ready = []
    for feature in features:
        if feature.get("status") == "passing":
            continue
        if dependencies_satisfied(feature, features_by_id):
            ready.append(feature)
    return ready


def feature_command_config(feature: dict) -> tuple[list[str], str, int]:
    autopilot = feature.get("autopilot") if isinstance(feature.get("autopilot"), dict) else {}
    commands = normalize_command_list(autopilot.get("commands"))
    if not commands:
        commands = normalize_command_list(feature.get("autopilot_commands"))
    if not commands and feature.get("command"):
        commands = normalize_command_list(feature.get("command"))
    workdir = str(autopilot.get("workdir") or feature.get("autopilot_workdir") or ".").strip() or "."
    timeout = int(autopilot.get("timeout_sec") or feature.get("autopilot_timeout_sec") or 300)
    return commands, workdir, timeout


def run_command(command: str, *, cwd: Path, timeout: int = 300) -> dict:
    started_at = now_iso()
    started = time.time()
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        shell=True,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "duration_sec": round(time.time() - started, 3),
        "started_at": started_at,
        "finished_at": now_iso(),
    }


def write_feature_report(project_root: Path, feature: dict, command_results: list[dict], ok: bool) -> Path:
    report_dir = project_root / FEATURE_REPORT_DIR
    report_path = report_dir / f"feature-{feature.get('id')}.md"
    lines = [
        f"# Feature {feature.get('id')} — {feature.get('title', 'Untitled')}",
        "",
        f"- Status: {'passing' if ok else 'failing'}",
        f"- Updated: {now_iso()}",
        "",
    ]
    for index, result in enumerate(command_results, start=1):
        lines.extend(
            [
                f"## Command {index}",
                "",
                f"- Command: `{result['command']}`",
                f"- Exit code: {result['returncode']}",
                f"- Duration: {result['duration_sec']}s",
                "",
                "```text",
                (result.get("stdout") or "").rstrip(),
                "```",
            ]
        )
        stderr = (result.get("stderr") or "").rstrip()
        if stderr:
            lines.extend(["", "```text", stderr, "```"])
        lines.append("")
    return write_text(report_path, "\n".join(lines).rstrip() + "\n")


def execute_feature(project_root: Path, feature: dict) -> dict:
    commands, relative_workdir, timeout = feature_command_config(feature)
    workdir = (project_root / relative_workdir).resolve()
    if not commands:
        return {
            "feature_id": feature.get("id"),
            "title": feature.get("title", "Untitled"),
            "ok": False,
            "detail": "No autopilot commands are configured for this feature.",
            "command_results": [],
        }

    command_results = []
    for command in commands:
        result = run_command(command, cwd=workdir, timeout=timeout)
        command_results.append(result)
        if result["returncode"] != 0:
            return {
                "feature_id": feature.get("id"),
                "title": feature.get("title", "Untitled"),
                "ok": False,
                "detail": f"Command failed: {command}",
                "command_results": command_results,
            }

    return {
        "feature_id": feature.get("id"),
        "title": feature.get("title", "Untitled"),
        "ok": True,
        "detail": "All feature commands passed.",
        "command_results": command_results,
    }


def system_test_commands(project_root: Path, feature_payload: dict) -> list[str]:
    real_test = feature_payload.get("real_test") if isinstance(feature_payload.get("real_test"), dict) else {}
    explicit = normalize_command_list(real_test.get("system_test_command") or real_test.get("command"))
    if explicit:
        return explicit

    language = infer_language(project_root, feature_payload)
    if language == "python" and (project_root / "tests").exists():
        return ["python -m pytest tests -q"]
    if language in {"typescript", "javascript"} and (project_root / "package.json").exists():
        return ["npm test -- --runInBand"]
    if language == "rust" and (project_root / "Cargo.toml").exists():
        return ["cargo test"]
    if language == "java" and (project_root / "pom.xml").exists():
        return ["mvn test"]
    return []


def qa_test_commands(feature_payload: dict) -> list[str]:
    real_test = feature_payload.get("real_test") if isinstance(feature_payload.get("real_test"), dict) else {}
    return normalize_command_list(real_test.get("qa_command"))


def write_phase_artifact(path: Path, title: str, sections: list[tuple[str, str]]) -> Path:
    lines = [f"# {title}", ""]
    for heading, body in sections:
        lines.extend([f"## {heading}", "", body.strip(), ""])
    return write_text(path, "\n".join(lines).rstrip() + "\n")


def execute_build_init(project_root: Path, state: dict, runtime: dict) -> dict:
    feature_path = feature_list_path(project_root)
    if not feature_path.exists():
        payload = create_default_feature_payload(project_root, state)
        save_feature_payload(project_root, payload)
        detail = f"Created {feature_path.name} with {len(payload.get('features', []))} feature(s)."
    else:
        payload = load_feature_payload(project_root)
        if not payload.get("features"):
            payload = create_default_feature_payload(project_root, state)
            save_feature_payload(project_root, payload)
            detail = f"Filled empty {feature_path.name} from tasks/defaults."
        else:
            detail = f"{feature_path.name} already exists."

    set_checkpoint(state, "build_init", True, phase="build-init")
    save_state(project_root, state)
    append_phase_history(project_root, {"timestamp": now_iso(), "phase": "build-init", "status": "completed", "detail": detail})
    append_runtime_event(runtime, kind="phase", title="Build Init completed", detail=detail, phase="build-init", status="success")
    record_phase_run(runtime, phase="build-init", status="completed", detail=detail)
    append_session_log(project_root, detail)
    return {"ok": True, "detail": detail}


def execute_build_config(project_root: Path, state: dict, runtime: dict) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "new-vibeflow-work-config.py"), "--project-root", str(project_root)],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
    )
    detail = (result.stdout or result.stderr or "").strip() or "Generated work-config.json."
    if result.returncode != 0:
        append_runtime_event(runtime, kind="phase", title="Build Config failed", detail=detail, phase="build-config", status="error")
        record_phase_run(runtime, phase="build-config", status="failed", detail=detail)
        append_session_log(project_root, f"Build config failed: {detail}")
        return {"ok": False, "detail": detail}

    set_checkpoint(state, "build_config", True, phase="build-config")
    if feature_list_path(project_root).exists():
        set_checkpoint(state, "build_init", True)
    save_state(project_root, state)
    append_phase_history(project_root, {"timestamp": now_iso(), "phase": "build-config", "status": "completed", "detail": detail})
    append_runtime_event(runtime, kind="phase", title="Build Config completed", detail=detail, phase="build-config", status="success")
    record_phase_run(runtime, phase="build-config", status="completed", detail=detail)
    append_session_log(project_root, detail)
    return {"ok": True, "detail": detail}


def pending_active_features(payload: dict) -> list[dict]:
    return [feature for feature in active_features(payload) if feature.get("status") != "passing"]


def execute_build_work(project_root: Path, state: dict, runtime: dict, *, parallel: bool = True, max_workers: int = 2) -> dict:
    payload = load_feature_payload(project_root)
    if not payload:
        return {"ok": False, "detail": "feature-list.json is missing."}

    while True:
        pending = pending_active_features(payload)
        if not pending:
            set_checkpoint(state, "build_work", True, phase="build-work")
            save_state(project_root, state)
            detail = "All active features are passing."
            append_phase_history(project_root, {"timestamp": now_iso(), "phase": "build-work", "status": "completed", "detail": detail})
            append_runtime_event(runtime, kind="phase", title="Build Work completed", detail=detail, phase="build-work", status="success")
            record_phase_run(runtime, phase="build-work", status="completed", detail=detail)
            append_session_log(project_root, detail)
            return {"ok": True, "detail": detail}

        ready = find_ready_features(payload)
        if not ready:
            detail = "No ready features found. Check dependencies or failing prerequisites."
            append_runtime_event(runtime, kind="phase", title="Build Work blocked", detail=detail, phase="build-work", status="warning")
            record_phase_run(runtime, phase="build-work", status="blocked", detail=detail)
            append_session_log(project_root, detail)
            return {"ok": False, "detail": detail}

        batch = ready[:1]
        if parallel and max_workers > 1:
            batch = ready[: max(1, min(len(ready), max_workers))]

        for feature in batch:
            feature["status"] = "running"
        save_feature_payload(project_root, payload)

        append_runtime_event(
            runtime,
            kind="phase",
            title="Build Work running",
            detail=f"Executing {len(batch)} feature(s): {', '.join(str(item.get('id')) for item in batch)}",
            phase="build-work",
            status="info",
        )
        record_phase_run(runtime, phase="build-work", status="running", detail=f"{len(batch)} feature(s) scheduled.")
        for feature in batch:
            record_feature_run(runtime, feature_id=feature.get("id"), title=feature.get("title", "Untitled"), status="running")
        save_runtime(project_root, runtime)

        if len(batch) == 1:
            results = [execute_feature(project_root, batch[0])]
        else:
            with ThreadPoolExecutor(max_workers=len(batch)) as pool:
                futures = [pool.submit(execute_feature, project_root, feature) for feature in batch]
                done, _ = wait(futures, return_when=FIRST_COMPLETED)
                if not done:
                    done = set(futures)
                results = [future.result() for future in futures]

        for result in results:
            feature_id = result["feature_id"]
            feature = next(item for item in payload.get("features", []) if item.get("id") == feature_id)
            feature["status"] = "passing" if result["ok"] else "failing"
            report_path = write_feature_report(project_root, feature, result["command_results"], result["ok"])
            record_feature_run(
                runtime,
                feature_id=feature_id,
                title=result["title"],
                status="completed" if result["ok"] else "failed",
                detail=result["detail"],
            )
            append_phase_history(
                project_root,
                {
                    "timestamp": now_iso(),
                    "phase": "build-work",
                    "type": "feature",
                    "feature_id": feature_id,
                    "title": result["title"],
                    "status": "passing" if result["ok"] else "failing",
                    "detail": f"{result['detail']} Report: {report_path}",
                },
            )
            append_session_log(project_root, f"Feature #{feature_id} {'passed' if result['ok'] else 'failed'}: {result['title']}")
            if not result["ok"]:
                save_feature_payload(project_root, payload)
                save_state(project_root, state)
                detail = f"Feature #{feature_id} failed: {result['detail']}"
                append_runtime_event(runtime, kind="phase", title="Build Work failed", detail=detail, phase="build-work", status="error")
                record_phase_run(runtime, phase="build-work", status="failed", detail=detail)
                save_runtime(project_root, runtime)
                return {"ok": False, "detail": detail, "feature_id": feature_id}

        save_feature_payload(project_root, payload)
        save_state(project_root, state)
        save_runtime(project_root, runtime)

        if not parallel:
            break

    detail = "A serial build step completed. Re-run build work to continue."
    append_runtime_event(runtime, kind="phase", title="Build Work progressed", detail=detail, phase="build-work", status="success")
    record_phase_run(runtime, phase="build-work", status="partial", detail=detail)
    save_runtime(project_root, runtime)
    return {"ok": True, "detail": detail}


def execute_review(project_root: Path, state: dict, runtime: dict) -> dict:
    commands = [
        [sys.executable, str(SCRIPT_DIR / "validate_features.py"), str(feature_list_path(project_root))],
        [sys.executable, str(SCRIPT_DIR / "check_configs.py"), str(feature_list_path(project_root))],
        [sys.executable, str(SCRIPT_DIR / "check_st_readiness.py"), "--project-root", str(project_root)],
    ]
    sections = []
    for command in commands:
        result = subprocess.run(command, cwd=str(REPO_ROOT), text=True, capture_output=True)
        label = " ".join(command[1:])
        body = (result.stdout or result.stderr or "").strip() or "No output."
        sections.append((label, f"Exit code: {result.returncode}\n\n```text\n{body}\n```"))
        if result.returncode != 0:
            detail = f"Review failed on: {label}"
            append_runtime_event(runtime, kind="phase", title="Review failed", detail=detail, phase="review", status="error")
            record_phase_run(runtime, phase="review", status="failed", detail=detail)
            return {"ok": False, "detail": detail}

    contract = path_contract(project_root, state)
    write_phase_artifact(contract["artifacts"]["review"], "Review", sections)
    set_checkpoint(state, "review", True, phase="review")
    save_state(project_root, state)
    detail = "Review checks passed."
    append_phase_history(project_root, {"timestamp": now_iso(), "phase": "review", "status": "completed", "detail": detail})
    append_runtime_event(runtime, kind="phase", title="Review completed", detail=detail, phase="review", status="success")
    record_phase_run(runtime, phase="review", status="completed", detail=detail)
    append_session_log(project_root, detail)
    return {"ok": True, "detail": detail}


def execute_test_system(project_root: Path, state: dict, runtime: dict) -> dict:
    payload = load_feature_payload(project_root)
    commands = system_test_commands(project_root, payload)
    if not commands:
        return {"ok": False, "detail": "No system test command could be inferred. Configure real_test.system_test_command."}

    sections = []
    for command in commands:
        result = run_command(command, cwd=project_root, timeout=900)
        output = (result["stdout"] or result["stderr"] or "").strip() or "No output."
        sections.append((command, f"Exit code: {result['returncode']}\n\n```text\n{output}\n```"))
        if result["returncode"] != 0:
            detail = f"System test failed: {command}"
            append_runtime_event(runtime, kind="phase", title="System Test failed", detail=detail, phase="test-system", status="error")
            record_phase_run(runtime, phase="test-system", status="failed", detail=detail)
            return {"ok": False, "detail": detail}

    contract = path_contract(project_root, state)
    write_phase_artifact(contract["artifacts"]["system_test"], "System Test", sections)
    set_checkpoint(state, "test_system", True, phase="test-system")
    save_state(project_root, state)
    detail = "System tests passed."
    append_phase_history(project_root, {"timestamp": now_iso(), "phase": "test-system", "status": "completed", "detail": detail})
    append_runtime_event(runtime, kind="phase", title="System Test completed", detail=detail, phase="test-system", status="success")
    record_phase_run(runtime, phase="test-system", status="completed", detail=detail)
    append_session_log(project_root, detail)
    return {"ok": True, "detail": detail}


def execute_test_qa(project_root: Path, state: dict, runtime: dict) -> dict:
    payload = load_feature_payload(project_root)
    commands = qa_test_commands(payload)
    if not commands:
        return {"ok": False, "detail": "QA is required but no qa_command is configured in feature-list.json real_test block."}

    sections = []
    for command in commands:
        result = run_command(command, cwd=project_root, timeout=900)
        output = (result["stdout"] or result["stderr"] or "").strip() or "No output."
        sections.append((command, f"Exit code: {result['returncode']}\n\n```text\n{output}\n```"))
        if result["returncode"] != 0:
            detail = f"QA failed: {command}"
            append_runtime_event(runtime, kind="phase", title="QA failed", detail=detail, phase="test-qa", status="error")
            record_phase_run(runtime, phase="test-qa", status="failed", detail=detail)
            return {"ok": False, "detail": detail}

    contract = path_contract(project_root, state)
    write_phase_artifact(contract["artifacts"]["qa"], "QA", sections)
    set_checkpoint(state, "test_qa", True, phase="test-qa")
    save_state(project_root, state)
    detail = "QA checks passed."
    append_phase_history(project_root, {"timestamp": now_iso(), "phase": "test-qa", "status": "completed", "detail": detail})
    append_runtime_event(runtime, kind="phase", title="QA completed", detail=detail, phase="test-qa", status="success")
    record_phase_run(runtime, phase="test-qa", status="completed", detail=detail)
    append_session_log(project_root, detail)
    return {"ok": True, "detail": detail}


def execute_ship(project_root: Path, state: dict, runtime: dict) -> dict:
    contract = path_contract(project_root, state)
    path = contract["release_notes"]
    active_change = state.get("active_change") or {}
    section = (
        f"## {now_iso()} — {active_change.get('id', project_root.name)}\n\n"
        "- Build completed\n"
        "- Review passed\n"
        "- System tests passed\n"
    )
    if not path.exists():
        write_text(path, "# Release Notes\n\n" + section)
    else:
        content = path.read_text(encoding="utf-8")
        if active_change.get("id", "") not in content:
            append_text(path, "\n" + section)
    set_checkpoint(state, "ship", True, phase="ship")
    save_state(project_root, state)
    detail = "Release notes are ready."
    append_phase_history(project_root, {"timestamp": now_iso(), "phase": "ship", "status": "completed", "detail": detail})
    append_runtime_event(runtime, kind="phase", title="Ship completed", detail=detail, phase="ship", status="success")
    record_phase_run(runtime, phase="ship", status="completed", detail=detail)
    append_session_log(project_root, detail)
    return {"ok": True, "detail": detail}


def execute_reflect(project_root: Path, state: dict, runtime: dict) -> dict:
    logs_dir = project_root / ".vibeflow" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    payload = load_feature_payload(project_root)
    path = logs_dir / f"retro-{datetime.now().strftime('%Y-%m-%d')}.md"
    lines = [
        "# Retro",
        "",
        f"- Change: {state.get('active_change', {}).get('id', project_root.name)}",
        f"- Features passing: {len([item for item in active_features(payload) if item.get('status') == 'passing'])}",
        f"- Generated: {now_iso()}",
        "",
        "## Notes",
        "",
        "- Autopilot completed the post-design delivery chain.",
    ]
    write_text(path, "\n".join(lines) + "\n")
    set_checkpoint(state, "reflect", True, phase="reflect")
    save_state(project_root, state)
    detail = "Retrospective recorded."
    append_phase_history(project_root, {"timestamp": now_iso(), "phase": "reflect", "status": "completed", "detail": detail})
    append_runtime_event(runtime, kind="phase", title="Reflect completed", detail=detail, phase="reflect", status="success")
    record_phase_run(runtime, phase="reflect", status="completed", detail=detail)
    append_session_log(project_root, detail)
    return {"ok": True, "detail": detail}


def execute_phase(project_root: Path, phase: str, *, parallel_build: bool = True, max_workers: int = 2) -> dict:
    state = ensure_state(project_root)
    runtime = ensure_runtime(project_root)
    persist_runtime(
        project_root,
        runtime,
        status="running",
        phase=phase,
        action=f"Executing {phase}",
        message=friendly_message_for_phase(phase),
        stop_reason="",
    )

    handlers = {
        "build-init": lambda: execute_build_init(project_root, state, runtime),
        "build-config": lambda: execute_build_config(project_root, state, runtime),
        "build-work": lambda: execute_build_work(project_root, state, runtime, parallel=parallel_build, max_workers=max_workers),
        "review": lambda: execute_review(project_root, state, runtime),
        "test-system": lambda: execute_test_system(project_root, state, runtime),
        "test-qa": lambda: execute_test_qa(project_root, state, runtime),
        "ship": lambda: execute_ship(project_root, state, runtime),
        "reflect": lambda: execute_reflect(project_root, state, runtime),
    }
    if phase not in handlers:
        detail = f"Phase '{phase}' is not auto-runnable."
        append_runtime_event(runtime, kind="phase", title="Autopilot stopped", detail=detail, phase=phase, status="warning")
        persist_runtime(
            project_root,
            runtime,
            status="waiting_manual",
            phase=phase,
            message=friendly_message_for_phase(phase, status="waiting_manual", detail=detail),
            stop_reason=detail,
        )
        return {"ok": False, "detail": detail}

    result = handlers[phase]()
    runtime = load_runtime(project_root)
    if result["ok"]:
        persist_runtime(
            project_root,
            runtime,
            status="running",
            phase=phase,
            action=f"Completed {phase}",
            message=friendly_message_for_phase(phase, detail=result["detail"]),
            stop_reason="",
        )
    else:
        persist_runtime(
            project_root,
            runtime,
            status="blocked",
            phase=phase,
            action=f"Blocked at {phase}",
            message=friendly_message_for_phase(phase, status="blocked", detail=result["detail"]),
            stop_reason=result["detail"],
        )
    return result


def run_autopilot(
    project_root: Path,
    *,
    max_steps: int | None = None,
    stop_at: set[str] | None = None,
    parallel_build: bool | None = None,
    max_workers: int | None = None,
) -> dict:
    project_root = project_root.resolve()
    state = ensure_state(project_root)
    runtime = ensure_runtime(project_root)
    autopilot_config = state.get("autopilot") or {}

    manual_only = set(autopilot_config.get("manual_only") or MANUAL_ONLY_PHASES)
    auto_runnable = set(autopilot_config.get("auto_runnable") or AUTO_RUNNABLE_PHASES)
    retryable = set(autopilot_config.get("retryable") or RETRYABLE_PHASES)
    step_limit = max_steps or int(autopilot_config.get("max_steps") or 20)
    retry_limit = int(autopilot_config.get("max_retries_per_phase") or 0)
    stop_points = stop_at or set()
    parallel_enabled = bool(autopilot_config.get("parallel_build", True) if parallel_build is None else parallel_build)
    workers = max_workers or int(autopilot_config.get("parallel_build_workers") or 2)

    run_id = f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    runtime["run_id"] = run_id
    runtime["step_count"] = 0
    runtime["attempts"] = {}
    persist_runtime(
        project_root,
        runtime,
        status="running",
        action="Autopilot started",
        message="自动执行已启动，准备接管后续链路。",
        stop_reason="",
    )
    append_runtime_event(runtime, kind="run", title="Autopilot started", detail=f"Run id: {run_id}")
    save_runtime(project_root, runtime)

    executed = []
    while runtime["step_count"] < step_limit:
        phase_info = detect_phase(project_root, verbose=True)
        phase = phase_info["phase"]
        reason = phase_info["reason"]

        if phase == "done":
            runtime = load_runtime(project_root)
            append_runtime_event(runtime, kind="run", title="Workflow completed", detail="Autopilot reached done.", status="success")
            persist_runtime(
                project_root,
                runtime,
                status="completed",
                phase="done",
                action="Workflow completed",
                message=friendly_message_for_phase("done"),
                stop_reason="",
            )
            return {"ok": True, "status": "completed", "run_id": run_id, "executed": executed, "final_phase": "done"}

        if phase in stop_points:
            runtime = load_runtime(project_root)
            detail = f"Stopped at requested phase: {phase}"
            append_runtime_event(runtime, kind="run", title="Autopilot paused", detail=detail, phase=phase, status="warning")
            persist_runtime(project_root, runtime, status="waiting_manual", phase=phase, action=f"Stopped at {phase}", message=f"已按要求停在 {phase}。", stop_reason=detail)
            return {"ok": True, "status": "stopped", "run_id": run_id, "executed": executed, "final_phase": phase}

        if phase in manual_only:
            runtime = load_runtime(project_root)
            detail = reason or f"{phase} requires manual confirmation."
            append_runtime_event(runtime, kind="run", title="Autopilot waiting for manual input", detail=detail, phase=phase, status="warning")
            persist_runtime(
                project_root,
                runtime,
                status="waiting_manual",
                phase=phase,
                action=f"Waiting at {phase}",
                message=friendly_message_for_phase(phase, status="waiting_manual", detail=detail),
                stop_reason=detail,
            )
            return {"ok": True, "status": "waiting_manual", "run_id": run_id, "executed": executed, "final_phase": phase}

        if phase not in auto_runnable:
            runtime = load_runtime(project_root)
            detail = f"Phase '{phase}' is not configured for autopilot."
            append_runtime_event(runtime, kind="run", title="Autopilot stopped", detail=detail, phase=phase, status="error")
            persist_runtime(project_root, runtime, status="blocked", phase=phase, action=f"Blocked at {phase}", message=friendly_message_for_phase(phase, status="blocked", detail=detail), stop_reason=detail)
            return {"ok": False, "status": "blocked", "run_id": run_id, "executed": executed, "final_phase": phase}

        attempts = runtime.setdefault("attempts", {})
        attempts[phase] = int(attempts.get(phase, 0)) + 1
        save_runtime(project_root, runtime)

        result = execute_phase(project_root, phase, parallel_build=parallel_enabled, max_workers=workers)
        executed.append({"phase": phase, "ok": result["ok"], "detail": result["detail"]})
        runtime = load_runtime(project_root)
        runtime["step_count"] = int(runtime.get("step_count", 0)) + 1
        save_runtime(project_root, runtime)

        if result["ok"]:
            runtime.setdefault("attempts", {})[phase] = 0
            save_runtime(project_root, runtime)
            continue

        if phase in retryable and attempts[phase] <= retry_limit:
            append_runtime_event(runtime, kind="run", title="Retrying phase", detail=f"Retry {attempts[phase]}/{retry_limit} for {phase}", phase=phase, status="warning")
            save_runtime(project_root, runtime)
            continue

        persist_runtime(
            project_root,
            runtime,
            status="blocked",
            phase=phase,
            action=f"Blocked at {phase}",
            message=friendly_message_for_phase(phase, status="blocked", detail=result["detail"]),
            stop_reason=result["detail"],
        )
        return {"ok": False, "status": "blocked", "run_id": run_id, "executed": executed, "final_phase": phase}

    runtime = load_runtime(project_root)
    detail = f"Autopilot reached the max step limit ({step_limit})."
    append_runtime_event(runtime, kind="run", title="Autopilot stopped", detail=detail, status="warning")
    persist_runtime(project_root, runtime, status="blocked", action="Max steps reached", message=detail, stop_reason=detail)
    return {"ok": False, "status": "blocked", "run_id": run_id, "executed": executed, "final_phase": detect_phase(project_root)["phase"]}
