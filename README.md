**[English](README_EN.md) | 中文**

---

# VibeFlow

**让 AI 按工程纪律交付软件，而不是随机 vibe coding。**

别再让 AI "先写代码再说的" 了——VibeFlow 是一个结构化的 16 阶段软件交付框架，从问题框定到反思回顾，每一步都有文件状态持久化、确定性路由和质量门禁。

> "VibeFlow is what happens when you take a senior engineer's discipline and give it to an AI that never gets tired, never forgets, and never ships without tests."

---

## 三种安装方式

### 方式一：Claude Code Marketplace（推荐）

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.sh | bash

# Windows PowerShell
irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.ps1 | iex

# 安装完成后，在 Claude Code 中激活插件：
/plugin install vibeflow@vibeflow
```

### 方式二：Shell 脚本（手动）

```bash
curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/install.sh | bash
```

### 方式三：OpenCode

```bash
curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/install.sh | bash
```

---

## 为什么需要 VibeFlow

| 没有 VibeFlow 的 AI 编程 | 使用 VibeFlow |
|---|---|
| "帮我写个 API" → 直接开写，没有需求分析 | Think → Plan → Requirements → Design → 再编码 |
| 写到一半忘记在做什么，换个会话全部丢失 | 文件持久化，跨会话秒级恢复 |
| 测试？覆盖率？"能用就行" | TDD 铁律 → 覆盖率门禁 → 变异测试 → 验收，五层关卡 |
| AI 审查自己写的代码 | 三视角评审（CEO 价值 + 工程 + 设计）|
| 做完就完了，没有任何文档或回顾 | Ship 生成发布说明，Reflect 产出复盘改进 |
| 项目越大 AI 越不知道该做什么 | 确定性路由，永远知道现在该做什么 |

---

## 核心哲学

**需求驱动，而非代码驱动。** 先写需求规格（SRS），再写技术设计，最后才写代码。

**文件即状态。** 所有工作流状态持久化在仓库文件中（`.vibeflow/`、`docs/plans/`）。关闭会话、换机器、甚至换 AI — 项目状态完整保留。

**确定性路由。** `get-vibeflow-phase.py` 通过检查文件存在性确定当前阶段。16 个阶段状态，严格 elif 链，没有歧义。

**模板控制严格度。** 四种静态模板（prototype → enterprise）控制哪些阶段必须执行、质量门禁阈值多高。一次选择，全局生效。

**单功能循环。** Build 阶段一次只处理一个功能，每个功能必须走完完整管道才算完成。杜绝"先全部写完再一起测试"的反模式。

---

## 16 阶段架构

```
Think ── Plan ── Requirements ── Design
  │                          │
  ▼                          ▼
Office Hours（可选）     Brainstorming（可选）
                          │
                          ▼
Build-init ── Build-config ── Build-work
                                    │
                              ┌──────┴──────┐
                              ▼              ▼
                          TDD 循环     Quality Gates
                              │              │
                              ▼              ▼
                      Feature-ST ◄───── Spec-Review
                              │              │
                              └──────┬───────┘
                                     ▼
                               Review（跨功能）
                                     │
                        ┌────────────┼────────────┐
                        ▼            ▼            ▼
                   Test-System   Test-QA       Ship
                        │            │            │
                        └────────────┴────────────┘
                                     │
                                     ▼
                                  Reflect
```

### Think（思考）

**目标**：定义问题、理解边界、扫描机会、选择工作流模板。

- 产出 `.vibeflow/think-output.md`
- 可选：先跑一轮 `vibeflow-office-hours`（YC Office Hours 风格头脑风暴）验证想法是否值得投入
- 推荐并确认模板（prototype / web-standard / api-standard / enterprise）

### Plan（计划）

**目标**：CEO 视角价值评审，唯一关卡。

- 调用 `vibeflow-plan-value-review` 评估项目价值
- **价值评审失败 = 项目终止**（fail-fast）
- 工程视角和设计视角评审移到 Design 阶段末尾执行（因为那时候才有具体设计文档可审）

### Requirements（需求）

**目标**：编写需求规格说明书（SRS），遵循 ISO/IEC/IEEE 29148。

- 产出 `docs/plans/*-srs.md`
- 逐条与用户确认，每条需求可测试

### Design（设计）

**目标**：技术设计 + 用户体验设计 + 三视角评审。

这是整个框架最复杂的阶段：

| 步骤 | Skill | 产出物 |
|---|---|---|
| 0. 问题探索 | `vibeflow-brainstorming`（可选）| `docs/plans/*-brainstorming.md` |
| 1. 读取 SRS + UCD | 内置（UCD 按需生成）| 设计驱动提取 |
| 2. 探索上下文 | 内置 | 上下文文档 |
| 3. 提出方案 | 内置 | 方案对比 |
| 4. 用户逐节审批 | 内置 | 用户签字确认 |
| 5. **AI 深度评审** | `vibeflow-plan-eng-review` + `vibeflow-plan-design-review` | `.vibeflow/plan-eng-review.md` + `.vibeflow/plan-design-review.md` |
| 6. **范围决策** | 内置 | Expand / Hold / Reduce |
| 7. 编写设计文档 | 内置 | `docs/plans/*-design.md` |
| 8. 过渡到初始化 | 内置 | — |

### Build-init（构建初始化）

**目标**：初始化构建产物。

- `feature-list.json`、`task-progress.md`、`RELEASE_NOTES.md`
- 生成 `.vibeflow/work-config.json`（质量阈值）

### Build-config（构建配置）

**目标**：配置每个功能的实现细节。

- 为每个 feature 分配阶段（设计/开发/测试）
- 确认外部依赖和交付顺序

### Build-work（构建执行）

**目标**：逐功能实现，每个功能通过完整质量管道。

```
Pick Feature → TDD Red-Green-Refactor → Quality Gates
                                         · 行覆盖率
                                         · 分支覆盖率
                                         · 变异分数
                                    ┌──────┴──────┐
                                    ▼              ▼
                              Feature-ST     Spec-Review
                                    │              │
                                    └──────┬──────┘
                                           ▼
                                      Acceptance
```

### Review（审查）

**目标**：跨功能整体变更审查。

- `vibeflow-review`：架构一致性、安全性、性能分析
- 可选激活安全护栏：`vibeflow-careful`（危险命令警告）、`vibeflow-freeze`（编辑边界）、`vibeflow-guard`（最大安全模式）

### Test-System（系统测试）

**目标**：系统级集成测试和非功能需求验证。

- 集成测试、E2E 测试、NFR 验证、探索性测试四路并行（~4x 加速）

### Test-QA（QA 测试）

**目标**：浏览器驱动的 QA 验证（仅 UI 项目）。

- 仅当模板需要 UI 且 `qa-report.md` 不存在时执行

### Ship（发布）

**目标**：准备发布产物。

- 版本管理、PR 创建、标签打标、变更日志
- `vibeflow-ship` 自动执行，可选（`ship_required()` 检测）

### Reflect（反思）

**目标**：回顾本轮迭代，为下一轮产出改进建议。

- 产出 `.vibeflow/retro-YYYY-MM-DD.md`
- 可选（`reflect_required()` 检测）

---

## Skill 超能力架构

VibeFlow 由 23 个独立 skill 组成，分为五层：

### 核心层

| Skill | 职责 |
|---|---|
| `vibeflow` | 框架入口，概览和快速开始 |
| `vibeflow-router` | 会话路由器，基于文件状态分派到正确阶段 |
| `vibeflow-think` | Think 阶段，问题框定和模板选择 |

### 计划层

| Skill | 职责 |
|---|---|
| `vibeflow-plan` | Plan 阶段入口（调用 value-review） |
| `vibeflow-plan-value-review` | CEO 视角价值评审，fail-fast 关卡 |
| `vibeflow-plan-eng-review` | 工程视角评审（架构、代码质量、测试、性能） |
| `vibeflow-plan-design-review` | 设计视角评审（信息架构、交互、用户体验） |
| `vibeflow-requirements` | 需求规格说明书（ISO 29148） |
| `vibeflow-design` | 技术设计文档（含 UCD 内联 + 三视角评审） |

### 辅助探索层

| Skill | 职责 |
|---|---|
| `vibeflow-office-hours` | YC Office Hours 风格头脑风暴（Think 前置） |
| `vibeflow-brainstorming` | 设计前问题探索（Design 前置） |

### 构建层

| Skill | 职责 |
|---|---|
| `vibeflow-build-init` | 初始化构建产物 |
| `vibeflow-build-work` | 单功能编排器，驱动 TDD → Quality → ST → Review 管道 |
| `vibeflow-tdd` | TDD Red-Green-Refactor 循环 |
| `vibeflow-quality` | 质量门禁：行覆盖率、分支覆盖率、变异测试 |
| `vibeflow-feature-st` | 功能级验收测试（ISO 29119） |
| `vibeflow-spec-review` | 规范合规性审查，对照 SRS 和 Design 逐条验证 |

### 安全护栏（可选）

| Skill | 职责 |
|---|---|
| `vibeflow-careful` | 危险命令警告（rm -rf、DROP TABLE 等）|
| `vibeflow-freeze` | 编辑边界限制（限制 Edit/Write 在指定目录）|
| `vibeflow-guard` | 最大安全模式（组合 careful + freeze）|
| `vibeflow-unfreeze` | 解除冻结 |

### 验证与发布层

| Skill | 职责 |
|---|---|
| `vibeflow-review` | 跨功能整体变更审查 |
| `vibeflow-test-system` | 系统级集成测试和 NFR 验证 |
| `vibeflow-test-qa` | 浏览器驱动的 QA 验证（仅 UI 项目）|
| `vibeflow-ship` | 版本发布、PR 创建、变更日志 |
| `vibeflow-reflect` | 迭代回顾和改进建议 |

### Skill 调用图

```
Session Start
    │
    ▼
vibeflow-router ──── get-vibeflow-phase.py ──── 检测 16 种阶段状态
    │
    ├── think ─────────── vibeflow-think
    │       └── [可选] ─── vibeflow-office-hours
    │
    ├── plan ───────────── vibeflow-plan
    │       └── Step 1: ── vibeflow-plan-value-review
    │
    ├── requirements ───── vibeflow-requirements
    │
    ├── design ──────────── vibeflow-design
    │       ├── [可选] ──── vibeflow-brainstorming
    │       ├── Step 1: ── 读取 SRS + 条件 UCD
    │       ├── Step 5: ── vibeflow-plan-eng-review
    │       └── Step 5: ── vibeflow-plan-design-review
    │
    ├── build-init ──────── vibeflow-build-init
    ├── build-config ────── vibeflow-build-config
    ├── build-work ──────── vibeflow-build-work
    │                        ├── vibeflow-tdd
    │                        ├── vibeflow-quality
    │                        ├── vibeflow-feature-st
    │                        └── vibeflow-spec-review
    │
    ├── review ──────────── vibeflow-review
    │       └── [可选] ──── vibeflow-careful / freeze / guard
    │
    ├── test-system ─────── vibeflow-test-system
    ├── test-qa ────────── vibeflow-test-qa
    ├── ship ────────────── vibeflow-ship
    └── reflect ─────────── vibeflow-reflect
```

---

## 模板系统

四种静态模板控制工作流严格度：

| 维度 | Prototype | Web-Standard | API-Standard | Enterprise |
|---|---|---|---|---|
| **Think 深度** | quick | standard | standard | deep |
| **Plan 评审** | CEO 削减模式 | CEO 保持模式 | CEO 保持模式 | CEO 扩展模式 |
| **需求规格** | 必需 | 必需 | 必需 | 必需 |
| **UCD** | 按需 | 按需 | 按需 | 按需 |
| **TDD** | 必需 | 必需 | 必需 | 必需 |
| **行覆盖率** | 60% | 90% | 90% | 95% |
| **分支覆盖率** | 40% | 80% | 80% | 85% |
| **变异分数** | 50% | 80% | 80% | 85% |
| **功能验收** | 可选 | 必需 | 可选 | 必需 |
| **规范审查** | 可选 | 必需 | 必需 | 必需 |
| **全局审查** | 可选 | 必需 | 必需 | 必需 |
| **系统测试** | 可选 | 必需 | 必需 | 必需 |
| **QA 测试** | 可选（无 UI 跳过）| 按需 | 按需 | 按需 |
| **反思** | 可选 | 可选 | 可选 | 必需 |
| **版本策略** | manual | semver | semver | semver |
| **适用场景** | 黑客马拉松、POC | Web 应用 | API 服务 | 企业/合规系统 |

---

## 安装方式对比

| 安装方式 | 适合人群 | 自动化程度 | 插件注册 |
|---|---|---|---|
| Claude Code Marketplace | Claude Code 用户 | 高（一条命令）| 自动注册 |
| Shell 脚本 | 手动管理插件的用户 | 高 | 需手动 |
| OpenCode | OpenCode 用户 | 高 | 需手动 |

---

## 项目状态文件

### 运行时状态（`.vibeflow/`）

| 文件 | 用途 |
|---|---|
| `think-output.md` | Think 阶段产物：问题陈述、边界、模板推荐 |
| `workflow.yaml` | 当前生效的工作流配置（从模板复制）|
| `work-config.json` | 构建配置：启用的步骤、质量阈值 |
| `plan-value-review.md` | Plan 阶段产物：CEO 价值评审结论 |
| `plan-eng-review.md` | Design 阶段产物：工程评审结论 |
| `plan-design-review.md` | Design 阶段产物：设计评审结论 |
| `review-report.md` | 全局代码审查报告 |
| `qa-report.md` | QA 测试报告 |
| `retro-YYYY-MM-DD.md` | 迭代回顾文档 |

### 交付产物

| 文件 | 用途 |
|---|---|
| `docs/plans/*-srs.md` | 需求规格说明书 |
| `docs/plans/*-design.md` | 技术设计文档（含 UCD 内联章节）|
| `docs/plans/*-st-report.md` | 系统测试报告 |
| `docs/test-cases/feature-*.md` | 功能测试用例文档 |
| `feature-list.json` | 功能清单（构建阶段的单一事实来源）|
| `task-progress.md` | 任务进度日志 |
| `RELEASE_NOTES.md` | 发布说明 |

---

## 仓库结构

```text
vibeflow/
├── skills/                          # 23 个工作流 skill
│   ├── vibeflow/                    # 框架入口
│   ├── vibeflow-router/             # 会话路由器
│   ├── vibeflow-think/              # Think 阶段
│   ├── vibeflow-office-hours/       # YC Office Hours（可选）
│   ├── vibeflow-plan/               # Plan 阶段入口
│   ├── vibeflow-plan-value-review/  # CEO 价值评审
│   ├── vibeflow-plan-eng-review/    # 工程评审
│   ├── vibeflow-plan-design-review/ # 设计评审
│   ├── vibeflow-requirements/       # 需求规格
│   ├── vibeflow-design/             # 技术设计（含 UCD + 三视角评审）
│   ├── vibeflow-brainstorming/      # 问题探索（可选）
│   ├── vibeflow-build-init/         # 构建初始化
│   ├── vibeflow-build-config/       # 构建配置
│   ├── vibeflow-build-work/         # 功能编排
│   ├── vibeflow-tdd/                # TDD 循环
│   ├── vibeflow-quality/            # 质量门禁
│   ├── vibeflow-feature-st/         # 功能验收
│   ├── vibeflow-spec-review/        # 规范审查
│   ├── vibeflow-review/             # 全局审查
│   ├── vibeflow-careful/            # 危险命令警告
│   ├── vibeflow-freeze/             # 编辑边界
│   ├── vibeflow-guard/              # 最大安全模式
│   ├── vibeflow-unfreeze/           # 解除冻结
│   ├── vibeflow-test-system/        # 系统测试
│   ├── vibeflow-test-qa/            # QA 测试
│   ├── vibeflow-ship/               # 发布
│   └── vibeflow-reflect/            # 反思
├── scripts/                         # Python 脚本
│   ├── get-vibeflow-phase.py        # 阶段检测（16 状态路由器）
│   ├── new-vibeflow-config.py       # 工作流配置生成
│   └── new-vibeflow-work-config.py  # 构建配置生成
├── templates/                       # 静态工作流模板
│   ├── prototype.yaml
│   ├── web-standard.yaml
│   ├── api-standard.yaml
│   └── enterprise.yaml
├── hooks/                           # 会话钩子
│   ├── hooks.json
│   ├── session-start.ps1
│   └── session-start.sh
├── claude-code/                     # Claude Code Marketplace 安装脚本
│   ├── install.sh
│   └── install.ps1
├── .claude-plugin/                  # Claude Code 插件元数据
│   ├── plugin.json
│   └── marketplace.json
└── install.sh                       # OpenCode 安装脚本
```

---

## 文档

| 文档 | 说明 |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | 完整架构图和组件说明 |
| [USAGE.md](USAGE.md) | 目标项目操作指南 |
| [VIBEFLOW-DESIGN.md](VIBEFLOW-DESIGN.md) | 设计契约和 skill 目录 |

---

## 许可证

MIT
