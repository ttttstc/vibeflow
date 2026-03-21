#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


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
    workflow_path = project_root / '.vibeflow' / 'workflow.yaml'
    if not workflow_path.exists():
        raise SystemExit(f'Workflow file not found: {workflow_path}')

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
            'system': 'st:\n    skill:' in content and 'st:\n    skill:' in content and 'required: true' in content,
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
    print(path)


if __name__ == '__main__':
    main()
