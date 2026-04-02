# VibeFlow Project Rules Preset

This directory contains project-level rules that VibeFlow can inject into implementation packets.

## Usage

- Put cross-stack constraints in `rules/00-global.md`.
- Put language-specific constraints in `rules/coding/<stack>.md`.
- Keep rules concise, prescriptive, and reviewable.
- Prefer project rules here over adding large policy blocks to `CLAUDE.md`.
- When rules conflict, the more specific rule should win.

## Suggested Workflow

- Keep only the stacks your project actually uses.
- Delete files that do not apply to reduce noise in agent context.
- Add project-specific rules beside these presets instead of editing every skill.
- Treat these files as versioned engineering policy, reviewed like code.

## Naming

- Use one file per language or framework.
- Start with a clear H1 so rule summaries are easy to extract.
- Write rules as must/should statements, not long essays.

## Optional Front Matter

You can scope rules with Markdown front matter:

```md
---
id: python-coding-standard
title: Python Coding Standard
languages: [python]
globs: ["**/*.py"]
layers: [runtime, tests]
stages: [design, build, review]
checks: [python-no-bare-except]
---
```

- `languages` controls stack matching.
- `globs` narrows rules to changed files.
- `layers` supports coarse scoping such as `runtime`, `tests`, `ui`, `data`, `scripts`, `api`.
- `stages` lets a rule apply only in `design`, `build`, or `review`.
- `checks` enables executable enforcement during quality/review.

