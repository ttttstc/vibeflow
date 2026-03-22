---
name: vibeflow
description: Start or continue a VibeFlow project. Automatically detects the current phase and routes to the correct workflow step.
disable-model-invocation: true
---

Invoke the vibeflow:using-vibeflow skill and follow it exactly as presented to you.

This is the main entry point for VibeFlow. It will:
1. Detect the current project phase via `scripts/get-vibeflow-phase.py`
2. Route you to the correct phase skill automatically
3. You do not need to know which phase you are in — the router handles it

If you already know which phase you want, you can use a specific command instead:
- `/vibeflow:work` — start a feature development cycle
- `/vibeflow:requirements` — write requirements spec
- `/vibeflow:design` — write technical design
- `/vibeflow:init` — initialize build artifacts
- `/vibeflow:ucd` — write UI component design
- `/vibeflow:st` — run system testing
- `/vibeflow:status` — check project progress
- `/vibeflow:increment` — add incremental requirements
