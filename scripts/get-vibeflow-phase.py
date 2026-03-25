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
    load_state,
    path_contract,
    quick_meta,
    quick_readiness_issues,
    state_path,
    workflow_path,
)


def latest_matching_file(base: Path, pattern: str):
    if not base.exists():
        return None
    matches = sorted(base.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0] if matches else None


def resolve_yaml(directory: Path, stem: str) -> Path:
    """Return the first existing path among <stem>.yaml and <stem>.yml."""
    for ext in (".yaml", ".yml"):
        p = directory / f"{stem}{ext}"
        if p.exists():
            return p
    return directory / f"{stem}.yaml"


def workflow_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def ui_required(workflow_path_obj: Path) -> bool:
    content = workflow_text(workflow_path_obj)
    return ("qa:\n    required: true" in content) or ("design_review:\n    required: true" in content)


def ship_required(workflow_path_obj: Path) -> bool:
    content = workflow_text(workflow_path_obj)
    if "ship:\n  required: true" in content:
        return True
    if "ship:\n    required: true" in content:
        return True
    return False


def reflect_required(workflow_path_obj: Path) -> bool:
    content = workflow_text(workflow_path_obj)
    if "reflect:\n  required: true" in content:
        return True
    if "reflect:\n    required: true" in content:
        return True
    return False


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


def build_packets_ready(feature_list_path: Path, packets_dir: Path) -> bool:
    if not feature_list_path.exists():
        return False
    data = json.loads(feature_list_path.read_text(encoding="utf-8"))
    features = [f for f in data.get("features", []) if not f.get("deprecated")]
    if not features:
        return False
    return all((packets_dir / f"feature-{feature.get('id')}.json").exists() for feature in features if feature.get("id") is not None)


def increment_pending(project_root: Path) -> bool:
    queue_json = increment_queue_path(project_root)
    if queue_json.exists():
        try:
            data = json.loads(queue_json.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                items = data.get("items", [])
                return bool(items)
            if isinstance(data, list):
                return bool(data)
        except json.JSONDecodeError:
            pass

    legacy_queue = project_root / ".vibeflow" / "increment-queue.txt"
    if legacy_queue.exists():
        lines = [line.strip() for line in legacy_queue.read_text(encoding="utf-8").splitlines()]
        return any(line and not line.startswith("#") for line in lines)

    requests_dir = project_root / ".vibeflow" / "increments" / "requests"
    if requests_dir.exists():
        return any(requests_dir.glob("*.json"))

    legacy_increment = project_root / ".vibeflow" / "increment-request.json"
    return legacy_increment.exists()


def legacy_detect_phase(project_root: Path, verbose: bool = False) -> dict:
    state_root = project_root / ".vibeflow"
    think_path = state_root / "think-output.md"
    workflow_path_obj = resolve_yaml(state_root, "workflow")
    work_config_path = state_root / "work-config.json"
    qa_report_path = state_root / "qa-report.md"
    plan_path = state_root / "plan.md"
    review_report_path = state_root / "review-report.md"
    increment_path = state_root / "increment-request.json"
    feature_list_path = project_root / "feature-list.json"
    plans_path = project_root / "docs" / "plans"
    latest_srs = latest_matching_file(plans_path, "*-srs.md")
    latest_design = latest_matching_file(plans_path, "*-design.md")
    latest_st = latest_matching_file(plans_path, "*-st-report.md")
    latest_retro = latest_matching_file(state_root, "retro-*.md") if state_root.exists() else None
    quick_config_path = state_root / "quick-config.json"
    quick_design_path = project_root / "docs" / "quick-design.md"
    checks = []
    _ui_req = ui_required(workflow_path_obj)
    _ship_req = ship_required(workflow_path_obj)
    _reflect_req = reflect_required(workflow_path_obj)

    checks.append(("quick", quick_config_path.exists(), "quick-config " + ("exists" if quick_config_path.exists() else "missing")))
    checks.append(("increment", increment_path.exists(), "increment-path " + ("exists" if increment_path.exists() else "missing")))
    checks.append(("think", not think_path.exists(), "think-output " + ("missing" if not think_path.exists() else "exists")))
    checks.append(("template-selection", not workflow_path_obj.exists(), "workflow.yaml " + ("missing" if not workflow_path_obj.exists() else "exists")))
    checks.append(("plan", not plan_path.exists(), "plan " + ("missing" if not plan_path.exists() else "exists")))
    checks.append(("requirements", latest_srs is None, "SRS " + (f"{latest_srs.name}" if latest_srs else "not found")))
    checks.append(("design", latest_design is None, "design " + (f"{latest_design.name}" if latest_design else "not found")))
    checks.append(("design-eng-review", latest_design is not None and not (state_root / "plan-eng-review.md").exists(), "plan-eng-review " + ("missing" if latest_design is not None and not (state_root / "plan-eng-review.md").exists() else "exists")))
    checks.append(("design-design-review", latest_design is not None and not (state_root / "plan-design-review.md").exists(), "plan-design-review " + ("missing" if latest_design is not None and not (state_root / "plan-design-review.md").exists() else "exists")))
    checks.append(("quick-design", quick_config_path.exists() and not quick_design_path.exists(), "quick-design " + ("missing" if quick_config_path.exists() and not quick_design_path.exists() else "exists")))
    checks.append(("build-init", not feature_list_path.exists(), "feature-list " + ("missing" if not feature_list_path.exists() else "exists")))
    checks.append(("build-config", not work_config_path.exists(), "work-config " + ("missing" if not work_config_path.exists() else "exists")))
    checks.append(("build-work", not all_features_passing(feature_list_path), "features " + ("not passing" if not all_features_passing(feature_list_path) else "all passing")))
    checks.append(("review", not review_report_path.exists(), "review-report " + ("missing" if not review_report_path.exists() else "exists")))
    checks.append(("test-system", latest_st is None, "ST " + (f"{latest_st.name}" if latest_st else "not found")))
    checks.append(("test-qa", _ui_req and not qa_report_path.exists(), f'UI={_ui_req}, QA={"missing" if not qa_report_path.exists() else "exists"}'))
    checks.append(("ship", _ship_req and not (project_root / "RELEASE_NOTES.md").exists(), "RELEASE_NOTES " + ("missing" if not (project_root / "RELEASE_NOTES.md").exists() else "exists") + " (required=" + str(_ship_req) + ")"))
    checks.append(("reflect", _reflect_req and latest_retro is None, "retro " + (f"{latest_retro.name}" if latest_retro else "not found") + " (required=" + str(_reflect_req) + ")"))

    phase = "done"
    reason = "All detectable phases completed."

    if quick_config_path.exists() and not quick_design_path.exists():
        phase, reason = "quick", "docs/quick-design.md is missing."
    elif quick_config_path.exists() and quick_design_path.exists() and not feature_list_path.exists():
        phase, reason = "build-work", "Quick mode: quick-design complete, proceeding to build."
    elif increment_path.exists():
        phase, reason = "increment", ".vibeflow/increment-request.json exists."
    elif not think_path.exists():
        phase, reason = "think", ".vibeflow/think-output.md is missing."
    elif not workflow_path_obj.exists():
        phase, reason = "template-selection", ".vibeflow/workflow.yaml (or .yml) is missing."
    elif not plan_path.exists():
        phase, reason = "plan", ".vibeflow/plan.md is missing."
    elif latest_srs is None:
        phase, reason = "requirements", "No SRS document found in docs/plans."
    elif latest_design is None:
        phase, reason = "design", "No design document found in docs/plans."
    elif not (state_root / "plan-eng-review.md").exists():
        phase, reason = "design", ".vibeflow/plan-eng-review.md is missing."
    elif not (state_root / "plan-design-review.md").exists():
        phase, reason = "design", ".vibeflow/plan-design-review.md is missing."
    elif not feature_list_path.exists():
        phase, reason = "build-init", "feature-list.json is missing."
    elif not work_config_path.exists():
        phase, reason = "build-config", ".vibeflow/work-config.json is missing."
    elif not all_features_passing(feature_list_path):
        phase, reason = "build-work", "Some active features are not passing."
    elif not review_report_path.exists():
        phase, reason = "review", ".vibeflow/review-report.md is missing."
    elif latest_st is None:
        phase, reason = "test-system", "System test report is missing."
    elif _ui_req and not qa_report_path.exists():
        phase, reason = "test-qa", "UI workflow requires .vibeflow/qa-report.md."
    elif _ship_req and not (project_root / "RELEASE_NOTES.md").exists():
        phase, reason = "ship", "RELEASE_NOTES.md is missing."
    elif _reflect_req and latest_retro is None:
        phase, reason = "reflect", "No retrospective file exists."

    result = {
        "phase": phase,
        "reason": reason,
        "has_ui": _ui_req,
        "ship_required": _ship_req,
        "reflect_required": _reflect_req,
        "is_quick_mode": quick_config_path.exists(),
        "paths": {
            "think": str(think_path),
            "workflow": str(workflow_path_obj),
            "plan": str(plan_path),
            "work_config": str(work_config_path),
            "review": str(review_report_path),
            "feature_list": str(feature_list_path),
            "qa_report": str(qa_report_path),
            "latest_srs": str(latest_srs) if latest_srs else None,
            "latest_design": str(latest_design) if latest_design else None,
            "latest_st": str(latest_st) if latest_st else None,
            "latest_retro": str(latest_retro) if latest_retro else None,
            "quick_design": str(quick_design_path),
        },
    }
    if verbose:
        result["checks"] = [{"condition": c[0], "triggered": c[1], "detail": c[2]} for c in checks]
    return result


def state_based_detect_phase(project_root: Path, verbose: bool = False) -> dict:
    state = load_state(project_root)
    contract = path_contract(project_root, state)
    workflow_path_obj = contract["workflow"]
    feature_list = contract["feature_list"]
    work_config = contract["work_config"]
    packets_dir = contract["packets_dir"]
    release_notes = contract["release_notes"]
    artifacts = contract["artifacts"]
    state_root = project_root / ".vibeflow"
    retro_logs = project_root / ".vibeflow" / "logs"
    latest_retro = latest_matching_file(retro_logs, "retro-*.md") or latest_matching_file(state_root, "retro-*.md")
    _ui_req = ui_required(workflow_path_obj)
    _ship_req = ship_required(workflow_path_obj)
    _reflect_req = reflect_required(workflow_path_obj)
    is_quick_mode = state.get("mode") == "quick"
    pending_increment = increment_pending(project_root)
    quick_issues = quick_readiness_issues(project_root, state) if is_quick_mode else []
    quick_state_meta = quick_meta(state) if is_quick_mode else {}
    build_init_ready = feature_list.exists() and has_active_features(feature_list) and (
        checkpoint_done(state, "build_init")
        or build_packets_ready(feature_list, packets_dir)
        or work_config.exists()
    )

    checks = []
    checks.append(
        (
            "quick",
            is_quick_mode and bool(quick_issues),
            f"mode={state.get('mode')}, quick_issues={'; '.join(quick_issues) if quick_issues else 'none'}",
        )
    )
    checks.append(("increment", pending_increment, "increment queue " + ("pending" if pending_increment else "empty")))
    checks.append(("think", not checkpoint_done(state, "think") or not artifacts["think"].exists(), f'checkpoint={checkpoint_done(state, "think")}, artifact={"exists" if artifacts["think"].exists() else "missing"}'))
    checks.append(("template-selection", not workflow_path_obj.exists(), "workflow " + ("missing" if not workflow_path_obj.exists() else "exists")))
    checks.append(("plan", not checkpoint_done(state, "plan") or not artifacts["plan"].exists(), f'checkpoint={checkpoint_done(state, "plan")}, artifact={"exists" if artifacts["plan"].exists() else "missing"}'))
    checks.append(("requirements", not checkpoint_done(state, "requirements") or not artifacts["requirements"].exists(), f'checkpoint={checkpoint_done(state, "requirements")}, artifact={"exists" if artifacts["requirements"].exists() else "missing"}'))
    checks.append(("design", (not checkpoint_done(state, "design")) or (not artifacts["design"].exists()) or (not artifacts["design_review"].exists()), f'design={checkpoint_done(state, "design")}, design_doc={"exists" if artifacts["design"].exists() else "missing"}, design_review={"exists" if artifacts["design_review"].exists() else "missing"}'))
    checks.append(
        (
            "build-init",
            not build_init_ready,
            "build-init "
            + (
                "ready"
                if build_init_ready
                else "feature-list, work-config, or implementation packets are missing/incomplete"
            ),
        )
    )
    checks.append(("build-config", not work_config.exists(), "work-config " + ("missing" if not work_config.exists() else "exists")))
    checks.append(("build-work", not all_features_passing(feature_list), "features " + ("not passing" if not all_features_passing(feature_list) else "all passing")))
    checks.append(("review", not checkpoint_done(state, "review") or not artifacts["review"].exists(), f'review={checkpoint_done(state, "review")}, artifact={"exists" if artifacts["review"].exists() else "missing"}'))
    checks.append(("test-system", not checkpoint_done(state, "test_system") or not artifacts["system_test"].exists(), f'test_system={checkpoint_done(state, "test_system")}, artifact={"exists" if artifacts["system_test"].exists() else "missing"}'))
    checks.append(("test-qa", _ui_req and (not checkpoint_done(state, "test_qa") or not artifacts["qa"].exists()), f'UI={_ui_req}, test_qa={checkpoint_done(state, "test_qa")}, artifact={"exists" if artifacts["qa"].exists() else "missing"}'))
    checks.append(("ship", _ship_req and (not checkpoint_done(state, "ship") or not release_notes.exists()), f'ship={checkpoint_done(state, "ship")}, release_notes={"exists" if release_notes.exists() else "missing"}'))
    checks.append(("reflect", _reflect_req and (not checkpoint_done(state, "reflect") or latest_retro is None), f'reflect={checkpoint_done(state, "reflect")}, retro={"exists" if latest_retro else "missing"}'))

    phase = "done"
    reason = "All detectable phases completed."

    if is_quick_mode and quick_issues:
        phase = "quick"
        promote_hint = ""
        if quick_state_meta.get("decision") in {"rejected", "promoted"} or any("Full Mode" in issue for issue in quick_issues):
            promote_hint = " Run scripts/promote-vibeflow-quick.py to switch back to the Full Mode flow."
        reason = f"Quick mode is not ready: {' '.join(quick_issues)}{promote_hint}".strip()
    elif pending_increment:
        phase, reason = "increment", "Increment queue has pending items."
    elif is_quick_mode:
        if not feature_list.exists():
            phase, reason = "build-work", "Quick mode is ready and should proceed directly into build."
        elif not all_features_passing(feature_list):
            phase, reason = "build-work", "Quick mode has unfinished features."
        elif not checkpoint_done(state, "review") or not artifacts["review"].exists():
            phase, reason = "review", "Global review artifact is missing or not approved."
        elif not checkpoint_done(state, "test_system") or not artifacts["system_test"].exists():
            phase, reason = "test-system", "System test artifact is missing or not approved."
        elif _ui_req and (not checkpoint_done(state, "test_qa") or not artifacts["qa"].exists()):
            phase, reason = "test-qa", "UI workflow requires QA artifact."
        elif _ship_req and (not checkpoint_done(state, "ship") or not release_notes.exists()):
            phase, reason = "ship", "Ship is required and release notes are missing."
        elif _reflect_req and (not checkpoint_done(state, "reflect") or latest_retro is None):
            phase, reason = "reflect", "Reflect is required and no retrospective exists."
    elif not checkpoint_done(state, "think") or not artifacts["think"].exists():
        phase, reason = "think", "Think artifact is missing or not approved."
    elif not workflow_path_obj.exists():
        phase, reason = "template-selection", "Workflow file is missing."
    elif not checkpoint_done(state, "plan") or not artifacts["plan"].exists():
        phase, reason = "plan", "Plan artifact is missing or not approved."
    elif not checkpoint_done(state, "requirements") or not artifacts["requirements"].exists():
        phase, reason = "requirements", "Requirements artifact is missing or not approved."
    elif not checkpoint_done(state, "design") or not artifacts["design"].exists() or not artifacts["design_review"].exists():
        phase, reason = "design", "Design or design review artifact is missing or not approved."
    elif not build_init_ready:
        phase, reason = "build-init", "feature-list.json is missing, empty, or no build-init readiness signal exists."
    elif not work_config.exists():
        phase, reason = "build-config", ".vibeflow/work-config.json is missing."
    elif not all_features_passing(feature_list):
        phase, reason = "build-work", "Some active features are not passing."
    elif not checkpoint_done(state, "review") or not artifacts["review"].exists():
        phase, reason = "review", "Global review artifact is missing or not approved."
    elif not checkpoint_done(state, "test_system") or not artifacts["system_test"].exists():
        phase, reason = "test-system", "System test artifact is missing or not approved."
    elif _ui_req and (not checkpoint_done(state, "test_qa") or not artifacts["qa"].exists()):
        phase, reason = "test-qa", "UI workflow requires QA artifact."
    elif _ship_req and (not checkpoint_done(state, "ship") or not release_notes.exists()):
        phase, reason = "ship", "Ship is required and release notes are missing."
    elif _reflect_req and (not checkpoint_done(state, "reflect") or latest_retro is None):
        phase, reason = "reflect", "Reflect is required and no retrospective exists."

    result = {
        "phase": phase,
        "reason": reason,
        "has_ui": _ui_req,
        "ship_required": _ship_req,
        "reflect_required": _reflect_req,
        "is_quick_mode": is_quick_mode,
        "paths": {
            "state": str(state_path(project_root)),
            "workflow": str(workflow_path_obj),
            "work_config": str(work_config),
            "feature_list": str(feature_list),
            "release_notes": str(release_notes),
            "change_root": str(contract["change_root"]),
            "phase_history": str(contract["phase_history"]),
            "session_log": str(contract["session_log"]),
            "think": str(artifacts["think"]),
            "plan": str(artifacts["plan"]),
            "requirements": str(artifacts["requirements"]),
            "ucd": str(artifacts["ucd"]),
            "design": str(artifacts["design"]),
            "design_review": str(artifacts["design_review"]),
            "review": str(artifacts["review"]),
            "system_test": str(artifacts["system_test"]),
            "qa": str(artifacts["qa"]),
            "latest_retro": str(latest_retro) if latest_retro else None,
        },
    }
    if verbose:
        result["checks"] = [{"condition": c[0], "triggered": c[1], "detail": c[2]} for c in checks]
    return result


def detect_phase(project_root: Path, verbose: bool = False) -> dict:
    if state_path(project_root).exists():
        return state_based_detect_phase(project_root, verbose=verbose)
    return legacy_detect_phase(project_root, verbose=verbose)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    result = detect_phase(Path(args.project_root).resolve(), verbose=args.verbose)
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
