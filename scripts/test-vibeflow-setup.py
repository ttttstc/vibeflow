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
    'vibeflow', 'vibeflow-router', 'vibeflow-think', 'vibeflow-plan-review',
    'vibeflow-requirements', 'vibeflow-ucd', 'vibeflow-design', 'vibeflow-build-init',
    'vibeflow-build-work', 'vibeflow-tdd', 'vibeflow-quality', 'vibeflow-feature-st',
    'vibeflow-spec-review', 'vibeflow-review', 'vibeflow-test-system', 'vibeflow-test-qa',
    'vibeflow-ship', 'vibeflow-reflect'
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
    phase_info = phase_module.detect_phase(Path(args.project_root).resolve())
    project_root = Path(args.project_root).resolve()
    skills_dir = project_root / 'skills'

    skill_results = []
    missing_count = 0
    for name in SKILL_NAMES:
        result = check_skill_skillmd(skills_dir, name)
        if result['status'] != 'ok':
            missing_count += 1
        skill_results.append(result)

    all_ok = missing_count == 0
    report = {
        'setup_ok': all_ok,
        'phase': phase_info['phase'],
        'workflow': (project_root / '.vibeflow' / 'workflow.yaml').exists(),
        'work_config': (project_root / '.vibeflow' / 'work-config.json').exists(),
        'skills': skill_results,
        'missing_count': missing_count,
    }
    if args.as_json:
        print(json.dumps(report, indent=2))
    else:
        if all_ok:
            print(f"{phase_info['phase']} (all {len(SKILL_NAMES)} skills verified)")
        else:
            missing = [r['skill'] for r in skill_results if r['status'] != 'ok']
            print(f"{phase_info['phase']} (WARNING: {missing_count} skills missing: {', '.join(missing)})")


if __name__ == '__main__':
    main()
