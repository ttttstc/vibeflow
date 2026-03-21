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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project-root', default='.')
    parser.add_argument('--json', action='store_true', dest='as_json')
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    phase_module = load_module(repo_root / 'scripts' / 'get-vibeflow-phase.py')
    phase_info = phase_module.detect_phase(Path(args.project_root).resolve())
    project_root = Path(args.project_root).resolve()
    report = {
        'phase': phase_info['phase'],
        'workflow': (project_root / '.vibeflow' / 'workflow.yaml').exists(),
        'work_config': (project_root / '.vibeflow' / 'work-config.json').exists(),
        'skills': [
            'vibeflow', 'vibeflow-router', 'vibeflow-think', 'vibeflow-plan-review',
            'vibeflow-requirements', 'vibeflow-ucd', 'vibeflow-design', 'vibeflow-build-init',
            'vibeflow-build-work', 'vibeflow-tdd', 'vibeflow-quality', 'vibeflow-feature-st',
            'vibeflow-spec-review', 'vibeflow-review', 'vibeflow-test-system', 'vibeflow-test-qa',
            'vibeflow-ship', 'vibeflow-reflect'
        ],
    }
    if args.as_json:
        print(json.dumps(report, indent=2))
    else:
        print(report['phase'])


if __name__ == '__main__':
    main()
