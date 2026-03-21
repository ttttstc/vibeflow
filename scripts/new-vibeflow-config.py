#!/usr/bin/env python3
import argparse
from datetime import date
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--template', required=True, choices=['prototype', 'web-standard', 'api-standard', 'enterprise'])
    parser.add_argument('--project-root', default='.')
    parser.add_argument('--template-root', default=None)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    project_root = Path(args.project_root).resolve()
    template_root = Path(args.template_root).resolve() if args.template_root else repo_root / 'templates'
    template_path = template_root / f'{args.template}.yaml'
    if not template_path.exists():
        raise SystemExit(f'Template not found: {template_path}')

    workflow_dir = project_root / '.vibeflow'
    workflow_dir.mkdir(parents=True, exist_ok=True)
    workflow_path = workflow_dir / 'workflow.yaml'
    content = template_path.read_text(encoding='utf-8').replace('TEMPLATE_DATE', date.today().isoformat())
    workflow_path.write_text(content, encoding='utf-8')
    print(workflow_path)


if __name__ == '__main__':
    main()
