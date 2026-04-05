**[中文](README.md) | English**

---

<div align="center">

# VibeFlow

### Make AI produce not just code, but a delivery path that actually completes

> “Well begun is half done.”
>
> First establish the form, then let the system carry the work to completion.

[Install](#install) · [3-Minute Quick Start](#3-minute-quick-start) · [Core Capabilities](#core-capabilities) · [Comparison](#vibeflow-vs-leading-ai-harness-frameworks)

</div>

---

## What VibeFlow Is

VibeFlow is an AI software delivery control plane for Claude Code.

It does not try to think for the agent, and it does not try to rebuild the runtime. Its job is simpler and more useful: it turns one AI-driven software change into a workflow that can actually finish, instead of leaving progress scattered across chat history.

That workflow is not only about writing code. It also covers:

- requirements and scope
- design and task breakdown
- implementation progress
- review and test evidence
- release and retrospective output

In one sentence:

**VibeFlow turns AI coding from chat-driven improvisation into a delivery workflow.**

## Documentation Map

- [Install](README_EN.md#install)
- [3-minute quick start](README_EN.md#3-minute-quick-start)
- [Core capabilities](README_EN.md#core-capabilities)
- [Common commands](README_EN.md#common-commands)
- [Detailed usage guide](USAGE.md)
- [Architecture](ARCHITECTURE.md)
- [Deep Technical Architecture Overview](https://deepwiki.com/ttttstc/vibeflow/1-vibeflow-overview)
- [Design contract and implementation notes](VIBEFLOW-DESIGN.md)

---

## Install

### Option 1: Install It Yourself

The default behavior installs the latest released version. To pin a version, add `VIBEFLOW_VERSION=v1.0.0`.

| Platform | Install Command | After Install |
|---|---|---|
| macOS / Linux | `/sh curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.sh \| bash` | run `/plugin install vibeflow@vibeflow` |
| Windows PowerShell | `irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.ps1 \| iex` | run `/plugin install vibeflow@vibeflow` |

Pinned version examples:

| Platform | Version-Pinned Command |
|---|---|
| macOS / Linux | `/sh curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.sh \| VIBEFLOW_VERSION=v1.0.0 bash` |
| Windows | `$env:VIBEFLOW_VERSION="v1.0.0"; irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.ps1 \| iex` |

### Verify Installation

Run `/vibeflow` and confirm the VibeFlow entry flow appears.

### Mode Selection on First Run

- First time running `/vibeflow` in a project: choose `Full Mode` or `Quick Mode`
- If `.vibeflow/state.json` already exists: VibeFlow reuses the stored mode
- If you explicitly run `/vibeflow-quick`: it enters Quick flow directly

Recommended default:
- use `Full Mode` unless the change is small, low-risk, and easy to roll back

### Option 2: Ask AI to Install It

If you want Claude Code to handle setup, paste this:

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

### Other Hosts

If you are not using Claude Code:

| Host | Command |
|---|---|
| Codex / macOS / Linux | `curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/codex/install.sh \| bash` |
| Codex / Windows PowerShell | `irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/codex/install.ps1 \| iex` |
| OpenCode / macOS / Linux | `curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/opencode/install.sh \| bash` |

### Update and Uninstall

Update uses the same commands as install.

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.sh | bash
```

Specific version on macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.sh | VIBEFLOW_VERSION=v1.0.0 bash
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.ps1 | iex
```

Specific version on Windows:

```powershell
$env:VIBEFLOW_VERSION="v1.0.0"; irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.ps1 | iex
```

After updating, restart Claude Code and run:

```text
/plugin install vibeflow@vibeflow
```

To uninstall:
1. close Claude Code
2. remove the marketplace directory
3. remove the `vibeflow` entry from `known_marketplaces.json`
4. reopen Claude Code

---

## 3-Minute Quick Start

1. Install and activate the plugin, then run `/vibeflow`
2. On first run, choose `Full Mode` or `Quick Mode`
3. Finish the required approvals in `Spark -> Design -> Tasks`
4. Once the workflow reaches `Build`, the system keeps going through `Review -> Test -> Ship / Reflect`
5. Use `/vibeflow-status` or `/vibeflow-dashboard` whenever you want to see progress

Short version:

- you make decisions in the first half
- the system drives the second half
- it comes back only when something is blocked or needs approval

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

## What You Get

In a real project, what VibeFlow gives you is not a pile of prompts. It is a delivery mechanism that can keep running.

### 1. A structured delivery flow

- `Spark -> Design -> Tasks` for framing, solutioning, and execution handoff
- `Build -> Review -> Test` for implementation and verification
- optional `Ship / Reflect` for release and learning

### 2. Files as workflow state

VibeFlow keeps state in the repo instead of a chat session.

Core files include:
- `.vibeflow/state.json`
- `feature-list.json`
- `docs/changes/<change-id>/...`

That gives you:
- cross-session recovery
- machine-independent continuity
- AI-independent continuity

### 3. Automatic continuation after Build starts

Once design is locked, the system does not expect you to manually walk every build sub-step.

Default behavior:

- enter `Build`
- complete internal build preparation, then continue through `Review -> Test -> Ship -> Reflect`
- stop only when the work is done, blocked, or waiting for approval

### 4. A more stable implementation loop

Build is no longer “throw a huge context window at the model and hope it stays focused.”

Current capabilities include:
- feature-level implementation inputs
- dependency-aware build execution
- safe fallback to serial execution
- review results split into “did we build the right thing?” and “is the code solid?”

### 5. Support for existing repositories

VibeFlow is not only for greenfield work.

It can now:
- maintain a reusable project-level codebase map
- generate change-scoped impact analysis
- feed that context into Spark and Design

### 6. A local live dashboard

You do not need to read raw JSON and markdown files to understand what the system is doing.

The dashboard shows:
- current mode and phase
- workflow stage status
- feature status
- key artifacts
- recent events, resume reason, and next-action guidance

### 7. A quality loop

The default path already includes:
- TDD
- coverage gates
- mutation testing
- feature acceptance
- global review
- system testing
- QA for UI flows when needed

### 8. Increments, release, and retrospectives

In addition to the main workflow, VibeFlow also supports:
- increment request queues
- release notes
- retrospective logs

### 9. Template strictness and safety guardrails

VibeFlow is not a single fixed-intensity workflow.

It also includes:
- four templates to control workflow strictness and quality thresholds
- `careful / freeze / guard` safety rails for destructive commands and edit boundaries

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
| VibeFlow | High | High | High | Medium | High | Medium-High | High | Medium-High |

## What To Read In A Generated Project

Inside a target project generated by VibeFlow, most users only need these entry points:

- `README.md`
  Start here to understand what the project is and how to run it
- `docs/overview/CURRENT-STATE.md`
  The current project snapshot: active change, progress, and recommended next files
- `docs/overview/PROJECT.md`
  Long-lived project positioning, stable capabilities, and product boundaries
- `docs/overview/ARCHITECTURE.md`
  Long-lived architecture and module boundaries
- `docs/changes/<change-id>/`
  The full design, tasks, and verification for the current change
- `feature-list.json`
  The main implementation progress table
- `RELEASE_NOTES.md`
  Shipped changes and release output

Short version:

- whole project context: `docs/overview/`
- current change: `docs/changes/<change-id>/`
- implementation progress: `feature-list.json`

Most users do not need to read `.vibeflow/` directly. Those files mainly exist for internal workflow state.

If Claude closes unexpectedly, running `/vibeflow` again resumes from the interrupted step and explicitly tells you:

- the current phase
- why the workflow is paused there
- what you should do next
- which files to open first

---

## Workflow at a Glance

```text
Decision phase (interactive)
Spark -> Design -> Tasks

Execution phase (automatic continuation)
Build -> Review -> Test

Optional finish
Ship -> Reflect
```

`Quick Mode` compresses the front half, but still keeps Review and Test.  
`Full Mode` is the default path for most serious work.

---

## Key Artifacts

| File | Purpose |
|---|---|
| `docs/overview/PROJECT.md` | Project background, scope, and long-lived context |
| `docs/overview/ARCHITECTURE.md` | Project-level architecture summary |
| `docs/overview/CURRENT-STATE.md` | Current project snapshot |
| `.vibeflow/state.json` | Source of truth for phase, mode, active change, checkpoints, and resume guidance |
| `rules/` | Optional project custom constraints; when present they are treated as spec-side input and take precedence over root `CLAUDE.md` / `AGENT.md` guidance |
| `feature-list.json` | Build-time source of truth for features and execution state |
| `docs/changes/<change-id>/brief.md` | Goal, scope, constraints, and acceptance baseline |
| `docs/changes/<change-id>/design.md` | Implementation, review summary, and integration plan |
| `docs/changes/<change-id>/tasks.md` | Execution-grade task handoff |
| `docs/changes/<change-id>/codebase-impact.md` | What parts of the current repo this change touches |
| `docs/changes/<change-id>/verification/review.md` | Global review result |
| `docs/changes/<change-id>/verification/system-test.md` | System test result |
| `docs/changes/<change-id>/verification/qa.md` | UI / browser verification result |
| `RELEASE_NOTES.md` | Release-facing summary |

For deeper operational details, see [USAGE.md](USAGE.md).

---

## Best Fit

- New projects from zero to one
- Existing repositories that keep evolving
- Teams that want recoverable, traceable AI-assisted delivery
- Builders who want the system to keep going after Build starts
- Projects where a dashboard and artifact trail matter

If you only want AI to make a tiny ad-hoc edit, VibeFlow may feel heavy.  
If you want to manage the delivery process itself, VibeFlow is a better fit.

---

## Documentation

| Document | Description |
|---|---|
| [USAGE.md](USAGE.md) | Detailed operating guide, commands, and target-project usage |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Architecture diagrams, state model, and component boundaries |
| [VIBEFLOW-DESIGN.md](VIBEFLOW-DESIGN.md) | Naming rules, file layout, and implementation conventions |

---

## License

MIT
