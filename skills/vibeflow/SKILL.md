---
name: vibeflow
description: VibeFlow框架入口。运行 /vibeflow 开始新项目或继续现有工作流。
---

# VibeFlow框架

VibeFlow是一个结构化的六阶段工作流程，用于有目的性地、有质量关卡地、持续反思地构建软件。

## 入口选择

入口规则先定死：

- **首次进入新项目**：如果 `.vibeflow/state.json` 不存在，必须先让用户选择 `Full Mode` 或 `Quick Mode`
- **继续已有项目**：如果 `.vibeflow/state.json` 已存在，直接沿用其中的 `mode`，不要重复询问
- **直达 Quick**：如果用户显式运行 `/vibeflow-quick`，直接进入 Quick 入口，不再额外问模式

对不明确的首次请求，默认推荐 `Full Mode`；只有在“小范围、低风险、可快速回滚”的改动下，才推荐 `Quick Mode`。

运行 `/vibeflow` 后，请按上面的规则处理模式选择：

### 模式 1: Quick Mode（快速开发）

**适用场景**：
- Bug fix 或 hot fix
- 小改动、单文件修改
- 配置文件更新
- 测试文件编写
- 文档更新

**关键约束**：
- 只适合小范围、低风险、可快速回滚的工作
- 需要在 `.vibeflow/state.json` 中写明 `quick_meta`
- 需要最小产物：`docs/changes/<change-id>/design.md` 和 `tasks.md`
- 仍然必须经过 Review 和 Test

**压缩**：前置分析大幅压缩，但不是“无设计直冲代码”

**入口**：`/vibeflow-quick`

### 模式 2: Full Mode（完整流程）

**适用场景**：
- 新功能开发
- 架构变更
- 需要 UI/UX 设计的工作
- 重要系统变更（支付、认证等）
- 不确定复杂度的任务

**完整流程**：Spark → Requirements → Design → Build Init → Tasks Review → Build → Review → Test

**入口**：`/vibeflow`（选择 Full Mode）

## 框架概述

VibeFlow是一个严谨的软件开发框架，强调在构建之前思考、在每个阶段验证、持续改进。它专为质量、可维护性和清晰进度重要的项目而设计。

### 六个阶段

| 阶段 | 目的 | 关键产出物 |
|------|------|-----------|
| 1. Spark（灵感迸发） | 灵感探索、问题框定、DeepResearch、复杂度扫描、CEO 价值评估 | `docs/changes/<change-id>/context.md` |
| 2. Requirements（需求） | 需求规格说明书 | `docs/changes/<change-id>/requirements.md` |
| 3. Design（设计） | 技术设计 + 三视角评审 | `docs/changes/<change-id>/design.md` |
| 4. Build（构建） | 通过TDD、质量关卡、规范审查实现功能 | `feature-list.json` |
| 5. Review（审查） | 跨功能的整体变更分析 | 审查报告 |
| 6. Test（测试） | 系统测试和QA验证 | 测试报告 |

### 价值主张

- **目的性**：每个阶段都有明确的进入标准和完成定义
- **质量关卡**：功能不通过自动化和人工检查就无法推进
- **可追溯性**：每个决策都有文档记录，每个功能都在`feature-list.json`中跟踪
- **迭代改进**：反思阶段确保每次迭代都从前一次中学习
- **并行执行**：通过 Agent 工具在关键环节并行执行互不依赖的子任务，缩短交付周期

---

## 快速开始

对于新项目或首次设置，按顺序运行以下命令：

### 步骤1：开始Spark阶段

```
使用vibeflow-spark skill来探索灵感、确定方向并进行价值评估。
```

### 步骤2：运行Requirements阶段

```
使用vibeflow-requirements编写需求规范。
```

### 步骤3：运行Design阶段

```
使用vibeflow-design编写技术设计。
```

### 步骤4：初始化Build阶段

```
Design 确认后先进入 `build-init` 生成交付计划。
在 Claude Code 插件里，Build 的默认路径会先跑 `build-init`，产出 `tasks.md` + `feature-list.json` 并停在 `tasks` 人工确认闸门。
只有 `tasks` 获批后，才继续后续自动链路。
只有在调试单个子阶段时，才单独调用 vibeflow-build-init 或 vibeflow-build-work。
```

---

## 前置条件检查

在任何VibeFlow工作开始之前，验证环境是否正确设置。

### 1. 验证仓库钩子已安装

运行以下命令确保pre-commit钩子处于活动状态：

```bash
ls -la .git/hooks/pre-commit
```

如果钩子未安装，初始化它们：

```bash
git config core.hooksPath .githooks
```

### 2. 验证VibeFlow设计文档存在

VibeFlow需要在仓库根目录有一个`VIBEFLOW-DESIGN.md`。检查：

```bash
cat VIBEFLOW-DESIGN.md
```

如果此文件不存在，必须先完成Think和Plan阶段来创建它。

### 3. 验证所有子技能都存在

列出所有vibeflow-*技能：

```bash
ls skills/vibeflow-*/
```

预期技能：
- vibeflow-router
- vibeflow-think
- vibeflow-plan-review
- vibeflow-requirements
- vibeflow-design
- vibeflow-build-init
- vibeflow-build-work
- vibeflow-tdd
- vibeflow-quality
- vibeflow-feature-st
- vibeflow-spec-review
- vibeflow-review
- vibeflow-test-system
- vibeflow-test-qa
- vibeflow-ship
- vibeflow-reflect

### 4. 验证功能列表已初始化（仅Build阶段）

如果您处于Build阶段，验证`feature-list.json`存在：

```bash
cat feature-list.json
```

---

## 六阶段工作流程概述

### 阶段1：Spark（灵感迸发）

**目的**：灵感探索、问题框定、方向确定、DeepResearch（按需）、复杂度扫描、CEO 价值评估。

**何时进入**：项目开始或面对不清晰的问题时。

**关键产出物**：`docs/changes/<change-id>/context.md`

**使用的技能**：
- `vibeflow-spark`
- `vibeflow-deepresearch`（按需）

**退出标准**：问题框定完成、方向明确、价值评估通过（EXPANSION/SELECTIVE/HOLD），自动进入 Requirements。

---

### 阶段2：Requirements（需求）

**目的**：编写需求规格说明书。

**何时进入**：Spark 阶段价值评估通过后。

**关键产出物**：
- `docs/changes/<change-id>/requirements.md`

**使用的技能**：
- `vibeflow-requirements`

**退出标准**：需求文档完成并批准。

---

### 阶段3：Design（设计）

**目的**：技术设计 + 三视角评审。

**何时进入**：Requirements 阶段完成后。

**关键产出物**：
- `docs/changes/<change-id>/design.md`
- `docs/changes/<change-id>/design-review.md`

**使用的技能**：
- `vibeflow-design`

**退出标准**：技术设计完成，通过 eng review 和 design review。

---

### 阶段4：Build（构建）

**目的**：先生成交付计划并获得人工确认，再自动接管后半程执行链路。

**何时进入**：Design 阶段批准后。

**关键产出物**：`feature-list.json`、`docs/changes/<change-id>/tasks.md`

**默认执行方式**：
- `build-init` 先生成 `feature-list.json`、任务包、`tasks.md`
- 在 `tasks` 阶段展示全量交付计划并等待人工确认
- 获批后 router 持续执行 `build-config -> build-work -> review -> test`
- 直到 `done`、阻塞、或需要人工确认

**子技能（默认作为内部子步骤 / fallback）**：
- `vibeflow-build-init` - 初始化构建产物（运行一次）
- `vibeflow-build-work` - 编排功能流程
- `vibeflow-tdd` - 红-绿-重构循环
- `vibeflow-quality` - 覆盖率和变异测试关卡
- `vibeflow-feature-st` - 功能验收测试（与 spec-review **并行**）
- `vibeflow-spec-review` - 每个功能的合规性审查（与 feature-st **并行**）

**并行执行**：Quality Gates 通过后，Feature-ST 和 Spec-Review 通过 Agent 工具并行执行。

**退出标准**：`feature-list.json`中的所有功能标记为完成并通过，然后自动继续进入 Review/Test。

---

### 阶段5：Review（审查）

**目的**：跨整个分支或差异的整体变更审查，发现跨功能问题。

**何时进入**：所有功能通过Build阶段后。

**使用的技能**：
- `vibeflow-review`

**并行执行**：结构审查、回归检查、完整性检查通过 Agent 工具三路并行执行。

**退出标准**：生成的审查报告没有阻塞性问题。

---

### 阶段6：Test（测试）

**目的**：系统级测试和QA验证，确保整个系统端到端工作。

**何时进入**：Review阶段通过后。

**使用的技能**：
- `vibeflow-test-system` - 集成和系统测试
- `vibeflow-test-qa` - 面向浏览器的QA验证

**并行执行**：回归测试通过后，集成测试、E2E 场景、NFR 验证、探索性测试通过 Agent 工具四路并行执行。

**退出标准**：所有系统测试通过，QA报告生成没有阻塞性问题。

---

## 模板指南

VibeFlow支持四种工作流程模板。根据项目范围、团队规模和治理要求进行选择。

### Prototype（原型）模板

**使用场景**：构建快速原型、概念验证或MVP，其中UI是可选的或推迟的。

**特点**：
- 最小文档开销
- UI工作可选
- 适合快速探索想法
- 不需要正式需求文档

**最适合**：黑客马拉松、POC、内部工具实验。

---

### Web-Standard（Web标准）模板

**使用场景**：构建具有前端、后端和潜在UI工作的完整Web应用程序。

**特点**：
- 完整的需求和设计文档
- 如果UI在范围内则需要UCD
- 标准质量关卡适用
- 所有功能都需要TDD

**最适合**：面向客户的Web应用程序、SaaS产品。

---

### API-Standard（API标准）模板

**使用场景**：构建后端优先项目，其中主要交付物是API或服务。

**特点**：
- 需求侧重于API契约
- 设计侧重于数据模型和服务架构
- UI工作推迟或最少
- 强调集成测试

**最适合**：微服务、API产品、后端系统。

---

### Enterprise（企业）模板

**使用场景**：大型团队、严格治理要求或受监管环境。

**特点**：
- 正式需求规范（SRS）是强制性的
- 需要设计审查委员会批准
- 严格的变更控制流程
- 所有产物完全可追溯
- 扩展的QA和合规性验证

**最适合**：企业软件、安全关键系统、受监管行业。

---

## 常见陷阱

### 陷阱1：没有先思考就开始

**问题**：不定义问题就直接跳入代码会导致范围蔓延、优先级不清和返工。

**预防**：在任何实现之前始终完成 Spark 阶段。`docs/changes/<change-id>/context.md` 产物必须存在并经过价值评估。

---

### 陷阱2：跳过阶段

**问题**：在没有批准的需求或设计的情况下尝试构建会导致不对齐和昂贵的返工。

**预防**：每个阶段都有明确的进入标准。在Requirements和Design完全批准之前不要进入Build。

---

### 陷阱3：不使用feature-list.json

**问题**：在临时笔记或记忆中跟踪功能会导致功能遗漏、状态不清和集成失败。

**预防**：在Build阶段将`feature-list.json`作为所有功能状态的单一事实来源。

---

### 陷阱4：绕过质量关卡

**问题**：跳过TDD、覆盖率阈值或变异测试来"节省时间"会引入技术债务和回归。

**预防**：质量关卡是不可协商的。一个功能直到所有四个关卡都通过才算完成。

---

### 陷阱5：跳过审查阶段

**问题**：只关注每个功能的审查会忽略跨功能交互、隐藏依赖和系统性问题。

**预防**：在进入Test之前，始终在Build之后运行`vibeflow-review`。

---

## 子技能参考

以下15个子技能支持VibeFlow框架：

| 技能 | 目的 |
|------|------|
| `vibeflow-router` | 在会话开始时路由整个VibeFlow生命周期的工作 |
| `vibeflow-spark` | 灵感迸发：问题框定、DeepResearch、复杂度扫描、CEO 价值评估 |
| `vibeflow-deepresearch` | 深度调研：竞品分析、技术栈分析、能力矩阵、产品护城河调研 |
| `vibeflow-requirements` | 编写批准的需求规范（SRS） |
| `vibeflow-design` | 在初始化之前编写技术设计（含 UCD 内联：视觉风格、Token、组件提示词） |
| `vibeflow-build-init` | 在设计批准后初始化实现产物 |
| `vibeflow-build-work` | 驱动功能通过TDD到质量关卡再到规范审查 |
| `vibeflow-tdd` | 构建阶段内的红-绿-重构步骤 |
| `vibeflow-quality` | 构建期间覆盖率和变异质量关卡 |
| `vibeflow-feature-st` | 构建期间的功能级验收测试 |
| `vibeflow-spec-review` | 每个功能对需求和设计的合规性审查 |
| `vibeflow-review` | 构建后跨功能的整体变更审查 |
| `vibeflow-test-system` | 构建完成后的系统级测试 |
| `vibeflow-test-qa` | 系统测试后的浏览器导向QA验证 |

---

## 硬规则

1. 当`VIBEFLOW-DESIGN.md`存在于仓库中时，**始终在会话开始时读取`skills/vibeflow-router/SKILL.md`**
2. **永不跳过阶段**：每个阶段都有必须在推进之前满足的进入标准。
3. **在Build阶段维护`feature-list.json`**作为单一事实来源。
4. **将所有工作流程技能保持在仓库内的`skills/`**下。
5. **将`VIBEFLOW-DESIGN.md`视为仓库的产品契约**。
6. **通过本地阶段别名重用现有基础技能**，而不是重新编写它们。
