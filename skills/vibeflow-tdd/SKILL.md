---
name: vibeflow-tdd
description: Use as the red-green-refactor step within the VibeFlow build stage.
---

# Test-Driven Development for VibeFlow

Run test-first development for the current feature. Write the test first. Watch it fail. Write minimal code to pass. Refactor.

**Announce at start:** "I'm using the vibeflow-tdd skill to implement this feature via TDD."

## The Iron Law

```
NO IMPLEMENTATION CODE WITHOUT A FAILING TEST FIRST
```

Write code before the test? Delete it. Start over. No exceptions.

## Red-Green-Refactor Cycle

```
Red  → Write failing tests for all verification_steps
Green → Write minimal code to make tests pass
Refactor → Clean up without breaking green
```

## Step 1: TDD Red — Write Failing Tests

### 1.1 Load Feature Context

Read the following artifacts for the current feature:
- **Feature spec** from `feature-list.json` — ID, title, description, `verification_steps[]`, `dependencies[]`, `ui` flag
- **Requirements doc** — `docs/plans/*-srs.md` for the relevant FR section
- **Design doc** — `docs/plans/*-design.md` for the feature's design section
- **Work config** — `.vibeflow/work-config.json` for TDD enablement and thresholds

### 1.2 Identify Test Categories

For each `verification_step`, derive test cases covering:

| Category | What to test | Example |
|----------|-------------|---------|
| Happy path | Normal operation, valid inputs | Valid input returns expected output |
| Error handling | Known failures, invalid inputs | Invalid input returns error |
| Boundary/edge | Limits, empty, max, zero | Empty string; max-length input |
| Security | Injection, authorization | Malformed input sanitized |

When a category does not apply, state it explicitly in a comment.

### 1.3 Write Tests (TDD Red)

**Rule 1: Write tests BEFORE any implementation code exists.**

For each `verification_step`:
1. Write one or more test functions that exercise the described behavior
2. Use the project's test framework (from `feature-list.json` `tech_stack.test_framework`)
3. Place tests in the appropriate test file (follow project convention)
4. Label tests by layer:
   ```python
   # [unit] — internal logic, mocked dependencies
   def test_feature_behavior():
       ...

   # [integration] — real external dependency (DB, API, file system)
   def test_feature_with_real_dependency():
       ...
   ```

**Rule 2: Negative test ratio >= 40%**
```
negative_test_count / total_test_count >= 0.40
```

**Rule 3: Assertion quality — low-value assertions <= 20%**
- Avoid: `assert x is not None`, `assert isinstance(x, SomeType)`, `assert len(x) > 0`
- Prefer: specific value checks, state verification, data correctness

**Rule 4: "Wrong implementation" challenge**
For each test, ask: "What wrong implementation would this test catch?"
- Would a hardcoded value still pass?
- Would swapped fields still pass?
- Would off-by-one errors still pass?

If "almost any wrong implementation would still pass" → rewrite with more specific assertions.

### 1.4 Verify Tests Fail

**Activate environment** per project setup, then run the test command:
```bash
# Python
source .venv/bin/activate  # or appropriate
pytest tests/ -v

# Node.js
npm test

# Java
mvn test
```

**All tests must FAIL at this point.** If any test passes → it tests nothing useful, rewrite it.

### 1.5 Real Test Requirement (if feature has external dependencies)

For features with external dependencies (DB, HTTP, file system):
1. Write at least one `[integration]` test that uses the real dependency
2. Mark it clearly with the `[integration]` label
3. If the feature has no external dependencies, declare explicitly:
   ```python
   # [no integration test] — pure function, no external I/O
   ```

## Step 2: TDD Green — Minimal Implementation

**Rule: Write ONLY enough code to make failing tests pass.**

### 2.1 Implement Feature

1. Read the current failing tests one by one
2. For each failing test, implement the minimal change to make it pass
3. Do NOT implement features not yet tested
4. Do NOT optimize or refactor during this step

### 2.2 Run Tests After Each Change

After implementing each test's required change:
```bash
pytest tests/ -v  # or project-specific command
```

All tests must pass before proceeding.

### 2.3 Service/Server Startup (if applicable)

If the feature implements a server process:
1. Implementation MUST log at startup: bound port, PID, ready signal
2. Write a TDD Red test that verifies the startup output before implementing the server binding

## Step 3: TDD Refactor — Clean Up

**Rule: Keep tests green while improving code quality.**

### 3.1 Refactor

With all tests passing:
1. Extract duplication
2. Improve naming
3. Simplify logic
4. Do NOT add new functionality

### 3.2 Verify Tests Still Pass

After each refactoring change:
```bash
pytest tests/ -v
```

If any test fails → revert the refactor and try a different approach.

## Checklist

Before marking TDD complete:

- [ ] All `verification_steps` have corresponding tests
- [ ] All tests FAIL in Red phase (before implementation)
- [ ] All tests PASS in Green phase (after implementation)
- [ ] Negative test ratio >= 40%
- [ ] Low-value assertion ratio <= 20%
- [ ] At least one integration test (if feature has external deps)
- [ ] All tests still pass after refactoring
- [ ] No implementation code without a failing test first (Iron Law compliance)

## Quality Gates

| Gate | Threshold | Tool |
|------|-----------|------|
| Test pass rate | 100% | `pytest --tb=short` / `npm test` |
| Line coverage | Per `work-config.json` | `coverage report` |
| Branch coverage | Per `work-config.json` | `coverage report` |

## Integration

**Called by:** `vibeflow-build-work` (Step 3 — TDD execution)
**Dispatches:** Implementation subagent if needed
**Requires:**
- Feature spec from `feature-list.json`
- `verification_steps[]` from the feature
- SRS requirements section from `docs/plans/*-srs.md`
- Design section from `docs/plans/*-design.md`
- `tech_stack` and `quality_gates` from `feature-list.json`
**Produces:** Passing tests + implementation code
**Chains to:** `vibeflow-quality` (after TDD complete)
