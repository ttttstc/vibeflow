# VibeFlow

**结构化的七阶段软件交付框架** — 让 AI 按工程纪律交付软件，而不是随机 vibe coding。

[English](README.md) | 中文

---

## 快速开始

### 前置条件

克隆完整的 VibeFlow 仓库。Skills、scripts、templates 和 hooks 协同工作，不支持部分拷贝。

```bash
git clone https://github.com/ttttstc/vibeflow.git
```

### 使用

```bash
# 1. 在目标项目中启动 Think 阶段
#    AI 会自动写 .vibeflow/think-output.md 并推荐模板

# 2. 生成工作流配置
python scripts/new-vibeflow-config.py --template api-standard --project-root <你的项目>

# 3. 生成构建配置（控制哪些步骤启用、质量阈值）
python scripts/new-vibeflow-work-config.py --project-root <你的项目>

# 4. 检测当前阶段（session hook 会自动调用）
python scripts/get-vibeflow-phase.py --project-root <你的项目> --json

# 5. 开始工作 — AI 会根据阶段自动路由到正确的 skill
```

---

## 为什么需要 VibeFlow

| 没有 VibeFlow 的 AI 编程 | 使用 VibeFlow |
|---|---|
| "帮我写个 API" → 直接开始编码，没有需求分析 | Think → 问题框定 → 模板选择 → 需求规格 → 技术设计 → 再编码 |
| 功能写到一半忘记做了什么，换个会话全部丢失 | `feature-list.json` + `task-progress.md` 持久化所有状态，跨会话恢复 |
| 测试？覆盖率？"看起来能用就行" | TDD 铁律 → 覆盖率门禁 → 变异测试 → 功能验收 → 规范审查，五层质量关卡 |
| 代码审查只有 AI 自己看自己的代码 | 结构化规范审查：对照 SRS 和 Design 逐条验证合规性 |
| 做完就完了，没有任何文档或回顾 | Ship 阶段生成发布说明，Reflect 阶段产出回顾文档和改进建议 |
| 项目越大越混乱，AI 越来越不知道该做什么 | 文件驱动的确定性路由：AI 永远知道现在该做什么，下一步是什么 |

---

## 核心理念

### 1. 需求驱动，而非代码驱动

先写需求规格（SRS），再写技术设计，最后才写代码。每个功能的实现都可以追溯到具体的需求条目。

### 2. 文件即状态

所有工作流状态都持久化在仓库文件中（`.vibeflow/`、`docs/plans/`、`feature-list.json`）。不依赖 AI 记忆或聊天历史。关闭会话、换一台机器，甚至换一个 AI — 项目状态完整保留。

### 3. 确定性路由

`get-vibeflow-phase.py` 通过检查文件存在性和特征状态，确定性地计算当前阶段。16 个阶段状态、严格的 elif 链，没有歧义。

### 4. 模板控制严格度

四种静态模板（prototype → enterprise）控制哪些阶段必须执行、质量门禁阈值多高、是否需要 UI 测试和反思。一次选择，全局生效。

### 5. 单功能循环

Build 阶段一次只处理一个功能，每个功能必须走完完整的 TDD → Quality → Feature-ST → Spec-Review 流程才算完成。杜绝"先全部写完再一起测试"的反模式。

### 6. Subagent 并行执行

在互不依赖的子任务之间，通过 Claude Code 的 Agent 工具创建 subagent 并行执行，缩短交付周期：

| 环节 | 并行策略 | 加速比 |
|---|---|---|
| Build: Quality 后 | Feature-ST + Spec-Review 双路并行 | ~2x |
| Review | 结构审查 + 回归检查 + 完整性检查 三路并行 | ~3x |
| Test-System | 集成 + E2E + NFR + 探索性 四路并行 | ~4x |

所有并行执行都有回退机制：如 Agent 工具不可用，自动降级为顺序执行。

---

## 七阶段架构

```
Think → Plan → Build → Review → Test → Ship → Reflect
  │        │       │        │        │       │       │
  ▼        ▼       ▼        ▼        ▼       ▼       ▼
问题框定  需求规格  TDD实现  跨功能审查 系统测试 发布产物 回顾改进
模板选择  技术设计  质量关卡  合规检查  QA验证  版本标签 经验教训
```

### 阶段 1：Think（思考）

**目标**：定义问题、理解边界、扫描机会、选择工作流模板。

- 产出 `.vibeflow/think-output.md`：问题陈述、范围边界、用户画像、复杂度评估、机会扫描
- 推荐并确认模板（prototype / web-standard / api-standard / enterprise）
- 生成 `.vibeflow/workflow.yaml`

### 阶段 2：Plan（计划）

**目标**：获得范围认可、编写需求规格、产出技术设计。

| 子阶段 | Skill | 产出物 |
|---|---|---|
| 计划评审 | `vibeflow-plan-review` | `.vibeflow/plan-review.md` |
| 需求规格 | `vibeflow-requirements` | `docs/plans/*-srs.md` |
| 界面设计 | `vibeflow-ucd` | `docs/plans/*-ucd.md`（按需） |
| 技术设计 | `vibeflow-design` | `docs/plans/*-design.md` |

### 阶段 3：Build（构建）

**目标**：逐功能实现，每个功能通过完整的质量管道。

```
初始化 → 选择功能 → TDD Red-Green-Refactor → 质量门禁 ──┬── 功能验收 ──┬── 下一个功能
                          │                      │       │              │
                          ▼                      ▼       │  (并行)      │
                    vibeflow-tdd          vibeflow-quality│              │
                                          · 行覆盖率     └── 规范审查 ──┘
                                          · 分支覆盖率       (Agent)
                                          · 变异分数
```

- `vibeflow-build-init`：初始化 `feature-list.json`、`task-progress.md`、`RELEASE_NOTES.md` 等构建产物
- `vibeflow-build-work`：编排单功能流程，驱动 TDD → Quality → Feature-ST → Spec-Review 管道
- `.vibeflow/work-config.json`：根据模板裁剪步骤（prototype 跳过规范审查，enterprise 全部强制）

### 阶段 4：Review（审查）

**目标**：跨功能的整体变更审查，发现跨功能交互问题。

- `vibeflow-review`：分析整个分支的差异，检查架构一致性、安全性、性能
- 产出 `.vibeflow/review-report.md`

### 阶段 5：Test（测试）

**目标**：系统级测试和 QA 验证。

- `vibeflow-test-system`：集成测试、端到端测试、非功能需求验证
- `vibeflow-test-qa`：浏览器驱动的 QA 测试（仅 UI 项目）
- 产出 `docs/plans/*-st-report.md`、`.vibeflow/qa-report.md`

### 阶段 6：Ship（发布）

**目标**：准备发布产物。

- `vibeflow-ship`：版本号管理、PR 创建、标签打标、发布文档
- 产出 `RELEASE_NOTES.md`

### 阶段 7：Reflect（反思）

**目标**：回顾本轮迭代，为下一轮产出改进建议。

- `vibeflow-reflect`：一通率、缺陷密度、覆盖率趋势等度量分析
- 产出 `.vibeflow/retro-YYYY-MM-DD.md`

---

## 18 个 Skill 架构

VibeFlow 由 18 个独立 skill 组成，分为四层：

### 核心层

| Skill | 职责 |
|---|---|
| `vibeflow` | 框架入口，七阶段概览和快速开始 |
| `vibeflow-router` | 会话路由器，基于文件状态分派到正确的阶段 skill |
| `vibeflow-think` | Think 阶段，问题框定和模板选择 |

### 计划层

| Skill | 职责 |
|---|---|
| `vibeflow-plan-review` | 执行范围审查，在规范编写前获得认可 |
| `vibeflow-requirements` | 编写需求规格说明书（SRS），遵循 ISO/IEC/IEEE 29148 |
| `vibeflow-ucd` | 界面控制文档，设计系统和组件规范 |
| `vibeflow-design` | 技术设计文档，架构方案和数据模型 |

### 构建层

| Skill | 职责 |
|---|---|
| `vibeflow-build-init` | 初始化构建产物（`feature-list.json` 等） |
| `vibeflow-build-work` | 单功能编排器，驱动 TDD → Quality → ST → Review 管道 |
| `vibeflow-tdd` | TDD Red-Green-Refactor 循环 |
| `vibeflow-quality` | 质量门禁：行覆盖率、分支覆盖率、变异测试分数 |
| `vibeflow-feature-st` | 功能级验收测试，ISO/IEC/IEEE 29119 测试用例文档 |
| `vibeflow-spec-review` | 规范合规性审查，对照 SRS 和 Design 逐条验证 |

### 验证与发布层

| Skill | 职责 |
|---|---|
| `vibeflow-review` | 跨功能整体变更审查 |
| `vibeflow-test-system` | 系统级集成测试和非功能需求验证 |
| `vibeflow-test-qa` | 浏览器驱动的 QA 验证（仅 UI 项目） |
| `vibeflow-ship` | 版本发布、PR 创建、变更日志 |
| `vibeflow-reflect` | 迭代回顾和改进建议 |

### Skill 调用图

```
Session Start
    │
    ▼
vibeflow-router ──── get-vibeflow-phase.py ──── 检测 16 种阶段状态
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

## 模板系统

四种静态模板控制工作流严格度：

| 维度 | Prototype | Web-Standard | API-Standard | Enterprise |
|---|---|---|---|---|
| **Think 深度** | quick | standard | standard | deep |
| **计划评审** | CEO 削减模式 | CEO 保持模式 | CEO 保持模式 | CEO 扩展模式 |
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
| **QA 测试** | 可选（无 UI 跳过） | 按需 | 按需 | 按需 |
| **反思** | 可选 | 可选 | 可选 | 必需 |
| **版本策略** | manual | semver | semver | semver |
| **适用场景** | 黑客马拉松、POC | Web 应用 | API 服务 | 企业/合规系统 |

---

## 文件驱动路由

VibeFlow 的核心创新是文件驱动的确定性路由。`get-vibeflow-phase.py` 通过检查仓库中特定文件的存在性和内容，确定当前应该执行哪个阶段：

```
increment-request.json 存在?  ──yes──▶ increment
think-output.md 不存在?       ──yes──▶ think
workflow.yaml 不存在?         ──yes──▶ template-selection
plan-review.md 不存在?        ──yes──▶ plan-review
*-srs.md 不存在?              ──yes──▶ requirements
需要 UI 且 *-ucd.md 不存在?   ──yes──▶ ucd
*-design.md 不存在?           ──yes──▶ design
feature-list.json 不存在?     ──yes──▶ build-init
work-config.json 不存在?      ──yes──▶ build-config
有功能未通过?                  ──yes──▶ build-work
review-report.md 不存在?      ──yes──▶ review
*-st-report.md 不存在?        ──yes──▶ test-system
需要 UI 且 qa-report.md 不存在? ─yes─▶ test-qa
RELEASE_NOTES.md 不存在?      ──yes──▶ ship
retro-*.md 不存在?            ──yes──▶ reflect
以上全部通过                          ▶ done
```

这个设计意味着：
- **跨会话恢复**：关闭聊天窗口再打开，AI 立刻知道该继续做什么
- **多 AI 协作**：不同的 AI 可以接力完成同一个项目
- **无歧义**：不存在"AI 理解错了当前阶段"的情况

---

## 会话钩子

VibeFlow 通过 session hook 在每次会话开始时自动注入上下文：

```
hooks/
  hooks.json          ← Claude Code 钩子配置
  session-start.ps1   ← Windows PowerShell 入口
  session-start.sh    ← macOS/Linux bash 入口
```

Session hook 的职责：
1. 调用 `get-vibeflow-phase.py` 检测当前阶段
2. 读取 `vibeflow-router` 的 SKILL.md
3. 将阶段信息和路由指令注入会话上下文
4. AI 收到上下文后自动路由到正确的阶段 skill

---

## 项目状态文件

### 运行时状态（`.vibeflow/`）

| 文件 | 用途 |
|---|---|
| `think-output.md` | Think 阶段产物：问题陈述、边界、模板推荐 |
| `workflow.yaml` | 当前生效的工作流配置（从模板复制） |
| `work-config.json` | 构建配置：启用的步骤、质量阈值 |
| `plan-review.md` | 计划评审记录 |
| `review-report.md` | 全局代码审查报告 |
| `qa-report.md` | QA 测试报告 |
| `retro-YYYY-MM-DD.md` | 迭代回顾文档 |
| `increment-request.json` | 增量需求信号文件 |

### 交付产物

| 文件 | 用途 |
|---|---|
| `docs/plans/*-srs.md` | 需求规格说明书 |
| `docs/plans/*-ucd.md` | 界面控制文档 |
| `docs/plans/*-design.md` | 技术设计文档 |
| `docs/plans/*-st-report.md` | 系统测试报告 |
| `docs/test-cases/feature-*.md` | 功能测试用例文档 |
| `feature-list.json` | 功能清单（构建阶段的单一事实来源） |
| `task-progress.md` | 任务进度日志 |
| `RELEASE_NOTES.md` | 发布说明 |

---

## 对比矩阵

| 维度 | 典型 AI 编程 | VibeFlow |
|---|---|---|
| **需求** | 口头描述或没有 | 结构化 SRS 文档（ISO 29148） |
| **设计** | 直接写代码 | 技术设计文档 + UCD |
| **状态管理** | 依赖聊天历史 | 文件持久化，确定性路由 |
| **质量保证** | "看起来能用" | TDD + 覆盖率 + 变异测试 + 验收 |
| **测试文档** | 没有 | ISO 29119 测试用例文档 |
| **代码审查** | 无或自我审查 | 结构化规范合规审查 |
| **跨会话** | 每次重新开始 | 文件状态完整保留，秒级恢复 |
| **工作流** | 手动或无 | 自动路由，16 阶段状态机 |
| **严格度** | 无法调节 | 4 种模板，从原型到企业级 |
| **可追溯性** | 无 | 需求 → 设计 → 功能 → 测试，全链路追溯 |

---

## 仓库结构

```text
vibeflow/
├── .claude-plugin/                  # 插件清单
│   └── plugin.json
├── commands/                        # 用户斜杠命令 (/vibeflow:*)
│   ├── work.md
│   ├── status.md
│   ├── requirements.md
│   ├── design.md
│   ├── init.md
│   ├── ucd.md
│   ├── st.md
│   └── increment.md
├── skills/                          # 19 个工作流 skill
│   ├── using-vibeflow/              # 引导路由器（会话入口）
│   ├── vibeflow/                    # 框架入口
│   ├── vibeflow-router/             # 会话路由器
│   ├── vibeflow-think/              # Think 阶段
│   ├── vibeflow-plan-review/        # 计划评审
│   ├── vibeflow-requirements/       # 需求规格
│   ├── vibeflow-ucd/                # 界面设计
│   ├── vibeflow-design/             # 技术设计
│   ├── vibeflow-build-init/         # 构建初始化
│   ├── vibeflow-build-work/         # 功能编排
│   ├── vibeflow-tdd/                # TDD 循环
│   ├── vibeflow-quality/            # 质量门禁
│   ├── vibeflow-feature-st/         # 功能验收
│   ├── vibeflow-spec-review/        # 规范审查
│   ├── vibeflow-review/             # 全局审查
│   ├── vibeflow-test-system/        # 系统测试
│   ├── vibeflow-test-qa/            # QA 测试
│   ├── vibeflow-ship/               # 发布
│   └── vibeflow-reflect/            # 反思
├── scripts/                         # Python 脚本
│   ├── get-vibeflow-phase.py        # 阶段检测（16 状态路由器）
│   ├── new-vibeflow-config.py       # 工作流配置生成
│   ├── new-vibeflow-work-config.py  # 构建配置生成
│   └── test-vibeflow-setup.py       # 环境验证
├── templates/                       # 静态工作流模板
│   ├── prototype.yaml
│   ├── web-standard.yaml
│   ├── api-standard.yaml
│   └── enterprise.yaml
├── hooks/                           # 会话钩子
│   ├── hooks.json
│   ├── session-start.ps1
│   └── session-start.sh
├── validation/                      # 验证项目
│   └── sample-priority-api/
├── VIBEFLOW-DESIGN.md               # 设计契约
├── ARCHITECTURE.md                  # 架构文档
├── USAGE.md                         # 使用指南
└── TODOS.md                         # 待办事项
```

---

## 设计原则

1. **厂商中立**：所有面向项目的名称只用 `vibeflow`，不绑定任何特定 AI 提供商
2. **文件驱动路由**：当前阶段由仓库文件状态确定，而非聊天历史或进程内存
3. **薄编排层**：skill 定义路由和契约，具体实现细节留在目标项目中
4. **模板派生行为**：工作流严格度一次选择、全局传播，通过生成的配置控制
5. **仓库本地产物**：所有恢复或续做所需的状态都在目标项目的文件中

---

## 用户命令

安装后可通过 `/` 命令直接调起工作流：

| 命令 | 用途 |
|---|---|
| `/vibeflow:work` | 启动功能开发循环（TDD 管线） |
| `/vibeflow:status` | 查看项目进度和当前阶段 |
| `/vibeflow:requirements` | 启动需求规格编写 |
| `/vibeflow:design` | 启动技术设计编写 |
| `/vibeflow:init` | 初始化构建产物 |
| `/vibeflow:ucd` | 启动界面设计文档编写 |
| `/vibeflow:st` | 启动系统测试 |
| `/vibeflow:increment` | 启动增量需求开发 |

## 路线图

- [ ] 移植 9 个验证脚本（init_project、validate_features、check_st_readiness 等）
- [ ] 添加 3 个文档模板（SRS/Design/ST-Case）
- [ ] 拆分 router SKILL.md（877 行 → ~200 行核心 + references/）
- [x] ~~添加用户快捷命令（commands/）~~
- [ ] 添加 skill 参考文档（references/）
- [ ] 框架核心脚本单元测试
- [ ] CLAUDE.md 跨会话上下文注入

详见 [TODOS.md](TODOS.md) 和 [GitHub Issues](https://github.com/ttttstc/vibeflow/issues)。

---

## 文档

| 文档 | 说明 |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | 完整架构图和组件说明 |
| [USAGE.md](USAGE.md) | 目标项目操作指南 |
| [VIBEFLOW-DESIGN.md](VIBEFLOW-DESIGN.md) | 设计契约和 skill 目录 |
| [TODOS.md](TODOS.md) | 待办事项和优先级 |

---

## 许可证

MIT
