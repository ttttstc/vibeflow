---
name: vibeflow-design
description: Use when VibeFlow needs a technical design document before initialization.
---

## Purpose

Produce the technical design document in `docs/plans/*-design.md`.

## Inputs

- latest SRS in `docs/plans/`
- latest UCD when UI exists
- `.vibeflow/workflow.yaml`

## Outputs

- `docs/plans/YYYY-MM-DD-<topic>-design.md`

## Rules

- define architecture, dependencies, risks, and task decomposition
- make the design specific enough for initialization and build work
- keep the document aligned with the selected workflow template
