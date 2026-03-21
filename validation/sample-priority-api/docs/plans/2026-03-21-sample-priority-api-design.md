# Sample Priority API Design

## Architecture
- Language: Python 3.11+
- Module: `src/sample_priority_api/workflow.py`
- Entry points: direct function calls and example script

## Main Decisions
- Keep all business logic in a single pure module for low ceremony validation.
- Use a dictionary-based normalization map for stable alias handling.
- Use `collections.Counter` to produce deterministic summary counts.
- Use `unittest` to avoid external dependencies.

## Feature Breakdown
- Feature 1: normalize priority aliases
- Feature 2: summarize normalized work items
- Feature 3: provide runnable example and system test evidence
