# VibeFlow

VibeFlow is a repository-local workflow orchestration layer for structured software delivery.
It standardizes a full delivery lifecycle inside a codebase using local skills, file-driven routing, static templates, and generated runtime state.

## What It Does

VibeFlow provides:

- a unified `vibeflow-*` skill surface
- a deterministic phase router based on repository files
- static workflow templates for different delivery strictness levels
- generated runtime state under `.vibeflow/`
- validation through independent sample projects rather than self-validation on the framework repo

## Lifecycle

A target project moves through these stages:

1. Think
2. Plan Review
3. Requirements
4. UCD when needed
5. Design
6. Build Init
7. Build Work
8. Review
9. Test
10. Ship
11. Reflect

## Repository Layout

```text
skills/       Local workflow skills and phase aliases
scripts/      Python scripts for routing and config generation
templates/    Static workflow templates
hooks/        Host entrypoints for session context injection
validation/   Independent sample projects used for workflow verification
```

## Core Files

Runtime state for a target project is stored under `.vibeflow/`.
Typical artifacts include:

- `.vibeflow/think-output.md`
- `.vibeflow/workflow.yaml`
- `.vibeflow/work-config.json`
- `.vibeflow/plan-review.md`
- `.vibeflow/review-report.md`
- `.vibeflow/qa-report.md`
- `.vibeflow/retro-YYYY-MM-DD.md`
- `.vibeflow/increment-request.json`

Delivery artifacts remain in conventional project paths:

- `docs/plans/*-srs.md`
- `docs/plans/*-ucd.md`
- `docs/plans/*-design.md`
- `docs/plans/*-st-report.md`
- `docs/test-cases/feature-*.md`
- `feature-list.json`
- `task-progress.md`
- `RELEASE_NOTES.md`

## Quick Start

1. Create or choose a target project.
2. Start from the Think phase and write `.vibeflow/think-output.md`.
3. Generate a workflow file:

```bash
python scripts/new-vibeflow-config.py --template api-standard --project-root <target-project>
```

4. Generate build config:

```bash
python scripts/new-vibeflow-work-config.py --project-root <target-project>
```

5. Detect the active phase:

```bash
python scripts/get-vibeflow-phase.py --project-root <target-project> --json
```

6. Validate setup:

```bash
python scripts/test-vibeflow-setup.py --project-root <target-project> --json
```

## Templates

Available templates:

- `prototype`
- `web-standard`
- `api-standard`
- `enterprise`

The selected template controls:

- required stages
- quality gate strictness
- whether UI-specific review paths are enabled
- whether reflection is required

## Documentation

- `ARCHITECTURE.md`: implementation architecture and full diagrams
- `USAGE.md`: operating guide for target projects
- `VIBEFLOW-DESIGN.md`: compact design summary
- `README.zh-CN.md`: Chinese overview

## Validation Project

The repository includes an independent validation target:

- `validation/sample-priority-api`

Useful verification commands:

```bash
python -m unittest discover -s validation/sample-priority-api/tests -v
python scripts/get-vibeflow-phase.py --project-root validation/sample-priority-api --json
python scripts/test-vibeflow-setup.py --project-root validation/sample-priority-api --json
```
