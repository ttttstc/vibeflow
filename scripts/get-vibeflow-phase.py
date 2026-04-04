#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from vibeflow_paths import (  # noqa: E402
    checkpoint_done,
    increment_queue_path,
    load_runtime,
    load_state,
    path_contract,
    quick_meta,
    quick_readiness_issues,
    save_runtime,
    set_runtime_invariant,
    state_path,
    workflow_path,
)
from validate_phase_invariants import validate_phase  # noqa: E402


MANUAL_PHASES = {"increment", "spark", "design", "tasks", "quick"}


def workflow_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def ui_required(workflow_path_obj: Path) -> bool:
    content = workflow_text(workflow_path_obj)
    return (
        ("qa:\n    required: true" in content)
        or ("qa:\n  required: true" in content)
        or ("design_review:\n    required: true" in content)
        or ("design_review:\n  required: true" in content)
    )


def ship_required(workflow_path_obj: Path) -> bool:
    content = workflow_text(workflow_path_obj)
    return ("ship:\n  required: true" in content) or ("ship:\n    required: true" in content)


def reflect_required(workflow_path_obj: Path) -> bool:
    content = workflow_text(workflow_path_obj)
    return ("reflect:\n  required: true" in content) or ("reflect:\n    required: true" in content)


def all_features_passing(feature_list_path: Path) -> bool:
    if not feature_list_path.exists():
        return False
    data = json.loads(feature_list_path.read_text(encoding="utf-8"))
    features = [f for f in data.get("features", []) if not f.get("deprecated")]
    return bool(features) and all(f.get("status") == "passing" for f in features)


def has_active_features(feature_list_path: Path) -> bool:
    if not feature_list_path.exists():
        return False
    data = json.loads(feature_list_path.read_text(encoding="utf-8"))
    features = [f for f in data.get("features", []) if not f.get("deprecated")]
    return bool(features)


def increment_pending(project_root: Path) -> bool:
    queue_json = increment_queue_path(project_root)
    if queue_json.exists():
        try:
            data = json.loads(queue_json.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return bool(data.get("items", []))
            if isinstance(data, list):
                return bool(data)
        except json.JSONDecodeError:
            return True
    legacy_increment = project_root / ".vibeflow" / "increment-request.json"
    if legacy_increment.exists():
        return True
    requests_dir = project_root / ".vibeflow" / "increments" / "requests"
    return requests_dir.exists() and any(requests_dir.glob("*.json"))


def latest_matching_file(base: Path, pattern: str):
    if not base.exists():
        return None
    matches = sorted(base.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0] if matches else None


def phase_open_files(contract: dict, phase: str) -> list[str]:
    artifacts = contract["artifacts"]
    if phase == "spark":
        return [str(artifacts["spark"])]
    if phase == "design":
        return [str(artifacts["spark"]), str(artifacts["design"])]
    if phase == "tasks":
        return [str(artifacts["design"]), str(artifacts["tasks"])]
    if phase == "build":
        return [str(artifacts["tasks"]), str(contract["feature_list"])]
    if phase == "review":
        return [str(contract["feature_list"]), str(artifacts["review"])]
    if phase == "test":
        return [str(artifacts["review"]), str(artifacts["system_test"]), str(artifacts["qa"])]
    if phase == "ship":
        return [str(artifacts["system_test"]), str(contract["release_notes"])]
    if phase == "reflect":
        return [str(contract["release_notes"])]
    return [str(contract["state"])]


def next_action_for_phase(phase: str, reason: str, *, ui_required_flag: bool, ship_required_flag: bool, reflect_required_flag: bool) -> str:
    if phase == "increment":
        return "先处理增量队列，再继续主链。"
    if phase == "spark":
        return "补全 brief.md，明确目标、边界、验收标准和约束。"
    if phase == "design":
        return "完善 design.md，并把评审结论合并进设计文档。"
    if phase == "tasks":
        return "生成 execution-grade tasks.md，确保包含精确文件路径、验证步骤和回滚说明。"
    if phase == "build":
        return "继续 Build：先确保 feature-list.json 已物化，然后把所有 active features 跑到 passing。"
    if phase == "review":
        return "生成 verification/review.md，确认结构、风险和一致性。"
    if phase == "test":
        if ui_required_flag:
            return "完成系统测试，并在需要时补齐 QA 结果，让 verification/ 下证据完整。"
        return "完成系统测试，生成 verification/system-test.md。"
    if phase == "ship":
        return "整理 RELEASE_NOTES.md，完成发布收口。"
    if phase == "reflect":
        return "生成 retro 复盘，结束这轮交付。"
    if phase == "quick":
        return "先补齐 Quick Mode 准入信息和最小设计/任务产物。"
    if phase == "done":
        if reflect_required_flag:
            return "主链已完成，可以开始下一轮 change。"
        if ship_required_flag:
            return "交付已完成，可以开始下一轮 change。"
        return "当前 workflow 已收口。"
    return reason or "查看当前 phase 对应产物。"


def result_with_guidance(result: dict, contract: dict, *, ui_required_flag: bool, ship_required_flag: bool, reflect_required_flag: bool) -> dict:
    phase = result["phase"]
    result["resume_mode"] = "manual" if phase in MANUAL_PHASES else ("completed" if phase == "done" else "auto")
    result["next_action"] = next_action_for_phase(
        phase,
        result["reason"],
        ui_required_flag=ui_required_flag,
        ship_required_flag=ship_required_flag,
        reflect_required_flag=reflect_required_flag,
    )
    result["open_files"] = phase_open_files(contract, phase)
    return result


def append_invariant_checks(checks: list, validation: dict) -> None:
    for entry in validation.get("checks", []):
        checks.append(
            (
                f'{validation.get("phase")}:{entry.get("category")}:{entry.get("item")}',
                not entry.get("ok", False),
                entry.get("detail", ""),
            )
        )


def apply_invariant_block(validation: dict, checks: list | None = None) -> tuple[str, str, str, str, dict]:
    if checks is not None:
        append_invariant_checks(checks, validation)
    return (
        validation["phase"],
        validation["friendly_reason"],
        validation.get("reason_code", ""),
        validation.get("blocking_item", ""),
        validation,
    )


def sync_runtime_from_detect(project_root: Path, result: dict) -> None:
    if not state_path(project_root).exists():
        return
    runtime = load_runtime(project_root)
    phase = result.get("phase", "")
    reason = result.get("reason", "")
    reason_code = result.get("reason_code", "")
    status = "clear" if phase == "done" else ("blocked" if reason_code else "pending")
    invariant_phase = "" if phase == "done" else phase
    invariant_reason = "" if phase == "done" else reason
    current_invariant = runtime.get("invariant") or {}
    if (
        runtime.get("current_phase") == phase
        and current_invariant.get("phase") == invariant_phase
        and current_invariant.get("reason") == invariant_reason
        and current_invariant.get("reason_code") == reason_code
        and current_invariant.get("status") == status
        and runtime.get("friendly_message") == result.get("next_action", "")
    ):
        return
    runtime["current_phase"] = phase
    runtime["friendly_message"] = result.get("next_action", "")
    runtime["stop_reason"] = reason
    set_runtime_invariant(
        runtime,
        phase=invariant_phase,
        reason=invariant_reason,
        reason_code=reason_code,
        status=status,
    )
    save_runtime(project_root, runtime)


def legacy_detect_phase(project_root: Path, verbose: bool = False) -> dict:
    workflow = workflow_path(project_root)
    flags = {
        "ui": ui_required(workflow),
        "ship": ship_required(workflow),
        "reflect": reflect_required(workflow),
    }
    checks = []
    if increment_pending(project_root):
        checks.append(("increment", True, "increment queue pending"))
        result = {
            "phase": "increment",
            "reason": "Increment queue has pending items.",
            "reason_code": "",
            "blocking_item": "",
            "invariant": {},
            "has_ui": flags["ui"],
            "ship_required": flags["ship"],
            "reflect_required": flags["reflect"],
            "is_quick_mode": False,
            "paths": {
                "state": str(project_root / ".vibeflow" / "state.json"),
                "workflow": str(workflow),
            },
        }
    else:
        result = {
            "phase": "spark",
            "reason": ".vibeflow/state.json is missing; start with Spark.",
            "reason_code": "missing_state",
            "blocking_item": "state",
            "invariant": {},
            "has_ui": flags["ui"],
            "ship_required": flags["ship"],
            "reflect_required": flags["reflect"],
            "is_quick_mode": False,
            "paths": {
                "state": str(project_root / ".vibeflow" / "state.json"),
                "workflow": str(workflow),
            },
        }
    contract = {
        "state": project_root / ".vibeflow" / "state.json",
        "feature_list": project_root / "feature-list.json",
        "release_notes": project_root / "RELEASE_NOTES.md",
        "artifacts": {
            "spark": project_root / "docs" / "changes" / "active" / "brief.md",
            "design": project_root / "docs" / "changes" / "active" / "design.md",
            "tasks": project_root / "docs" / "changes" / "active" / "tasks.md",
            "review": project_root / "docs" / "changes" / "active" / "verification" / "review.md",
            "system_test": project_root / "docs" / "changes" / "active" / "verification" / "system-test.md",
            "qa": project_root / "docs" / "changes" / "active" / "verification" / "qa.md",
        },
    }
    if verbose:
        result["checks"] = [{"condition": c[0], "triggered": c[1], "detail": c[2]} for c in checks]
    return result_with_guidance(
        result,
        contract,
        ui_required_flag=flags["ui"],
        ship_required_flag=flags["ship"],
        reflect_required_flag=flags["reflect"],
    )


def state_based_detect_phase(project_root: Path, verbose: bool = False) -> dict:
    state = load_state(project_root)
    contract = path_contract(project_root, state)
    workflow_path_obj = contract["workflow"]
    feature_list = contract["feature_list"]
    release_notes = contract["release_notes"]
    artifacts = contract["artifacts"]
    retro_logs = project_root / ".vibeflow" / "logs"
    latest_retro = latest_matching_file(retro_logs, "retro-*.md")
    flags = {
        "ui": ui_required(workflow_path_obj),
        "ship": ship_required(workflow_path_obj),
        "reflect": reflect_required(workflow_path_obj),
    }
    is_quick_mode = state.get("mode") == "quick"
    pending_increment = increment_pending(project_root)
    quick_issues = quick_readiness_issues(project_root, state) if is_quick_mode else []
    quick_state_meta = quick_meta(state) if is_quick_mode else {}

    checks = []
    checks.append(("increment", pending_increment, "increment queue " + ("pending" if pending_increment else "empty")))
    checks.append(("spark", not checkpoint_done(state, "spark") or not artifacts["spark"].exists(), f'spark={checkpoint_done(state, "spark")}, artifact={"exists" if artifacts["spark"].exists() else "missing"}'))
    checks.append(("design", not checkpoint_done(state, "design") or not artifacts["design"].exists(), f'design={checkpoint_done(state, "design")}, artifact={"exists" if artifacts["design"].exists() else "missing"}'))
    checks.append(("tasks", not checkpoint_done(state, "tasks") or not artifacts["tasks"].exists(), f'tasks={checkpoint_done(state, "tasks")}, artifact={"exists" if artifacts["tasks"].exists() else "missing"}'))
    checks.append(("build", not has_active_features(feature_list) or not all_features_passing(feature_list), "build " + ("pending" if not all_features_passing(feature_list) else "complete")))
    checks.append(("review", not checkpoint_done(state, "review") or not artifacts["review"].exists(), f'review={checkpoint_done(state, "review")}, artifact={"exists" if artifacts["review"].exists() else "missing"}'))
    checks.append(("test", not checkpoint_done(state, "test") or not artifacts["system_test"].exists() or (flags["ui"] and not artifacts["qa"].exists()), f'test={checkpoint_done(state, "test")}, system_test={"exists" if artifacts["system_test"].exists() else "missing"}, qa={"exists" if artifacts["qa"].exists() else "missing"}'))
    checks.append(("ship", flags["ship"] and (not checkpoint_done(state, "ship") or not release_notes.exists()), f'ship={checkpoint_done(state, "ship")}, release_notes={"exists" if release_notes.exists() else "missing"}'))
    checks.append(("reflect", flags["reflect"] and (not checkpoint_done(state, "reflect") or latest_retro is None), f'reflect={checkpoint_done(state, "reflect")}, retro={"exists" if latest_retro else "missing"}'))

    phase = "done"
    reason = "All detectable phases completed."
    reason_code = ""
    blocking_item = ""
    invariant = {}

    def evaluate_invariant(phase_name: str) -> dict:
        return validate_phase(project_root, phase_name, state=state, contract=contract)

    if is_quick_mode and quick_issues:
        phase = "quick"
        promote_hint = ""
        if quick_state_meta.get("decision") in {"rejected", "promoted"} or any("Full Mode" in issue for issue in quick_issues):
            promote_hint = " Run scripts/promote-vibeflow-quick.py to switch back to Full Mode."
        reason = f"Quick mode is not ready: {' '.join(quick_issues)}{promote_hint}".strip()
    elif pending_increment:
        phase, reason = "increment", "Increment queue has pending items."
    elif is_quick_mode:
        if not feature_list.exists():
            phase, reason = "build", "Quick mode is ready and should proceed into Build."
        elif not all_features_passing(feature_list):
            phase, reason = "build", "Quick mode has unfinished features."
        else:
            review_validation = evaluate_invariant("review")
            if not review_validation["ok"]:
                phase, reason, reason_code, blocking_item, invariant = apply_invariant_block(review_validation, checks if verbose else None)
            elif not checkpoint_done(state, "test") or not artifacts["system_test"].exists() or (flags["ui"] and not artifacts["qa"].exists()):
                phase = "test"
                if not artifacts["system_test"].exists():
                    reason = "System test artifact is missing."
                    reason_code = "missing_artifact"
                    blocking_item = "system_test"
                elif flags["ui"] and not artifacts["qa"].exists():
                    reason = "UI workflow requires QA artifact."
                    reason_code = "missing_artifact"
                    blocking_item = "qa"
                else:
                    reason = "Test approval is missing."
                    reason_code = "missing_approval"
                    blocking_item = "test"
            elif flags["ship"]:
                ship_validation = evaluate_invariant("ship")
                if not ship_validation["ok"]:
                    phase, reason, reason_code, blocking_item, invariant = apply_invariant_block(ship_validation, checks if verbose else None)
                elif flags["reflect"] and (not checkpoint_done(state, "reflect") or latest_retro is None):
                    phase = "reflect"
                    reason = "Reflect is required and no retrospective exists."
                    reason_code = "missing_completion_evidence"
                    blocking_item = "reflect"
            elif flags["reflect"] and (not checkpoint_done(state, "reflect") or latest_retro is None):
                phase = "reflect"
                reason = "Reflect is required and no retrospective exists."
                reason_code = "missing_completion_evidence"
                blocking_item = "reflect"
    else:
        spark_validation = evaluate_invariant("spark")
        if not spark_validation["ok"]:
            phase, reason, reason_code, blocking_item, invariant = apply_invariant_block(spark_validation, checks if verbose else None)
        else:
            design_validation = evaluate_invariant("design")
            if not design_validation["ok"]:
                phase, reason, reason_code, blocking_item, invariant = apply_invariant_block(design_validation, checks if verbose else None)
            else:
                tasks_validation = evaluate_invariant("tasks")
                if not tasks_validation["ok"]:
                    phase, reason, reason_code, blocking_item, invariant = apply_invariant_block(tasks_validation, checks if verbose else None)
                elif not feature_list.exists():
                    phase, reason = "build", "feature-list.json is missing."
                    reason_code = "missing_artifact"
                    blocking_item = "feature_list"
                elif not has_active_features(feature_list):
                    phase, reason = "build", "feature-list.json has no active features."
                    reason_code = "missing_completion_evidence"
                    blocking_item = "active_features"
                elif not all_features_passing(feature_list):
                    phase, reason = "build", "Some active features are not passing."
                else:
                    review_validation = evaluate_invariant("review")
                    if not review_validation["ok"]:
                        phase, reason, reason_code, blocking_item, invariant = apply_invariant_block(review_validation, checks if verbose else None)
                    elif not checkpoint_done(state, "test") or not artifacts["system_test"].exists() or (flags["ui"] and not artifacts["qa"].exists()):
                        phase = "test"
                        if not artifacts["system_test"].exists():
                            reason = "System test artifact is missing."
                            reason_code = "missing_artifact"
                            blocking_item = "system_test"
                        elif flags["ui"] and not artifacts["qa"].exists():
                            reason = "UI workflow requires QA artifact."
                            reason_code = "missing_artifact"
                            blocking_item = "qa"
                        else:
                            reason = "Test approval is missing."
                            reason_code = "missing_approval"
                            blocking_item = "test"
                    elif flags["ship"]:
                        ship_validation = evaluate_invariant("ship")
                        if not ship_validation["ok"]:
                            phase, reason, reason_code, blocking_item, invariant = apply_invariant_block(ship_validation, checks if verbose else None)
                        elif flags["reflect"] and (not checkpoint_done(state, "reflect") or latest_retro is None):
                            phase = "reflect"
                            reason = "Reflect is required and no retrospective exists."
                            reason_code = "missing_completion_evidence"
                            blocking_item = "reflect"
                    elif flags["reflect"] and (not checkpoint_done(state, "reflect") or latest_retro is None):
                        phase = "reflect"
                        reason = "Reflect is required and no retrospective exists."
                        reason_code = "missing_completion_evidence"
                        blocking_item = "reflect"

    result = {
        "phase": phase,
        "reason": reason,
        "reason_code": reason_code,
        "blocking_item": blocking_item,
        "invariant": invariant,
        "has_ui": flags["ui"],
        "ship_required": flags["ship"],
        "reflect_required": flags["reflect"],
        "is_quick_mode": is_quick_mode,
        "paths": {
            "state": str(state_path(project_root)),
            "workflow": str(workflow_path_obj),
            "feature_list": str(feature_list),
            "release_notes": str(release_notes),
            "change_root": str(contract["change_root"]),
            "session_log": str(contract["session_log"]),
            "spark": str(artifacts["spark"]),
            "ucd": str(artifacts["ucd"]),
            "design": str(artifacts["design"]),
            "tasks": str(artifacts["tasks"]),
            "review": str(artifacts["review"]),
            "system_test": str(artifacts["system_test"]),
            "qa": str(artifacts["qa"]),
            "latest_retro": str(latest_retro) if latest_retro else None,
        },
    }
    if verbose:
        result["checks"] = [{"condition": c[0], "triggered": c[1], "detail": c[2]} for c in checks]
    return result_with_guidance(
        result,
        contract,
        ui_required_flag=flags["ui"],
        ship_required_flag=flags["ship"],
        reflect_required_flag=flags["reflect"],
    )


def detect_phase(project_root: Path, verbose: bool = False, sync_runtime: bool = False) -> dict:
    if state_path(project_root).exists():
        result = state_based_detect_phase(project_root, verbose=verbose)
        if sync_runtime:
            sync_runtime_from_detect(project_root, result)
        return result
    result = legacy_detect_phase(project_root, verbose=verbose)
    if sync_runtime:
        sync_runtime_from_detect(project_root, result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    result = detect_phase(Path(args.project_root).resolve(), verbose=args.verbose, sync_runtime=True)
    if args.as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(result["phase"])
        if args.verbose and "checks" in result:
            print("\nDebug traces:")
            for ch in result["checks"]:
                status = "→" if ch["triggered"] else " "
                print(f'  [{status}] {ch["condition"]}: {ch["detail"]}')


if __name__ == "__main__":
    main()
