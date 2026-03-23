**[English](README_EN.md) | 中文**

---

# VibeFlow

**让 AI 按工程纪律交付软件，而不是随机 vibe coding。**

别再让 AI "先写代码再说的" 了——VibeFlow 是一个结构化的 7 阶段软件交付框架，从问题框定到测试完成，每一步都有文件状态持久化、确定性路由和质量门禁。

> "VibeFlow is what happens when you take a senior engineer's discipline and give it to an AI that never gets tired, never forgets, and never ships without tests."

---

## 三种安装方式

### 方式一：一键安装（推荐，最简单）

在 Claude Code 对话框中运行：

```
/sh curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/refs/heads/feat/plan-value-review/claude-code/install.sh | bash
```

安装完成后激活：

```
/plugin install vibeflow@vibeflow
```

### 方式二：让 Claude Code 自行安装

复制以下内容，粘贴到 Claude Code 对话框：

```
帮我安装 VibeFlow 插件。

执行以下步骤：

1. 下载仓库（选一种方式）：
   方式A - git clone：
   git clone --depth 1 https://github.com/ttttstc/vibeflow.git ~/.claude/plugins/marketplaces/vibeflow
   方式B - 如果 git 不可用，用 curl 下载 ZIP：
   curl -fsSL https://github.com/ttttstc/vibeflow/archive/refs/heads/feat/plan-value-review.zip -o /tmp/vibeflow.zip
   unzip /tmp/vibeflow.zip -d /tmp/
   rm -rf ~/.claude/plugins/marketplaces/vibeflow
   mv /tmp/vibeflow-feat-plan-value-review ~/.claude/plugins/marketplaces/vibeflow

2. 在 ~/.claude/plugins/known_marketplaces.json 注册（如果文件不存在则创建）：
   使用 jq 或 python3 更新 JSON，添加：
   "vibeflow": {
     "source": {"source": "github", "repo": "ttttstc/vibeflow"},
     "installLocation": "~/.claude/plugins/marketplaces/vibeflow/",
     "lastUpdated": "2026-03-23T00:00:00.000Z"
   }

3. 完成后报告
```

### 方式三：PowerShell 启动器（开箱即用）

双击即用，自动完成下载 + 安装 + 启动 Claude Code + 加载插件：

```powershell
irm https://raw.githubusercontent.com/ttttstc/vibeflow/refs/heads/feat/plan-value-review/claude-code/vibeflow-launcher.ps1 | iex
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

**确定性路由。** `get-vibeflow-phase.py` 通过检查文件存在性确定当前阶段。7 个核心阶段 + 2 个可选阶段，严格 elif 链，没有歧义。

**模板控制严格度。** 四种静态模板（prototype → enterprise）控制哪些阶段必须执行、质量门禁阈值多高。一次选择，全局生效。

**单功能循环。** Build 阶段一次只处理一个功能，每个功能必须走完完整管道才算完成。杜绝"先全部写完再一起测试"的反模式。

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
│  执行阶段（自动完成）                                          │
│  Build → Review → Test                                      │
│  设计方案确认后，AI 自动完成全部构建、审查、测试               │
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

### Build（构建）

**目标**：自动完成所有构建工作。

Design 阶段确认后，Build 阶段自动完成以下全部工作，无需人工干预：

| 步骤 | 内容 | 产出 |
|------|------|------|
| 初始化 | 创建脚手架文件 | `feature-list.json`、`task-progress.md`、`work-config.json` |
| 功能配置 | 分配每个功能的开发/测试阶段 | `feature-list.json`（更新）|
| 实现 | 逐功能 TDD 管道 | 源代码、测试文件 |
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

## 安装方式对比

| 安装方式 | 适合人群 | 是否需要 git | 插件注册 |
|---|---|---|---|
| 方式一：一键命令 | Claude Code 用户 | 否 | 需手动激活 |
| 方式二：Claude Code 自行安装 | 新机器、无 git 环境 | 否 | 需手动激活 |
| 方式三：PowerShell 启动器 | Windows 用户追求开箱即用 | 否 | 自动加载（会话级）|

> **激活**：无论用哪种方式，安装完成后都需要在 Claude Code 中运行 `/plugin install vibeflow@vibeflow` 激活插件（方式三除外，launcher 会自动加载）。

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
