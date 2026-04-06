#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import importlib.util


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem.replace('-', '_'), path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


SKILL_NAMES = [
    'vibeflow', 'vibeflow-router', 'vibeflow-spark',
    'vibeflow-plan-value-review', 'vibeflow-plan-eng-review', 'vibeflow-plan-design-review',
    'vibeflow-requirements', 'vibeflow-ucd', 'vibeflow-design', 'vibeflow-tasks', 'vibeflow-build-init',
    'vibeflow-build-work', 'vibeflow-tdd', 'vibeflow-quality', 'vibeflow-feature-st',
    'vibeflow-spec-review', 'vibeflow-review', 'vibeflow-test-system', 'vibeflow-test-qa',
    'vibeflow-browser-testing', 'vibeflow-ship', 'vibeflow-reflect', 'vibeflow-quick', 'vibeflow-learn',
    'vibeflow-status', 'vibeflow-dashboard'
]


def check_skill_skillmd(skills_dir: Path, skill_name: str) -> dict:
    skill_path = skills_dir / skill_name
    skillmd_path = skill_path / 'SKILL.md'
    if not skill_path.exists():
        return {'skill': skill_name, 'status': 'missing', 'detail': 'directory not found'}
    if not skillmd_path.exists():
        return {'skill': skill_name, 'status': 'missing', 'detail': 'SKILL.md not found'}
    return {'skill': skill_name, 'status': 'ok', 'detail': 'SKILL.md exists'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project-root', default='.')
    parser.add_argument('--json', action='store_true', dest='as_json')
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    phase_module = load_module(repo_root / 'scripts' / 'get-vibeflow-phase.py')
    project_root = Path(args.project_root).resolve()

    # Skills exist in the framework repo, not target projects
    skills_dir = repo_root / 'skills'
    workflow_path = project_root / '.vibeflow' / 'workflow.yaml'
    state_path = project_root / '.vibeflow' / 'state.json'

    # Check skills (framework-level verification)
    skill_results = []
    missing_count = 0
    for name in SKILL_NAMES:
        result = check_skill_skillmd(skills_dir, name)
        if result['status'] != 'ok':
            missing_count += 1
        skill_results.append(result)

    workflow_ok = workflow_path.exists() or (project_root / '.vibeflow' / 'workflow.yml').exists()
    state_ok = state_path.exists()

    all_ok = missing_count == 0 and state_ok and workflow_ok

    phase_info = phase_module.detect_phase(project_root)
    report = {
        'setup_ok': all_ok,
        'phase': phase_info['phase'],
        'state': state_ok,
        'workflow': workflow_ok,
        'skills': SKILL_NAMES,
    }
    if args.as_json:
        print(json.dumps(report, indent=2))
    else:
        missing_skills = [r['skill'] for r in skill_results if r['status'] != 'ok']
        warnings = []
        if missing_count > 0:
            warnings.append(f"{missing_count} skills missing")
        if not state_ok:
            warnings.append('state.json missing')
        if not workflow_ok:
            warnings.append('workflow.yaml missing')
        if warnings:
            print(f"{phase_info['phase']} (WARNING: {', '.join(warnings)})")
        else:
            print(f"{phase_info['phase']} (all checks passed)")


if __name__ == '__main__':
    main()
