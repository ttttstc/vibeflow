**[English](README_EN.md) | 中文**

---

# VibeFlow

**让 AI 写出的，不只是代码，而是一段有章法的交付。**

VibeFlow 是一个标准化AI工程交付编排框架。大模型擅长即兴，软件工程需要定力。真正稀缺的不是“生成一段代码”，而是把一个想法稳稳穿过需求、设计、实现、审查、测试、发布与复盘，直到它变成一个可以交付、可以追溯、可以继续演化的系统。VibeFlow 做的，就是给这条路铺上轨道，让 AI 少一点碰运气，多一点章法、记忆与收尾。

> “凡事预则立，不预则废。” —《礼记·中庸》
>
> 先定章法，再求速度；先有节奏，后有规模。

---
<img width="1376" height="768" alt="compare" src="https://github.com/user-attachments/assets/9a3be1a9-270c-46fc-b303-67b451ed860f" />




## 文档导航

- [安装与开始使用](README.md#安装)
- [3 分钟上手](README.md#3-分钟上手)
- [常用命令](README.md#常用命令)
- [详细使用指南](USAGE.md)
- [架构说明](ARCHITECTURE.md)
- [详细技术架构导览（DeepWiki）](https://deepwiki.com/ttttstc/vibeflow/1-vibeflow-overview)
- [设计契约与实现约定](VIBEFLOW-DESIGN.md)

---

## 安装

### 一句安装命令

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


### 让 AI 帮你安装

如果你想直接让 Claude Code 自己完成安装，粘贴下面这段：

```text
帮我安装 VibeFlow

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
5. 最后告诉我：
   - 是否安装成功
   - 安装到了哪里
   - 下一步该怎么验证
```


### 验证安装

运行 `/vibeflow`，能看到 VibeFlow 入口说明，就说明插件已正常加载。


## 3 分钟上手

1. 安装并激活插件后，在项目里运行 `/vibeflow`
2. 第一次进入时选择 `Full Mode` 或 `Quick Mode`
3. 在 `Think -> Plan -> Requirements -> Design` 完成必要确认
4. 一旦进入 `build-init`，系统默认自动继续 `Build -> Review -> Test -> Ship / Reflect`
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

### 1. 结构化交付流程

- `Think -> Plan -> Requirements -> Design` 负责想清楚问题、边界和方案
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

- 进入 `build-init`
- 自动继续 `build-config -> build-work -> review -> test -> ship -> reflect`
- 直到完成、阻塞，或遇到需要你确认的地方

### 4. 更稳的实现链路

Build 不是“把整份长上下文硬塞给 AI 再赌它别漂”。

当前已经支持：
- feature 级实施输入
- 依赖感知构建
- 安全回退到串行执行
- Review 中区分“做得对不对”和“代码写得稳不稳”

### 5. 现有项目也能用

VibeFlow 不只适合新项目，也适合在已有仓库上持续做改动。

它现在已经能：
- 维护项目级代码结构地图
- 为本次变更生成影响分析
- 在 Requirements / Design 阶段引用这些上下文
- <img width="1376" height="768" alt="image" src="https://github.com/user-attachments/assets/e658a4ca-75ba-414a-845a-71a9e623debb" />


### 6. 本地 live 看板

你不需要盯着 `state.json` 和一堆 markdown 文件猜系统跑到哪了。

看板会展示：
- 当前 mode 和 phase
- 主阶段状态
- feature 状态
- 关键产物是否生成
- 最近事件和友好提示

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

## 生成工程后先看什么

在 VibeFlow 生成出来的目标工程里，普通用户主要看这几处：

- `README.md`
  项目入口，先了解项目是什么、怎么运行
- `docs/overview/README.md`
  全局文档导航，告诉你先看项目背景、现状还是架构
- `docs/overview/CURRENT-STATE.md`
  当前项目快照：做到哪了、当前 active change 是什么、下一步建议看什么
- `docs/changes/<change-id>/`
  本次变更的完整方案和验证结果
- `feature-list.json`
  当前实施状态总表
- `RELEASE_NOTES.md`
  已交付内容和发布结果

## 关键产物

| 文件 | 作用 |
|---|---|
| `docs/overview/README.md` | 全局文档导航，第一次接手项目时先看这里 |
| `docs/overview/PROJECT.md` | 项目背景、范围和长期上下文 |
| `docs/overview/PRODUCT.md` | 产品能力、边界和用户视角 |
| `docs/overview/ARCHITECTURE.md` | 项目级架构说明 |
| `docs/overview/CURRENT-STATE.md` | 当前项目现状快照 |
| `.vibeflow/state.json` | 当前工作流真相：模式、阶段、工作包、checkpoint |
| `.vibeflow/runtime.json` | 运行态覆盖层：当前动作、友好提示、最近事件、heartbeat |
| `.vibeflow/codebase-map.json` | 项目级代码结构地图，给现有项目改动复用 |
| `feature-list.json` | Build 阶段的功能清单和执行真相 |
| `docs/changes/<change-id>/context.md` | 这次工作的起点、边界和目标 |
| `docs/changes/<change-id>/proposal.md` | 这次方案的范围和价值判断 |
| `docs/changes/<change-id>/requirements.md` | 本次需求定义 |
| `docs/changes/<change-id>/design.md` | 本次实现方案 |
| `docs/changes/<change-id>/tasks.md` | 可落地任务清单 |
| `docs/changes/<change-id>/codebase-impact.md` | 本次变更影响到哪些模块和测试 |
| `docs/changes/<change-id>/verification/review.md` | 全局审查结果 |
| `docs/changes/<change-id>/verification/system-test.md` | 系统测试结果 |
| `docs/changes/<change-id>/verification/qa.md` | UI / 浏览器验证结果 |
| `RELEASE_NOTES.md` | 发布说明 |

一句话区分：

- 看整个项目：`docs/overview/`
- 看这次工作：`docs/changes/<change-id>/`
- 看实施进度：`feature-list.json`

`.vibeflow/` 里的文件默认不用盯着看，它们主要是系统内部运行状态。

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

