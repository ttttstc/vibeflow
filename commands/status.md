---
name: vibeflow:status
description: Show progress summary for the current VibeFlow project.
disable-model-invocation: true
---

To check the status of a VibeFlow project:

1. Read `feature-list.json` to see passing/failing features
2. Read `task-progress.md` to see session history
3. Run `python scripts/get-vibeflow-phase.py --project-root . --json` to detect current phase
4. Run `python scripts/test-vibeflow-setup.py --project-root . --json` to validate setup
