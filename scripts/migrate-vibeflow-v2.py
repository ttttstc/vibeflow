#!/usr/bin/env python3
"""
Migrate a legacy VibeFlow project to the v2 state/artifact layout.

The migration is intentionally non-destructive:
- copies legacy artifacts into docs/changes/<change-id>/
- creates .vibeflow/state.json and v2 increment files
- leaves legacy files in place for manual comparison
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from vibeflow_paths import (  # noqa: E402
    default_change_id,
    increment_history_path,
    increment_queue_path,
    increment_requests_dir,
    load_state,
    mark_quick_approved,
    save_state,
    session_log_path,
    set_checkpoint,
    state_path,
    update_active_change,
)


def latest_matching_file(base: Path, pattern: str) -> Path | None:
    if not base.exists():
        return None
    matches = sorted(base.glob(pattern), key=lambda item: item.stat().st_mtime, reverse=True)
    return matches[0] if matches else None


def derive_change_id(project_root: Path, explicit: str | None) -> str:
    if explicit:
        return explicit
    plans_dir = project_root / "docs" / "plans"
    for pattern, suffix in [("*-srs.md", "-srs"), ("*-design.md", "-design"), ("*-ucd.md", "-ucd")]:
        latest = latest_matching_file(plans_dir, pattern)
        if latest:
            stem = latest.stem
            if stem.endswith(suffix):
                stem = stem[: -len(suffix)]
            return stem
    return default_change_id(project_root.name)


def copy_if_exists(src: Path | None, dst: Path, force: bool = False) -> bool:
    if src is None or not src.exists():
        return False
    if dst.exists() and not force:
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def write_combined_file(dst: Path, sections: list[tuple[str, Path | None]], force: bool = False) -> bool:
    available = [(title, src) for title, src in sections if src is not None and src.exists()]
    if not available:
        return False
    if dst.exists() and not force:
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    content_parts = []
    for title, src in available:
        content = src.read_text(encoding="utf-8").strip()
        content_parts.append(f"## {title}\n\n{content}")
    dst.write_text("\n\n".join(content_parts) + "\n", encoding="utf-8")
    return True


def write_text_if_missing(dst: Path, content: str, force: bool = False) -> bool:
    if dst.exists() and not force:
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(content, encoding="utf-8")
    return True


def all_features_passing(feature_list_path: Path) -> bool:
    if not feature_list_path.exists():
        return False
    data = json.loads(feature_list_path.read_text(encoding="utf-8"))
    features = [feat for feat in data.get("features", []) if not feat.get("deprecated")]
    return bool(features) and all(feat.get("status") == "passing" for feat in features)


def migrate_increment_requests(project_root: Path, force: bool = False) -> tuple[int, int]:
    requests_dir = increment_requests_dir(project_root)
    requests_dir.mkdir(parents=True, exist_ok=True)
    migrated = 0
    skipped = 0

    legacy_root = project_root / ".vibeflow" / "increment-request.json"
    if legacy_root.exists():
        target = requests_dir / "legacy-root.json"
        if copy_if_exists(legacy_root, target, force=force):
            migrated += 1
        else:
            skipped += 1

    for candidate in (project_root / ".vibeflow").glob("increment*.json"):
        if candidate.name == "increment-request.json":
            continue
        match = re.search(r"(increment[-_]?request[-_]?|increment[-_]?)(.+)\.json$", candidate.name)
        inc_id = match.group(2).strip("-_") if match else candidate.stem
        target = requests_dir / f"{inc_id}.json"
        if copy_if_exists(candidate, target, force=force):
            migrated += 1
        else:
            skipped += 1

    legacy_queue = project_root / ".vibeflow" / "increment-queue.txt"
    if legacy_queue.exists() and (force or not increment_queue_path(project_root).exists()):
        items = []
        for line in legacy_queue.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                items.append({"id": line})
        increment_queue_path(project_root).parent.mkdir(parents=True, exist_ok=True)
        increment_queue_path(project_root).write_text(
            json.dumps({"items": items}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    history_target = increment_history_path(project_root)
    legacy_phase_history = project_root / ".vibeflow" / "phase-history.json"
    if (force or not history_target.exists()) and legacy_phase_history.exists():
        phase_history = json.loads(legacy_phase_history.read_text(encoding="utf-8"))
        increment_entries = [entry for entry in phase_history if isinstance(entry, dict) and entry.get("increment_id")]
        history_target.parent.mkdir(parents=True, exist_ok=True)
        history_target.write_text(json.dumps(increment_entries, indent=2, ensure_ascii=False), encoding="utf-8")

    return migrated, skipped


def main():
    parser = argparse.ArgumentParser(description="Migrate a legacy VibeFlow project to v2")
    parser.add_argument("--project-root", default=".", help="Path to the project root")
    parser.add_argument("--change-id", default=None, help="Override generated change id")
    parser.add_argument("--force", action="store_true", help="Overwrite existing migrated files")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    vibeflow_dir = project_root / ".vibeflow"
    vibeflow_dir.mkdir(parents=True, exist_ok=True)

    existing_state = load_state(project_root) if state_path(project_root).exists() else load_state(project_root)
    change_id = derive_change_id(project_root, args.change_id)
    update_active_change(existing_state, change_id)
    change_root = project_root / existing_state["active_change"]["root"]
    verification_dir = change_root / "verification"
    verification_dir.mkdir(parents=True, exist_ok=True)

    migrated = []

    think_src = vibeflow_dir / "think-output.md"
    if copy_if_exists(think_src, change_root / "context.md", force=args.force):
        migrated.append(("think", change_root / "context.md"))

    if write_combined_file(
        change_root / "proposal.md",
        [
            ("Plan", vibeflow_dir / "plan.md"),
            ("Value Review", vibeflow_dir / "plan-value-review.md"),
        ],
        force=args.force,
    ):
        migrated.append(("plan", change_root / "proposal.md"))

    plans_dir = project_root / "docs" / "plans"
    requirements_src = latest_matching_file(plans_dir, "*-srs.md")
    if copy_if_exists(requirements_src, change_root / "requirements.md", force=args.force):
        migrated.append(("requirements", change_root / "requirements.md"))

    ucd_src = latest_matching_file(plans_dir, "*-ucd.md")
    if copy_if_exists(ucd_src, change_root / "ucd.md", force=args.force):
        migrated.append(("ucd", change_root / "ucd.md"))

    design_src = latest_matching_file(plans_dir, "*-design.md")
    quick_design_src = project_root / "docs" / "quick-design.md"
    if design_src and copy_if_exists(design_src, change_root / "design.md", force=args.force):
        migrated.append(("design", change_root / "design.md"))
    elif quick_design_src.exists() and copy_if_exists(quick_design_src, change_root / "design.md", force=args.force):
        migrated.append(("design", change_root / "design.md"))
        existing_state["mode"] = "quick"
        existing_state["checkpoints"]["quick_ready"] = True
        mark_quick_approved(
            existing_state,
            category="small-change",
            scope="Migrated from legacy Quick Mode artifact.",
            touchpoints=["legacy-quick-mode"],
            validation_plan="Re-run the original targeted quick checks after migration.",
            rollback_plan="Restore the legacy quick artifact or revert the migrated quick change.",
        )
        tasks_target = change_root / "tasks.md"
        if write_text_if_missing(
            tasks_target,
            "# Tasks\n\n- Reconfirm the migrated quick scope.\n- Implement or continue the bounded quick change.\n- Run the targeted quick validation plan.\n- Ship or promote to Full Mode if scope expands.\n",
            force=args.force,
        ):
            migrated.append(("tasks", tasks_target))

    if write_combined_file(
        change_root / "design-review.md",
        [
            ("Engineering Review", vibeflow_dir / "plan-eng-review.md"),
            ("Design Review", vibeflow_dir / "plan-design-review.md"),
        ],
        force=args.force,
    ):
        migrated.append(("design_review", change_root / "design-review.md"))

    review_src = vibeflow_dir / "review-report.md"
    if copy_if_exists(review_src, verification_dir / "review.md", force=args.force):
        migrated.append(("review", verification_dir / "review.md"))

    st_src = latest_matching_file(plans_dir, "*-st-report.md")
    if copy_if_exists(st_src, verification_dir / "system-test.md", force=args.force):
        migrated.append(("system_test", verification_dir / "system-test.md"))

    qa_src = vibeflow_dir / "qa-report.md"
    if copy_if_exists(qa_src, verification_dir / "qa.md", force=args.force):
        migrated.append(("qa", verification_dir / "qa.md"))

    session_src = project_root / "task-progress.md"
    copy_if_exists(session_src, session_log_path(project_root), force=args.force)

    build_guide_src = project_root / "vibeflow-guide.md"
    if build_guide_src.exists():
        target = project_root / ".vibeflow" / "guides" / "build.md"
        copy_if_exists(build_guide_src, target, force=args.force)

    services_guide_src = project_root / "env-guide.md"
    if services_guide_src.exists():
        target = project_root / ".vibeflow" / "guides" / "services.md"
        copy_if_exists(services_guide_src, target, force=args.force)

    migrated_requests, skipped_requests = migrate_increment_requests(project_root, force=args.force)

    artifacts = existing_state["artifacts"]
    checkpoints = existing_state["checkpoints"]
    checkpoints["think"] = Path(project_root / artifacts["think"]).exists()
    checkpoints["plan"] = Path(project_root / artifacts["plan"]).exists()
    checkpoints["requirements"] = Path(project_root / artifacts["requirements"]).exists()
    checkpoints["design"] = Path(project_root / artifacts["design"]).exists() and Path(project_root / artifacts["design_review"]).exists()
    checkpoints["build_init"] = (project_root / "feature-list.json").exists()
    checkpoints["build_config"] = (project_root / ".vibeflow" / "work-config.json").exists()
    checkpoints["build_work"] = all_features_passing(project_root / "feature-list.json")
    checkpoints["review"] = Path(project_root / artifacts["review"]).exists()
    checkpoints["test_system"] = Path(project_root / artifacts["system_test"]).exists()
    checkpoints["test_qa"] = Path(project_root / artifacts["qa"]).exists()
    checkpoints["ship"] = (project_root / "RELEASE_NOTES.md").exists()
    latest_retro = latest_matching_file(vibeflow_dir, "retro-*.md") or latest_matching_file(vibeflow_dir / "logs", "retro-*.md")
    checkpoints["reflect"] = latest_retro is not None

    if checkpoints["reflect"]:
        existing_state["current_phase"] = "reflect"
    elif checkpoints["ship"]:
        existing_state["current_phase"] = "ship"
    elif checkpoints["test_qa"]:
        existing_state["current_phase"] = "test-qa"
    elif checkpoints["test_system"]:
        existing_state["current_phase"] = "test-system"
    elif checkpoints["review"]:
        existing_state["current_phase"] = "review"
    elif checkpoints["build_work"]:
        existing_state["current_phase"] = "build-work"
    elif checkpoints["build_config"]:
        existing_state["current_phase"] = "build-config"
    elif checkpoints["build_init"]:
        existing_state["current_phase"] = "build-init"
    elif checkpoints["design"]:
        existing_state["current_phase"] = "design"
    elif checkpoints["requirements"]:
        existing_state["current_phase"] = "requirements"
    elif checkpoints["plan"]:
        existing_state["current_phase"] = "plan"
    elif checkpoints["think"]:
        existing_state["current_phase"] = "think"

    save_state(project_root, existing_state)

    print(f"Migrated project: {project_root}")
    print(f"Active change: {change_id}")
    print(f"State file: {state_path(project_root)}")
    print(f"Migrated artifacts: {len(migrated)}")
    for label, path in migrated:
        print(f"  - {label}: {path}")
    print(f"Increment requests migrated: {migrated_requests}, skipped: {skipped_requests}")
    print("Legacy files were left in place for comparison.")


if __name__ == "__main__":
    main()
