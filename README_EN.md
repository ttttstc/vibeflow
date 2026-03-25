**[中文](README.md) | English**

---

# VibeFlow

**Make AI deliver software with engineering discipline, not random vibe coding.**

VibeFlow is a structured delivery framework for Claude Code. It connects requirements, design, implementation, review, testing, release, and retrospectives into one recoverable workflow so AI can finish a real delivery cycle instead of just producing code.

> Think first, then let the system carry the second half of the delivery loop.

---

## Documentation Map

- [Install and get started](README_EN.md#install)
- [3-minute quick start](README_EN.md#3-minute-quick-start)
- [Common commands](README_EN.md#common-commands)
- [Detailed usage guide](USAGE.md)
- [Architecture](ARCHITECTURE.md)
- [Design contract and implementation notes](VIBEFLOW-DESIGN.md)

---

## Install

### Claude Code One-Liner

Run this inside Claude Code:

```text
/sh curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.sh | bash
```

Then activate the plugin:

```text
/plugin install vibeflow@vibeflow
```

### Windows Launcher

```powershell
irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/vibeflow-launcher.ps1 | iex
```

### Verify Installation

```text
/vibeflow
```

If Claude Code shows the VibeFlow entry flow, the plugin is installed and ready.

### Mode Selection on First Run

- First time running `/vibeflow` in a project: choose `Full Mode` or `Quick Mode`
- If `.vibeflow/state.json` already exists: VibeFlow reuses the stored mode
- If you explicitly run `/vibeflow-quick`: it enters Quick flow directly

Recommended default:
- use `Full Mode` unless the change is small, low-risk, and easy to roll back

### Ask Claude Code to Install It for You

If you want Claude Code to handle setup, paste this:

```text
Install VibeFlow into Claude Code for me.

Requirements:
1. Prefer the official install script:
   /sh curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.sh | bash
2. If that fails, install it manually into the Claude Code marketplace directory
3. After installation, run:
   /plugin install vibeflow@vibeflow
4. Then tell me:
   - whether installation succeeded
   - where it was installed
   - which command I should run next
```

### Update and Uninstall

Update:

```bash
curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.sh | bash
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.ps1 | iex
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
3. Finish the required approvals in `Think -> Plan -> Requirements -> Design`
4. Once the workflow reaches `build-init`, the system keeps going through `Build -> Review -> Test -> Ship / Reflect`
5. Use `/vibeflow-status` or `/vibeflow-dashboard` whenever you want to see progress

Short version:

- you make decisions in the first half
- the system drives the second half
- it comes back only when something is blocked or needs approval

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

## What You Get

### 1. A structured delivery flow

- `Think -> Plan -> Requirements -> Design` for framing and approval
- `Build -> Review -> Test` for implementation and verification
- optional `Ship / Reflect` for release and learning

### 2. Files as workflow state

VibeFlow keeps state in the repo instead of a chat session.

Core files include:
- `.vibeflow/state.json`
- `.vibeflow/runtime.json`
- `feature-list.json`
- `docs/changes/<change-id>/...`

That gives you:
- cross-session recovery
- machine-independent continuity
- AI-independent continuity

### 3. Automatic continuation after Build starts

Once design is locked, the system does not expect you to manually walk every build sub-step.

Default behavior:

- enter `build-init`
- continue through `build-config -> build-work -> review -> test -> ship -> reflect`
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
- feed that context into Requirements and Design

### 6. A local live dashboard

You do not need to read raw JSON and markdown files to understand what the system is doing.

The dashboard shows:
- current mode and phase
- workflow stage status
- feature status
- key artifacts
- recent events and friendly guidance

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

## What To Read In A Generated Project

Inside a target project generated by VibeFlow, most users only need these entry points:

- `README.md`
  Start here to understand what the project is and how to run it
- `docs/overview/README.md`
  The global document index for project background, current state, and architecture
- `docs/overview/CURRENT-STATE.md`
  The current project snapshot: active change, progress, and recommended next files
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

---

## Workflow at a Glance

```text
Decision phase (interactive)
Think -> Plan -> Requirements -> Design

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
| `docs/overview/README.md` | Global document index for first-time readers |
| `docs/overview/PROJECT.md` | Project background, scope, and long-lived context |
| `docs/overview/PRODUCT.md` | Product capabilities, boundaries, and user-facing shape |
| `docs/overview/ARCHITECTURE.md` | Project-level architecture summary |
| `docs/overview/CURRENT-STATE.md` | Current project snapshot |
| `.vibeflow/state.json` | Source of truth for phase, mode, active change, and checkpoints |
| `.vibeflow/runtime.json` | Runtime overlay for current action, friendly guidance, recent events, and heartbeat |
| `.vibeflow/codebase-map.json` | Reusable project-level code structure map |
| `feature-list.json` | Build-time source of truth for features and execution state |
| `docs/changes/<change-id>/context.md` | Starting context, scope, and constraints |
| `docs/changes/<change-id>/proposal.md` | Scope and value framing for this change |
| `docs/changes/<change-id>/requirements.md` | Formal requirement baseline |
| `docs/changes/<change-id>/design.md` | Implementation and integration plan |
| `docs/changes/<change-id>/tasks.md` | Executable task checklist |
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
