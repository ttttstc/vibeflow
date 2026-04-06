**[English](README_EN.md) | 中文**

<div align="center">

# VibeFlow

### VibeFlow 不是一个agent工具，而是一个把每次AI 驱动的软件改动组织成稳定交付链路的 skill 交付编排层

> "凡事预则立，不预则废。"
> 先定章法，再求速度；先有节奏，后有规模。

[安装](#安装) · [3 分钟上手](#3-分钟上手) · [核心能力](#核心能力) · [Skills](#skills) · [能力对比](#vibeflow-与主流-ai-编排框架能力对比)

  <a href="https://github.com/ttttstc/vibeflow/releases"><img src="https://img.shields.io/github/v/tag/ttttstc/vibeflow?label=version&style=flat-square" alt="Version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>

</div>

---

<img width="1024" height="682" alt="image" src="https://github.com/user-attachments/assets/300825bb-526c-4e90-b875-dfccb08c91f1" />


## VibeFlow 是什么

VibeFlow 不替智能体思考，也不试图再造一个执行内核。它做的事情更直接：把一次 AI 驱动的软件改动组织成一条能真正走完的交付流程，让工作不只"写出来"，还能继续、恢复、交接、审查、测试、发布和复盘。

一句话理解：**VibeFlow 把 AI 编码从"聊天里临场发挥"，变成"按SDD+Harness理念交付流程推进"**

---

## 核心能力

| 能力 | VibeFlow 做什么 |
|---|---|
| 把想法变成计划 | 先把需求、方案和任务拆清楚，再开始做 |
| 把改动真正做完 | 不只写代码，还继续推进审查、测试、发布和复盘 |
| 让工作不中断 | 会话关掉、换人接手、隔天继续，都还能接着跑 |
| 让结果有证据 | 每次改动都能留下审查、测试和交付痕迹 |
| 降低跑偏概率 | 用阶段、规则和门禁约束 AI 不要一路猜下去 |
| 让复杂任务更稳 | 把大任务拆成可推进、可回收、可验证的小块 |
| 让进度看得见 | 当前做到哪、卡在哪、下一步做什么，都有地方看 |
| 适配真实仓库 | 可以持续跑在已有项目里，而不只是新建项目模板 |

---

## 安装

### 方式一：自己安装

默认安装最新发布版本。

| 平台 | 安装命令 | 安装后 |
|---|---|---|
| macOS / Linux | `/sh curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.sh \| bash` | 运行 `/plugin install vibeflow@vibeflow` |
| Windows PowerShell | `irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.ps1 \| iex` | 运行 `/plugin install vibeflow@vibeflow` |

<details>
<summary>指定版本安装</summary>

| 平台 | 命令 |
|---|---|
| macOS / Linux | `/sh curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.sh \| VIBEFLOW_VERSION=v1.0.0 bash` |
| Windows | `$env:VIBEFLOW_VERSION="v1.0.0"; irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.ps1 \| iex` |

</details>

### 方式二：让 AI 帮你安装

<details>
<summary>粘贴以下内容到 Claude Code</summary>

```text
帮我安装 VibeFlow，并确保最后能正常使用。

要求：
1. 根据当前系统选择官方安装命令：
   - macOS / Linux：
     /sh curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.sh | bash
   - Windows：
     irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.ps1 | iex
2. 如果我给了版本号，就安装指定版本；否则安装最新发布版本
3. 如果脚本不可用，再手动安装到 Claude Code marketplace 目录
4. 安装完成后执行：
   /plugin install vibeflow@vibeflow
5. 验证安装是否成功：
   - 重启或刷新 Claude Code 后运行 /vibeflow
   - 如果没有成功，继续排查直到成功或明确告诉我卡在哪一步
6. 最后告诉我：
   - 是否安装成功
   - 安装到了哪里
   - 当前安装版本
   - 下一步该怎么开始使用
```

</details>


### 验证安装

运行 `/vibeflow`，能看到 VibeFlow 入口说明，就说明插件已正常加载。
如果还想确认 plugin 可见工具入口也已就绪，再执行 `/vibeflow-status` 或 `/vibeflow-dashboard`。

<details>
<summary>更新与卸载</summary>

更新使用与安装相同的命令。更新后重启 Claude Code 并再次执行 `/plugin install vibeflow@vibeflow`。
</details>

---

## 3 分钟上手

1. 安装并激活插件后，在项目里运行 `/vibeflow`
2. 第一次进入时选择 `Full Mode` 或 `Quick Mode`
3. 在 `Spark → Design → Tasks` 完成必要确认
4. 一旦进入 `Build`，系统默认自动继续 `Review → Test → Ship / Reflect`
5. 想看进度时用 `/vibeflow-status` 或 `/vibeflow-dashboard`

一句话理解：**前半程你拍板，后半程系统推进，卡住了再回来问你。**


> **模式选择建议：** 不确定时优先选 `Full Mode`。只有小范围、低风险、可快速回滚的改动再用 `Quick Mode`。如果项目里已有 `.vibeflow/state.json`，会自动沿用已有 mode 继续工作。

---

## 常用命令

| 需求 | 命令 |
|---|---|
| 开始或继续工作流 | `/vibeflow` |
| 快速处理小改动 | `/vibeflow-quick` |
| 启动独立学习流 | `/vibeflow-learn` |
| 查看当前状态摘要 | `/vibeflow-status` |
| 打开本地 live 看板 | `/vibeflow-dashboard` |

---

## 深入了解

如果把 VibeFlow 用在一个真实项目里，你最终得到的不是一组提示词，而是一套可以持续运行的软件交付机制。

### 结构化交付流程

- `Spark → Design → Tasks` 负责想清楚问题、方案和执行顺序
- `Build → Review → Test` 负责把实现、审查和验证真正跑完
- `Ship / Reflect` 作为可选收尾，处理发布和复盘

<img width="2528" height="1684" alt="phase" src="https://github.com/user-attachments/assets/bbe150db-e5e1-4f46-8a05-5934d49266b9" />


### 文件即状态

VibeFlow 把状态留在仓库里，而不是留在一次聊天里。关掉会话、换机器、换 AI，都能继续。

<img width="1376" height="768" alt="文件驱动状态" src="https://github.com/user-attachments/assets/eb46f4ea-6510-4118-823b-d2cf2940cb08" />

### Build 后自动继续

设计确认后，系统不需要你手动推进每个子步骤。进入 `Build` 后自动走完 `Review → Test → Ship → Reflect`，直到完成、阻塞，或需要你确认。

### 更稳的实现链路

Build 不是"把整份长上下文硬塞给 AI 再赌它别漂"。当前已支持：

- Feature 级实施输入，以 `design.md + tasks.md + feature-list.json + rules/` 为主输入
- 归一化 feature 合同和执行证据保存在 `feature-list.json`
- 依赖感知构建，安全回退到串行执行
- Review 区分"做得对不对"和"代码写得稳不稳"

### 现有项目也能用

VibeFlow 不只适合新项目。它能维护项目级代码结构地图，为本次变更生成影响分析，在 Spark / Design 阶段自动引用这些上下文。

<img width="1376" height="768" alt="现有项目支持" src="https://github.com/user-attachments/assets/e658a4ca-75ba-414a-845a-71a9e623debb" />

### 本地 live 看板

不需要盯着 `state.json` 猜系统跑到哪了。看板展示当前 mode/phase、主阶段状态、feature 状态、关键产物、最近事件和下一步建议。

### 质量闭环

默认链路包含：TDD、覆盖率门禁、变异测试、功能验收、全局审查、系统测试，以及 UI 场景下的 QA。

### 增量、发布与复盘

除主工作流外，还支持增量请求队列、发布说明和迭代复盘日志。

### 模板与安全护栏

四种模板控制流程严格度和质量阈值。`careful / freeze / guard` 安全护栏限制危险命令和编辑边界。

<img width="1376" height="768" alt="模板与安全护栏" src="https://github.com/user-attachments/assets/1e0cbb71-9abf-4920-8533-509afe333e81" />

---

## Skills

VibeFlow 不只是一条 `/vibeflow` 命令，而是一组按交付链和工程协作分工的 skills。你触发入口命令后，系统会调用对应 playbook，而不是把所有工作都塞进一个大 prompt。

### 入口 Skills

| Skill | When | What it does |
|---|---|---|
| `/vibeflow` | 需要开始或继续完整软件交付 | 进入主控制面，按仓库状态路由到 Spark / Design / Tasks / Build / Review / Test / Ship / Reflect。 |
| `/vibeflow-quick` | 小范围、低风险、可快速回滚的改动 | 走压缩前置分析的 Quick Mode，保留最小设计、Review 和 Test。 |
| `/vibeflow-learn` | 陌生领域学习、研究文章写作、把资料变成输出 | 进入独立学习流，用 `Collect -> Digest -> Outline -> Fill In -> Refine -> Publish` 六阶段推进，不写入 `/vibeflow` 主链路状态。 |
| `/vibeflow-status` | 想快速知道当前做到哪 | 输出当前 phase、恢复原因、建议下一步和推荐打开文件。 |
| `/vibeflow-dashboard` | 想可视化查看整个运行态 | 打开本地 live dashboard，看 mode、phase、feature 状态、关键产物和最近事件。 |

### 主链路 Skills

| Skill | When | What it does |
|---|---|---|
| `vibeflow-spark` | 定义问题和范围 | 编排 Office Hours、复杂度扫描、DeepResearch、Roundtable 和价值评估，输出 `brief.md`。 |
| `vibeflow-design` | 方向确定后，要把 HOW 设计清楚 | 产出 `design.md` |
| `vibeflow-tasks` | 设计获批后，要把执行顺序落细 | 生成 execution-grade `tasks.md`，作为 Build 前的正式 handoff。 |
| `vibeflow-build-init` + `vibeflow-build-work` | 进入 Build 后推进实现 | 初始化实现产物、按 feature 合同推进开发，并把执行真相写回 `feature-list.json`。 |
| `vibeflow-review` | 功能实现后做整体变更审查 | 从跨功能角度检查架构、安全、性能和完整性问题。 |
| `vibeflow-test-system` + `vibeflow-test-qa` | 审查通过后做系统验证 | 覆盖系统测试、集成验证和 UI/浏览器 QA。 |
| `vibeflow-ship` + `vibeflow-reflect` | 测试通过后收尾 | 处理发布说明、交付收尾和迭代复盘。 |

### 辅助 Skills

| Skill | When | What it does |
|---|---|---|
| `vibeflow-wiki` | 需要补齐或刷新项目长期上下文 | 维护 `docs/overview/`，让项目记忆和 change 上下文保持新鲜。 |
| `vibeflow-deepresearch` | 竞品或技术调研 | 系统化分析 GitHub 同领域项目，输出能力矩阵、技术栈分布和差异化机会。 |
| `vibeflow-plan-value-review` | 判断值不值得做 | 从价值、范围和投入产出角度做前置审视。 |
| `vibeflow-plan-eng-review` | 在设计阶段做工程审查 | 审架构、数据流、测试策略、性能与风险。 |
| `vibeflow-plan-design-review` | 在设计阶段做体验审查 | 审信息架构、交互状态、AI slop 风险、响应式和无障碍。 |
| `vibeflow-tdd` + `vibeflow-quality` + `vibeflow-feature-st` + `vibeflow-spec-review` | Build 内部质量关卡 | 用 TDD、覆盖率/变异测试、功能验收和规格审查把实现链路收紧。 |
| `vibeflow-careful` / `vibeflow-freeze` / `vibeflow-guard` / `vibeflow-unfreeze` | 需要安全护栏时 | 限制危险命令、限制编辑边界，或解除这些限制。 |

这些 skill 是文件夹，不只是单个 Markdown。它们可以带自己的 reference、脚本、约束和 gotchas，所以 VibeFlow 的能力不是一段提示词，而是一套可维护的交付 playbooks。

---

## VibeFlow 与主流 AI 编排框架能力对比

说明：`高 / 中 / 低` 表示该能力是不是这个框架的主轴，不代表绝对优劣。

| 框架 | 规格先行 | 工程纪律 | 长任务稳定 | 多智能体编排 | 验证闭环 | 项目记忆 | 交付收尾 | 重量 |
|---|---|---|---|---|---|---|---|---|
| OpenSpec | 高 | 低 | 中 | 低 | 低 | 中 | 低 | 低 |
| Superpowers | 中 | 高 | 中 | 中 | 中 | 低 | 低 | 中 |
| GSD | 中 | 中 | 高 | 中 | 中 | 中 | 中 | 中 |
| OMC | 低 | 中 | 中 | 高 | 中 | 中 | 中 | 中高 |
| ECC | 中 | 高 | 高 | 中 | 高 | 高 | 中 | 高 |
| Trellis | 高 | 中 | 高 | 中 | 中 | 高 | 中 | 中高 |
| **VibeFlow** | **高** | **高** | **高** | 中 | **高** | 中高 | 中高 | 中高 |

---

## 关键产物

### 项目级（`docs/overview/`）

| 文件 | 作用 |
|---|---|
| `PROJECT.md` | 项目背景、范围和长期上下文 |
| `ARCHITECTURE.md` | 项目级架构说明 |
| `CURRENT-STATE.md` | 当前项目现状快照：做到哪了、active change、下一步建议 |

### 变更级（`docs/changes/<change-id>/`）

| 文件 | 作用 |
|---|---|
| `brief.md` | 起点、目标、范围、约束和验收边界 |
| `design.md` | 实现方案，也是 Build Contract 的权威来源 |
| `tasks.md` | execution-grade 任务清单，供 Build 直接消费 |
| `docs/overview/CURRENT-STATE.md` | 当前变更关注点、受影响模块、建议阅读顺序 |
| `verification/review.md` | 全局审查结果 |
| `verification/system-test.md` | 系统测试结果 |
| `verification/qa.md` | UI / 浏览器验证结果 |

### 系统与配置

| 文件 | 作用 |
|---|---|
| `.vibeflow/state.json` | 工作流真相：模式、阶段、工作包、checkpoint、恢复提示 |
| `feature-list.json` | Build 阶段的功能清单和执行真相 |
| `rules/` | 项目自定义约束；优先于 `CLAUDE.md` / `AGENT.md` |
| `RELEASE_NOTES.md` | 发布说明 |

> 一句话区分：看整个项目 → `docs/overview/`，看这次工作 → `docs/changes/<change-id>/`，看实施进度 → `feature-list.json`。`.vibeflow/` 通常不需要手动查看。

> 如果 Claude 意外关闭，再次运行 `/vibeflow` 会自动恢复到中断位置，并提示当前阶段、停止原因、下一步操作和建议查看的文件。

---

## 适合什么场景

**适合：**
- 新项目从 0 到 1，或在已有工程上持续迭代
- 希望 AI 不只写代码，还能推进完整交付
- 需要可恢复、可追踪、可审查的工作流
- 希望进入 Build 后少盯流程，多看结果

**不适合：**
- 只想让 AI 随手改两行代码
- 不想维护状态文件和验证产物

---

## 文档

| 文档 | 说明 |
|---|---|
| [USAGE.md](USAGE.md) | 详细使用方式、命令入口和目标项目操作 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 架构图、状态机、组件关系 |
| [VIBEFLOW-DESIGN.md](VIBEFLOW-DESIGN.md) | 命名规则、文件布局、实现约定 |
| [DeepWiki 技术架构导览](https://deepwiki.com/ttttstc/vibeflow/1-vibeflow-overview) | 在线深度架构文档 |

---

## 学习网站

[访问学习网站](https://ttttstc.github.io/vibeflow)

---

## 许可证

MIT

<img width="1376" height="768" alt="VibeFlow" src="https://github.com/user-attachments/assets/3c2f8d03-ae18-41b8-844a-de8cfa45c9c0" />
