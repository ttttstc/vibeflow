#!/usr/bin/env python3
"""
VibeFlow Increment Handler.

Supports both:
- legacy increment layout under .vibeflow/
- v2 increment layout under .vibeflow/increments/

The handler keeps feature-list.json as the build source of truth, but routes all
newly written increment metadata to the v2 layout.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from vibeflow_paths import (  # noqa: E402
    append_phase_history,
    ensure_state,
    increment_history_path,
    increment_queue_path,
    increment_requests_dir,
    load_state,
    path_contract,
    save_state,
    set_checkpoint,
    state_path,
)


FEATURE_LIST_FILE = "feature-list.json"
LEGACY_QUEUE_FILE = ".vibeflow/increment-queue.txt"
LEGACY_ROOT_REQUEST = ".vibeflow/increment-request.json"
LEGACY_REQUEST_PATTERNS = [
    ".vibeflow/increment-request-{id}.json",
    ".vibeflow/increment-{id}.json",
    ".vibeflow/increment_request_{id}.json",
]
CHECKPOINT_ORDER = [
    "think",
    "plan",
    "requirements",
    "design",
    "build_init",
    "build_config",
    "build_work",
    "review",
    "test_system",
    "test_qa",
    "ship",
    "reflect",
]


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def normalize_queue_item(item, fallback_id: str | None = None) -> dict:
    if isinstance(item, str):
        return {"id": item}
    if isinstance(item, dict):
        normalized = dict(item)
        if "id" not in normalized:
            normalized["id"] = fallback_id or f"increment-{datetime.now().strftime('%H%M%S')}"
        return normalized
    return {"id": fallback_id or f"increment-{datetime.now().strftime('%H%M%S')}"}


def read_queue(project_root: Path) -> list[dict]:
    queue_path = increment_queue_path(project_root)
    if queue_path.exists():
        payload = load_json(queue_path, {"items": []})
        if isinstance(payload, dict):
            items = payload.get("items", [])
        elif isinstance(payload, list):
            items = payload
        else:
            items = []
        return [normalize_queue_item(item) for item in items]

    legacy_queue = project_root / LEGACY_QUEUE_FILE
    if legacy_queue.exists():
        items = []
        for line in legacy_queue.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                items.append({"id": line})
        return items

    legacy_root_request = project_root / LEGACY_ROOT_REQUEST
    if legacy_root_request.exists():
        return [{"id": "legacy-root"}]

    return []


def write_queue(project_root: Path, items: list[dict]) -> None:
    normalized = [normalize_queue_item(item) for item in items]
    save_json(increment_queue_path(project_root), {"items": normalized})


def load_increment_request(project_root: Path, item: dict) -> tuple[str, dict]:
    inc_id = item.get("id", "unknown")
    requests_dir = increment_requests_dir(project_root)
    request_path = requests_dir / f"{inc_id}.json"
    if request_path.exists():
        data = load_json(request_path, {})
        if isinstance(data, dict):
            data.setdefault("id", inc_id)
            return inc_id, data

    if inc_id == "legacy-root":
        legacy_root = project_root / LEGACY_ROOT_REQUEST
        if legacy_root.exists():
            data = load_json(legacy_root, {})
            if isinstance(data, dict):
                data.setdefault("id", inc_id)
                return inc_id, data

    for pattern in LEGACY_REQUEST_PATTERNS:
        candidate = project_root / pattern.format(id=inc_id)
        if candidate.exists():
            data = load_json(candidate, {})
            if isinstance(data, dict):
                data.setdefault("id", inc_id)
                return inc_id, data

    if "request" in item and isinstance(item["request"], dict):
        data = dict(item["request"])
        data.setdefault("id", inc_id)
        return inc_id, data

    raise FileNotFoundError(f"Increment request file not found for id: {inc_id}")


def load_feature_list(project_root: Path) -> dict:
    path = project_root / FEATURE_LIST_FILE
    if not path.exists():
        raise FileNotFoundError(f"feature-list.json not found at {path}")
    return load_json(path, {})


def save_feature_list(project_root: Path, data: dict) -> None:
    save_json(project_root / FEATURE_LIST_FILE, data)


def next_feature_id(fl: dict) -> int:
    return max([feat.get("id", 0) for feat in fl.get("features", [])], default=0) + 1


def mark_feature_for_rework(feature: dict) -> None:
    if not feature.get("deprecated"):
        feature["status"] = "failing"


def process_add_feature(inc: dict, fl: dict) -> str:
    new_id = inc.get("feature_id") or next_feature_id(fl)
    new_feature = {
        "id": new_id,
        "title": inc.get("title", f"New feature {new_id}"),
        "description": inc.get("description", ""),
        "priority": inc.get("priority", "medium"),
        "status": inc.get("status", "failing"),
        "dependencies": inc.get("dependencies", []),
        "verification_steps": inc.get("verification_steps", []),
    }
    for optional_key in ("ui", "wave", "st_case_path", "owner", "tags"):
        if optional_key in inc:
            new_feature[optional_key] = inc[optional_key]
    fl.setdefault("features", []).append(new_feature)
    return f"Added feature #{new_id}: {new_feature['title']}"


def process_modify_feature(inc: dict, fl: dict) -> str:
    target_id = inc.get("feature_id")
    for feat in fl.get("features", []):
        if feat.get("id") == target_id:
            for key in [
                "title",
                "description",
                "priority",
                "dependencies",
                "verification_steps",
                "ui",
                "wave",
                "st_case_path",
                "owner",
                "tags",
            ]:
                if key in inc:
                    feat[key] = inc[key]
            mark_feature_for_rework(feat)
            return f"Modified feature #{target_id}"
    return f"WARNING: feature #{target_id} not found, nothing modified"


def process_deprecate_feature(inc: dict, fl: dict) -> str:
    target_id = inc.get("feature_id")
    for feat in fl.get("features", []):
        if feat.get("id") == target_id:
            feat["deprecated"] = True
            feat["deprecated_reason"] = inc.get("reason", "superseded by increment")
            return f"Deprecated feature #{target_id}"
    return f"WARNING: feature #{target_id} not found"


def latest_matching_file(base: Path, pattern: str) -> Path | None:
    if not base.exists():
        return None
    matches = sorted(base.glob(pattern), key=lambda item: item.stat().st_mtime, reverse=True)
    return matches[0] if matches else None


def resolve_doc_target(project_root: Path, doc_type: str) -> Path | None:
    normalized = doc_type.lower()

    if state_path(project_root).exists():
        state = load_state(project_root)
        contract = path_contract(project_root, state)
        artifact_map = {
            "proposal": contract["artifacts"]["plan"],
            "plan": contract["artifacts"]["plan"],
            "requirements": contract["artifacts"]["requirements"],
            "srs": contract["artifacts"]["requirements"],
            "ucd": contract["artifacts"]["ucd"],
            "design": contract["artifacts"]["design"],
            "design_review": contract["artifacts"]["design_review"],
            "tasks": contract["artifacts"]["tasks"],
            "review": contract["artifacts"]["review"],
            "system_test": contract["artifacts"]["system_test"],
            "st": contract["artifacts"]["system_test"],
            "qa": contract["artifacts"]["qa"],
        }
        if normalized in artifact_map:
            return artifact_map[normalized]

    plans_dir = project_root / "docs" / "plans"
    legacy_patterns = {
        "requirements": "*-srs.md",
        "srs": "*-srs.md",
        "design": "*-design.md",
        "ucd": "*-ucd.md",
        "st": "*-st-report.md",
        "system_test": "*-st-report.md",
    }
    pattern = legacy_patterns.get(normalized)
    if pattern:
        return latest_matching_file(plans_dir, pattern)
    return None


def process_update_doc(inc: dict, project_root: Path) -> str:
    doc_type = inc.get("doc_type", "")
    target = resolve_doc_target(project_root, doc_type)
    if target is None:
        return f"Unknown doc_type: {doc_type}"

    target.parent.mkdir(parents=True, exist_ok=True)
    original_content = target.read_text(encoding="utf-8") if target.exists() else f"# {doc_type.upper()}\n"
    patch = inc.get("patch") or inc.get("content") or inc.get("description") or ""
    title = inc.get("title") or inc.get("reason") or "Increment update"
    stamp = datetime.now().strftime("%Y-%m-%d")
    new_content = (
        f"{original_content.rstrip()}\n\n"
        f"## Increment Update ({stamp})\n\n"
        f"### {title}\n\n"
        f"{patch.strip()}\n"
    )
    target.write_text(new_content, encoding="utf-8")
    return f"Updated {target}"


def append_increment_history(project_root: Path, entry: dict) -> None:
    history_path = increment_history_path(project_root)
    history = load_json(history_path, [])
    history.append(entry)
    save_json(history_path, history)
    append_phase_history(project_root, entry)


def reset_downstream_checkpoints(state: dict, start_key: str) -> None:
    if start_key not in CHECKPOINT_ORDER:
        return
    start = CHECKPOINT_ORDER.index(start_key)
    for key in CHECKPOINT_ORDER[start:]:
        set_checkpoint(state, key, False)


def update_state_after_increment(project_root: Path, inc: dict, result: str) -> None:
    if not state_path(project_root).exists():
        return

    state = load_state(project_root)
    inc_type = inc.get("type")
    doc_type = str(inc.get("doc_type", "")).lower()
    next_phase = state.get("current_phase", "increment")

    if inc_type in {"add_feature", "modify_feature", "deprecate_feature"}:
        reset_downstream_checkpoints(state, "build_work")
        next_phase = "build-work"
    elif inc_type == "update_doc":
        if doc_type in {"proposal", "plan"}:
            reset_downstream_checkpoints(state, "plan")
            next_phase = "plan"
        elif doc_type in {"requirements", "srs"}:
            reset_downstream_checkpoints(state, "requirements")
            next_phase = "requirements"
        elif doc_type in {"design", "ucd", "design_review"}:
            reset_downstream_checkpoints(state, "design")
            next_phase = "design"
        elif doc_type in {"review"}:
            reset_downstream_checkpoints(state, "review")
            next_phase = "review"
        elif doc_type in {"system_test", "st"}:
            reset_downstream_checkpoints(state, "test_system")
            next_phase = "test-system"
        elif doc_type in {"qa"}:
            reset_downstream_checkpoints(state, "test_qa")
            next_phase = "test-qa"

    state["current_phase"] = next_phase
    save_state(project_root, state)


def record_increment(project_root: Path, inc_id: str, inc: dict, result: str) -> None:
    entry = {
        "timestamp": datetime.now().isoformat(),
        "increment_id": inc_id,
        "type": inc.get("type"),
        "scope": inc.get("scope"),
        "reason": inc.get("reason"),
        "result": result,
    }
    append_increment_history(project_root, entry)


def process_increment(project_root: Path, item: dict, dry_run: bool = False) -> tuple[bool, str]:
    try:
        inc_id, inc = load_increment_request(project_root, item)
    except FileNotFoundError as exc:
        return False, str(exc)

    inc_type = inc.get("type")
    fl = None
    if inc_type in {"add_feature", "modify_feature", "deprecate_feature"}:
        try:
            fl = load_feature_list(project_root)
        except FileNotFoundError:
            return False, "feature-list.json not found"

    if dry_run:
        if inc_type in {"add_feature", "modify_feature", "deprecate_feature", "update_doc"}:
            return True, f"[dry-run] Would process {inc_type}"
        return True, f"[dry-run] Unknown increment type: {inc_type}"

    if inc_type == "add_feature":
        result = process_add_feature(inc, fl)
    elif inc_type == "modify_feature":
        result = process_modify_feature(inc, fl)
    elif inc_type == "deprecate_feature":
        result = process_deprecate_feature(inc, fl)
    elif inc_type == "update_doc":
        result = process_update_doc(inc, project_root)
    else:
        return False, f"Unknown increment type: {inc_type}"

    if fl is not None:
        save_feature_list(project_root, fl)

    update_state_after_increment(project_root, inc, result)
    record_increment(project_root, inc_id, inc, result)
    return True, result


def migrate_legacy_queue_if_needed(project_root: Path) -> None:
    queue_path = increment_queue_path(project_root)
    if queue_path.exists():
        return
    legacy_queue = project_root / LEGACY_QUEUE_FILE
    if not legacy_queue.exists():
        return
    items = read_queue(project_root)
    write_queue(project_root, items)


def main():
    parser = argparse.ArgumentParser(description="VibeFlow Increment Handler")
    parser.add_argument("--project-root", default=".", help="Path to project root (default: current directory)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    ensure_state(project_root)
    migrate_legacy_queue_if_needed(project_root)

    queue_items = read_queue(project_root)
    if not queue_items:
        print("Increment queue is empty — nothing to process.")
        sys.exit(0)

    if args.dry_run:
        print(f"[dry-run] Would process {len(queue_items)} increment(s) — no changes will be made")

    processed_ids = []
    failed = []

    for item in queue_items:
        inc_id = normalize_queue_item(item).get("id", "unknown")
        print(f"\n[{inc_id}] {'[dry-run] would process' if args.dry_run else 'Processing'}...")
        success, message = process_increment(project_root, item, dry_run=args.dry_run)
        print(f"  -> {message}")
        if success:
            processed_ids.append(inc_id)
        else:
            failed.append((inc_id, message))

    if args.dry_run:
        remaining = queue_items
    else:
        remaining = [item for item in queue_items if normalize_queue_item(item).get("id") not in processed_ids]
        write_queue(project_root, remaining)

    print(f"\nDone: {len(processed_ids)} succeeded, {len(failed)} failed.")
    if args.dry_run:
        print("[dry-run] Queue unchanged.")
    if failed:
        print("\nFailed:")
        for inc_id, message in failed:
            print(f"  [{inc_id}] {message}")
        sys.exit(1)

    print("All increments processed successfully." if not args.dry_run else "Dry-run complete.")
    sys.exit(0)


if __name__ == "__main__":
    main()
