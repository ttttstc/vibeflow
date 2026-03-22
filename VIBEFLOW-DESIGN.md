# VibeFlow Design

> Version: v1.0
> Date: 2026-03-21
> Status: Full local workflow scaffold implemented

## Overview

VibeFlow is a seven-stage workflow for iterative product delivery:

1. Think
2. Plan
3. Build
4. Review
5. Test
6. Ship
7. Reflect

The repository now contains the complete local scaffold for all seven stages.
All project-facing names are unified under `vibeflow`.

## Naming Rules

Use only these project-facing names:

- skills live under `skills/`
- runtime state lives under `.vibeflow/`
- design contract is `VIBEFLOW-DESIGN.md`
- helper scripts live under `scripts/`
- templates live under `templates/`

## File Layout

```text
skills/
  vibeflow/
  vibeflow-router/
  vibeflow-think/
  vibeflow-plan-review/
  vibeflow-requirements/
  vibeflow-ucd/
  vibeflow-design/
  vibeflow-build-init/
  vibeflow-build-work/
  vibeflow-tdd/
  vibeflow-quality/
  vibeflow-feature-st/
  vibeflow-spec-review/
  vibeflow-review/
  vibeflow-test-system/
  vibeflow-test-qa/
  vibeflow-ship/
  vibeflow-reflect/

hooks/
  hooks.json
  session-start.ps1

scripts/
  get-vibeflow-phase.py
  new-vibeflow-config.py
  new-vibeflow-work-config.py
  test-vibeflow-setup.py

templates/
  prototype.yaml
  web-standard.yaml
  api-standard.yaml
  enterprise.yaml
```

## Router State Machine

Routing is file-driven through `scripts/get-vibeflow-phase.py`.

Detected phases:

- `increment`
- `think`
- `template-selection`
- `plan-review`
- `requirements`
- `ucd`
- `design`
- `build-init`
- `build-config`
- `build-work`
- `review`
- `test-system`
- `test-qa`
- `ship`
- `reflect`
- `done`

## Runtime Artifacts

VibeFlow uses these runtime artifacts:

- `.vibeflow/think-output.md`
- `.vibeflow/workflow.yaml`
- `.vibeflow/work-config.json`
- `.vibeflow/qa-report.md`
- `.vibeflow/retro-YYYY-MM-DD.md`
- `.vibeflow/increment-request.json`

Inherited project artifacts remain where the build and test process expects them:

- `docs/plans/*-srs.md`
- `docs/plans/*-ucd.md`
- `docs/plans/*-design.md`
- `docs/plans/*-st-report.md`
- `docs/test-cases/feature-*.md`
- `feature-list.json`
- `task-progress.md`
- `RELEASE_NOTES.md`

## Templates

The project includes four static templates:

- `prototype`
- `web-standard`
- `api-standard`
- `enterprise`

Template selection writes `.vibeflow/workflow.yaml`.
Template-derived build trimming writes `.vibeflow/work-config.json`.

## Skill Catalog

### Core

- `vibeflow`
- `vibeflow-router`
- `vibeflow-think`

### Plan

- `vibeflow-plan-review`
- `vibeflow-requirements`
- `vibeflow-ucd`
- `vibeflow-design`

### Build

- `vibeflow-build-init`
- `vibeflow-build-work`
- `vibeflow-tdd`
- `vibeflow-quality`
- `vibeflow-feature-st`
- `vibeflow-spec-review`

### Post-Build

- `vibeflow-review`
- `vibeflow-test-system`
- `vibeflow-test-qa`
- `vibeflow-ship`
- `vibeflow-reflect`

## Implementation Notes

- the repository contains the full local alias layer for all stages
- routing is deterministic and based on files rather than memory
- workflow-specific build trimming is derived from the selected template
- UI-only testing remains conditional on workflow state and generated artifacts

## Verification

Use these commands locally:

```powershell
python scripts/get-vibeflow-phase.py
python scripts/test-vibeflow-setup.py --json
```


