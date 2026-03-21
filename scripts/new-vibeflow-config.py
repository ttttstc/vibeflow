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
    template_path = None
    for ext in ('.yaml', '.yml'):
        candidate = template_root / f'{args.template}{ext}'
        if candidate.exists():
            template_path = candidate
            break
    if template_path is None:
        raise SystemExit(f'Template not found: {template_root / args.template}.yaml (or .yml)')

    workflow_dir = project_root / '.vibeflow'
    workflow_dir.mkdir(parents=True, exist_ok=True)
    # Remove any existing workflow file to avoid stale-config conflicts
    for ext in ('.yaml', '.yml'):
        stale = workflow_dir / f'workflow{ext}'
        if stale.exists():
            stale.unlink()
    workflow_path = workflow_dir / f'workflow{template_path.suffix}'
    content = template_path.read_text(encoding='utf-8').replace('TEMPLATE_DATE', date.today().isoformat())
    workflow_path.write_text(content, encoding='utf-8')
    print(workflow_path)


if __name__ == '__main__':
    main()
