---
name: vibeflow-test-system
description: Use when all active features are passing and system-level testing must begin.
---

## Purpose

Run system-level testing after build completion.

## Outputs

- `docs/plans/*-st-report.md`

## Rules

- validate integration behavior, not just feature-local behavior
- do not skip when the selected workflow marks system testing as required
