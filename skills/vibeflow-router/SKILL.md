---
name: vibeflow-router
description: 在此仓库中用于在会话开始时路由整个VibeFlow生命周期的工作。
---

<EXTREMELY-IMPORTANT>
如果此仓库包含`VIBEFLOW-DESIGN.md`，在执行阶段工作之前必须使用此路由器。
</EXTREMELY-IMPORTANT>

## 框架概述：6 阶段 + Quick Mode

VibeFlow 对外暴露两种开发模式：

### Full Mode（完整流程）

| 阶段 | 性质 | 说明 |
|------|------|------|
| Spark | 人工 | 灵感迸发：问题框定、DeepResearch、复杂度扫描、CEO 价值评估 |
| Requirements | 人工 | 需求规格说明书 |
| Design | 人工 | 技术设计 + 三视角评审 |
| Build | 自动接管 | 进入 `build-init` 后默认由系统自动继续后续链路，不再逐段等待用户 |
| Review | 自动 | 跨功能审查（架构、安全、性能）|
| Test | 自动 | 系统测试 + QA 验证 |

**可选阶段：** Ship、Reflect

### Quick Mode（快速开发）

压缩前置分析，保留最小设计和任务清单，通过 Quick 准入校验后直接进入 Build。

**适用**：Bug fix、小改动、配置更新、测试/文档修补

**最低要求**：
- `.vibeflow/state.json` 中 `mode=quick`
- `quick_meta.decision=approved`
- `checkpoints.quick_ready=true`
- `docs/changes/<change-id>/design.md`
- `docs/changes/<change-id>/tasks.md`

**不适用**：
- 新功能
- 认证、支付、安全、数据迁移
- 多服务、多数据库、架构变更
- UI 重设计

**入口**：`/vibeflow-quick`

### 模式选择规则

- `.vibeflow/state.json` **不存在**：这是首次进入，必须先让用户明确选择 `Full Mode` 或 `Quick Mode`
- `.vibeflow/state.json` **已存在**：直接沿用已有 `mode`，不要自动改写，也不要重复询问
- `/vibeflow-quick`：显式 Quick 直达入口，不需要再问模式

VibeFlow 当前**不会自动推断**首次进入应该用哪个 mode。首次选择是显式决策，后续恢复才是沿用状态。

---

## 会话开始协议

在每个会话的**开始**，无例外地遵循此序列：

### 步骤1：确定当前阶段

运行阶段检测脚本：`python scripts/get-vibeflow-phase.py`
返回：`increment`、`spark`、`requirements`、`design`、`build-init`、`build-config`、`build-work`、`review`、`test-system`、`test-qa`、`ship`、`reflect`、`done`

> 注意：内部 phase 检测仍然细分（build-init/build-config/build-work 等），对外统一描述为 Build 阶段。

### 步骤2：注入会话上下文

读取以下文件并格式化摘要：
1. **`.vibeflow/state.json`** — 当前阶段、模式、活跃工作包
2. **`.vibeflow/phase-history.json`** — 已完成阶段历史
3. **`.vibeflow/work-config.json`** — 当前工作配置
4. **`feature-list.json`** — 功能清单和状态
5. 运行 **`python scripts/get-vibeflow-paths.py --json`** — 解析当前工作包产物路径
6. **`VIBEFLOW-DESIGN.md`**（如存在）— 项目设计文档

```
=== Session Context ===
Current Phase: <phase>
Completed Phases: <list>
Active Features: <count>
Pending: <from work-config.json>
====================
```

### 步骤3：检查增量

```bash
cat .vibeflow/increments/queue.json 2>/dev/null || echo "No pending increments"
```
如有待处理增量，先处理。

### 步骤4：路由到阶段处理器

根据检测到的阶段调用相应 skill 或脚本（见下方路由表）。

---

## 阶段路由表

路由器是**文件驱动的**。阶段仅从`scripts/get-vibeflow-phase.py`确定。

| 阶段 | Skill / 脚本 | 关键产出物 |
|------|-------------|-----------|
| `quick` | `skills/vibeflow-quick/SKILL.md` | `.vibeflow/state.json`（含 `quick_meta`）+ `docs/changes/<change-id>/design.md` + `tasks.md` |
| `increment` | `scripts/increment-handler.py` | 更新 feature-list.json |
| `spark` | `skills/vibeflow-spark/SKILL.md` | `docs/changes/<change-id>/context.md` |
| `requirements` | `skills/vibeflow-requirements/SKILL.md` | `docs/changes/<change-id>/requirements.md` |
| `design` | `skills/vibeflow-design/SKILL.md` | `docs/changes/<change-id>/design.md` + `docs/changes/<change-id>/design-review.md` |
| `build-init` | Build 后自动继续（Claude Code 默认） / `scripts/run-vibeflow-autopilot.py`（CLI 对应入口） | 项目脚手架 |
| `build-config` | Build 后自动继续（默认继续） | `.vibeflow/work-config.json` |
| `build-work` | Build 后自动继续（默认继续） | 已实现功能 |
| `review` | Build 后自动继续（默认继续） | `docs/changes/<change-id>/verification/review.md` |
| `test-system` | Build 后自动继续（默认继续） | `docs/changes/<change-id>/verification/system-test.md` |
| `test-qa` | Build 后自动继续（默认继续） | `docs/changes/<change-id>/verification/qa.md` |
| `ship` | Build 后自动继续（默认继续） | `RELEASE_NOTES.md` |
| `reflect` | Build 后自动继续（默认继续） | `.vibeflow/logs/retro-*.md` |
| `done` | — | 完成摘要 |

**详细阶段说明**（完整文档见 `references/`）：

## Build 后自动继续规则

当 `detect_phase()` 返回以下任一阶段时：

- `build-init`
- `build-config`
- `build-work`
- `review`
- `test-system`
- `test-qa`
- `ship`
- `reflect`

Claude Code 插件里的默认行为不是停在当前子阶段等用户继续，而是开始自动继续后续链路：

1. 执行当前 phase 对应的子步骤
2. 立刻重新运行 `python scripts/get-vibeflow-phase.py`
3. 如果下一个 phase 仍属于上述实施阶段，则继续自动推进
4. 直到：
   - `done`
   - 审查/测试失败后回到 `build-work`
   - 命中人工确认点
   - 出现阻塞需要人工处理

对 Claude Code 来说，**Build 是实施入口，自动继续后续链路是默认执行语义**。  
`vibeflow-build-init`、`vibeflow-build-work`、`vibeflow-review`、`vibeflow-test-system` 等子 skill 仍然保留，但默认定位是：

- 自动继续链路里的内部子步骤
- 单阶段调试入口
- 失败后的恢复入口

如果用户明确要求命令行无人值守、CI 执行或 dashboard 配套运行，则使用这条自动执行链路的脚本入口：

```bash
python scripts/run-vibeflow-autopilot.py --project-root .
```

### 阶段：`increment`
**条件**：有待处理的增量请求。
**操作**：读取 `scripts/increment-handler.py` 获取协议，按 FIFO 处理每个增量，更新 feature-list.json，并同步 `.vibeflow/increments/history.json` 与 `.vibeflow/phase-history.json`。

### 阶段：`spark`
**条件**：用户输入功能需求，需探索灵感、确定方向和价值评估。
**操作**：使用 `skills/vibeflow-spark/SKILL.md`，按需触发 DeepResearch，执行问题框定、复杂度扫描、CEO 价值评估，输出到 `docs/changes/<change-id>/context.md`。
价值评估通过后自动进入 requirements，无需用户额外确认。

### 阶段：`requirements`
**条件**：计划已批准，开始需求收集。
**操作**：使用 `skills/vibeflow-requirements/SKILL.md`，输出 `docs/changes/<change-id>/requirements.md`，更新 feature-list.json。

### 阶段：`design`
**条件**：需求已完成，开始技术设计。
**操作**：使用 `skills/vibeflow-design/SKILL.md`，输出 `docs/changes/<change-id>/design.md`。含内置步骤：UCD（如需）→ 用户审批 → AI eng review → AI design review → scope decision，并把评审结论汇总到 `docs/changes/<change-id>/design-review.md`。
**说明**：UCD（视觉风格指南）已并入 design 阶段。如 SRS 有 UI 需求且无现有 UCD 文档，design 阶段内生成；无 UI 需求时跳过。

### 阶段：`build-init`
**条件**：设计完成，初始化构建。
**操作**：开始自动继续后续链路。先执行 `skills/vibeflow-build-init/SKILL.md` 完成初始化，再立即重检 phase 并继续后续阶段。仅在用户明确要求调试单阶段时，才把 `vibeflow-build-init` 当成独立停顿点。

### 阶段：`build-config`
**条件**：build-init 完成，需功能配置。
**操作**：作为自动继续链路的内部子步骤运行 `python scripts/new-vibeflow-work-config.py`，完成后立即继续下一阶段，不等待用户额外确认。

### 阶段：`build-work`
**条件**：build-config 完成，開始实现功能。
**操作**：作为自动继续链路的核心执行步骤，使用 `skills/vibeflow-build-work/SKILL.md` 遍历 feature-list.json 按优先级实现功能。若审查/测试失败返回此阶段，自动执行会从这里恢复。

### 阶段：`review`
**条件**：功能实现完成，需代码审查。
**操作**：作为自动继续链路的一部分运行 `skills/vibeflow-review/SKILL.md`，输出 `docs/changes/<change-id>/verification/review.md`。审查失败则自动回到 `build-work` 继续处理。

### 阶段：`test-system`
**条件**：审查通过，需系统测试。
**操作**：作为自动继续链路的一部分运行 `skills/vibeflow-test-system/SKILL.md`，输出 `docs/changes/<change-id>/verification/system-test.md`。

### 阶段：`test-qa`
**条件**：系统测试通过，需 QA 验证。
**操作**：作为自动继续链路的一部分运行 `skills/vibeflow-test-qa/SKILL.md`，输出 `docs/changes/<change-id>/verification/qa.md`。

### 阶段：`ship`
**条件**：所有测试通过，部署就绪。
**操作**：作为自动继续链路的一部分运行 `skills/vibeflow-ship/SKILL.md`，生成 `RELEASE_NOTES.md`，更新 feature-list.json。

### 阶段：`reflect`
**条件**：项目交付完成，需回顾。
**操作**：作为自动继续链路的一部分运行 `skills/vibeflow-reflect/SKILL.md`，输出 `.vibeflow/logs/retro-*.md`。

### 阶段：`done`
**条件**：所有阶段完成。
**操作**：生成完成摘要（阶段列表、功能计数、耗时、retro 链接）。

---

更详细的参考文档见 `skills/vibeflow-router/references/` 目录。

## 硬规则

这些规则是**不可协商的**。

### 规则1：供应商中立命名

始终使用 VibeFlow 别名而非底层名称：
| 使用这个 | 不是那个 |
|----------|----------|
| Vector store | Chroma, Pinecone, Weaviate |
| LLM | GPT-4, Claude, Gemini |
| Embedding model | text-embedding-ada-002, bge-large |
| Framework | LangChain, LlamaIndex |
| Runtime | Docker, Kubernetes |

**例外**：在 `design.md` 中明确要求特定供应商时可用。

### 规则2：文件驱动优于记忆

阶段必须从 `scripts/get-vibeflow-phase.py` 读取。绝不从对话历史推断阶段。

**如果脚本缺失**：从 `phase-history.json` 重建阶段并请用户确认。

### 规则3：feature-list.json 是事实来源

构建顺序、状态、依赖、阻塞均来自 feature-list.json。绝不假设功能已完成。

### 规则3.5：进入 Build 后默认自动继续后续链路

当 phase 首次进入 `build-init` 时，默认开始自动继续后续链路，并持续推进 `build-init -> build-config -> build-work -> review -> test -> ship -> reflect`。除非用户明确要求单阶段调试，否则不要在这些子阶段之间停下来等待下一条指令。

### 规则4：phase-history.json 仅追加

不编辑、不删除、不重排序历史条目。恢复事件是**添加**的。

### 规则5：未经用户同意不得阶段回归

回归仅在用户要求、恢复协议要求、审查/测试失败时发生。

### 规则6：产物保持同步

完成设计 → 更新 feature-list.json **且**写 design.md
完成 build-work → 更新功能状态 **且**物理文件存在
完成 ship → 标记 shipped **且**发布产物存在

### 规则7：增量队列 FIFO

按先进先出顺序处理，不跳步，不并行。
