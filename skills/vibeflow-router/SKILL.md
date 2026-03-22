---
name: vibeflow-router
description: 在此仓库中用于在会话开始时路由整个VibeFlow生命周期的工作。
---

<EXTREMELY-IMPORTANT>
如果此仓库包含`VIBEFLOW-DESIGN.md`，在执行阶段工作之前必须使用此路由器。
</EXTREMELY-IMPORTANT>

## 会话开始协议

在每个会话的**开始**，无例外地遵循此序列：

### 步骤1：确定当前阶段

运行阶段检测脚本：`python scripts/get-vibeflow-phase.py`
返回：`increment`、`think`、`template-selection`、`plan`、`requirements`、`ucd`、`design`、`build-init`、`build-config`、`build-work`、`review`、`test-system`、`test-qa`、`ship`、`reflect`、`done`

### 步骤2：注入会话上下文

读取以下文件并格式化摘要：
1. **`.vibeflow/phase-history.json`** — 已完成阶段历史
2. **`.vibeflow/work-config.json`** — 当前工作配置
3. **`.vibeflow/feature-list.json`** — 功能清单和状态
4. **`VIBEFLOW-DESIGN.md`**（如存在）— 项目设计文档

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
cat .vibeflow/increment-queue.txt 2>/dev/null || echo "No pending increments"
```
如有待处理增量，先处理。

### 步骤4：路由到阶段处理器

根据检测到的阶段调用相应 skill 或脚本（见下方路由表）。

---

## 阶段路由表

路由器是**文件驱动的**。阶段仅从`scripts/get-vibeflow-phase.py`确定。

| 阶段 | Skill / 脚本 | 关键产出物 |
|------|-------------|-----------|
| `increment` | `scripts/increment-handler.py` | 更新 feature-list.json |
| `think` | `skills/vibeflow-think/SKILL.md` | `.vibeflow/think-output.md` |
| `template-selection` | `scripts/new-vibeflow-config.py` + `scripts/new-vibeflow-work-config.py` | `.vibeflow/workflow.yaml` |
| `plan` | `skills/vibeflow-plan/SKILL.md` | `.vibeflow/plan.md` + `.vibeflow/plan-value-review.md` + `.vibeflow/plan-review.md` |
| `requirements` | `skills/vibeflow-requirements/SKILL.md` | `docs/plans/*-srs.md` |
| `ucd` | `skills/vibeflow-ucd/SKILL.md` | `docs/plans/*-ucd.md` |
| `design` | `skills/vibeflow-design/SKILL.md` | `docs/plans/*-design.md` |
| `build-init` | `skills/vibeflow-build-init/SKILL.md` | 项目脚手架 |
| `build-config` | `scripts/new-vibeflow-work-config.py` | `.vibeflow/work-config.json` |
| `build-work` | `skills/vibeflow-build-work/SKILL.md` | 已实现功能 |
| `review` | `skills/vibeflow-review/SKILL.md` | `.vibeflow/review-report.md` |
| `test-system` | `skills/vibeflow-test-system/SKILL.md` | `.vibeflow/test-results/` |
| `test-qa` | `skills/vibeflow-test-qa/SKILL.md` | `.vibeflow/qa-report.md` |
| `ship` | `skills/vibeflow-ship/SKILL.md` | `RELEASE_NOTES.md` |
| `reflect` | `skills/vibeflow-reflect/SKILL.md` | `.vibeflow/retro-*.md` |
| `done` | — | 完成摘要 |

**详细阶段说明**（完整文档见 `references/`）：

### 阶段：`increment`
**条件**：有待处理的增量请求。
**操作**：读取 `scripts/increment-handler.py` 获取协议，按 FIFO 处理每个增量，更新 feature-list.json 并记录到 phase-history.json。

### 阶段：`think`
**条件**：需要探索、问题分解或初始概念分析。
**操作**：使用 `skills/vibeflow-think/SKILL.md`，输出到 `.vibeflow/think-output.md`。

### 阶段：`template-selection`
**条件**：Think 阶段完成，需选择模板。
**操作**：
1. 阅读 `.vibeflow/think-output.md` 和 `feature-list.json`
2. 参考 `references/template-guide.md` 推荐模板
3. 用户确认后运行：`python scripts/new-vibeflow-config.py --template <template>`，然后 `scripts/new-vibeflow-work-config.py`

### 阶段：`plan`
**条件**：模板已选定，需进行价值评估 + 范围审查。
**操作**：使用 `skills/vibeflow-plan/SKILL.md`，两步审查：
1. CEO 价值评估（调用 `vibeflow-plan-value-review`）→ 产出 `.vibeflow/plan-value-review.md`
2. 执行范围审查 → 产出 `.vibeflow/plan-review.md`
价值审查失败则项目终止；两者都通过后写入 `.vibeflow/plan.md`，进入 requirements。

### 阶段：`requirements`
**条件**：计划已批准，开始需求收集。
**操作**：使用 `skills/vibeflow-requirements/SKILL.md`，输出 `docs/plans/*-srs.md`，更新 feature-list.json。

### 阶段：`ucd`
**条件**：需求已完成，需用例设计。
**操作**：使用 `skills/vibeflow-ucd/SKILL.md`，输出 `docs/plans/*-ucd.md`。

### 阶段：`design`
**条件**：用例已完成，开始技术设计。
**操作**：使用 `skills/vibeflow-design/SKILL.md`，输出 `docs/plans/*-design.md`。

### 阶段：`build-init`
**条件**：设计完成，初始化构建。
**操作**：使用 `skills/vibeflow-build-init/SKILL.md`，生成项目脚手架。

### 阶段：`build-config`
**条件**：build-init 完成，需功能配置。
**操作**：运行 `python scripts/new-vibeflow-work-config.py`，审查 `.vibeflow/work-config.json` 完整性。

### 阶段：`build-work`
**条件**：build-config 完成，開始实现功能。
**操作**：使用 `skills/vibeflow-build-work/SKILL.md`，遍历 feature-list.json 按优先级实现功能。

### 阶段：`review`
**条件**：功能实现完成，需代码审查。
**操作**：使用 `skills/vibeflow-review/SKILL.md`，输出 `.vibeflow/review-report.md`。审查失败则路由回 `build-work`。

### 阶段：`test-system`
**条件**：审查通过，需系统测试。
**操作**：使用 `skills/vibeflow-test-system/SKILL.md`，输出 `.vibeflow/test-results/`。

### 阶段：`test-qa`
**条件**：系统测试通过，需 QA 验证。
**操作**：使用 `skills/vibeflow-test-qa/SKILL.md`，输出 `.vibeflow/qa-report.md`。

### 阶段：`ship`
**条件**：所有测试通过，部署就绪。
**操作**：使用 `skills/vibeflow-ship/SKILL.md`，生成 `RELEASE_NOTES.md`，更新 feature-list.json。

### 阶段：`reflect`
**条件**：项目交付完成，需回顾。
**操作**：使用 `skills/vibeflow-reflect/SKILL.md`，输出 `.vibeflow/retro-*.md`。

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
