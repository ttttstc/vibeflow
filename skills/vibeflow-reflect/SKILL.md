---
name: vibeflow-reflect
description: Use after shipping to create the retrospective and next-iteration input.
---

# Reflect Stage for VibeFlow

Close the loop after delivery. Create retrospective and next-iteration input.

**Announce at start:** "I'm using the vibeflow-reflect skill to run the retrospective."

## Purpose

After shipping, capture learnings:
- What worked well
- What failed
- What should change next iteration
- Concrete improvements for next cycle

## Prerequisites

Before running this skill:
- Release shipped (vibeflow-ship complete)
- All features complete
- Task progress available

## Step 1: Gather Session Data

### 1.1 Read Task Progress

From `task-progress.md`:
- Session log entries
- Features completed
- Issues encountered
- Time estimates vs actual

### 1.2 Read Feature List

From `feature-list.json`:
- All features with final status
- Features that took longer than expected
- Features with scope changes

### 1.3 Review Previous Retro

If previous retro exists at `.vibeflow/retro-YYYY-MM-DD.md`:
- Note action items from previous retro
- Check if they were implemented
- Carry forward incomplete items

### 1.4 Review Release Notes

From `RELEASE_NOTES.md`:
- What was delivered
- Known limitations
- Breaking changes

## Step 2: Analyze What Worked

### 2.1 Identify Wins

For each positive pattern:
- What happened
- Why it worked
- How to replicate

Categories to consider:
- **Process**: Planning, review, testing
- **Architecture**: Design decisions that worked
- **Team**: Collaboration, communication
- **Tools**: Automation, scripts, skills

### 2.2 Document Wins

```
### What Worked

#### Process
- [Win 1]: Description of what worked well

#### Architecture
- [Win 1]: Description

#### Team
- [Win 1]: Description

#### Tools
- [Win 1]: Description
```

## Step 3: Analyze What Failed

### 3.1 Identify Failures

For each issue or failure:
- What happened
- Root cause
- Impact

Categories to consider:
- **Process**: Planning gaps, review failures
- **Architecture**: Design decisions that caused problems
- **Team**: Communication issues, skill gaps
- **Tools**: Missing automation, broken processes

### 3.2 Document Failures

```
### What Failed

#### Process
- [Failure 1]: Description of what went wrong
  - Root cause: Why it happened
  - Impact: What was the effect

#### Architecture
- [Failure 1]: Description
  - Root cause: ...
  - Impact: ...

#### Team
- [Failure 1]: Description
  - Root cause: ...
  - Impact: ...

#### Tools
- [Failure 1]: Description
  - Root cause: ...
  - Impact: ...
```

## Step 4: Identify Action Items

### 4.1 Process Improvements

For each improvement identified:
```
#### Action: [Short title]
**Owner**: Who will own this
**What**: Specific change to make
**When**: Before next iteration starts
**Success criteria**: How to know it's done
```

### 4.2 Architecture Improvements

For architectural issues:
```
#### Action: [Short title]
**Owner**: Who will own this
**What**: Specific refactor or design change
**When**: In next iteration
**Success criteria**: How to verify
```

### 4.3 Tool Improvements

For tool/process gaps:
```
#### Action: [Short title]
**Owner**: Who will own this
**What**: New automation or process to create
**When**: Before next iteration starts
**Success criteria**: How to verify
```

## Step 5: Create Retro Document

### 5.1 Create Retro File

File: `.vibeflow/retro-YYYY-MM-DD.md`

```markdown
# Retrospective — YYYY-MM-DD

## Summary
- **Features delivered**: N
- **Total time**: X days
- **Key wins**: 1-2 sentence summary
- **Key failures**: 1-2 sentence summary

---

## What Worked

### Process
- [Win 1]
- [Win 2]

### Architecture
- [Win 1]
- [Win 2]

### Team
- [Win 1]
- [Win 2]

### Tools
- [Win 1]
- [Win 2]

---

## What Failed

### Process
- [Failure 1]
- [Failure 2]

### Architecture
- [Failure 1]
- [Failure 2]

### Team
- [Failure 1]
- [Failure 2]

### Tools
- [Failure 1]
- [Failure 2]

---

## Action Items

| # | Action | Owner | When | Done |
|---|--------|-------|------|------|
| 1 | Action description | Name | Before next | [ ] |
| 2 | Action description | Name | Next cycle | [ ] |

---

## Next Iteration Input

### Carry-over
- [Item from previous retro completed]
- [Item from previous retro not completed — reason]

### New Considerations
- [New insight from this cycle]

### Scope建议
- [Recommendations for next iteration scope]
```

### 5.2 Save Retro Document

Write to `.vibeflow/retro-YYYY-MM-DD.md`.

## Step 6: Create Increment Request (if needed)

### 6.1 Identify Follow-up Work

From failures and action items:
- Refactoring needed
- Technical debt to address
- Features deferred

### 6.2 Create Increment Request

File: `.vibeflow/increment-request.json`

```json
{
  "created": "YYYY-MM-DD",
  "source_retro": "retro-YYYY-MM-DD.md",
  "follow_up_work": [
    {
      "title": "Description of work",
      "category": "refactor|debt|deferred_feature",
      "priority": "high|medium|low",
      "reason": "Why this is needed",
      "estimated_impact": "What improvement"
    }
  ],
  "process_improvements": [
    {
      "title": "Description",
      "action": "Specific change",
      "owner": "Who",
      "when": "When"
    }
  ]
}
```

### 6.3 Save Increment Request

Write to `.vibeflow/increment-request.json`.

## Step 7: Update Task Progress

In `task-progress.md`:
- Mark retrospective complete
- Link to retro document
- Link to increment request (if created)

## Checklist

Before marking reflect complete:

- [ ] All session data gathered
- [ ] Wins identified and documented
- [ ] Failures identified and documented
- [ ] Root causes analyzed
- [ ] Action items created with owners
- [ ] Retro document saved
- [ ] Increment request created (if needed)
- [ ] Task progress updated
- [ ] Next iteration informed

## Outputs

| File | Purpose |
|------|---------|
| `.vibeflow/retro-YYYY-MM-DD.md` | Retrospective document |
| `.vibeflow/increment-request.json` | Next iteration input (if needed) |

## Integration

**Called by:** `vibeflow` router (after ship complete)
**Requires:**
- `task-progress.md` (session log)
- `feature-list.json` (completed features)
- Previous retro (if exists)
- `RELEASE_NOTES.md`
**Produces:**
- Retro document at `.vibeflow/retro-YYYY-MM-DD.md`
- Increment request at `.vibeflow/increment-request.json` (if needed)
**Chains to:** Next VibeFlow cycle (Think stage)
