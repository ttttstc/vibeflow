---
name: vibeflow-router
description: 在此仓库中用于在会话开始时路由整个VibeFlow生命周期的工作。
---

<EXTREMELY-IMPORTANT>
如果此仓库包含`VIBEFLOW-DESIGN.md`，在执行阶段工作之前必须使用此路由器。
</EXTREMELY-IMPORTANT>

## 框架概述：Spark / Design / Tasks + Delivery Chain

VibeFlow 对外暴露两种开发模式：

### Full Mode（完整流程）

| 阶段 | 性质 | 说明 |
|------|------|------|
| Spark | 人工 | 默认先进入 Office Hours 做问题框定，完成复杂度扫描、可选 DeepResearch、可选 Roundtable、CEO 价值评估，并在收口总结后等待用户确认 |
| Design | 人工 | 技术设计 + 三视角评审，并在阶段收口时等待用户确认是否进入 Tasks |
| Tasks | 人工 | 执行级任务化 handoff，生成 `tasks.md` |
| Build | 自动接管 | 进入 `build` 后默认由系统自动继续后续链路，不再逐段等待用户 |
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
返回：`increment`、`spark`、`design`、`tasks`、`build`、`review`、`test`、`ship`、`reflect`、`done`

### 步骤2：注入会话上下文

读取以下文件并格式化摘要：
1. **`.vibeflow/state.json`** — 当前阶段、模式、活跃工作包
2. **`.vibeflow/state.json.phase_history`** — 已完成阶段历史
3. **`.vibeflow/state.json.runtime`** — 当前恢复原因、下一步建议、推荐打开文件
4. **`docs/overview/PROJECT.md`**、**`docs/overview/ARCHITECTURE.md`**、**`docs/overview/CURRENT-STATE.md`**（如存在）— 项目级长期上下文
5. **`feature-list.json`** — 功能清单和状态
6. 运行 **`python scripts/get-vibeflow-paths.py --json`** — 解析当前工作包产物路径
7. **`VIBEFLOW-DESIGN.md`**（如存在）— 项目设计文档

```
=== Session Context ===
Current Phase: <phase>
Completed Phases: <list>
Reason: <why paused here>
Next Action: <what to do now>
Open Files: <recommended files>
Active Features: <count>
====================
```

### 步骤3：检查增量

```bash
cat .vibeflow/increments/queue.json 2>/dev/null || echo "No pending increments"
```
如有待处理增量，先处理。

### 步骤4：路由到阶段处理器

根据检测到的阶段调用相应 skill 或脚本（见下方路由表）。

### 步骤5：检查 overview freshness

优先读取 `.vibeflow/wiki-status.json`；如果不存在，再回退看 `CURRENT-STATE.md` 的“文档同步状态”段落。

如果满足以下任一条件：

- `docs/overview/PROJECT.md` 不存在
- `docs/overview/ARCHITECTURE.md` 不存在
- `docs/overview/CURRENT-STATE.md` 不存在
- `.vibeflow/wiki-status.json` 中任一正式 overview 文档 `stale=true`
- `CURRENT-STATE.md` 显示 overview 文档待同步

则在进入 Spark / Design / Review / Ship 前，优先调用 `skills/vibeflow-wiki/SKILL.md`。

调用时应明确说明：

- 缺的是哪份文档
- 还是 freshness 已过期
- 刷新后应重新检查 `.vibeflow/wiki-status.json`

---

## 阶段路由表

路由器是**文件驱动的**。阶段仅从`scripts/get-vibeflow-phase.py`确定。

| 阶段 | Skill / 脚本 | 关键产出物 |
|------|-------------|-----------|
| `quick` | `skills/vibeflow-quick/SKILL.md` | `.vibeflow/state.json`（含 `quick_meta`）+ `docs/changes/<change-id>/design.md` + `tasks.md` |
| `increment` | `scripts/increment-handler.py` | 更新 feature-list.json |
| `wiki` | `skills/vibeflow-wiki/SKILL.md` | `docs/overview/*.md` + `.vibeflow/wiki-status.json` |
| `spark` | `skills/vibeflow-spark/SKILL.md` | `docs/changes/<change-id>/brief.md` |
| `design` | `skills/vibeflow-design/SKILL.md` | `docs/changes/<change-id>/design.md` |
| `tasks` | `skills/vibeflow-tasks/SKILL.md` | `docs/changes/<change-id>/tasks.md` |
| `build` | Build 后自动继续（Claude Code 默认） / `scripts/run-vibeflow-autopilot.py`（CLI 对应入口） | `feature-list.json` |
| `review` | Build 后自动继续（默认继续） | `docs/changes/<change-id>/verification/review.md` |
| `test` | Build 后自动继续（默认继续） | `docs/changes/<change-id>/verification/` |
| `ship` | Build 后自动继续（默认继续） | `RELEASE_NOTES.md` |
| `reflect` | Build 后自动继续（默认继续） | `.vibeflow/logs/retro-*.md` |
| `done` | — | 完成摘要 |

**详细阶段说明**（完整文档见 `references/`）：

## Build 后自动继续规则

当 `detect_phase()` 返回以下任一阶段时：

- `build`
- `review`
- `test`
- `ship`
- `reflect`

Claude Code 插件里的默认行为不是停在当前子阶段等用户继续，而是开始自动继续后续链路：

1. 执行当前 phase 对应的子步骤
2. 立刻重新运行 `python scripts/get-vibeflow-phase.py`
3. 如果下一个 phase 仍属于上述实施阶段，则继续自动推进
4. 直到：
   - `done`
   - 审查/测试失败后回到 `build`
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
**操作**：读取 `scripts/increment-handler.py` 获取协议，按 FIFO 处理每个增量，更新 feature-list.json，并同步 `.vibeflow/increments/history.json` 与 `.vibeflow/state.json.phase_history`。

### 阶段：`spark`
**条件**：用户输入功能需求，需探索灵感、确定方向和价值评估。
**操作**：使用 `skills/vibeflow-spark/SKILL.md`。默认先进入 `skills/vibeflow-office-hours/SKILL.md` 做问题框定，并让用户确认本次验收标准；然后完成复杂度扫描，由用户选择是否执行 DeepResearch；调研后可选进入 `skills/vibeflow-roundtable/SKILL.md`；最后完成 CEO 价值评估，输出到 `docs/changes/<change-id>/brief.md`。
Spark 收口后必须向用户总结方向与范围，并确认是否进入 design。

### 阶段：`design`
**条件**：spark 已完成，开始技术设计。
**操作**：使用 `skills/vibeflow-design/SKILL.md`，输出 `docs/changes/<change-id>/design.md`。含内置步骤：UCD（如需）→ 用户审批 → AI eng review → AI design review → scope decision → 阶段产物展示与确认，并把评审结论汇总到 `design.md` 内的 review summary 章节。
**说明**：UCD（视觉风格指南）已并入 design 阶段。无 UI 需求时跳过。

### 阶段：`tasks`
**条件**：design 已批准，开始生成执行级任务计划。
**操作**：使用 `skills/vibeflow-tasks/SKILL.md`，输出 `docs/changes/<change-id>/tasks.md`。这里必须展示全量交付计划并等待人工确认；确认前不得进入 Build。

### 阶段：`build`
**条件**：tasks 已完成且人工已确认交付计划，进入实现。
**操作**：开始自动继续后续链路。Build 内部会先执行准备步骤，再使用 `skills/vibeflow-build-work/SKILL.md` 遍历 `feature-list.json` 按优先级实现功能。若审查/测试失败返回此阶段，自动执行会从这里恢复。

### 阶段：`review`
**条件**：功能实现完成，需代码审查。
**操作**：作为自动继续链路的一部分运行 `skills/vibeflow-review/SKILL.md`，输出 `docs/changes/<change-id>/verification/review.md`。审查失败则自动回到 `build` 继续处理。

### 阶段：`test`
**条件**：审查通过，需完成系统测试与必要的 QA 验证。
**操作**：作为自动继续链路的一部分运行 `skills/vibeflow-test-system/SKILL.md`；UI 项目再继续运行 `skills/vibeflow-test-qa/SKILL.md`，统一产出到 `docs/changes/<change-id>/verification/`。

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

**如果脚本缺失**：从 `state.json.phase_history` 重建阶段并请用户确认。

### 规则3：feature-list.json 是事实来源

构建顺序、状态、依赖、阻塞均来自 feature-list.json。绝不假设功能已完成。

### 规则3.5：进入 Build 后默认自动继续后续链路

当 phase 首次进入 `build` 时，默认开始自动继续后续链路，并持续推进 `build -> review -> test -> ship -> reflect`。除非用户明确要求单阶段调试，否则不要在这些阶段之间停下来等待下一条指令。

### 规则4：state.json.phase_history 仅追加

不编辑、不删除、不重排序历史条目。恢复事件是**添加**的。

### 规则5：未经用户同意不得阶段回归

回归仅在用户要求、恢复协议要求、审查/测试失败时发生。

### 规则6：产物保持同步

完成设计 → 更新 feature-list.json **且**写 design.md
完成 build → 更新功能状态 **且**物理文件存在
完成 ship → 标记 shipped **且**发布产物存在

### 规则7：增量队列 FIFO

按先进先出顺序处理，不跳步，不并行。

---

## Reverse-Spec Pre-Flight Check

在进入 Spark 或 Design 阶段之前：

1. 检查 `docs/architecture/full-spec.md` 是否存在
   - 如果存在 → 继续正常的阶段流程
2. 检查项目根目录是否包含源文件（.py, .ts, .tsx, .js, .jsx）
   - 如果包含 → 在首次进入时提示用户可以运行 `/vibeflow-reverse-spec` 生成架构文档
3. 如果 `docs/architecture/full-spec.md` 不存在且用户已选择生成 → 调用 `vibeflow-reverse-spec` skill
