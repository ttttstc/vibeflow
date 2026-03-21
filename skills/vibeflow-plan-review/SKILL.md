---
name: vibeflow-plan-review
description: Use during Plan to run the executive scope review before specs are authored.
---

## Purpose

Perform the VibeFlow plan review pass before requirements and design authoring continue.

## Inputs

- `VIBEFLOW-DESIGN.md`
- `.vibeflow/think-output.md`
- `.vibeflow/workflow.yaml` if it already exists

## Expected Output

- a scope decision for expansion, hold, or reduction
- review notes saved in `docs/plans/` or `.vibeflow/`
- a clear recommendation on whether to proceed to requirements

## Behavior

- challenge the problem framing
- confirm the recommended scope tier
- summarize major product and delivery risks
- keep the result concise and decision-oriented
