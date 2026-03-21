---
name: vibeflow-ucd
description: Use when the selected workflow includes UI work and a UCD plan is required.
---

## Purpose

Produce the interface and style guidance document in `docs/plans/*-ucd.md`.

## Inputs

- latest SRS in `docs/plans/`
- `.vibeflow/workflow.yaml`

## Outputs

- `docs/plans/YYYY-MM-DD-<topic>-ucd.md`

## Rules

- skip only when the chosen template and feature scope clearly have no UI
- define tokens, components, and page-level guidance
- keep guidance concrete enough for implementation and review
