# VibeFlow Framework Completion Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Complete the VibeFlow framework by enriching remaining skeleton skills, fixing encoding issues, resolving failing tests, and establishing validation project structure.

**Architecture:** Thin local orchestration (scripts + file-driven state) with pluggable execution via local skill aliases. The framework itself is the product — completeness here sets the standard for all downstream projects.

**Tech Stack:** Python 3.12+, pytest, Claude Code skills, YAML templates

---

## Overview

| Component | Status | Lines | Action |
|-----------|--------|-------|--------|
| `vibeflow-ucd` | Skeleton | 23 | Enrich |
| `vibeflow-router` | Partial | 59 | Enrich |
| `vibeflow` | Minimal | 17 | Enrich |
| `README.zh-CN.md` | Encoding error | ~130 | Rewrite |
| Unit tests | 9 failing | — | Fix |
| `docs/plans/` | Missing | — | Create structure |

---

## Task 1: Enrich vibeflow-ucd

**Files:**
- Modify: `skills/vibeflow-ucd/SKILL.md`

The UCD (User-Centered Design) skill produces interface and style guidance. Currently a skeleton.

**Step 1: Read current content**

Run: `cat skills/vibeflow-ucd/SKILL.md`

**Step 2: Write complete UCD skill**

Replace with 150-200 line skill covering:
- Purpose and scope of UCD in workflow
- Inputs (workflow.yaml, think-output.md)
- Steps to produce `docs/plans/*-ucd.md`
- UI element inventory (forms, navigation, responsive breakpoints)
- Accessibility requirements
- Output format template
- Integration with design and build phases

Write to: `skills/vibeflow-ucd/SKILL.md`

---

## Task 2: Enrich vibeflow-router

**Files:**
- Modify: `skills/vibeflow-router/SKILL.md`

The router skill is the entry point for every session. Currently 59 lines of routing table only.

**Step 1: Read current content**

Run: `cat skills/vibeflow-router/SKILL.md`

**Step 2: Write complete router skill**

Replace with 200+ line skill covering:
- Session start protocol (read phase, inject context)
- Phase routing table with all 16 phases
- Template selection guidance (when to recommend prototype vs enterprise)
- Feature list management rules
- Error recovery when artifacts are inconsistent
- Integration with hooks (session-start.ps1 / session-start.sh)
- Hard rules for routing

Write to: `skills/vibeflow-router/SKILL.md`

---

## Task 3: Enrich vibeflow (root skill)

**Files:**
- Modify: `skills/vibeflow/SKILL.md`

The root skill is 17 lines. Needs proper onboarding content.

**Step 1: Read current content**

Run: `cat skills/vibeflow/SKILL.md`

**Step 2: Write complete root skill**

Replace with 100+ line skill covering:
- Framework overview and value proposition
- Quick start (3 commands to first phase)
- Prerequisite check (verify hooks installed)
- Seven-stage workflow overview
- When to use each template
- Common pitfalls
- Reference to all sub-skills

Write to: `skills/vibeflow/SKILL.md`

---

## Task 4: Fix README.zh-CN.md Encoding

**Files:**
- Modify: `README.zh-CN.md`

The file was saved with incorrect encoding (mojibake). Rewrite in UTF-8.

**Step 1: Check encoding damage**

Run: `file README.zh-CN.md`

Expected: UTF-8 text, not ISO-8859 or GB encoding

**Step 2: Rewrite README.zh-CN.md**

Rewrite the complete Chinese README with:
- Framework introduction
- Seven stages listed
- Repository structure
- Runtime files
- Quick start commands
- Templates explanation
- Documentation links (ARCHITECTURE.md, USAGE.md, VIBEFLOW-DESIGN.md)
- Validation commands

Write to: `README.zh-CN.md` (save as UTF-8)

---

## Task 5: Fix Failing Unit Tests

**Files:**
- Modify: `tests/test_detect_phase.py`
- Modify: `tests/test_new_vibeflow_work_config.py`
- Modify: `tests/test_new_vibeflow_config.py`

**Step 1: Run tests to see failures**

Run: `python -m pytest tests/ -v --tb=short 2>&1 | tail -40`

Expected failures in:
- `test_tdd_enabled`, `test_feature_st_enabled` (step_enabled format mismatch)
- `test_system_test_enabled`, `test_qa_enabled` (YAML structure vs test content)
- `test_prototype_template_copies`, `test_date_replaced` (template dir path)

**Step 2: Fix TestStepEnabled regex expectations**

The `step_enabled()` function uses regex: `rf'- id: {re.escape(step_id)}[\s\S]*?required: true'`

Update test YAML content to match actual template format:
```python
def test_tdd_enabled():
    content = '''build:
  steps:
    - id: tdd
      required: true
'''
    assert step_enabled(content, 'tdd') is True
```

**Step 3: Fix TestNewVibeflowConfig template path**

The `new-vibeflow-config.py` uses `repo_root / 'templates'` by default. Tests must either:
- Mock the default path, or
- Create `templates/` in the temp project root

Fix by creating template in tmp_path:
```python
def test_prototype_template_copies(self, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'templates').mkdir()
    (tmp_path / 'templates' / 'prototype.yaml').write_text('template: "prototype"\ndate: TEMPLATE_DATE')
    # ... rest of test
```

**Step 4: Verify all tests pass**

Run: `python -m pytest tests/ -v`
Expected: 44 passed

---

## Task 6: Create docs/plans Structure

**Files:**
- Create: `docs/plans/.gitkeep` (placeholder for directory)
- Create: `docs/plans/README.md` (index of plan templates)

**Step 1: Create index**

Write: `docs/plans/README.md`

Content:
```markdown
# VibeFlow Plan Templates

Plans produced by VibeFlow phases:

- `*-srs.md` — Software Requirements Specification (from vibeflow-requirements)
- `*-ucd.md` — User-Centered Design document (from vibeflow-ucd)
- `*-design.md` — Technical design document (from vibeflow-design)
- `*-st-report.md` — System test report (from vibeflow-test-system)

Plans are dated and named: `YYYY-MM-DD-<feature-name>-<type>.md`
```

**Step 2: Create placeholder**

Run: `touch docs/plans/.gitkeep`

---

## Task 7: Validate End-to-End

**Files:**
- Run: `validation/sample-priority-api/`

**Step 1: Verify phase detection on validation project**

Run:
```bash
python scripts/get-vibeflow-phase.py --project-root validation/sample-priority-api --json
python scripts/test-vibeflow-setup.py --project-root validation/sample-priority-api --json
```

Expected: `done` phase, all skills verified

**Step 2: Verify test suite passes**

Run:
```bash
python -m pytest tests/ -v
```

Expected: All 44 tests pass

---

## Task 8: Commit

**Step 1: Stage changes**

Run:
```bash
git add skills/vibeflow-ucd/SKILL.md \
  skills/vibeflow-router/SKILL.md \
  skills/vibeflow/SKILL.md \
  README.zh-CN.md \
  tests/ \
  docs/plans/
```

**Step 2: Commit**

```bash
git commit -m "feat: complete VibeFlow framework - enrich skills, fix tests, add docs structure"
```

---

## Verification Checklist

- [ ] `vibeflow-ucd` skill ≥150 lines with step-by-step guidance
- [ ] `vibeflow-router` skill ≥200 lines with routing rules
- [ ] `vibeflow` root skill ≥100 lines with onboarding content
- [ ] `README.zh-CN.md` reads correctly in UTF-8
- [ ] All 44 unit tests pass
- [ ] `docs/plans/` directory created with index
- [ ] `get-vibeflow-phase.py` reports `done` for validation project
- [ ] `test-vibeflow-setup.py` reports all skills verified for validation project
