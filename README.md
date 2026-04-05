**[English](README_EN.md) | 中文**

---

<div align="center">

# VibeFlow

### 让 AI 写出的，不只是代码，而是一条能走完的交付链

> “凡事预则立，不预则废。”
>
> 先定章法，再求速度；先有节奏，后有规模。

[安装](#安装) · [3 分钟上手](#3-分钟上手) · [核心能力](#核心能力) · [能力对比](#vibeflow-与主流-ai-编排框架能力对比)

</div>

---
<img width="1376" height="768" alt="compare" src="https://github.com/user-attachments/assets/9a3be1a9-270c-46fc-b303-67b451ed860f" />




## VibeFlow 是什么

VibeFlow 是一个面向 Claude Code 的 AI 软件交付控制面。

它不替智能体思考，也不试图再造一个执行内核。它做的事情更直接：把一次 AI 驱动的软件改动组织成一条能真正走完的交付流程，让工作不只“写出来”，还能继续、恢复、交接、审查、测试、发布和复盘。

这条流程不只有“写代码”，还包括：

- 明确需求和范围
- 写清设计和任务
- 推进实现
- 补齐审查和测试证据
- 完成发布和复盘

一句话理解：

**VibeFlow 把 AI 编码从“聊天里临场发挥”，变成“按交付流程推进”。**

## 文档导航

- [安装](README.md#安装)
- [3 分钟上手](README.md#3-分钟上手)
- [核心能力](README.md#核心能力)
- [常用命令](README.md#常用命令)
- [详细使用指南](USAGE.md)
- [架构说明](ARCHITECTURE.md)
- [详细技术架构导览（DeepWiki）](https://deepwiki.com/ttttstc/vibeflow/1-vibeflow-overview)
- [设计契约与实现约定](VIBEFLOW-DESIGN.md)

---

## 安装

### 方式一：自己安装

默认安装最新发布版本；指定版本时为命令增加 `VIBEFLOW_VERSION=v1.0.0`。

| 平台 | 安装命令 | 安装后 |
|---|---|---|
| macOS / Linux | `/sh curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.sh \| bash` | 运行 `/plugin install vibeflow@vibeflow` |
| Windows PowerShell | `irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.ps1 \| iex` | 运行 `/plugin install vibeflow@vibeflow` |

指定版本示例：

| 平台 | 指定版本命令 |
|---|---|
| macOS / Linux | `/sh curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.sh \| VIBEFLOW_VERSION=v1.0.0 bash` |
| Windows | `$env:VIBEFLOW_VERSION="v1.0.0"; irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.ps1 \| iex` |


### 方式二：让 AI 帮你安装

如果你想直接让 Claude Code 自己完成安装，粘贴下面这段：

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


### 验证安装

运行 `/vibeflow`，能看到 VibeFlow 入口说明，就说明插件已正常加载。

### 更新与卸载

更新使用与安装相同的命令。更新后重启 Claude Code，并再次执行：

```text
/plugin install vibeflow@vibeflow
```

卸载步骤：

1. 关闭 Claude Code
2. 删除 marketplace 目录中的 `vibeflow`
3. 从 `known_marketplaces.json` 中删除 `vibeflow` 条目
4. 重新打开 Claude Code

### 其他宿主

如果你不是在 Claude Code 中使用，也可以用以下入口：

| 宿主 | 命令 |
|---|---|
| Codex / macOS / Linux | `curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/codex/install.sh \| bash` |
| Codex / Windows PowerShell | `irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/codex/install.ps1 \| iex` |
| OpenCode / macOS / Linux | `curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/opencode/install.sh \| bash` |


## 3 分钟上手

1. 安装并激活插件后，在项目里运行 `/vibeflow`
2. 第一次进入时选择 `Full Mode` 或 `Quick Mode`
3. 在 `Spark -> Design -> Tasks` 完成必要确认
4. 一旦进入 `Build`，系统默认自动继续 `Review -> Test -> Ship / Reflect`
5. 想看进度时用 `/vibeflow-status` 或 `/vibeflow-dashboard`

一句话理解：

- 前半程你拍板
- 后半程系统自己推进
- 卡住了再回来问你

---

### 首次启动的模式选择

- 第一次在项目里运行 `/vibeflow`：先选 `Full Mode` 或 `Quick Mode`
- 如果项目里已经有 `.vibeflow/state.json`：沿用已有 mode，继续当前工作
- 如果你明确运行 `/vibeflow-quick`：直接进入 Quick 流程

建议：
- 不确定时优先选 `Full Mode`
- 只有小范围、低风险、可快速回滚的改动再用 `Quick Mode`

<img width="1377" height="768" alt="image" src="https://github.com/user-attachments/assets/77257c8b-ba38-4f24-a11e-7920e4297165" />



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

## 常用命令

| 需求 | 命令 |
|---|---|
| 开始或继续工作流 | `/vibeflow` |
| 快速处理小改动 | `/vibeflow-quick` |
| 查看当前状态摘要 | `/vibeflow-status` |
| 打开本地 live 看板 | `/vibeflow-dashboard` |
| 脚本方式启动看板 | `python scripts/run-vibeflow-dashboard.py` |
| 脚本方式打印一次看板快照 | `python scripts/run-vibeflow-dashboard.py --snapshot-json` |
| 脚本方式继续当前流程 | `python scripts/run-vibeflow-autopilot.py --project-root <repo>` |

---

## 你得到什么

如果把 VibeFlow 用在一个真实项目里，你最终得到的不是一组提示词，而是一套可以持续运行的软件交付机制。

### 1. 结构化交付流程

- `Spark -> Design -> Tasks` 负责想清楚问题、方案和执行顺序
- `Build -> Review -> Test` 负责把实现、审查和验证真正跑完
- `Ship / Reflect` 作为可选收尾，处理发布和复盘

<img width="1376" height="768" alt="7 stage" src="https://github.com/user-attachments/assets/410e78e6-70c5-4e72-99e6-0855e6c889eb" />

### 2. 文件即状态

VibeFlow 把状态留在仓库里，而不是留在一次聊天里。

- 看整个项目：`docs/overview/`
- 看这次工作：`docs/changes/<change-id>/`
- 看实施进度：`feature-list.json`

这意味着：
- 关掉会话还能继续
- 换机器还能继续
- 换 AI 也能继续

<img width="1376" height="768" alt="image" src="https://github.com/user-attachments/assets/eb46f4ea-6510-4118-823b-d2cf2940cb08" />


### 3. Build 后自动继续

设计确认后，系统不会让你继续手动点一串 Build 子步骤。

默认行为是：

- 进入 `Build`
- 系统先完成内部准备，再自动继续 `Review -> Test -> Ship -> Reflect`
- 直到完成、阻塞，或遇到需要你确认的地方

### 4. 更稳的实现链路

Build 不是“把整份长上下文硬塞给 AI 再赌它别漂”。

当前已经支持：
- feature 级实施输入
- 以 `design.md + tasks.md + feature-list.json + rules/` 为主输入
- 归一化 feature 合同和执行证据直接保存在 `feature-list.json`
- 依赖感知构建
- 安全回退到串行执行
- Review 中区分“做得对不对”和“代码写得稳不稳”

### 5. 现有项目也能用

VibeFlow 不只适合新项目，也适合在已有仓库上持续做改动。

它现在已经能：
- 维护项目级代码结构地图
- 为本次变更生成影响分析
- 在 Spark / Design 阶段引用这些上下文

<img width="1376" height="768" alt="image" src="https://github.com/user-attachments/assets/e658a4ca-75ba-414a-845a-71a9e623debb" />


### 6. 本地 live 看板

你不需要盯着 `state.json` 和一堆 markdown 文件猜系统跑到哪了。

看板会展示：
- 当前 mode 和 phase
- 主阶段状态
- feature 状态
- 关键产物是否生成
- 最近事件、恢复原因和下一步建议

### 7. 质量闭环

默认链路里已经包含：
- TDD
- 覆盖率门禁
- 变异测试
- 功能验收
- 全局审查
- 系统测试
- UI 场景下的 QA

### 8. 增量、发布与复盘

除了主工作流，你还可以继续使用：
- 增量请求队列
- 发布说明
- 迭代复盘日志

### 9. 模板与安全护栏

VibeFlow 不只有一条固定强度的流程。

你还可以使用：
- 四种模板控制流程严格度和质量阈值
- `careful / freeze / guard` 安全护栏限制危险命令和编辑边界

<img width="1376" height="768" alt="image" src="https://github.com/user-attachments/assets/1e0cbb71-9abf-4920-8533-509afe333e81" />

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
| VibeFlow | 高 | 高 | 高 | 中 | 高 | 中高 | 高 | 中高 |

## 生成工程后先看什么

在 VibeFlow 生成出来的目标工程里，普通用户主要看这几处：

- `README.md`
  项目入口，先了解项目是什么、怎么运行
- `docs/overview/CURRENT-STATE.md`
  当前项目快照：做到哪了、当前 active change 是什么、下一步建议看什么
- `docs/overview/PROJECT.md`
  全局项目说明：项目定位、长期能力和边界
- `docs/overview/ARCHITECTURE.md`
  长期稳定的系统结构和模块边界
- `docs/changes/<change-id>/`
  本次变更的完整方案和验证结果
- `feature-list.json`
  当前实施状态总表
- `RELEASE_NOTES.md`
  已交付内容和发布结果

如果 Claude 意外关闭，再次运行 `/vibeflow` 时会直接恢复到上次中断的位置，并显式提示：

- 当前停在什么阶段
- 为什么停在这里
- 你现在应该做什么
- 建议先打开哪些文件

## 关键产物

| 文件 | 作用 |
|---|---|
| `docs/overview/PROJECT.md` | 项目背景、范围和长期上下文 |
| `docs/overview/ARCHITECTURE.md` | 项目级架构说明 |
| `docs/overview/CURRENT-STATE.md` | 当前项目现状快照 |
| `.vibeflow/state.json` | 当前工作流真相：模式、阶段、工作包、checkpoint、phase history，以及恢复所需的运行态提示 |
| `rules/` | 项目自定义约束目录；存在时会作为 spec 补充输入，并优先于根目录 `CLAUDE.md` / `AGENT.md` |
| `feature-list.json` | Build 阶段的功能清单和执行真相，优先由 `design.md` 中的执行契约派生 |
| `docs/changes/<change-id>/brief.md` | 这次工作的起点、目标、范围、约束和验收边界 |
| `docs/changes/<change-id>/design.md` | 本次实现方案，也是评审结论与 Build Contract / Implementation Contract 的权威来源 |
| `docs/changes/<change-id>/tasks.md` | execution-grade 任务清单，供 Build 直接消费 |
| `docs/changes/<change-id>/codebase-impact.md` | 本次变更影响到哪些模块和测试 |
| `docs/changes/<change-id>/verification/review.md` | 全局审查结果 |
| `docs/changes/<change-id>/verification/system-test.md` | 系统测试结果 |
| `docs/changes/<change-id>/verification/qa.md` | UI / 浏览器验证结果 |
| `RELEASE_NOTES.md` | 发布说明 |

一句话区分：

- 看整个项目：`docs/overview/`
- 看这次工作：`docs/changes/<change-id>/`
- 看实施进度：`feature-list.json`

`.vibeflow/` 里的文件默认不用盯着看，除 `state.json` 外大多数都属于系统内部运行状态或派生产物。

---

## 适合什么场景

- 新项目从 0 到 1
- 在已有工程上新增或修改功能
- 希望 AI 工作流可恢复、可追踪、可审查
- 希望进入 Build 后少盯流程，多看结果
- 希望用 dashboard 看系统当前在做什么

如果你只是想让 AI 直接随手改两行代码，VibeFlow 可能偏重。  
如果你想把“交付过程”本身管起来，VibeFlow 会更合适。

---

## 文档

| 文档 | 说明 |
|---|---|
| [USAGE.md](USAGE.md) | 详细使用方式、命令入口和目标项目操作 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 架构图、状态机、组件关系 |
| [VIBEFLOW-DESIGN.md](VIBEFLOW-DESIGN.md) | 命名规则、文件布局、实现约定 |

---

## 学习网站
[访问学习网站](https://ttttstc.github.io/vibeflow)
---

## 许可证

MIT

<img width="1376" height="768" alt="image" src="https://github.com/user-attachments/assets/3c2f8d03-ae18-41b8-844a-de8cfa45c9c0" />

