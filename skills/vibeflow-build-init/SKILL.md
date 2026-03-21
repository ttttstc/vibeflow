---
name: vibeflow-build-init
description: Use when design exists but feature-list.json has not been initialized.
---

## Purpose

Initialize implementation artifacts for the build stage.

## Outputs

- `feature-list.json`
- `task-progress.md`
- worker guidance file expected by the active delivery pipeline
- any project bootstrap files required by the implementation flow

## Rules

- initialize only after requirements and design are present
- after init, generate `.vibeflow/work-config.json` if it does not exist

