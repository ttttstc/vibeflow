# VibeFlow

**A structured seven-stage software delivery framework** — making AI deliver software with engineering discipline, not random vibe coding.

English | [中文](README.zh-CN.md)

---

## Quick Start

```bash
# 1. Install vibeflow as a skill for Claude Code
#    (place the skills/ directory in your project or global skill path)

# 2. Start the Think phase in your target project
#    AI will write .vibeflow/think-output.md and recommend a template

# 3. Generate workflow config
python scripts/new-vibeflow-config.py --template api-standard --project-root <your-project>

# 4. Generate build config (controls which steps are enabled, quality thresholds)
python scripts/new-vibeflow-work-config.py --project-root <your-project>

# 5. Detect current phase (session hook calls this automatically)
python scripts/get-vibeflow-phase.py --project-root <your-project> --json

# 6. Start working — AI routes to the correct skill based on phase
```

---

## Why VibeFlow

| AI Coding Without VibeFlow | With VibeFlow |
|---|---|
| "Build me an API" → jumps straight to code, no requirements | Think → problem framing → template → SRS → design → then code |
| Forgets halfway through, loses everything on session switch | `feature-list.json` + `task-progress.md` persist all state across sessions |
| Tests? Coverage? "If it looks like it works, ship it" | TDD iron law → coverage gates → mutation testing → acceptance → spec review — five quality layers |
| Code review is AI reviewing its own code | Structured spec review: validates compliance against SRS and Design line by line |
| Done is done, no docs or retrospective | Ship phase generates release notes, Reflect phase produces retrospective and improvement suggestions |
| Bigger projects = more confusion, AI loses track | File-driven deterministic routing: AI always knows what to do now and what comes next |

---

## Core Philosophy

### 1. Requirements-Driven, Not Code-Driven

Write the requirements spec (SRS) first, then the technical design, then the code. Every feature implementation traces back to a specific requirement.

### 2. Files as State

All workflow state is persisted in repository files (`.vibeflow/`, `docs/plans/`, `feature-list.json`). No dependence on AI memory or chat history. Close the session, switch machines, even switch AIs — project state is fully preserved.

### 3. Deterministic Routing

`get-vibeflow-phase.py` computes the current phase deterministically by checking file existence and feature status. 16 phase states, strict elif chain, zero ambiguity.

### 4. Template-Controlled Strictness

Four static templates (prototype → enterprise) control which stages are mandatory, quality gate thresholds, whether UI testing and reflection are required. Choose once, applied globally.

### 5. Single-Feature Cycle

Build phase processes one feature at a time. Each feature must complete the full TDD → Quality → Feature-ST → Spec-Review pipeline before it's considered done. Eliminates the "write everything first, test later" anti-pattern.

---

## Seven-Stage Architecture

```
Think → Plan → Build → Review → Test → Ship → Reflect
  │        │       │        │        │       │       │
  ▼        ▼       ▼        ▼        ▼       ▼       ▼
Problem   SRS    TDD      Cross-   System  Release  Retro
framing   Design Quality  feature  test    artifact  Lessons
Template  UCD    Gates    audit    QA      Version   Metrics
```

### Stage 1: Think

**Goal**: Define the problem, understand boundaries, scan opportunities, select workflow template.

- Produces `.vibeflow/think-output.md`: problem statement, scope boundaries, user profile, complexity assessment, opportunity scan
- Recommends and confirms template (prototype / web-standard / api-standard / enterprise)
- Generates `.vibeflow/workflow.yaml`

### Stage 2: Plan

**Goal**: Get scope approval, write requirements spec, produce technical design.

| Sub-stage | Skill | Output |
|---|---|---|
| Plan Review | `vibeflow-plan-review` | `.vibeflow/plan-review.md` |
| Requirements | `vibeflow-requirements` | `docs/plans/*-srs.md` |
| UI Design | `vibeflow-ucd` | `docs/plans/*-ucd.md` (when needed) |
| Technical Design | `vibeflow-design` | `docs/plans/*-design.md` |

### Stage 3: Build

**Goal**: Implement features one at a time, each passing through the full quality pipeline.

```
Init → Pick Feature → TDD Red-Green-Refactor → Quality Gates → Acceptance → Spec Review → Next Feature
                           │                        │               │              │
                           ▼                        ▼               ▼              ▼
                     vibeflow-tdd            vibeflow-quality  vibeflow-     vibeflow-
                                             · line coverage   feature-st   spec-review
                                             · branch coverage
                                             · mutation score
```

- `vibeflow-build-init`: Scaffolds `feature-list.json`, `task-progress.md`, `RELEASE_NOTES.md`
- `vibeflow-build-work`: Orchestrates single-feature flow through TDD → Quality → Feature-ST → Spec-Review
- `.vibeflow/work-config.json`: Trims steps per template (prototype skips spec review, enterprise enforces all)

### Stage 4: Review

**Goal**: Cross-feature holistic change review.

- `vibeflow-review`: Analyzes the full branch diff for architecture consistency, security, performance
- Produces `.vibeflow/review-report.md`

### Stage 5: Test

**Goal**: System-level testing and QA verification.

- `vibeflow-test-system`: Integration tests, E2E tests, non-functional requirement validation
- `vibeflow-test-qa`: Browser-driven QA testing (UI projects only)
- Produces `docs/plans/*-st-report.md`, `.vibeflow/qa-report.md`

### Stage 6: Ship

**Goal**: Prepare release artifacts.

- `vibeflow-ship`: Version management, PR creation, tagging, release documentation
- Produces `RELEASE_NOTES.md`

### Stage 7: Reflect

**Goal**: Review the iteration, produce improvement suggestions for the next cycle.

- `vibeflow-reflect`: Metrics analysis — one-pass rate, defect density, coverage trends
- Produces `.vibeflow/retro-YYYY-MM-DD.md`

---

## 18-Skill Architecture

VibeFlow consists of 18 independent skills organized in four layers:

### Core Layer

| Skill | Responsibility |
|---|---|
| `vibeflow` | Framework entry point, seven-stage overview and quick start |
| `vibeflow-router` | Session router, dispatches to correct phase skill based on file state |
| `vibeflow-think` | Think phase, problem framing and template selection |

### Planning Layer

| Skill | Responsibility |
|---|---|
| `vibeflow-plan-review` | Scope review before spec writing |
| `vibeflow-requirements` | Software Requirements Specification (SRS), aligned with ISO/IEC/IEEE 29148 |
| `vibeflow-ucd` | UI Component Design document, design system and component specs |
| `vibeflow-design` | Technical design document, architecture and data models |

### Build Layer

| Skill | Responsibility |
|---|---|
| `vibeflow-build-init` | Initialize build artifacts (`feature-list.json`, etc.) |
| `vibeflow-build-work` | Single-feature orchestrator, drives TDD → Quality → ST → Review pipeline |
| `vibeflow-tdd` | TDD Red-Green-Refactor cycle |
| `vibeflow-quality` | Quality gates: line coverage, branch coverage, mutation score |
| `vibeflow-feature-st` | Feature-level acceptance testing, ISO/IEC/IEEE 29119 test case docs |
| `vibeflow-spec-review` | Spec compliance review, validates against SRS and Design |

### Verification & Release Layer

| Skill | Responsibility |
|---|---|
| `vibeflow-review` | Cross-feature holistic change review |
| `vibeflow-test-system` | System-level integration and NFR testing |
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
    ├── think ────────── vibeflow-think
    ├── plan-review ──── vibeflow-plan-review
    ├── requirements ─── vibeflow-requirements
    ├── ucd ──────────── vibeflow-ucd
    ├── design ───────── vibeflow-design
    ├── build-init ───── vibeflow-build-init
    ├── build-work ───── vibeflow-build-work
    │                        ├── vibeflow-tdd
    │                        ├── vibeflow-quality
    │                        ├── vibeflow-feature-st
    │                        └── vibeflow-spec-review
    ├── review ───────── vibeflow-review
    ├── test-system ──── vibeflow-test-system
    ├── test-qa ──────── vibeflow-test-qa
    ├── ship ─────────── vibeflow-ship
    └── reflect ──────── vibeflow-reflect
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
| **Best For** | Hackathons, POCs | Web apps | API services | Enterprise / compliance |

---

## File-Driven Routing

VibeFlow's core innovation is file-driven deterministic routing. `get-vibeflow-phase.py` checks specific files in the repository to determine which phase should execute:

```
increment-request.json exists?     ──yes──▶ increment
think-output.md missing?           ──yes──▶ think
workflow.yaml missing?             ──yes──▶ template-selection
plan-review.md missing?            ──yes──▶ plan-review
*-srs.md missing?                  ──yes──▶ requirements
UI required and *-ucd.md missing?  ──yes──▶ ucd
*-design.md missing?               ──yes──▶ design
feature-list.json missing?        ──yes──▶ build-init
work-config.json missing?         ──yes──▶ build-config
features not all passing?          ──yes──▶ build-work
review-report.md missing?         ──yes──▶ review
*-st-report.md missing?           ──yes──▶ test-system
UI required and qa-report missing? ──yes──▶ test-qa
RELEASE_NOTES.md missing?         ──yes──▶ ship
retro-*.md missing?               ──yes──▶ reflect
all checks pass                           ▶ done
```

This design means:
- **Cross-session recovery**: Close the chat, reopen — AI instantly knows what to continue
- **Multi-AI collaboration**: Different AIs can relay the same project
- **Zero ambiguity**: No chance of "AI misunderstood the current phase"

---

## Session Hooks

VibeFlow uses session hooks to automatically inject context at every session start:

```
hooks/
  hooks.json          ← Claude Code hook config
  session-start.ps1   ← Windows PowerShell entry
  session-start.sh    ← macOS/Linux bash entry
```

Session hook responsibilities:
1. Call `get-vibeflow-phase.py` to detect current phase
2. Read the `vibeflow-router` SKILL.md
3. Inject phase info and routing instructions into session context
4. AI receives context and auto-routes to the correct phase skill

---

## Project State Files

### Runtime State (`.vibeflow/`)

| File | Purpose |
|---|---|
| `think-output.md` | Think output: problem statement, boundaries, template recommendation |
| `workflow.yaml` | Active workflow config (copied from template) |
| `work-config.json` | Build config: enabled steps, quality thresholds |
| `plan-review.md` | Plan review record |
| `review-report.md` | Global code review report |
| `qa-report.md` | QA test report |
| `retro-YYYY-MM-DD.md` | Iteration retrospective |
| `increment-request.json` | Incremental requirements signal file |

### Delivery Artifacts

| File | Purpose |
|---|---|
| `docs/plans/*-srs.md` | Software Requirements Specification |
| `docs/plans/*-ucd.md` | UI Component Design document |
| `docs/plans/*-design.md` | Technical design document |
| `docs/plans/*-st-report.md` | System test report |
| `docs/test-cases/feature-*.md` | Feature test case documents |
| `feature-list.json` | Feature inventory (single source of truth during Build) |
| `task-progress.md` | Task progress log |
| `RELEASE_NOTES.md` | Release notes |

---

## Comparison Matrix

| Dimension | Typical AI Coding | VibeFlow |
|---|---|---|
| **Requirements** | Verbal or none | Structured SRS (ISO 29148) |
| **Design** | Jump to code | Technical design doc + UCD |
| **State Management** | Relies on chat history | File persistence, deterministic routing |
| **Quality Assurance** | "Looks like it works" | TDD + coverage + mutation testing + acceptance |
| **Test Documentation** | None | ISO 29119 test case documents |
| **Code Review** | None or self-review | Structured spec compliance review |
| **Cross-Session** | Start over each time | File state fully preserved, instant recovery |
| **Workflow** | Manual or none | Auto-routing, 16-state machine |
| **Strictness** | Not adjustable | 4 templates, from prototype to enterprise |
| **Traceability** | None | Requirements → design → features → tests, full chain |

---

## Repository Structure

```text
vibeflow/
├── skills/                          # 18 workflow skills
│   ├── vibeflow/                    # Framework entry
│   ├── vibeflow-router/             # Session router
│   ├── vibeflow-think/              # Think phase
│   ├── vibeflow-plan-review/        # Plan review
│   ├── vibeflow-requirements/       # Requirements spec
│   ├── vibeflow-ucd/                # UI design
│   ├── vibeflow-design/             # Technical design
│   ├── vibeflow-build-init/         # Build initialization
│   ├── vibeflow-build-work/         # Feature orchestration
│   ├── vibeflow-tdd/                # TDD cycle
│   ├── vibeflow-quality/            # Quality gates
│   ├── vibeflow-feature-st/         # Feature acceptance
│   ├── vibeflow-spec-review/        # Spec review
│   ├── vibeflow-review/             # Global review
│   ├── vibeflow-test-system/        # System testing
│   ├── vibeflow-test-qa/            # QA testing
│   ├── vibeflow-ship/               # Release
│   └── vibeflow-reflect/            # Reflection
├── scripts/                         # Python scripts
│   ├── get-vibeflow-phase.py        # Phase detection (16-state router)
│   ├── new-vibeflow-config.py       # Workflow config generation
│   ├── new-vibeflow-work-config.py  # Build config generation
│   └── test-vibeflow-setup.py       # Environment validation
├── templates/                       # Static workflow templates
│   ├── prototype.yaml
│   ├── web-standard.yaml
│   ├── api-standard.yaml
│   └── enterprise.yaml
├── hooks/                           # Session hooks
│   ├── hooks.json
│   ├── session-start.ps1
│   └── session-start.sh
├── validation/                      # Validation projects
│   └── sample-priority-api/
├── VIBEFLOW-DESIGN.md               # Design contract
├── ARCHITECTURE.md                  # Architecture documentation
├── USAGE.md                         # Usage guide
└── TODOS.md                         # Backlog
```

---

## Design Principles

1. **Vendor-Neutral**: All project-facing names use `vibeflow` only, no binding to any specific AI provider
2. **File-Driven Routing**: Current phase is determined by repository file state, not chat history or process memory
3. **Thin Orchestration**: Skills define routing and contracts; implementation details stay in the target project
4. **Template-Derived Behavior**: Workflow strictness is selected once and propagated globally through generated config
5. **Repo-Local Artifacts**: All state needed for recovery or continuation lives in files under the target project

---

## Roadmap

- [ ] Port 9 validation scripts (init_project, validate_features, check_st_readiness, etc.)
- [ ] Add 3 document templates (SRS/Design/ST-Case)
- [ ] Split router SKILL.md (877 lines → ~200 line core + references/)
- [ ] Add user shortcut commands (commands/)
- [ ] Add skill reference docs (references/)
- [ ] Unit tests for framework core scripts
- [ ] CLAUDE.md cross-session context injection

See [TODOS.md](TODOS.md) and [GitHub Issues](https://github.com/ttttstc/vibeflow/issues) for details.

---

## Documentation

| Document | Description |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Full architecture diagrams and component descriptions |
| [USAGE.md](USAGE.md) | Operating guide for target projects |
| [VIBEFLOW-DESIGN.md](VIBEFLOW-DESIGN.md) | Design contract and skill catalog |
| [TODOS.md](TODOS.md) | Backlog and priorities |

---

## License

MIT
