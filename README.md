**[English](README_EN.md) | 中文**

---

# VibeFlow

**让 AI 按工程纪律交付软件，而不是随机 vibe coding。**

别再让 AI "先写代码再说的" 了——VibeFlow 是一个结构化的 7 阶段软件交付框架，从问题框定到测试完成，每一步都有文件状态持久化、确定性路由和质量门禁。

> "VibeFlow is what happens when you take a senior engineer's discipline and give it to an AI that never gets tired, never forgets, and never ships without tests."

---

## 安装

### Claude Code 一键安装（推荐）

在 Claude Code 对话框中运行：

```
/sh curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.sh | bash
```

安装完成后激活：

```
/plugin install vibeflow@vibeflow
```

### Claude Code Prompt

如果你想让 Claude Code 自己完成安装，直接粘贴下面这段：

```
帮我安装 VibeFlow 到 Claude Code。

要求：
1. 优先用官方安装脚本：
   /sh curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.sh | bash
2. 如果脚本方式不可用，再把仓库安装到 Claude Code marketplace 目录。
3. 安装完成后执行：
   /plugin install vibeflow@vibeflow
4. 最后告诉我：
   - 是否安装成功
   - 插件安装到了哪里
   - 接下来我该输入什么命令开始使用
```

### Windows 启动器

双击即用，自动完成下载 + 安装 + 启动 Claude Code + 加载插件：

```powershell
irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/vibeflow-launcher.ps1 | iex
```

### 验证安装

安装完成后，在 Claude Code 里输入：

```text
/vibeflow
```

如果能看到 VibeFlow 入口说明，说明插件已经正常加载。

### 首次启动怎么选模式

- **第一次在一个项目里运行 `/vibeflow`**：VibeFlow 应先让你明确选择 `Full Mode` 或 `Quick Mode`
- **如果项目里已经有 `.vibeflow/state.json`**：VibeFlow 会沿用已有 `mode`，继续当前工作流，不会重复询问
- **如果你明确运行 `/vibeflow-quick`**：直接进入 Quick 流程

简化理解：

- 新项目或首次接入：先选 mode
- 已有项目继续工作：沿用原 mode
- 不确定时：优先选 `Full Mode`

### 更新 VibeFlow

重新运行安装脚本即可覆盖旧版本：

```bash
curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.sh | bash
```

Windows PowerShell：

```powershell
irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.ps1 | iex
```

更新后建议：

- 如果 Claude Code 正在运行，先重启 Claude Code
- 然后重新执行 `/plugin install vibeflow@vibeflow`

### 卸载 VibeFlow

1. 关闭 Claude Code
2. 删除 marketplace 目录

macOS / Linux：

```bash
rm -rf ~/.claude/plugins/marketplaces/vibeflow
```

Windows PowerShell：

```powershell
Remove-Item "$env:USERPROFILE\\.claude\\plugins\\marketplaces\\vibeflow" -Recurse -Force
```

3. 从以下文件中删除 `vibeflow` 条目：

- macOS / Linux：`~/.claude/plugins/known_marketplaces.json`
- Windows：`%USERPROFILE%\\.claude\\plugins\\known_marketplaces.json`

4. 重新打开 Claude Code

如果你只是想临时停用插件，也可以保留文件不删，只移除 Claude Code 里的已加载插件条目。

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

**文件即状态。** 所有工作流状态持久化在仓库文件中（`.vibeflow/state.json`、`.vibeflow/runtime.json`、`docs/changes/`、`feature-list.json`）。关闭会话、换机器、甚至换 AI — 项目状态完整保留。

**确定性路由。** `get-vibeflow-phase.py` 通过检查文件存在性确定当前阶段。7 个核心阶段 + 2 个可选阶段，严格 elif 链，没有歧义。

**模板控制严格度。** 四种静态模板（prototype → enterprise）控制哪些阶段必须执行、质量门禁阈值多高。一次选择，全局生效。

**依赖感知构建。** Build 默认保持严谨的功能级管道；当功能彼此独立时，也支持按依赖关系并行推进，而不是盲目一起开跑。

---

## Build 后自动继续与看板

Design 确认后，Claude Code 插件里的默认行为只有一个：

- **进入 `build-init` 后系统自动继续后续链路**
  router 会继续推进 `build-init -> build-config -> build-work -> review -> test -> ship -> reflect`，直到 `done`、阻塞或人工确认点。

如果你是在命令行、CI 或 dashboard 联动场景里运行同一条自动执行链路，对应的脚本入口是：

- `python scripts/run-vibeflow-autopilot.py --project-root <repo>`
  从当前 phase 执行同一条自动继续链路，直到 `done`、遇到阻塞，或停在人工确认点。
- `python scripts/run-vibeflow-build-work.py --project-root <repo> --max-workers 4`
  单独执行 Build-Work，支持依赖感知并行。
- `python scripts/run-vibeflow-dashboard.py --project-root <repo>`
  启动本地 live dashboard，实时展示阶段、feature、产物和事件时间线。

如果只想看一次当前状态，也可以直接输出 dashboard 快照：

```bash
python scripts/run-vibeflow-dashboard.py --project-root <repo> --snapshot-json
```

---

## 7 阶段架构

```
┌─────────────────────────────────────────────────────────────┐
│  决策阶段（人工参与）                                          │
│  Think → Plan → Requirements → Design                       │
│  人做判断、做审批、做签字确认                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  执行阶段（自动接管）                                          │
│  Build → Review → Test                                      │
│  进入 build-init 后默认由系统自动继续到结束或阻塞               │
└─────────────────────────────────────────────────────────────┘
                              │
                         ┌────┴────┐
                         ▼         ▼
                       Ship    Reflect
                         │         │
                         └── 可选 ──┘
```

**7 个核心阶段：**

| 阶段 | 性质 | 说明 |
|------|------|------|
| Think | 人工 | 问题框定、模板选择 |
| Plan | 人工 | CEO 视角价值评审（fail-fast 关卡）|
| Requirements | 人工 | 需求规格说明书（ISO 29148）|
| Design | 人工 | 技术设计 + 三视角评审 + 用户签字 |
| Build | 自动 | 构建初始化 → 功能配置 → 实现（TDD 管道）|
| Review | 自动 | 跨功能审查（架构、安全、性能）|
| Test | 自动 | 系统测试 + QA 验证 |

**2 个可选阶段（Ship / Reflect）：** 发布和复盘，非必选。

### Think（思考）

**目标**：定义问题、理解边界、扫描机会、选择工作流模板。

- 产出 `docs/changes/<change-id>/context.md`：本次工作的起点说明，记录问题、边界、目标和约束
- 可选：先跑一轮 `vibeflow-office-hours`（YC Office Hours 风格头脑风暴）验证想法是否值得投入
- 推荐并确认模板（prototype / web-standard / api-standard / enterprise）

### Plan（计划）

**目标**：CEO 视角价值评审，唯一关卡。

- 调用 `vibeflow-plan-value-review` 评估项目价值
- **价值评审失败 = 项目终止**（fail-fast）
- 工程视角和设计视角评审移到 Design 阶段末尾执行（因为那时候才有具体设计文档可审）

### Requirements（需求）

**目标**：编写需求规格说明书（SRS），遵循 ISO/IEC/IEEE 29148。

- 产出 `docs/changes/<change-id>/requirements.md`：本次变更的正式需求定义，后续设计和测试都要对齐它
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
| 5. **AI 深度评审** | `vibeflow-plan-eng-review` + `vibeflow-plan-design-review` | `docs/changes/<change-id>/design-review.md`（记录工程和设计评审结论） |
| 6. **范围决策** | 内置 | Expand / Hold / Reduce |
| 7. 编写设计文档 | 内置 | `docs/changes/<change-id>/design.md`（本次实现方案、接入点、兼容与验证方式） |
| 8. 过渡到初始化 | 内置 | — |

### Build（构建）

**目标**：进入 Build 后由系统自动继续后续链路，而不是让用户手动逐段推进。

在 Claude Code 插件里，进入 `build-init` 后默认开始自动继续后续链路；`run-vibeflow-autopilot.py` 只是这条链路的命令行入口。

Build 阶段负责完成以下全部工作：

| 步骤 | 内容 | 产出 |
|------|------|------|
| 初始化 | 创建脚手架文件 | `feature-list.json`（功能清单主索引）、`.vibeflow/runtime.json`（运行态覆盖层）、`.vibeflow/logs/session-log.md`（进度日志）、`.vibeflow/work-config.json`（构建配置） |
| 功能配置 | 分配每个功能的开发/测试阶段 | `feature-list.json`（更新后的功能状态、依赖和顺序） |
| 实现 | 串行或依赖感知并行构建 | 源代码、测试文件、`.vibeflow/build-reports/feature-*.md`（功能执行报告） |
| 质量门禁 | 行覆盖率、分支覆盖率、变异测试 | 覆盖率报告 |
| 功能验收 | Feature-ST + Spec-Review | 验收报告 |

```
Design 确认
    │
    ▼
Build-init ── Build-config ── Build-work
    │              │             │
    │              │         ┌────┴────┐
    │              │         ▼         ▼
    │              │    TDD 循环  Quality Gates
    │              │         │         │
    │              │         ▼         ▼
    │              │   Feature-ST  Spec-Review
    │              │         │         │
    │              │         └────┬────┘
    │              │              ▼
    │              │         Acceptance
    │              │              │
    └──────────────┴──────────────┘
                   │
                   ▼
              Review（自动）
```

### Review（审查）

**目标**：跨功能整体变更审查（自动完成）。

- `vibeflow-review`：架构一致性、安全性、性能分析
- 可选激活安全护栏：`vibeflow-careful`（危险命令警告）、`vibeflow-freeze`（编辑边界）、`vibeflow-guard`（最大安全模式）

### Test（测试）

**目标**：系统级集成测试和 QA 验证（自动完成）。

| 步骤 | 内容 | 触发条件 |
|------|------|---------|
| Test-System | 集成测试、E2E、NFR 验证、探索性测试 | 所有项目 |
| Test-QA | 浏览器驱动 QA 验证 | 仅 UI 项目 |

Test-QA 发现的问题：
- **严重/重要**：自动修复后重新验证
- **次要/外观**：与用户确认是否修复或推迟

### Ship（发布）

**目标**：准备发布产物。

- 版本管理、PR 创建、标签打标、变更日志
- `vibeflow-ship` 自动执行，可选（`ship_required()` 检测）

### Reflect（反思）

**目标**：回顾本轮迭代，为下一轮产出改进建议。

- 产出 `.vibeflow/logs/retro-YYYY-MM-DD.md`：记录这轮做对了什么、踩了什么坑、下轮要怎么改
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

### 构建层（Build 阶段内部 skill）

| Skill | 职责 |
|---|---|
| `vibeflow-build-init` | 初始化构建产物 |
| `vibeflow-build-config` | 配置每个功能的实现细节 |
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
vibeflow-router ──── get-vibeflow-phase.py ──── 检测 7 种核心阶段
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
    ├── build ───────────── vibeflow-build-work（内部编排 build-init → build-config → build-work）
    │                        ├── vibeflow-tdd
    │                        ├── vibeflow-quality
    │                        ├── vibeflow-feature-st
    │                        └── vibeflow-spec-review
    │
    ├── review ──────────── vibeflow-review
    │       └── [可选] ──── vibeflow-careful / freeze / guard
    │
    ├── test ────────────── vibeflow-test-system
    │                       vibeflow-test-qa（仅 UI 项目）
    │
    ├── ship ────────────── vibeflow-ship（可选）
    └── reflect ─────────── vibeflow-reflect（可选）
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

## 项目状态文件

### 运行时状态（`.vibeflow/`）

| 文件 | 用途 |
|---|---|
| `state.json` | 工作流中心状态：当前阶段、模式、活跃工作包；这是路由判断的主入口 |
| `runtime.json` | 运行态覆盖层：记录 Build 后自动执行链路的当前动作、友好提示、最近事件和 heartbeat；dashboard 直接读取它做 live 刷新 |
| `workflow.yaml` | 当前生效的工作流配置（从模板复制）；决定哪些阶段必须执行 |
| `work-config.json` | 构建配置：启用的步骤、质量阈值；Build 阶段按它收紧规则 |
| `phase-history.json` | 阶段推进历史；记录 phase 切换、增量处理和自动执行事件 |
| `logs/session-log.md` | 人类可读的过程日志；用于快速理解最近发生了什么 |
| `increments/queue.json` | 增量请求队列；用于在主流程之外排队新的 change |
| `increments/requests/*.json` | 增量请求明细；记录新增、修改、废弃和文档更新动作 |
| `logs/retro-YYYY-MM-DD.md` | 迭代回顾文档；给下一轮输入经验和改进项 |

### 交付产物

| 文件 | 用途 |
|---|---|
| `docs/changes/<change-id>/context.md` | 问题上下文文档；说明这次为什么做、从哪里开始 |
| `docs/changes/<change-id>/proposal.md` | 方案提案；记录范围、价值和是否值得做 |
| `docs/changes/<change-id>/requirements.md` | 需求规格说明书；是实现和验收的基线 |
| `docs/changes/<change-id>/ucd.md` | 体验设计文档；只在有 UI 设计需求时出现 |
| `docs/changes/<change-id>/design.md` | 技术设计文档；说明怎么实现、接到哪里、怎么验证 |
| `docs/changes/<change-id>/design-review.md` | 设计评审结果；沉淀工程和设计视角的修改意见 |
| `docs/changes/<change-id>/tasks.md` | 执行清单；把设计拆成可完成、可验证的任务 |
| `docs/changes/<change-id>/verification/review.md` | Review 报告；记录跨功能审查结论 |
| `docs/changes/<change-id>/verification/system-test.md` | 系统测试报告；记录集成和端到端验证结果 |
| `docs/changes/<change-id>/verification/qa.md` | QA 报告；记录浏览器和交互验证结果 |
| `docs/test-cases/feature-*.md` | 功能测试用例文档；给功能级验收提供可执行用例 |
| `feature-list.json` | 功能清单；Build 阶段的单一事实来源，支持依赖、状态、校验步骤和自动执行命令 |
| `.vibeflow/logs/session-log.md` | 任务进度日志；给人看过程，不再充当状态权威 |
| `RELEASE_NOTES.md` | 发布说明；面向交付和发版，不负责驱动阶段路由 |

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
│   ├── run-vibeflow-autopilot.py    # Build 后自动执行链路的命令行入口
│   ├── run-vibeflow-build-work.py   # Build-Work 执行器（支持依赖感知并行）
│   ├── run-vibeflow-dashboard.py    # 本地 live dashboard
│   ├── new-vibeflow-config.py       # 工作流配置生成
│   ├── new-vibeflow-work-config.py  # 构建配置生成
│   ├── vibeflow_automation.py       # Build 后自动执行 / build orchestration 核心
│   └── vibeflow_dashboard.py        # dashboard snapshot + SSE 服务
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
│   ├── install.sh                   # bash 一键安装（支持 jq/python3 fallback）
│   ├── install.ps1                  # PowerShell git-based 安装
│   ├── install-simple.ps1           # PowerShell ZIP 下载安装（不需要 git）
│   ├── install-all-in-one.ps1      # Claude Code 内专用安装脚本
│   ├── vibeflow-launcher.ps1       # PowerShell 启动器（开箱即用）
│   ├── debug-install.ps1           # 安装诊断脚本
│   └── INSTALL-PROMPT.md           # 安装提示词文档
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
