#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def latest_matching_file(base: Path, pattern: str):
    if not base.exists():
        return None
    matches = sorted(base.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0] if matches else None


def workflow_text(path: Path) -> str:
    return path.read_text(encoding='utf-8') if path.exists() else ''


def ui_required(workflow_path: Path) -> bool:
    content = workflow_text(workflow_path)
    return ('qa:\n    required: true' in content) or ('design_review:\n    required: true' in content)


def reflect_required(workflow_path: Path) -> bool:
    return 'reflect:\n  required: true' in workflow_text(workflow_path)


def all_features_passing(feature_list_path: Path) -> bool:
    if not feature_list_path.exists():
        return False
    data = json.loads(feature_list_path.read_text(encoding='utf-8'))
    features = [f for f in data.get('features', []) if not f.get('deprecated')]
    return bool(features) and all(f.get('status') == 'passing' for f in features)


def detect_phase(project_root: Path) -> dict:
    state_root = project_root / '.vibeflow'
    think_path = state_root / 'think-output.md'
    workflow_path = state_root / 'workflow.yaml'
    work_config_path = state_root / 'work-config.json'
    qa_report_path = state_root / 'qa-report.md'
    plan_review_path = state_root / 'plan-review.md'
    review_report_path = state_root / 'review-report.md'
    increment_path = state_root / 'increment-request.json'
    feature_list_path = project_root / 'feature-list.json'
    plans_path = project_root / 'docs' / 'plans'
    latest_srs = latest_matching_file(plans_path, '*-srs.md')
    latest_ucd = latest_matching_file(plans_path, '*-ucd.md')
    latest_design = latest_matching_file(plans_path, '*-design.md')
    latest_st = latest_matching_file(plans_path, '*-st-report.md')
    latest_retro = latest_matching_file(state_root, 'retro-*.md') if state_root.exists() else None

    phase = 'done'
    reason = 'All detectable phases completed.'

    if increment_path.exists():
        phase, reason = 'increment', '.vibeflow/increment-request.json exists.'
    elif not think_path.exists():
        phase, reason = 'think', '.vibeflow/think-output.md is missing.'
    elif not workflow_path.exists():
        phase, reason = 'template-selection', '.vibeflow/workflow.yaml is missing.'
    elif not plan_review_path.exists():
        phase, reason = 'plan-review', '.vibeflow/plan-review.md is missing.'
    elif latest_srs is None:
        phase, reason = 'requirements', 'No SRS document found in docs/plans.'
    elif ui_required(workflow_path) and latest_ucd is None:
        phase, reason = 'ucd', 'UI workflow requires a UCD document.'
    elif latest_design is None:
        phase, reason = 'design', 'No design document found in docs/plans.'
    elif not feature_list_path.exists():
        phase, reason = 'build-init', 'feature-list.json is missing.'
    elif not work_config_path.exists():
        phase, reason = 'build-config', '.vibeflow/work-config.json is missing.'
    elif not all_features_passing(feature_list_path):
        phase, reason = 'build-work', 'Some active features are not passing.'
    elif not review_report_path.exists():
        phase, reason = 'review', '.vibeflow/review-report.md is missing.'
    elif latest_st is None:
        phase, reason = 'test-system', 'System test report is missing.'
    elif ui_required(workflow_path) and not qa_report_path.exists():
        phase, reason = 'test-qa', 'UI workflow requires .vibeflow/qa-report.md.'
    elif not (project_root / 'RELEASE_NOTES.md').exists():
        phase, reason = 'ship', 'RELEASE_NOTES.md is missing.'
    elif latest_retro is None:
        phase, reason = 'reflect', 'No retrospective file exists.'

    return {
        'phase': phase,
        'reason': reason,
        'has_ui': ui_required(workflow_path),
        'reflect_required': reflect_required(workflow_path),
        'paths': {
            'think': str(think_path),
            'workflow': str(workflow_path),
            'plan_review': str(plan_review_path),
            'work_config': str(work_config_path),
            'review': str(review_report_path),
            'feature_list': str(feature_list_path),
            'qa_report': str(qa_report_path),
            'latest_srs': str(latest_srs) if latest_srs else None,
            'latest_ucd': str(latest_ucd) if latest_ucd else None,
            'latest_design': str(latest_design) if latest_design else None,
            'latest_st': str(latest_st) if latest_st else None,
            'latest_retro': str(latest_retro) if latest_retro else None,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project-root', default='.')
    parser.add_argument('--json', action='store_true', dest='as_json')
    args = parser.parse_args()
    result = detect_phase(Path(args.project_root).resolve())
    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        print(result['phase'])


if __name__ == '__main__':
    main()
