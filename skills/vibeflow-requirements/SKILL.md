---
name: vibeflow-requirements
description: Use when VibeFlow needs an approved requirements specification in docs/plans.
---

## Purpose

Produce the project requirements document in `docs/plans/*-srs.md`.

## Inputs

- `VIBEFLOW-DESIGN.md`
- `.vibeflow/think-output.md`
- `.vibeflow/workflow.yaml`

## Outputs

- `docs/plans/YYYY-MM-DD-<topic>-srs.md`

## Rules

- do not start design implementation before the requirements document exists
- capture scope, exclusions, interfaces, assumptions, and acceptance criteria
- keep naming vendor-neutral inside project documents
