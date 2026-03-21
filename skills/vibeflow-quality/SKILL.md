---
name: vibeflow-quality
description: Use for coverage and mutation quality gates during the VibeFlow build stage.
---

# Quality Gates for VibeFlow

Validate the current feature against `.vibeflow/work-config.json` quality thresholds. Four sequential gates that MUST pass before marking a feature complete.

**Announce at start:** "I'm using the vibeflow-quality skill to run quality gates."

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you have not run the verification command in this session, you cannot claim it passes.

## Step 1: Real Test Verification (Gate 0)

Gate 0 runs BEFORE coverage. Coverage numbers are meaningless when the test suite is all-mock.

### 1.1 Check Real Test Existence

For features with external dependencies (DB, HTTP, file system):
1. Verify at least one `[integration]` labeled test exists
2. Verify the integration test uses a real dependency (not mocked)
3. If no integration test exists → FAIL Gate 0

### 1.2 Execute Real Tests

Run the test suite and verify all tests pass:
```bash
pytest tests/ -v  # or project-specific command
```

Any test failure → Gate 0 FAIL. Fix before proceeding.

**Evidence required:**
```
Gate 0 Result:
- Real test count: N
- All tests passing: YES/NO
- Gate 0: PASS/FAIL
```

## Step 2: Coverage Gate (Gate 1)

After all tests pass, run coverage verification.

### 2.1 Run Coverage Tool

```bash
# Python
coverage run -m pytest tests/
coverage report

# Node.js
npm test -- --coverage

# Java
mvn test jacoco:report
```

### 2.2 Verify Thresholds

Read `.vibeflow/work-config.json` for thresholds:
```json
{
  "quality": {
    "tdd": true,
    "quality_gates": {
      "line_coverage_min": 80,
      "branch_coverage_min": 70
    }
  }
}
```

| Metric | Threshold | If Below |
|--------|-----------|----------|
| Line coverage | `line_coverage_min` | Add tests for uncovered lines |
| Branch coverage | `branch_coverage_min` | Add tests for uncovered branches |

### 2.3 If Coverage Fails

1. Identify uncovered lines/branches from the coverage report
2. Add tests targeting the gaps
3. Return to TDD cycle (vibeflow-tdd) to add tests
4. Re-run coverage verification
5. Do NOT skip or bypass coverage requirements

**Evidence required:**
```
Gate 1 Result:
- Line coverage: XX% (threshold: Y%)
- Branch coverage: XX% (threshold: Y%)
- Gate 1: PASS/FAIL
```

## Step 3: Mutation Testing Gate (Gate 2)

After coverage passes, run mutation testing on changed files.

### 3.1 Run Mutation Testing

```bash
# Python
mutmut run

# Java
mvn pitest:mutationCoverage

# Node.js
stryker
```

### 3.2 Verify Mutation Score

Check `.vibeflow/work-config.json` for mutation threshold:
```json
{
  "quality": {
    "quality_gates": {
      "mutation_score_min": 70
    }
  }
}
```

| Score | Action |
|-------|--------|
| >= threshold | PASS Gate 2 |
| < threshold | Analyze surviving mutants |

### 3.3 Analyze Surviving Mutants

For each surviving mutant:
- **Equivalent mutant** (code change has no observable effect) → document and skip
- **Real gap** (test doesn't catch the mutation) → add/strengthen test
- **Unreachable code** → remove dead code

After analysis:
- Add/strengthen tests for real gaps
- Re-run mutation testing
- Do NOT skip mutation testing

**Evidence required:**
```
Gate 2 Result:
- Mutation score: XX% (threshold: Y%)
- Surviving mutants: N
- Equivalent: N, Real gap: N, Unreachable: N
- Gate 2: PASS/FAIL
```

## Step 4: Verify & Mark (Gate 3)

Final gate before marking feature complete.

### 4.1 Run Full Verification

Execute ALL verification in THIS session (not cached):
```bash
# 1. All tests pass
pytest tests/ -v

# 2. Coverage meets thresholds
coverage run -m pytest tests/
coverage report

# 3. Mutation score meets threshold
mutmut run
mutmut results
```

### 4.2 Read All Output

- Check exit codes for all commands
- Count pass/fail/skip for tests
- Read coverage percentages
- Read mutation score

### 4.3 Mark Feature Complete

ONLY after ALL gates pass:
1. Update feature status in `feature-list.json`: `"status": "passing"`
2. Record evidence in `task-progress.md`
3. Report results with evidence

If ANY gate fails → STOP. Do NOT mark as passing. Fix the issue first.

## Red Flag Words

If you catch yourself using any of these, STOP and re-verify:

| Red Flag | Correct Action |
|----------|----------------|
| "should pass" | Run the tests NOW |
| "probably works" | Execute and verify NOW |
| "coverage looks fine" | Run coverage tool NOW |
| "mutation score should be OK" | Run mutation tests NOW |
| "I've verified" (no output shown) | Show the actual output |

## Checklist

Before marking quality gates complete:

- [ ] Gate 0: Real tests exist and pass (or exemption declared)
- [ ] Gate 1: Line coverage >= threshold
- [ ] Gate 1: Branch coverage >= threshold
- [ ] Gate 2: Mutation score >= threshold
- [ ] Gate 2: Surviving mutants analyzed and addressed
- [ ] Gate 3: Full verification run in THIS session
- [ ] Gate 3: All commands executed with output captured
- [ ] Feature marked `"status": "passing"` in `feature-list.json`

## Integration

**Called by:** `vibeflow-build-work` (Step 4 — Quality gates)
**Requires:**
- Feature ID and `verification_steps`
- `quality_gates` thresholds from `feature-list.json`
- `tech_stack` tool names from `feature-list.json`
- All tests passing (from vibeflow-tdd)
**Produces:** Fresh verification evidence (test output, coverage %, mutation score)
**Chains to:** `vibeflow-feature-st` (if enabled in work-config)
