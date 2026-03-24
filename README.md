**[English](README_EN.md) | 中文**

---

# VibeFlow

**让 AI 按工程纪律交付软件，而不是把仓库写成即兴表演。**

AI 很会写代码，也很会忘上下文、跳步骤、先冲再说。  
VibeFlow 给它一套可恢复、可追踪、可测试的交付流程：**文件即状态，路由可确定，质量不过线就别想往下走。**

> 你可以把它理解成：给 AI 配上路线图、安全带和刹车系统。

## 为什么会有它

没有流程的 AI 编程，常见结局通常长这样：

- 会话一换，项目状态就像失忆
- 需求没落盘，设计没落盘，代码倒是先写了
- 小改动越修越大，最后重写半个系统
- 测试和审查靠心情，发布靠勇气

VibeFlow 解决的是这几个问题：

- **状态持久化**：项目状态放在仓库文件里，不靠聊天记忆
- **确定性路由**：每次打开会话，都知道下一步该做什么
- **双模式交付**：大活走 Full Mode，小改动走 Quick Mode
- **模板控严格度**：prototype 到 enterprise，一次选择，全局生效
- **增量友好**：已有项目继续迭代，不用每次从头开场

## 这次重构后，你真正得到什么

VibeFlow 现在的核心能力已经统一到了这套结构上：

- `.vibeflow/state.json`
  工作流中心状态，记录当前模式、阶段、活跃工作包和 checkpoints
- `docs/changes/<change-id>/...`
  一次工作包的完整交付物：`context / proposal / requirements / design / tasks / verification`
- `feature-list.json`
  Build 阶段唯一事实来源
- `.vibeflow/increments/*`
  增量请求队列、历史和请求载荷
- `scripts/migrate-vibeflow-v2.py`
  旧布局迁到新布局的迁移脚本

一句话：**状态归状态，文档归文档，构建清单归构建清单。终于不乱了。**

## 模式

### Full Mode

适合：

- 新功能
- 架构调整
- 复杂现有工程改动
- 涉及 UI、权限、安全、数据迁移的任务
- 你自己都说不清边界的任务

流程：

`Think -> Plan -> Requirements -> Design -> Build -> Review -> Test -> Ship? -> Reflect?`

### Quick Mode

适合：

- bug fix
- 小范围改动
- 配置调整
- 文档、测试、脚手架类修补
- 能快速回滚、能快速验证的变更

流程：

`Quick -> Build -> Review -> Test -> Ship? -> Reflect?`

Quick Mode 会保留最小设计和验证，但会跳过重前置流程。  
它是**快速交付模式**，不是**我先乱改一把模式**。

## 工作方式

### 1. 选择模式

- `/vibeflow`：进入 Full Mode
- `/vibeflow-quick`：进入 Quick Mode

### 2. 让路由器接管

每次会话开始，`vibeflow-router` 会基于文件状态判断当前阶段。  
不是“猜你上次做到哪了”，而是“直接看仓库里留了什么证据”。

### 3. 所有关键产物都写入仓库

最重要的交付物现在统一落在：

```text
.vibeflow/
  state.json
  workflow.yaml
  work-config.json
  increments/
  logs/

docs/changes/<change-id>/
  context.md
  proposal.md
  requirements.md
  ucd.md
  design.md
  design-review.md
  tasks.md
  verification/
    review.md
    system-test.md
    qa.md

feature-list.json
RELEASE_NOTES.md
```

## 安装

首页只保留最快路径，别让安装说明比框架本身还长。

### Claude Code

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.sh | bash
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.ps1 | iex
```

安装后激活：

```text
/plugin install vibeflow@vibeflow
```

### 想更省事

Windows 可以直接用启动器：

```powershell
irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/vibeflow-launcher.ps1 | iex
```

### 需要更多安装细节

详细脚本和替代安装方式见：

- [`claude-code/install.sh`](claude-code/install.sh)
- [`claude-code/install.ps1`](claude-code/install.ps1)
- [`claude-code/install-simple.ps1`](claude-code/install-simple.ps1)
- [`claude-code/INSTALL-PROMPT.md`](claude-code/INSTALL-PROMPT.md)
- [`install.sh`](install.sh)

## 3 分钟上手

1. 在 Claude Code 里安装并激活 VibeFlow
2. 新项目或复杂任务运行 `/vibeflow`
3. 小改动运行 `/vibeflow-quick`
4. 按路由推进阶段，不要手搓流程
5. 交付物会自动沉淀到 `.vibeflow/` 和 `docs/changes/`

## 模板

模板决定治理严格度，不决定你聪不聪明。

| 模板 | 适合什么 |
|---|---|
| `prototype` | POC、MVP、内部实验、快速验证 |
| `web-standard` | 标准 Web 应用 |
| `api-standard` | 后端 API / 服务型项目 |
| `enterprise` | 高约束、强审计、强治理系统 |

模板会写入 `.vibeflow/workflow.yaml`，再由 `.vibeflow/work-config.json` 派生执行配置。

## 核心能力

- **7 阶段主流程**：Think、Plan、Requirements、Design、Build、Review、Test
- **可选阶段**：Ship、Reflect
- **确定性路由**：基于文件状态恢复上下文
- **增量开发**：支持继续在已有项目上新增、修改、废弃功能
- **迁移支持**：旧布局可迁到 v2
- **Quick / Full 双模式**：一个偏稳，一个偏快，但都留痕

## 文档

- [ARCHITECTURE.md](ARCHITECTURE.md)：整体架构和边界
- [USAGE.md](USAGE.md)：目标项目中的实际使用方式
- [VIBEFLOW-DESIGN.md](VIBEFLOW-DESIGN.md)：设计契约、状态模型、技能目录

## 给谁用

适合这些人：

- 想让 AI 连续多会话开发，还不想每次重新解释背景
- 想把“AI 写代码”升级成“AI 按流程交付”
- 想在现有仓库里持续做增量，而不是每次开新坑

不太适合这些人：

- 只想让 AI 立刻吐几段代码，不关心后续维护
- 认为测试、评审、发布说明都是可选装饰

## License

MIT
