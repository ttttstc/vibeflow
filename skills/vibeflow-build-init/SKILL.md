---
name: vibeflow-build-init
description: "在 tasks 审批通过后使用，基于设计契约生成 feature-list.json 并准备进入 Build"
---

# 初始化 VibeFlow 项目

在 `tasks` 审批通过后运行一次。搭建所有持久化工件，将需求分解为可验证的功能，准备项目进入迭代构建。

在 Claude Code 插件的默认路径中，本 skill 是 **Build 自动继续链路的第一个内部子步骤**。只有 `tasks` 已经展示全量交付计划并经过人工确认后，才能进入这里。

**启动宣告：** "正在使用 vibeflow-build-init 初始化项目。"

## 输入文档

| 文档 | 位置 | 提供 |
|------|------|------|
| **概要** | `docs/changes/<change-id>/brief.md` | 目标、范围、非目标、验收标准、约束、假设、开放问题 |
| **设计** | `docs/changes/<change-id>/design.md` | 技术栈、架构、数据模型、API 设计、测试策略 |
| **执行计划** | `docs/changes/<change-id>/tasks.md` | execution-grade tasks，包含精确文件路径、验证步骤、回滚说明、依赖关系 |
| **工作流** | `.vibeflow/workflow.yaml` | 模板配置、质量门禁阈值 |

## 检查清单

按顺序完成以下步骤：

### 1. 读取审批文档
- 先运行 `python scripts/get-vibeflow-paths.py --json`
- 概要：`docs/changes/<change-id>/brief.md` — 目标、范围、验收标准、约束、假设
- 设计：`docs/changes/<change-id>/design.md` — 技术栈、架构决策
- 执行计划：`docs/changes/<change-id>/tasks.md` — execution-grade task blocks
- 工作流：`.vibeflow/workflow.yaml` — 质量阈值和启用的步骤

### 1.5 执行计划门禁（Execution Planning Gate）

在进入项目骨架生成和 feature 分解前，先验证 `tasks.md` 是否达到执行级质量。

**适用规则：**
- `tasks.md` 是必需输入

**必须检查：**
- `tasks.md` 存在且可解析为按任务块组织的计划
- 每个任务块包含：`task_id`、`goal`、`exact_file_paths`、`steps`、`verification_steps`、`rollback_note`、`expected_duration_min`
- `exact_file_paths` 为仓库内精确路径，不得出现“相关文件”“必要时”“视情况”“等”这类模糊词
- `verification_steps` 至少包含一个可执行检查
- `rollback_note` 说明最小撤销路径
- `expected_duration_min` 默认在 2-5 分钟范围；超过 10 分钟的任务必须阻塞并要求拆分
- 每个 feature 至少能映射到一个任务块；任务块必须能追溯到 `feature_id`、`build_contract_ref`、`design_section` 中至少一个正式索引

**阻塞规则：**
- Gate 不通过时，build-init 必须停止，不得继续生成 `feature-list.json`
- 不得在 build-init 阶段临时重写或脑补任务结构；缺失或过粗的任务应退回 tasks 阶段修正

### 2. 搭建项目骨架
基于设计文档的架构创建目录结构、配置文件、依赖清单。

### 3. 生成 feature-list.json
创建 `feature-list.json`，根结构：

**权威来源规则：**
- `design.md` 中的 `Build Contract` + `Implementation Contract` TOML 代码块是生成 `feature-list.json` 的唯一权威来源
- 不再允许从 `tasks.md` 或默认值回退推断 feature 合同
- 如缺少设计契约、解析失败、缺少 `Build Contract`、或 feature 契约不完整，必须阻塞 build-init

```json
{
  "project": "项目名",
  "created": "YYYY-MM-DD",
  "tech_stack": {
    "language": "python|java|typescript|c|cpp",
    "test_framework": "pytest|junit|vitest|gtest|...",
    "coverage_tool": "pytest-cov|jacoco|c8|gcov|...",
    "mutation_tool": "mutmut|pitest|stryker|mull|..."
  },
  "quality_gates": {
    "line_coverage_min": 90,
    "branch_coverage_min": 80,
    "mutation_score_min": 80
  },
  "constraints": ["硬限制 — 每项一个字符串"],
  "assumptions": ["隐含信念 — 每项一个字符串"],
  "required_configs": [],
  "features": []
}
```

**quality_gates 阈值**应从 `.vibeflow/workflow.yaml` 中读取，而非硬编码默认值。

### 4. 填充 brief 字段
从 `brief.md` 中：
- `constraints[]` — 复制 CON-xxx 项
- `assumptions[]` — 复制 ASM-xxx 项
- NFR-xxx -> 创建 `category: "non-functional"` 的功能条目，带可度量的 `verification_steps`

如设计契约已经声明 `constraints[]`、`assumptions[]`、`required_configs[]`，优先采用设计文档中的执行版本；`brief.md` 作为追溯和补全来源。

### 5. 分解需求为功能
优先从设计文档中每个 feature 的 `Implementation Contract` 填充 `features[]`；必要时再从 `brief.md` 与设计文档的**开发计划**（任务分解章节）补全。

- 每个 FR-xxx -> 一个或多个功能条目，含 `id`、`category`、`title`、`description`、`priority`、`status`（始终为 `"failing"`）、`verification_steps`、`dependencies`
- `verification_steps` 应追溯到 brief 中的验收标准（Given/When/Then）
- UI 功能：设置 `"ui": true`，可选 `"ui_entry": "/路径"`
- 设计契约中的 `file_scope`、`requirements_refs`、`integration_points`、`required_configs`、`autopilot_commands` 必须原样保留到 feature 条目中

每个功能条目：
```json
{
  "id": 1,
  "category": "core",
  "title": "功能标题",
  "description": "做什么",
  "priority": "high|medium|low",
  "status": "failing",
  "verification_steps": ["步骤 1", "步骤 2"],
  "dependencies": [],
  "ui": false,
  "ui_entry": "/可选路径"
}
```

**验证步骤质量规则**：
- 每步**必须**是带 Given/When/Then 结构的行为场景，不是简单断言
- 差：`"登录页正常显示"` -> 无动作，无断言
- 好：`"导航到 /login -> 预期：邮箱输入框、密码输入框、'登录'按钮；填入有效凭证 -> 点击登录 -> 预期：跳转到 /dashboard，头部显示用户名"`
- UI 功能的每个 `[devtools]` 步骤**必须**描述多步交互链

**前后端配对排序规则**：前端功能（`"ui": true`）**必须**在 `dependencies[]` 中列出其后端 API 依赖。且 `features[]` 数组中在每个后端功能之后紧跟其对应的前端功能。

**优先级排序**：遵循设计文档的任务分解表 — P0/P1/P2/P3 映射为 high/high/medium/low

目标：10-200+ 个功能；每个独立可验证，可在一个会话中完成。

### 5.1 归一化 feature 合同
在 `feature-list.json` 准备完成后，为每个 feature 补齐归一化合同字段，至少包括：

- 功能目标
- 依赖关系
- 文件范围
- 验证方式
- 完成定义
  - 相关文档引用（spark/context / design section / build contract / tasks）

如果 feature 来自设计契约，条目必须包含：
- `design_section`
- `build_contract_ref`
- `requirements_refs`
- `integration_points`

Build 阶段后续独立实施单元的正式输入应以 `feature-list.json + design.md + tasks.md + rules/` 为准，不应依赖长会话上下文记忆。

### 6. 填充 required_configs
从 brief（IFR-xxx 接口需求）和设计文档：
- API 密钥、服务 URL -> type `env`
- 配置文件、证书 -> type `file`
- 通过 `required_by` 链接到功能；提供 `check_hint` 含设置说明

### 7. 生成 .env.example
从 `required_configs` 生成：
```
# <名称> — <描述>
# 提示：<check_hint>
# 功能依赖：<required_by ids>
<KEY>=
```
将 `.env` 加入 `.gitignore`。

### 8. 生成 build.md
创建项目专属的构建会话指南，放在 `.vibeflow/guides/build.md`：

必须包含的章节：
- **环境命令** — 环境激活、测试执行、覆盖率、变异测试的具体命令
- **构建流程** — Orient -> Bootstrap -> Config Gate -> TDD -> Quality -> Feature ST -> Review -> Persist
- **服务命令**（仅当项目有服务进程时）— 引用 `.vibeflow/guides/services.md`
- **关键规则** — 一次一个功能、严格步骤顺序、不跳过子步骤

### 9. 生成 services.md（如项目有服务进程）
在 `.vibeflow/guides/services.md` 创建服务生命周期指南：

- 服务表格（名称、端口、启动命令、停止命令、健康检查 URL）
- 启动所有服务（含日志输出捕获、PID 提取）
- 验证服务运行
- 停止所有服务（按 PID 或按端口）
- 验证服务已停止
- 重启协议（4 步：Kill -> 验证死亡 -> 启动 -> 验证存活）

### 10. 生成初始化脚本
创建 `init.sh`（Unix/macOS）和 `init.ps1`（Windows）：
- 环境创建与激活
- 依赖安装
- 工具版本验证
- 必须幂等（重复运行安全）
- 克隆后立即可执行

### 11. 生成辅助文件
- `.vibeflow/logs/session-log.md` — 含 `## Current State` 头部（在首次执行写入时生成）
- `RELEASE_NOTES.md` — Keep a Changelog 格式

### 12. 验证
运行初始化脚本，验证环境搭建无错误。验证测试命令可执行（此时全部失败是预期的）。

### 13. Git 提交
初始提交，包含所有搭建的工件。

### 14. 进入构建
不要在这里停下来等待下一条用户指令。完成初始化后立即重新检测 phase，继续 Build 自动执行链路；仅在调试或恢复时，才手动转入 `vibeflow-build-work`。

## 生成的持久化工件

| 文件 | 用途 |
|------|------|
| `feature-list.json` | 带状态的结构化任务清单 |
| `.vibeflow/build-reports/feature-*.md` | 每个 feature 的执行证据报告 |
| `.vibeflow/logs/session-log.md` | 逐会话进度日志 |
| `RELEASE_NOTES.md` | 活跃的发布说明 |
| `.vibeflow/guides/build.md` | 项目专属构建指南 |
| `.vibeflow/guides/services.md` | 服务生命周期命令（如适用） |
| `init.sh` / `init.ps1` | 环境引导脚本 |
| `.env.example` | 必需环境配置模板 |

## 集成

**调用者：** vibeflow-router 的 Build 自动继续链路，或调试/恢复场景下的手动调用
**读取：** `docs/changes/<change-id>/brief.md` + `docs/changes/<change-id>/design.md` + `docs/changes/<change-id>/tasks.md` + `.vibeflow/workflow.yaml`
**链接到：** Build 自动继续链路（默认） / `vibeflow-build-work`（手动 fallback）
**产出：** feature-list.json + 上述所有工件
