**[中文](README.md) | English**

<div align="center">

# VibeFlow

### Make AI produce not just code, but a delivery path that actually completes

> "Well begun is half done."
>
> First establish the form, then let the system carry the work to completion.

[Install](#install) · [3-Minute Quick Start](#3-minute-quick-start) · [Core Capabilities](#core-capabilities) · [Comparison](#vibeflow-vs-leading-ai-harness-frameworks)

</div>

---

<img width="1376" height="768" alt="VibeFlow vs traditional AI coding" src="https://github.com/user-attachments/assets/9a3be1a9-270c-46fc-b303-67b451ed860f" />

## What VibeFlow Is

VibeFlow is an AI software delivery control plane for Claude Code.

It does not try to think for the agent, and it does not try to rebuild the runtime. Its job is simpler and more useful: it turns one AI-driven software change into a workflow that can actually finish, instead of leaving progress scattered across chat history.

In one sentence: **VibeFlow turns AI coding from chat-driven improvisation into a delivery workflow.**

---

## Core Capabilities

| Capability | What VibeFlow does |
|---|---|
| Turns ideas into plans | Clarifies scope, solution, and task breakdown before implementation |
| Helps work actually finish | Keeps moving through review, testing, release, and reflection |
| Keeps work resumable | Lets teams continue after interruption, handoff, or a new session |
| Leaves evidence behind | Preserves review, test, and delivery output instead of hiding progress in chat |
| Reduces drift | Uses phases, rules, and gates so the model is less likely to wander |
| Makes complex work steadier | Breaks large work into smaller, recoverable, verifiable chunks |
| Makes progress visible | Shows what stage you are in, what is blocked, and what comes next |
| Fits real repositories | Works on ongoing repositories, not only fresh project templates |

---

## Install

### Option 1: Install It Yourself

Installs the latest released version by default.

| Platform | Install Command | After Install |
|---|---|---|
| macOS / Linux | `/sh curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.sh \| bash` | run `/plugin install vibeflow@vibeflow` |
| Windows PowerShell | `irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.ps1 \| iex` | run `/plugin install vibeflow@vibeflow` |

<details>
<summary>Pin a specific version</summary>

| Platform | Command |
|---|---|
| macOS / Linux | `/sh curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.sh \| VIBEFLOW_VERSION=v1.0.0 bash` |
| Windows | `$env:VIBEFLOW_VERSION="v1.0.0"; irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.ps1 \| iex` |

</details>

### Option 2: Ask AI to Install It

<details>
<summary>Paste this into Claude Code</summary>

```text
Install VibeFlow for me and make sure it actually works.

Requirements:
1. Choose the official install command based on the current OS:
   - macOS / Linux:
     /sh curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.sh | bash
   - Windows:
     irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.ps1 | iex
2. If I give you a version number, install that version. Otherwise install the latest released version
3. If that fails, install it manually into the Claude Code marketplace directory
4. After installation, run:
   /plugin install vibeflow@vibeflow
5. Verify the result by running /vibeflow after restart or refresh
6. If something fails, keep debugging until it works or tell me exactly what is blocking it
7. Then tell me:
   - whether installation succeeded
   - where it was installed
   - the installed version
   - how I should start using it
```

</details>

### Other Hosts

Install entry points for Codex, OpenCode, and other hosts still exist in the repository, but this README keeps the primary install path focused on Claude Code so the main onboarding flow stays clear.

### Verify Installation

Run `/vibeflow` and confirm the VibeFlow entry flow appears.

<details>
<summary>Update and Uninstall</summary>

Update uses the same install commands. After updating, restart Claude Code and run `/plugin install vibeflow@vibeflow`.

To uninstall: close Claude Code → remove the marketplace directory → remove the `vibeflow` entry from `known_marketplaces.json` → reopen Claude Code.

</details>

---

## 3-Minute Quick Start

1. Install and activate the plugin, then run `/vibeflow`
2. On first run, choose `Full Mode` or `Quick Mode`
3. Finish the required approvals in `Spark → Design → Tasks`
4. Once the workflow reaches `Build`, the system keeps going through `Review → Test → Ship / Reflect`
5. Use `/vibeflow-status` or `/vibeflow-dashboard` whenever you want to see progress

Short version: **You make decisions in the first half. The system drives the second half. It comes back only when something is blocked.**

<img width="1377" height="768" alt="Mode selection" src="https://github.com/user-attachments/assets/77257c8b-ba38-4f24-a11e-7920e4297165" />

> **Mode selection tip:** Use `Full Mode` unless the change is small, low-risk, and easy to roll back. If `.vibeflow/state.json` already exists, VibeFlow reuses the stored mode automatically.

---

## Common Commands

| Need | Command |
|---|---|
| Start or resume the workflow | `/vibeflow` |
| Fast-track a small change | `/vibeflow-quick` |
| View a quick status summary | `/vibeflow-status` |
| Open the live dashboard | `/vibeflow-dashboard` |
| Start dashboard from CLI | `python scripts/run-vibeflow-dashboard.py` |
| Print one dashboard snapshot | `python scripts/run-vibeflow-dashboard.py --snapshot-json` |
| Continue the current workflow from CLI | `python scripts/run-vibeflow-autopilot.py --project-root <repo>` |

---

## Deep Dive

In a real project, what VibeFlow gives you is not a pile of prompts. It is a delivery mechanism that can keep running.

### Structured Delivery Flow

- `Spark → Design → Tasks` for framing, solutioning, and execution handoff
- `Build → Review → Test` for implementation and verification
- Optional `Ship / Reflect` for release and learning

<img width="1376" height="768" alt="Delivery flow" src="https://github.com/user-attachments/assets/410e78e6-70c5-4e72-99e6-0855e6c889eb" />

### Files as Workflow State

VibeFlow keeps state in the repo instead of a chat session. Close the session, switch machines, switch AI models — the work persists.

<img width="1376" height="768" alt="File-driven state" src="https://github.com/user-attachments/assets/eb46f4ea-6510-4118-823b-d2cf2940cb08" />

### Automatic Continuation After Build

Once design is locked, you don't manually walk every sub-step. The system enters `Build` and auto-continues through `Review → Test → Ship → Reflect`, stopping only when done, blocked, or awaiting approval.

### Stable Implementation Loop

Build is no longer "throw a huge context window at the model and hope it stays focused." Current capabilities include:

- Feature-level implementation inputs with `design.md + tasks.md + feature-list.json + rules/` as primary inputs
- Normalized feature contracts and execution evidence saved in `feature-list.json`
- Dependency-aware build execution with safe fallback to serial
- Review split into "did we build the right thing?" and "is the code solid?"

### Existing Repository Support

VibeFlow is not only for greenfield work. It maintains a project-level codebase map, generates change-scoped impact analysis, and feeds that context into Spark and Design automatically.

<img width="1376" height="768" alt="Existing project support" src="https://github.com/user-attachments/assets/e658a4ca-75ba-414a-845a-71a9e623debb" />

### Local Live Dashboard

No need to read raw JSON and markdown files. The dashboard shows current mode/phase, workflow stage status, feature status, key artifacts, recent events, and next-action guidance.

### Quality Loop

The default path includes: TDD, coverage gates, mutation testing, feature acceptance, global review, system testing, and QA for UI flows when needed.

### Increments, Release, and Retrospectives

Beyond the main workflow: increment request queues, release notes, and retrospective logs.

### Templates and Safety Guardrails

Four templates control workflow strictness and quality thresholds. `careful / freeze / guard` safety rails restrict destructive commands and edit boundaries.

<img width="1376" height="768" alt="Templates and safety guardrails" src="https://github.com/user-attachments/assets/1e0cbb71-9abf-4920-8533-509afe333e81" />

---

## VibeFlow vs Leading AI Harness Frameworks

Note: `High / Medium / Low` indicates how central that capability is to each framework.

| Framework | Spec-first | Engineering discipline | Long-task stability | Multi-agent orchestration | Verification loop | Project memory | Delivery wrap-up | Weight |
|---|---|---|---|---|---|---|---|---|
| OpenSpec | High | Low | Medium | Low | Low | Medium | Low | Low |
| Superpowers | Medium | High | Medium | Medium | Medium | Low | Low | Medium |
| GSD | Medium | Medium | High | Medium | Medium | Medium | Medium | Medium |
| OMC | Low | Medium | Medium | High | Medium | Medium | Medium | Medium-High |
| ECC | Medium | High | High | Medium | High | High | Medium | High |
| Trellis | High | Medium | High | Medium | Medium | High | Medium | Medium-High |
| **VibeFlow** | **High** | **High** | **High** | Medium | **High** | Medium-High | **High** | Medium-High |

---

## Key Artifacts

### Project-Level (`docs/overview/`)

| File | Purpose |
|---|---|
| `PROJECT.md` | Project background, scope, and long-lived context |
| `ARCHITECTURE.md` | Project-level architecture summary |
| `CURRENT-STATE.md` | Current project snapshot: active change, progress, and recommended next files |

### Change-Level (`docs/changes/<change-id>/`)

| File | Purpose |
|---|---|
| `brief.md` | Goal, scope, constraints, and acceptance baseline |
| `design.md` | Implementation plan and Build Contract source of truth |
| `tasks.md` | Execution-grade task handoff |
| `docs/overview/CURRENT-STATE.md` | Current change focus, affected areas, and recommended reading order |
| `verification/review.md` | Global review result |
| `verification/system-test.md` | System test result |
| `verification/qa.md` | UI / browser verification result |

### System and Config

| File | Purpose |
|---|---|
| `.vibeflow/state.json` | Source of truth for phase, mode, active change, checkpoints, and resume guidance |
| `feature-list.json` | Build-time source of truth for features and execution state |
| `rules/` | Project custom constraints; takes precedence over `CLAUDE.md` / `AGENT.md` |
| `RELEASE_NOTES.md` | Release-facing summary |

> Short version: project context → `docs/overview/`, current change → `docs/changes/<change-id>/`, implementation progress → `feature-list.json`. Most users don't need to read `.vibeflow/` directly.

> If Claude closes unexpectedly, running `/vibeflow` again resumes from the interrupted step, showing the current phase, why it paused, what to do next, and which files to open first.

---

## Best Fit

**Good fit:**
- New projects from zero to one, or continuous iteration on existing repos
- Teams that want AI to drive full delivery, not only generate code
- Teams that need recoverable, traceable, auditable workflows
- Builders who want the system to keep going after Build starts

**Not a fit:**
- You only want AI to make a tiny ad-hoc edit
- You don't want to maintain state files or verification artifacts

---

## Documentation

| Document | Description |
|---|---|
| [USAGE.md](USAGE.md) | Detailed operating guide, commands, and target-project usage |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Architecture diagrams, state model, and component boundaries |
| [VIBEFLOW-DESIGN.md](VIBEFLOW-DESIGN.md) | Naming rules, file layout, and implementation conventions |
| [DeepWiki Architecture](https://deepwiki.com/ttttstc/vibeflow/1-vibeflow-overview) | Online deep-dive architecture docs |

---

## Learning Site

[Visit the learning site](https://ttttstc.github.io/vibeflow)

---

## License

MIT

<img width="1376" height="768" alt="VibeFlow" src="https://github.com/user-attachments/assets/3c2f8d03-ae18-41b8-844a-de8cfa45c9c0" />
