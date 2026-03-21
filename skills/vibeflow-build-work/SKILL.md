---
name: vibeflow-build-work
description: Use when build initialization is done and some features are still failing.
---

## Purpose

Drive one feature at a time through the implementation pipeline.

## Inputs

- `feature-list.json`
- `task-progress.md`
- `.vibeflow/work-config.json`
- latest design and requirements docs

## Required Flow

1. choose the next failing feature with satisfied dependencies
2. plan implementation for that feature
3. execute TDD if enabled
4. run quality gates if enabled
5. run feature acceptance tests if enabled
6. run spec compliance review if enabled
7. persist progress and mark status changes

## Rules

- `.vibeflow/work-config.json` is authoritative for enabled steps
- do not mark a feature passing without fresh evidence
