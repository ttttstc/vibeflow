---
name: vibeflow-brainstorming
description: |
  Brainstorming Ideas Into Designs for VibeFlow. Must use before any creative work —
  creating features, building components, adding functionality, or modifying behavior.
  Explores user intent, requirements and design before implementation.
  Use when asked to "brainstorm this", "help me design this", "think through this",
  or when a design needs exploration before technical specification.
---

# Brainstorming Ideas Into Designs

Help turn ideas into fully formed designs and specs through natural collaborative dialogue.

Start by understanding the current project context, then ask questions one at a time to refine the idea. Once you understand what you're building, present the design and get user approval.

**启动宣告：** "正在使用 vibeflow-brainstorming — 设计头脑风暴。"

<HARD-GATE>
Do NOT invoke any implementation skill, write any code, scaffold any project, or take any implementation action until you have presented a design and the user has approved it. This applies to EVERY project regardless of perceived simplicity.
</HARD-GATE>

## Anti-Pattern: "This Is Too Simple To Need A Design"

Every project goes through this process. A todo list, a single-function utility, a config change — all of them. "Simple" projects are where unexamined assumptions cause the most wasted work. The design can be short (a few sentences for truly simple projects), but you MUST present it and get approval.

## Checklist

You MUST create a task for each of these items and complete them in order:

1. **Explore project context** — check files, docs, recent commits
2. **Ask clarifying questions** — one at a time, understand purpose/constraints/success criteria
3. **Propose 2-3 approaches** — with trade-offs and your recommendation
4. **Present design** — in sections scaled to their complexity, get user approval after each section
5. **Write design doc** — save to `docs/plans/YYYY-MM-DD-<topic>-brainstorming.md` and commit
6. **User reviews written spec** — ask user to review the spec file before proceeding
7. **Transition to implementation** — invoke vibeflow-design skill

## The Process

**Understanding the idea:**

- Check out the current project state first (files, docs, recent commits)
- Before asking detailed questions, assess scope: if the request describes multiple independent subsystems (e.g., "build a platform with chat, file storage, billing, and analytics"), flag this immediately. Don't spend questions refining details of a project that needs to be decomposed first.
- If the project is too large for a single spec, help the user decompose into sub-projects: what are the independent pieces, how do they relate, what order should they be built? Then brainstorm the first sub-project through the normal design flow.
- For appropriately-scoped projects, ask questions one at a time to refine the idea
- Prefer multiple choice questions when possible
- Only one question per message
- Focus on understanding: purpose, constraints, success criteria

**Exploring approaches:**

- Propose 2-3 different approaches with trade-offs
- Present options conversationally with your recommendation and reasoning
- Lead with your recommended option and explain why

**Presenting the design:**

- Once you believe you understand what you're building, present the design
- Scale each section to its complexity: a few sentences if straightforward, up to 200-300 words if nuanced
- Ask after each section whether it looks right so far
- Cover: architecture, components, data flow, error handling, testing
- Be ready to go back and clarify if something doesn't make sense

**Design for isolation and clarity:**

- Break the system into smaller units that each have one clear purpose
- Communicate through well-defined interfaces
- Each unit can be understood and tested independently
- For each unit, you should be able to answer: what does it do, how do you use it, and what does it depend on?

**Working in existing codebases:**

- Explore the current structure before proposing changes. Follow existing patterns.
- Where existing code has problems that affect the work, include targeted improvements as part of the design.

## After the Design

**Documentation:**

- Write the validated design (spec) to `docs/plans/YYYY-MM-DD-<topic>-brainstorming.md`
- Commit the design document to git

**User Review Gate:**
After writing the spec document, ask the user to review:

> "Spec written and committed to `docs/plans/<filename>.md`. Please review it and let me know if you want to make any changes before we move to technical design."

Wait for the user's response. If they request changes, make them. Only proceed once the user approves.

**Implementation:**

- Invoke the vibeflow-design skill to create a detailed technical design
- Do NOT invoke any other skill. vibeflow-design is the next step.

## Key Principles

- **One question at a time** — Don't overwhelm with multiple questions
- **Multiple choice preferred** — Easier to answer than open-ended when possible
- **YAGNI ruthlessly** — Remove unnecessary features from all designs
- **Explore alternatives** — Always propose 2-3 approaches before settling
- **Incremental validation** — Present design, get approval before moving on
- **Be flexible** — Go back and clarify when something doesn't make sense

## Output Design Doc Template

```markdown
# Brainstorming: {title}

**日期**: YYYY-MM-DD
**分支**: {branch}
**模式**: Brainstorming

## Problem Statement
{what we're trying to solve}

## Key Decisions

### Approach Chosen
{selected approach and rationale}

### Alternatives Considered
{other options and why they weren't chosen}

## Design Overview
{architecture, components, data flow}

## Open Questions
{unresolved questions from the brainstorming}

## Next Step
Transition to vibeflow-design for technical specification
```

## 集成

**调用者：** 用户在 design 阶段之前主动调用
**依赖：** `CLAUDE.md`、设计文档（如存在）
**产出：** `docs/plans/YYYY-MM-DD-<topic>-brainstorming.md`
**Gate：** 无强制 gate，用于设计前探索
**链接到：** vibeflow-design（用户审批后）

> **注意：** `vibeflow-design` 已内置问题探索能力（步骤 0）。如果通过 `vibeflow-design` 直接进入设计流程，问题探索会自动发生，无需先运行此 skill。
> 此 skill 作为可选独立入口保留——当用户想在进入完整设计流程前快速探索方向时使用。
