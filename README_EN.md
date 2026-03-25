**[中文](README.md) | English**

---

# VibeFlow

**A structured 16-phase software delivery framework** — making AI deliver software with engineering discipline, not random vibe coding.

Stop letting AI "just start coding" — VibeFlow provides file-driven deterministic routing, quality gates at every phase, and a three-perspective review system (CEO + Engineering + Design) that actually catches problems before they become production incidents.

> "VibeFlow is what happens when you take a senior engineer's discipline and give it to an AI that never gets tired, never forgets, and never ships without tests."

---

## Install

### Claude Code One-Liner (Recommended)

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.sh | bash

# Windows PowerShell
irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.ps1 | iex

# After installation, activate in Claude Code:
/plugin install vibeflow@vibeflow
```

### Claude Code Prompt

If you want Claude Code to handle the setup for you, paste this:

```text
Install VibeFlow into Claude Code for me.

Requirements:
1. Prefer the official install script first:
   /sh curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.sh | bash
2. If that fails, install the repo into the Claude Code marketplace directory manually.
3. After installation, run:
   /plugin install vibeflow@vibeflow
4. Then tell me:
   - whether installation succeeded
   - where the plugin was installed
   - which command I should run next to start using VibeFlow
```

### Windows Launcher

```powershell
irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/vibeflow-launcher.ps1 | iex
```

### Verify Installation

```bash
/vibeflow
```

If Claude Code shows the VibeFlow entry flow, the plugin is loaded and ready.

---

## Why VibeFlow

| AI Coding Without VibeFlow | With VibeFlow |
|---|---|
| "Build me an API" → jumps straight to code, no requirements | Think → Plan → Requirements → Design → then code |
| Forgets halfway through, loses everything on session switch | File persistence, instant cross-session recovery |
| Tests? Coverage? "If it looks like it works, ship it" | TDD iron law → coverage gates → mutation testing → acceptance, five quality layers |
| AI reviewing its own code | Three-perspective review (CEO value + Engineering + Design) |
| Done is done, no docs or retrospective | Ship generates release notes, Reflect produces retrospective |
| Bigger projects = more confusion, AI loses track | Deterministic routing: always knows what to do now and what comes next |

---

## Core Philosophy

**Requirements-Driven, Not Code-Driven.** Write the SRS first, then the technical design, then the code. Every feature implementation traces back to a specific requirement.

**Files as State.** All workflow state persists in repository files (`.vibeflow/state.json`, `.vibeflow/runtime.json`, `docs/changes/`, `feature-list.json`). Close the session, switch machines, even switch AIs — project state is fully preserved.

**Deterministic Routing.** `get-vibeflow-phase.py` computes the current phase by checking file existence. 16 phase states, strict elif chain, zero ambiguity.

**Template-Controlled Strictness.** Four static templates (prototype → enterprise) control which stages are mandatory and quality gate thresholds. Choose once, applied globally.

**Dependency-Aware Build.** Build still keeps feature-level discipline, but independent features can now run in parallel without breaking dependency order.

---

## Build Continuation and Dashboard

Once Design is locked, the Claude Code plugin has one default behavior:

- **reaching `build-init` makes the system continue the delivery chain automatically**
  The router keeps advancing `build-init -> build-config -> build-work -> review -> test -> ship -> reflect` until `done`, a blocker, or a manual checkpoint.

For command-line runs, CI, or dashboard-driven automation, the script entrypoint for that same automatic chain is:

- `python scripts/run-vibeflow-autopilot.py --project-root <repo>`
  Runs the same automatic continuation from the current phase until `done`, a blocker, or a manual checkpoint.
- `python scripts/run-vibeflow-build-work.py --project-root <repo> --max-workers 4`
  Runs Build-Work directly with dependency-aware parallel execution.
- `python scripts/run-vibeflow-dashboard.py --project-root <repo>`
  Starts the local live dashboard for phases, features, artifacts, and timeline events.

If you only want the current state once, print a dashboard snapshot:

```bash
python scripts/run-vibeflow-dashboard.py --project-root <repo> --snapshot-json
```

---

## 16-Phase Architecture

```
Think ── Plan ── Requirements ── Design
  │                          │
  ▼                          ▼
Office Hours (optional)  Brainstorming (optional)
                          │
                          ▼
Build-init ── Build-config ── Build-work
                                    │
                              ┌──────┴──────┐
                              ▼              ▼
                          TDD Loop      Quality Gates
                              │              │
                              ▼              ▼
                      Feature-ST ◄───── Spec-Review
                              │              │
                              └──────┬───────┘
                                     ▼
                               Review (cross-feature)
                                     │
                        ┌────────────┼────────────┐
                        ▼            ▼            ▼
                   Test-System   Test-QA        Ship
                        │            │            │
                        └────────────┴────────────┘
                                     │
                                     ▼
                                 Reflect
```

### Think

**Goal**: Define the problem, understand boundaries, scan opportunities, select workflow template.

- Produces `docs/changes/<change-id>/context.md` — the starting brief for this work package: problem, scope, goal, and constraints
- Optional: Run `vibeflow-office-hours` first to validate if the idea is worth pursuing (YC Office Hours style)
- Recommends and confirms template (prototype / web-standard / api-standard / enterprise)

### Plan

**Goal**: CEO value review — the only gate.

- Invokes `vibeflow-plan-value-review` to assess project value
- **Value review failure = project termination** (fail-fast)
- Engineering and Design perspective reviews are moved to the end of the Design phase (because that's when there's an actual design document to review)

### Requirements

**Goal**: Write Software Requirements Specification (SRS), aligned with ISO/IEC/IEEE 29148.

- Produces `docs/changes/<change-id>/requirements.md` — the formal requirement baseline that design and testing must follow
- Confirmed with user line by line; each requirement must be testable

### Design

**Goal**: Technical design + UX design + three-perspective review.

This is the most complex phase in the framework:

| Step | Skill | Output |
|---|---|---|
| 0. Problem Exploration | `vibeflow-brainstorming` (optional) | `docs/plans/*-brainstorming.md` |
| 1. Read SRS + UCD | Built-in (UCD conditional) | Design drivers extraction |
| 2. Explore Context | Built-in | Context document |
| 3. Propose Approaches | Built-in | Approach comparison |
| 4. User Section-by-Section Approval | Built-in | User sign-off |
| 5. **AI Deep Review** | `vibeflow-plan-eng-review` + `vibeflow-plan-design-review` | `docs/changes/<change-id>/design-review.md` (engineering + design review outcomes) |
| 6. **Scope Decision** | Built-in | Expand / Hold / Reduce |
| 7. Write Design Document | Built-in | `docs/changes/<change-id>/design.md` (implementation approach, integration points, validation plan) |
| 8. Transition to Initialization | Built-in | — |

### Build-init

**Goal**: Enter the automatic implementation continuation and prepare the build artifacts.

- `feature-list.json` — the feature inventory and build source of truth
- `.vibeflow/runtime.json` — the live runtime overlay used by the automatic continuation and the dashboard
- `.vibeflow/logs/session-log.md` — the human-readable progress log
- `RELEASE_NOTES.md` — the release-facing output file
- Generates `.vibeflow/work-config.json` — the active build rules and quality thresholds

### Build-config

**Goal**: Configure implementation details for each feature as part of the automatic continuation.

- Assigns phase (design/develop/test) to each feature
- Confirms external dependencies and delivery order

### Build-work

**Goal**: Implement features through the complete quality pipeline, either serially or in dependency-aware parallel lanes.

In Claude Code plugin mode, Build is no longer a sequence of manual stops. Once `build-init` begins, the system keeps running through Build, Review, Test, Ship, and Reflect unless it hits a blocker or a manual gate.

```
Pick Feature → TDD Red-Green-Refactor → Quality Gates
                                         · line coverage
                                         · branch coverage
                                         · mutation score
                                    ┌──────┴──────┐
                                    ▼              ▼
                              Feature-ST     Spec-Review
                                    │              │
                                    └──────┬──────┘
                                           ▼
                                      Acceptance
```

### Review

**Goal**: Cross-feature holistic change review.

- `vibeflow-review`: Architecture consistency, security, performance analysis
- Optional safety guardrails: `vibeflow-careful` (destructive command warnings), `vibeflow-freeze` (edit boundaries), `vibeflow-guard` (maximum safety mode)

### Test-System

**Goal**: System-level integration testing and NFR validation.

- Integration tests, E2E tests, NFR validation, exploratory testing in four parallel paths (~4x speedup)

### Test-QA

**Goal**: Browser-driven QA verification (UI projects only).

- Only runs when the workflow requires UI QA and `docs/changes/<change-id>/verification/qa.md` does not exist

### Ship

**Goal**: Prepare release artifacts.

- Version management, PR creation, tagging, changelog
- `vibeflow-ship` auto-executes; optional (`ship_required()` detection)

### Reflect

**Goal**: Review this iteration and produce improvement suggestions for the next cycle.

- Produces `.vibeflow/logs/retro-YYYY-MM-DD.md` — the retrospective record for what worked, what broke, and what to change next
- Optional (`reflect_required()` detection)

---

## Skill Superpowers Architecture

VibeFlow consists of 23 independent skills organized in five layers:

### Core Layer

| Skill | Responsibility |
|---|---|
| `vibeflow` | Framework entry point, overview and quick start |
| `vibeflow-router` | Session router, dispatches to correct phase based on file state |
| `vibeflow-think` | Think phase, problem framing and template selection |

### Planning Layer

| Skill | Responsibility |
|---|---|
| `vibeflow-plan` | Plan phase entry (invokes value-review) |
| `vibeflow-plan-value-review` | CEO perspective value review, fail-fast gate |
| `vibeflow-plan-eng-review` | Engineering perspective review (architecture, code quality, testing, performance) |
| `vibeflow-plan-design-review` | Design perspective review (information architecture, interaction, UX) |
| `vibeflow-requirements` | Software Requirements Specification (ISO 29148) |
| `vibeflow-design` | Technical design document (with inline UCD + three-perspective review) |

### Exploratory Layer (Optional)

| Skill | Responsibility |
|---|---|
| `vibeflow-office-hours` | YC Office Hours style brainstorming (pre-Think) |
| `vibeflow-brainstorming` | Problem exploration before design (pre-Design) |

### Build Layer

| Skill | Responsibility |
|---|---|
| `vibeflow-build-init` | Initialize build artifacts |
| `vibeflow-build-config` | Configure feature implementation details |
| `vibeflow-build-work` | Single-feature orchestrator, drives TDD → Quality → ST → Review pipeline |
| `vibeflow-tdd` | TDD Red-Green-Refactor cycle |
| `vibeflow-quality` | Quality gates: line coverage, branch coverage, mutation score |
| `vibeflow-feature-st` | Feature-level acceptance testing (ISO 29119) |
| `vibeflow-spec-review` | Spec compliance review, validates against SRS and Design |

### Safety Guardrails (Optional)

| Skill | Responsibility |
|---|---|
| `vibeflow-careful` | Destructive command warnings (rm -rf, DROP TABLE, etc.) |
| `vibeflow-freeze` | Edit boundary restrictions (limits Edit/Write to specified directory) |
| `vibeflow-guard` | Maximum safety mode (combines careful + freeze) |
| `vibeflow-unfreeze` | Clear freeze boundary |

### Verification & Release Layer

| Skill | Responsibility |
|---|---|
| `vibeflow-review` | Cross-feature holistic change review |
| `vibeflow-test-system` | System-level integration tests and NFR validation |
| `vibeflow-test-qa` | Browser-driven QA verification (UI projects only) |
| `vibeflow-ship` | Version release, PR creation, changelog |
| `vibeflow-reflect` | Iteration retrospective and improvement suggestions |

### Skill Call Graph

```
Session Start
    │
    ▼
vibeflow-router ──── get-vibeflow-phase.py ──── detects 16 phase states
    │
    ├── think ─────────── vibeflow-think
    │       └── [optional] vibeflow-office-hours
    │
    ├── plan ───────────── vibeflow-plan
    │       └── Step 1: ── vibeflow-plan-value-review
    │
    ├── requirements ───── vibeflow-requirements
    │
    ├── design ──────────── vibeflow-design
    │       ├── [optional] vibeflow-brainstorming
    │       ├── Step 1: ── Read SRS + conditional UCD
    │       ├── Step 5: ── vibeflow-plan-eng-review
    │       └── Step 5: ── vibeflow-plan-design-review
    │
    ├── build-init ──────── vibeflow-build-init
    ├── build-config ───── vibeflow-build-config
    ├── build-work ─────── vibeflow-build-work
    │                        ├── vibeflow-tdd
    │                        ├── vibeflow-quality
    │                        ├── vibeflow-feature-st
    │                        └── vibeflow-spec-review
    │
    ├── review ──────────── vibeflow-review
    │       └── [optional] vibeflow-careful / freeze / guard
    │
    ├── test-system ─────── vibeflow-test-system
    ├── test-qa ────────── vibeflow-test-qa
    ├── ship ────────────── vibeflow-ship
    └── reflect ─────────── vibeflow-reflect
```

---

## Template System

Four static templates control workflow strictness:

| Dimension | Prototype | Web-Standard | API-Standard | Enterprise |
|---|---|---|---|---|
| **Think Depth** | quick | standard | standard | deep |
| **Plan Review** | CEO reduction mode | CEO hold mode | CEO hold mode | CEO expansion mode |
| **Requirements** | Required | Required | Required | Required |
| **UCD** | On demand | On demand | On demand | On demand |
| **TDD** | Required | Required | Required | Required |
| **Line Coverage** | 60% | 90% | 90% | 95% |
| **Branch Coverage** | 40% | 80% | 80% | 85% |
| **Mutation Score** | 50% | 80% | 80% | 85% |
| **Feature Acceptance** | Optional | Required | Optional | Required |
| **Spec Review** | Optional | Required | Required | Required |
| **Global Review** | Optional | Required | Required | Required |
| **System Testing** | Optional | Required | Required | Required |
| **QA Testing** | Optional (skip if no UI) | On demand | On demand | On demand |
| **Reflection** | Optional | Optional | Optional | Required |
| **Version Strategy** | manual | semver | semver | semver |
| **Best For** | Hackathons, POC | Web apps | API services | Enterprise/compliance |

---

## Project State Files

### Runtime State (`.vibeflow/`)

| File | Purpose |
|---|---|
| `state.json` | Central workflow state: phase, mode, active change package; this is the primary routing anchor |
| `runtime.json` | Live runtime overlay: current implementation-loop action, friendly guidance, recent events, and heartbeat; the dashboard reads this directly |
| `workflow.yaml` | Active workflow config copied from a template; decides which stages are required |
| `work-config.json` | Build config: enabled steps and quality thresholds; Build enforces this file |
| `phase-history.json` | Phase progression history; records routing changes, increments, and automation events |
| `logs/session-log.md` | Human-readable process log; useful for understanding what just happened |
| `increments/queue.json` | Increment request queue; stages additional changes outside the active package |
| `increments/requests/*.json` | Increment request details; records add/modify/deprecate/doc update actions |
| `logs/retro-YYYY-MM-DD.md` | Iteration retrospective; feeds the next cycle |

### Delivery Artifacts

| File | Purpose |
|---|---|
| `docs/changes/<change-id>/context.md` | Problem context document; explains why this work starts and what it is bounded by |
| `docs/changes/<change-id>/proposal.md` | Proposal document; records scope, value, and whether the work should proceed |
| `docs/changes/<change-id>/requirements.md` | Software Requirements Specification; the baseline for implementation and acceptance |
| `docs/changes/<change-id>/ucd.md` | UX/UCD document; only appears when UI design is in scope |
| `docs/changes/<change-id>/design.md` | Technical design document; explains implementation, integration points, and validation |
| `docs/changes/<change-id>/design-review.md` | Design review outcome; captures engineering and design review feedback |
| `docs/changes/<change-id>/tasks.md` | Execution checklist; turns the design into implementable and verifiable tasks |
| `docs/changes/<change-id>/verification/review.md` | Review report; records cross-feature review conclusions |
| `docs/changes/<change-id>/verification/system-test.md` | System test report; records integration and end-to-end verification |
| `docs/changes/<change-id>/verification/qa.md` | QA report; records browser and interaction verification results |
| `docs/test-cases/feature-*.md` | Feature test case documents; executable cases for feature-level acceptance |
| `feature-list.json` | Feature inventory; the single source of truth during Build, including dependencies, status, verification steps, and automation commands |
| `.vibeflow/logs/session-log.md` | Task progress log; useful for humans, no longer the state authority |
| `RELEASE_NOTES.md` | Release notes; a delivery output, not a routing signal |

---

## Repository Structure

```text
vibeflow/
├── skills/                          # 23 workflow skills
│   ├── vibeflow/                    # Framework entry
│   ├── vibeflow-router/             # Session router
│   ├── vibeflow-think/              # Think phase
│   ├── vibeflow-office-hours/      # YC Office Hours (optional)
│   ├── vibeflow-plan/               # Plan phase entry
│   ├── vibeflow-plan-value-review/ # CEO value review
│   ├── vibeflow-plan-eng-review/    # Engineering review
│   ├── vibeflow-plan-design-review/# Design review
│   ├── vibeflow-requirements/       # Requirements spec
│   ├── vibeflow-design/             # Technical design (with inline UCD + 3-perspective review)
│   ├── vibeflow-brainstorming/      # Problem exploration (optional)
│   ├── vibeflow-build-init/         # Build initialization
│   ├── vibeflow-build-config/       # Build configuration
│   ├── vibeflow-build-work/         # Feature orchestration
│   ├── vibeflow-tdd/                # TDD cycle
│   ├── vibeflow-quality/            # Quality gates
│   ├── vibeflow-feature-st/         # Feature acceptance
│   ├── vibeflow-spec-review/        # Spec review
│   ├── vibeflow-review/             # Global review
│   ├── vibeflow-careful/            # Destructive command warnings
│   ├── vibeflow-freeze/             # Edit boundary
│   ├── vibeflow-guard/              # Maximum safety mode
│   ├── vibeflow-unfreeze/           # Clear freeze
│   ├── vibeflow-test-system/        # System testing
│   ├── vibeflow-test-qa/            # QA testing
│   ├── vibeflow-ship/               # Release
│   └── vibeflow-reflect/             # Reflection
├── scripts/                         # Python scripts
│   ├── get-vibeflow-phase.py        # Phase detection (16-state router)
│   ├── run-vibeflow-autopilot.py    # Command-line entrypoint for the automatic build continuation
│   ├── run-vibeflow-build-work.py   # Build-Work executor with dependency-aware parallelism
│   ├── run-vibeflow-dashboard.py    # Local live dashboard
│   ├── new-vibeflow-config.py       # Workflow config generation
│   ├── new-vibeflow-work-config.py  # Build config generation
│   ├── vibeflow_automation.py       # implementation-loop / build orchestration core
│   └── vibeflow_dashboard.py        # dashboard snapshot + SSE server
├── templates/                       # Static workflow templates
│   ├── prototype.yaml
│   ├── web-standard.yaml
│   ├── api-standard.yaml
│   └── enterprise.yaml
├── hooks/                           # Session hooks
│   ├── hooks.json
│   ├── session-start.ps1
│   └── session-start.sh
├── claude-code/                     # Claude Code Marketplace installers
│   ├── install.sh
│   └── install.ps1
├── .claude-plugin/                  # Claude Code plugin metadata
│   ├── plugin.json
│   └── marketplace.json
└── install.sh                       # OpenCode installer
```

---

## Documentation

| Document | Description |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Full architecture diagrams and component descriptions |
| [USAGE.md](USAGE.md) | Operating guide for target projects |
| [VIBEFLOW-DESIGN.md](VIBEFLOW-DESIGN.md) | Design contract and skill catalog |

---

## License

MIT
