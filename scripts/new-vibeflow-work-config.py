#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from vibeflow_paths import ensure_state, save_state, set_checkpoint  # noqa: E402


def step_enabled(content: str, step_id: str) -> bool:
    return re.search(rf'- id: {re.escape(step_id)}[\s\S]*?required: true', content) is not None


def read_gate(content: str, name: str, default: int) -> int:
    match = re.search(rf'{re.escape(name)}:\s*(\d+)', content)
    return int(match.group(1)) if match else default


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project-root', default='.')
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    workflow_path = None
    for ext in ('.yaml', '.yml'):
        candidate = project_root / '.vibeflow' / f'workflow{ext}'
        if candidate.exists():
            workflow_path = candidate
            break
    if workflow_path is None:
        raise SystemExit(f'Workflow file not found: {project_root / ".vibeflow" / "workflow.yaml"} (or .yml)')

    content = workflow_path.read_text(encoding='utf-8')
    template_match = re.search(r'template:\s*"([^"]+)"', content)
    config = {
        'template': template_match.group(1) if template_match else '',
        'build': {
            'tdd': step_enabled(content, 'tdd'),
            'quality': step_enabled(content, 'quality'),
            'feature_st': step_enabled(content, 'feature-st'),
            'spec_review': step_enabled(content, 'review'),
        },
        'quality_gates': {
            'line_coverage': read_gate(content, 'line_coverage', 90),
            'branch_coverage': read_gate(content, 'branch_coverage', 80),
            'mutation_score': read_gate(content, 'mutation_score', 80),
        },
        'test': {
            'system': re.search(r'st:[\s\S]*?required:\s+true', content) is not None,
            'qa': re.search(r'qa:[\s\S]*?required:\s+true', content) is not None,
        },
        'reflect': {
            'required': re.search(r'reflect:[\s\S]*?required:\s+true', content) is not None,
        },
    }
    state_root = project_root / '.vibeflow'
    state_root.mkdir(parents=True, exist_ok=True)
    path = state_root / 'work-config.json'
    path.write_text(json.dumps(config, indent=2), encoding='utf-8')

    state = ensure_state(project_root)
    set_checkpoint(state, 'build_config', True, phase='build-config')
    if (project_root / 'feature-list.json').exists():
        set_checkpoint(state, 'build_init', True)
    save_state(project_root, state)

    print(path)


if __name__ == '__main__':
    main()
