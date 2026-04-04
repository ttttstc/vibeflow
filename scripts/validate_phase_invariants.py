#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from vibeflow_paths import checkpoint_done, load_policy, load_state, path_contract  # noqa: E402


PHASE_LABELS = {
    "spark": "Spark",
    "design": "Design",
    "tasks": "Tasks",
    "build": "Build",
    "review": "Review",
    "test": "Test",
    "ship": "Ship",
}

ARTIFACT_LABELS = {
    "spark": "Spark artifact",
    "design": "Design artifact",
    "tasks": "Tasks artifact",
    "review": "Review artifact",
    "system_test": "System test artifact",
    "qa": "QA artifact",
    "feature_list": "feature-list.json",
    "release_notes": "RELEASE_NOTES.md",
}

CHECKPOINT_LABELS = {
    "spark": "spark checkpoint",
    "design": "design checkpoint",
    "tasks": "tasks checkpoint",
    "build": "build checkpoint",
    "review": "review checkpoint",
    "test": "test checkpoint",
    "ship": "ship checkpoint",
    "reflect": "reflect checkpoint",
}

BLOCKING_LABELS = {
    "pending_increment": "increment queue has pending items",
}

EVIDENCE_LABELS = {
    "active_features": "active features declared in feature-list.json",
    "release_notes_exists": "release notes file",
}


def _load_feature_payload(feature_list_path: Path) -> dict:
    if not feature_list_path.exists():
        return {}
    return json.loads(feature_list_path.read_text(encoding="utf-8"))


def has_active_features(feature_list_path: Path) -> bool:
    data = _load_feature_payload(feature_list_path)
    features = [feature for feature in data.get("features", []) if not feature.get("deprecated")]
    return bool(features)


def artifact_lookup(contract: dict) -> dict[str, Path]:
    lookup = dict(contract["artifacts"])
    lookup["feature_list"] = contract["feature_list"]
    lookup["release_notes"] = contract["release_notes"]
    return lookup


def evaluate_blocking_condition(condition: str, *, project_root: Path, state: dict, contract: dict) -> tuple[bool, str]:
    if condition == "pending_increment":
        queue_path = contract["increment_queue"]
        if queue_path.exists():
            try:
                data = json.loads(queue_path.read_text(encoding="utf-8"))
                if isinstance(data, dict) and data.get("items"):
                    return True, "increment queue still has pending items."
                if isinstance(data, list) and data:
                    return True, "increment queue still has pending items."
            except json.JSONDecodeError:
                return True, "increment queue exists but could not be parsed."
        legacy_increment = project_root / ".vibeflow" / "increment-request.json"
        if legacy_increment.exists():
            return True, "legacy increment request is still present."
        return False, "increment queue is empty."

    return False, f"unknown blocking condition '{condition}' is not active."


def evaluate_evidence(evidence: str, *, state: dict, contract: dict) -> tuple[bool, str]:
    if evidence.startswith("artifact:"):
        artifact_name = evidence.split(":", 1)[1]
        path = artifact_lookup(contract).get(artifact_name)
        exists = bool(path and path.exists())
        label = ARTIFACT_LABELS.get(artifact_name, artifact_name)
        return exists, f"{label} {'exists' if exists else 'is missing'}."

    if evidence.startswith("checkpoint:"):
        checkpoint_name = evidence.split(":", 1)[1]
        ok = checkpoint_done(state, checkpoint_name)
        label = CHECKPOINT_LABELS.get(checkpoint_name, checkpoint_name)
        return ok, f"{label} {'is approved' if ok else 'is not approved'}."

    if evidence == "active_features":
        ok = has_active_features(contract["feature_list"])
        return ok, "feature-list.json has active features." if ok else "feature-list.json has no active features."

    if evidence == "release_notes_exists":
        ok = contract["release_notes"].exists()
        return ok, "RELEASE_NOTES.md exists." if ok else "RELEASE_NOTES.md is missing."

    return False, f"unknown evidence '{evidence}' is not satisfied."


def _result_template(phase: str) -> dict:
    return {
        "phase": phase,
        "phase_label": PHASE_LABELS.get(phase, phase),
        "ok": True,
        "status": "clear",
        "reason_code": "",
        "blocking_item": "",
        "detail": "",
        "friendly_reason": "",
        "checks": [],
    }


def _failure(result: dict, *, reason_code: str, blocking_item: str, detail: str, friendly_reason: str) -> dict:
    result["ok"] = False
    result["status"] = "blocked"
    result["reason_code"] = reason_code
    result["blocking_item"] = blocking_item
    result["detail"] = detail
    result["friendly_reason"] = friendly_reason
    return result


def validate_phase(project_root: Path, phase: str, *, state: dict | None = None, contract: dict | None = None, policy: dict | None = None) -> dict:
    loaded_state = state or load_state(project_root)
    loaded_contract = contract or path_contract(project_root, loaded_state)
    loaded_policy = policy or load_policy(project_root)
    phase_policy = (loaded_policy.get("phases") or {}).get(phase) or {}
    result = _result_template(phase)
    lookup = artifact_lookup(loaded_contract)

    for condition in phase_policy.get("blocking_conditions", []):
        blocked, detail = evaluate_blocking_condition(
            condition,
            project_root=project_root,
            state=loaded_state,
            contract=loaded_contract,
        )
        result["checks"].append(
            {
                "category": "blocking_condition",
                "item": condition,
                "ok": not blocked,
                "detail": detail,
            }
        )
        if blocked:
            return _failure(
                result,
                reason_code="blocking_condition",
                blocking_item=condition,
                detail=detail,
                friendly_reason=f"{PHASE_LABELS.get(phase, phase)} is blocked because {detail}",
            )

    for artifact_name in phase_policy.get("required_artifacts", []):
        path = lookup.get(artifact_name)
        exists = bool(path and path.exists())
        label = ARTIFACT_LABELS.get(artifact_name, artifact_name)
        detail = f"{label} {'exists' if exists else 'is missing'}."
        result["checks"].append(
            {
                "category": "required_artifact",
                "item": artifact_name,
                "ok": exists,
                "detail": detail,
            }
        )
        if not exists:
            return _failure(
                result,
                reason_code="missing_artifact",
                blocking_item=artifact_name,
                detail=detail,
                friendly_reason=f"{PHASE_LABELS.get(phase, phase)} cannot continue because {label} is missing.",
            )

    for checkpoint_name in phase_policy.get("required_checkpoints", []):
        ok = checkpoint_done(loaded_state, checkpoint_name)
        label = CHECKPOINT_LABELS.get(checkpoint_name, checkpoint_name)
        detail = f"{label} {'is ready' if ok else 'is not ready'}."
        result["checks"].append(
            {
                "category": "required_checkpoint",
                "item": checkpoint_name,
                "ok": ok,
                "detail": detail,
            }
        )
        if not ok:
            return _failure(
                result,
                reason_code="missing_checkpoint",
                blocking_item=checkpoint_name,
                detail=detail,
                friendly_reason=f"{PHASE_LABELS.get(phase, phase)} is waiting for {label}.",
            )

    for approval_name in phase_policy.get("required_approvals", []):
        approved = checkpoint_done(loaded_state, approval_name)
        label = CHECKPOINT_LABELS.get(approval_name, approval_name)
        detail = f"{label} {'is approved' if approved else 'is not approved'}."
        result["checks"].append(
            {
                "category": "required_approval",
                "item": approval_name,
                "ok": approved,
                "detail": detail,
            }
        )
        if not approved:
            return _failure(
                result,
                reason_code="missing_approval",
                blocking_item=approval_name,
                detail=detail,
                friendly_reason=f"{PHASE_LABELS.get(phase, phase)} is waiting for {label}.",
            )

    for evidence_name in phase_policy.get("completion_evidence", []):
        ok, detail = evaluate_evidence(
            evidence_name,
            state=loaded_state,
            contract=loaded_contract,
        )
        result["checks"].append(
            {
                "category": "completion_evidence",
                "item": evidence_name,
                "ok": ok,
                "detail": detail,
            }
        )
        if not ok:
            label = EVIDENCE_LABELS.get(evidence_name, evidence_name)
            return _failure(
                result,
                reason_code="missing_completion_evidence",
                blocking_item=evidence_name,
                detail=detail,
                friendly_reason=f"{PHASE_LABELS.get(phase, phase)} is waiting for {label}.",
            )

    result["detail"] = f"{PHASE_LABELS.get(phase, phase)} invariants are satisfied."
    result["friendly_reason"] = result["detail"]
    return result


def validate_phase_invariants(project_root: Path, phase: str | None = None) -> dict:
    project_root = project_root.resolve()
    state = load_state(project_root)
    contract = path_contract(project_root, state)
    policy = load_policy(project_root)

    if phase:
        return validate_phase(project_root, phase, state=state, contract=contract, policy=policy)

    phases = []
    for phase_name in (policy.get("phases") or {}).keys():
        phases.append(validate_phase(project_root, phase_name, state=state, contract=contract, policy=policy))
    return {
        "ok": all(item["ok"] for item in phases),
        "phases": phases,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--phase")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    result = validate_phase_invariants(Path(args.project_root), phase=args.phase)
    if args.as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    if args.phase:
        print(result["friendly_reason"])
        return

    if result["ok"]:
        print("All configured phase invariants are satisfied.")
        return

    first_failed = next((item for item in result["phases"] if not item["ok"]), result["phases"][0])
    print(first_failed["friendly_reason"])


if __name__ == "__main__":
    main()
