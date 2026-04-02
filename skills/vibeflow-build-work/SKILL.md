---
name: vibeflow-build-work
description: "feature-list.json 存在且部分功能仍失败时使用 — 驱动功能通过完整 TDD 管线、质量门禁和代码审查"
---

# VibeFlow Build Work

通过每次循环实现一个功能来执行多会话软件项目。每个循环遵循严格管线：Orient -> Gate -> Plan -> TDD -> Quality -> ST 验收 -> Review -> Persist。

在 Claude Code 插件的默认路径中，本 skill 是 **Build 自动继续链路的核心内部子步骤**。只有在调试单个阶段、重跑某个功能、或处理失败恢复时，才把它当成显式入口。

**启动宣告：** "正在使用 vibeflow-build-work。让我先定位当前状态。"

**核心原则：** 每个子步骤有其专属 skill。严格遵循编排顺序。

## 执行模式选择

### 模式一：Sequential（顺序执行）

每次循环一个功能，主会话上下文顺序执行。

适用场景：
- 调试阶段，需要逐步观察
- 小项目（< 5 个 feature）
- 依赖关系复杂的场景

### 模式二：Parallel（并行执行）

使用 Agent 工具同时启动多个 subagent，每个 subagent 在独立 200k token 上下文中执行一个 feature。

适用场景：
- 中大项目（≥ 5 个 feature）
- feature 之间无文件重叠（设计阶段已验证）
- 需要快速完成多个独立功能

**启动并行模式：**

在调用 build-work 时明确告知模式选择：

```
请使用并行模式执行所有 failing features。
```

或

```
请使用顺序模式执行。
```

默认模式为 Sequential（更稳定）。

---

## work-config.json 步骤裁剪

`.vibeflow/work-config.json` 是**步骤启用的权威来源**。在执行前读取它，跳过标记为禁用的步骤。典型可裁剪步骤：

- `tdd` — 是否强制 TDD（prototype 模板可能禁用）
- `quality_gates` — 是否运行覆盖率/变异测试门禁
- `feature_st` — 是否运行功能验收测试
- `spec_review` — 是否运行规格合规审查

即使步骤被裁剪，**功能仍需测试和验证才能标记为 passing**。裁剪仅影响形式化门禁流程。

## 检查清单

### 1. Orient（定位）
- 加载 `.env`（如存在）
- 运行 `python scripts/get-vibeflow-paths.py --json`
- 读取 `.vibeflow/logs/session-log.md` 的 `## Current State` — 进度、上一个完成的功能、下一个功能
- 读取 `feature-list.json` — 注意 `constraints[]`、`assumptions[]`、`required_configs[]`、功能状态
- 优先读取 `feature-list.json` 中当前功能的归一化合同，并补读 `design.md`、`tasks.md`、`rules/`
- 如存在 `.vibeflow/packets/<change-id>/feature-<id>.json`，可把它当作缓存视图使用，但不要把它当成唯一真相
- 优先读取任务包中的 `design_contract.build_contract_ref` 与 `design_contract.design_section`
- 读取 `.vibeflow/guides/build.md` — 项目专属工作流指导
- 读取 `.vibeflow/guides/services.md`（如存在）— 服务名、端口、健康检查 URL
- 读取设计文档**第 1 节**（`docs/changes/<change-id>/design.md`）— 项目概览和架构快照
- 运行 `git log --oneline -10` — 近期提交上下文
- 选取下一个 `"status": "failing"` 的功能，按优先级然后按数组位置（第一个合格的胜出）— **跳过 `"deprecated": true` 的功能**
- **依赖满足检查**：选择候选功能后，验证其 `dependencies[]` 中所有功能 ID 在 feature-list.json 中状态为 `"passing"`。如有依赖未满足：
  - 记录："功能 #{id}（{title}）被跳过 — 未满足依赖：#{dep1}、#{dep2}"
  - 选取下一个合格的功能
  - 如**无**功能的依赖都已满足 -> 通过 `AskUserQuestion` 警告用户
- 如目标功能有 `"ui": true` 且 UCD 文档存在，读取 UCD 风格指南

**文档查找协议：**

当需要功能的设计章节或 SRS 需求时，**不要** grep 功能标题。而是：

1. 先读取任务包中的 `design_contract.design_section`
2. 读取设计文档的**第 4 节标题区域**，找到对应 `### 4.N` 子节
3. 如任务包缺失 section，再回退到设计文档标题区域手动定位 `### 4.N` 子节
4. 读取该子节的**完整内容**（从 `### 4.N` 到 `### 4.(N+1)` 前）
5. 如任务包提供 `design_contract.build_contract_ref`，再补读 `## Build Contract` 代码块
6. 同理读取 SRS 的完整 FR-xxx 子节
7. 存储为 `{build_contract}`、`{design_section}` 和 `{srs_section}` 供后续步骤使用

**功能合同规则：**

- 当前功能的主输入是 feature 合同，也就是 `feature-list.json` 中的 feature 条目加上文档引用
- 如 packet 存在，其中的 `design_contract` 字段可作为快捷索引，不是唯一真相
- 如缓存 packet 信息不足或不存在，再按 feature 条目中的文档引用补读原始章节
- 不要依赖父会话里残留的长上下文记忆来实现功能
- 不要直接修改共享状态文件；共享状态由主 orchestrator 统一回写

### 2. Bootstrap（引导）
- 确认开发环境就绪（如需运行 init.sh/init.ps1）
- 冒烟测试已通过的功能

### 3. Config Gate（配置门禁）
检查目标功能的 `required_configs` 是否齐备。缺失时通过 `AskUserQuestion` 向用户收集，追加到 `.env`。**配置齐备前阻塞。**

### 4. Plan（计划）
为选定功能编写逐步实现计划，追加到 `docs/changes/<change-id>/tasks.md` 的对应功能小节。

- **必须**使用文档查找协议读取完整 `{design_section}` 和 `{srs_section}`
- 如存在 `{build_contract}`，计划必须同时遵守其中的全局约束和 required configs
- 计划**必须**与审批的类图、序列流和架构决策对齐
- UI 功能**必须**指定适用的 UCD 风格 Token

### 5-7. TDD 循环（Red -> Green -> Refactor）
**如 work-config.json 启用了 tdd：**
读取并遵循 `skills/vibeflow-tdd/SKILL.md`。

传递上下文：当前功能对象、quality_gates、tech_stack、计划文件路径、完整 `{srs_section}`、完整 `{design_section}`。

### 8. Quality Gates（质量门禁）
**如 work-config.json 启用了 quality_gates：**
读取并遵循 `skills/vibeflow-quality/SKILL.md`。

### 9-10. ST 验收 + 规范审查（并行执行）

Quality Gates 通过后，Feature-ST 和 Spec-Review **互不依赖**，使用 Agent 工具**并行**执行：

```
Quality Gates 通过
        │
        ├──▶ Agent: vibeflow-feature-st（黑盒验收测试）
        │         产出：docs/test-cases/feature-{id}-{slug}.md
        │
        └──▶ Agent: vibeflow-spec-review（规范合规审查）
                  产出：审查裁定（PASS/FAIL）
        │
        ├── 两个 Agent 都返回 ──▶ 合并结果
        └── 任一失败 ──▶ 修复后重新运行失败的部分
```

**执行方式：**

在**同一条消息**中发起两个 Agent 调用：

1. **Agent 1 — Feature-ST**（如 work-config.json 启用了 feature_st）：
   - 提示词包含：功能对象、SRS 章节、设计章节、任务文档路径、`.vibeflow/guides/services.md` 路径
   - 指令：读取并遵循 `skills/vibeflow-feature-st/SKILL.md`，完成后返回执行结果摘要

2. **Agent 2 — Spec-Review**（如 work-config.json 启用了 spec_review）：
   - 提示词包含：功能对象、SRS 章节、设计章节、计划文档路径、UCD 路径（如 ui:true）、Git diff
   - 指令：读取并遵循 `skills/vibeflow-spec-review/SKILL.md`，完成后返回审查裁定

**结果合并：**
- 两个 Agent 都 PASS → 继续添加示例 + 持久化
- 任一 FAIL → 修复问题后，仅重新运行失败的 Agent
- 如仅启用其中一个步骤 → 单 Agent 执行，无需并行

**回退规则：** 如 Agent 工具不可用或执行异常，回退为顺序执行（先 ST，后 Review）。

### 11. 添加示例
在 `examples/` 中创建可运行的示例展示已完成的功能。纯基础设施功能可跳过。

### 12. Persist（持久化）
- Git 提交（实现、测试、示例、测试用例文档）
- 更新 `RELEASE_NOTES.md`（Keep a Changelog 格式）
- 更新 `.vibeflow/logs/session-log.md`：
  - 更新 `## Current State`：进度计数（X/Y 通过）、上一个完成的功能、下一个功能
  - 追加会话条目
- 标记功能 `"status": "passing"` 在 feature-list.json 中
- Git 再次提交（进度文件）

### 13. Continue（继续）
- 如还有失败的非废弃功能且上下文允许 -> 继续下一功能（回到步骤 1）
- 如**无失败的非废弃功能** -> 进入 `vibeflow-review`
- 如上下文耗尽 -> 结束会话（确保 `.vibeflow/logs/session-log.md` 已更新）

## 关键规则

- **每次循环一个功能** — 防止上下文耗尽
- **严格步骤顺序** — 不跳过，不重排
- **work-config.json 为启用步骤的权威** — 被禁用的步骤可跳过
- **不启用也需验证** — 即使 TDD 被禁用，仍需写测试和验证
- **配置门禁在计划前** — 缺配置时不计划不编码
- **不标记 "passing" 无新鲜证据** — 运行测试，读取输出，然后标记
- **不修改 verification_steps** — 需求变更使用增量流程
- **系统化调试** — 出错时追踪根因，不猜测修复
- **每次提交后更新 RELEASE_NOTES.md**
- **结束会话前必须提交 + 更新进度**
- **不留下破损代码** — 回退不完整的工作

## 红线

| 合理化借口 | 正确行动 |
|---|---|
| "配置之后再补" | 运行配置门禁。需要真实配置。 |
| "这功能太简单，跳过测试用例" | 运行 vibeflow-feature-st。每个功能。 |
| "这功能太简单，跳过 TDD" | 运行 vibeflow-tdd。每个功能。 |
| "测试通过了，标记完成" | 先运行 vibeflow-quality。 |
| "覆盖率差不多够了" | 阈值是硬门禁。运行工具。 |
| "我自己快速审查一下" | 运行 vibeflow-spec-review。始终。 |
| "让我快速试试这个修复" | 先系统化调试。 |
| "端口占用，手动杀掉" | 使用 `.vibeflow/guides/services.md` 的停止命令 |
| "后端没准备好先 mock" | 依赖检查存在是有原因的。先开发后端功能。 |

## 出错时

遵循系统化调试流程 — **不猜测修复**：
1. 收集证据（错误消息、堆栈跟踪、git diff）
2. 复现问题
3. 追踪根因
4. 为 bug 写失败测试
5. 单一有针对性的修改
6. 3 次尝试后放弃 -> 升级到用户

---

## Parallel Mode（并行执行）

当选择并行模式时，使用 Agent 工具同时执行多个 feature。

### 执行流程

```
1. 读取 feature-list.json
   → 找出所有 status=failing 的 feature
   → 按优先级排序

2. 读取每个 feature 的设计章节
   → 确认 feature 之间无文件重叠

3. 同时 Spawn N 个 Agent（每个 failing feature 一个）

4. 等待所有 Agent 完成

5. 汇总结果
   → 更新 feature-list.json
→ 更新 `.vibeflow/logs/session-log.md`
   → 报告汇总
```

### Agent 提示词模板

每个 subagent 收到：

```markdown
# Feature Implementation Agent

你是 VibeFlow 的 feature 实现 Agent。你的上下文是**全新的 200k token**，没有任何历史包袱。

## 你的任务

实现 feature：
- **ID**: {feature_id}
- **名称**: {feature_name}
- **优先级**: {priority}

## 上下文文件（请先读取）

1. `docs/changes/<change-id>/design.md` — 技术设计（找到第 4.N 节）
2. `feature-list.json` — 功能详情（找到 id={feature_id} 的条目）
3. `.vibeflow/work-config.json` — 启用了哪些步骤
4. `.vibeflow/guides/build.md`（如存在）— 项目专属指导

## 执行步骤

按顺序执行：

### Step 1: Orient
理解功能需求，确认设计章节。

### Step 2: TDD
读取 `skills/vibeflow-tdd/SKILL.md`，执行红→绿→重构循环。

### Step 3: Quality Gates
读取 `skills/vibeflow-quality/SKILL.md`，运行覆盖率 + 变异测试。

### Step 4: Feature-ST
读取 `skills/vibeflow-feature-st/SKILL.md`，执行验收测试。

### Step 5: Spec-Review
读取 `skills/vibeflow-spec-review/SKILL.md`，检查实现是否符合 SRS。

### Step 6: Persist
1. **不要直接 commit** — 并行模式下由 orchestrator 统一处理 git 操作
2. 将实现结果写入 `.vibeflow/subagent-results/{feature_id}.json`：
   ```json
   {
     "feature_id": "{id}",
     "status": "passing" | "failing",
     "implemented_files": ["file1.ts", "file2.ts"],
     "summary": "{一句话总结}",
     "error": "{失败原因，如有}"
   }
   ```
3. 如实现完成但测试失败，status 仍为 "failing"

**重要**：不要同时写入 `feature-list.json`、`.vibeflow/logs/session-log.md`、`RELEASE_NOTES.md` 等共享文件，这些由 orchestrator 统一更新。

## 产出

完成后返回结构化结果：

```
RESULT: {feature_id}: PASS
COMMIT: {git_hash}
SUMMARY: {一句话总结}
```

如失败：

```
RESULT: {feature_id}: FAIL
ERROR: {具体错误描述}
RETRY: {是否可自动重试}
```

## 重要约束

- **每个 feature 独立执行**，不知道其他 feature 的存在
- **不要与其他 subagent 通信**，结果通过文件共享
- **遇到错误不要放弃**，尽力完成，能走多远走多远
```

### Orchestrator 汇总逻辑

```markdown
所有 Agent 完成后：

1. 读取 subagent 结果文件：
   ls .vibeflow/subagent-results/*.json

2. 对于每个 PASS 的 feature：
   a. git add {implemented_files}
   b. git commit -m "feat({feature_id}): {summary}"
   c. 获取 commit hash

3. 更新 feature-list.json（统一操作，非并行）：
   - status = "passing"（如 PASS）
   - status = "failing" + last_error（如 FAIL）
   - completed_at = timestamp
   - commit = hash（如 PASS）

4. 更新 `.vibeflow/logs/session-log.md`（统一操作）

5. 更新 RELEASE_NOTES.md（统一操作）

6. 生成汇总报告：
   ```
   ═══════════════════════════════════
   Parallel Execution Results
   ═══════════════════════════════════
   Total: N | PASS: M | FAIL: K

   ✅ Feature A — PASS (commit: abc123)
   ✅ Feature B — PASS (commit: def456)
   ❌ Feature C — FAIL (覆盖率不足)

   Next: [处理失败 feature 的建议]
   ═══════════════════════════════════
   ```

7. 如有失败：
   - 询问用户是否继续 Sequential 模式逐个修复
   - 或在下一个会话处理
```

### 使用场景

| 场景 | 推荐模式 |
|------|---------|
| 项目启动，第一次执行所有 feature | Parallel |
| 调试某个具体 feature | Sequential |
| 有 feature 失败后的重试 | Sequential（修复单个） |
| 多个独立 feature 需要快速完成 | Parallel |

### 前提条件

**并行模式要求**：
- feature 之间**无文件重叠**（Plan 阶段已分配好文件范围）
- 所有 feature 的**依赖都已满足**（依赖的 feature 状态为 passing）
- 开发环境**已初始化**（build-init 已完成）

**如不满足条件**，自动降级为 Sequential 模式。

## 集成

**调用者：** vibeflow-router 的 Build 自动继续链路（默认）或 vibeflow-build-init 的手动 fallback
**调用顺序：**
1. `vibeflow-tdd`（步骤 5-7）— 顺序
2. `vibeflow-quality`（步骤 8）— 顺序（依赖 TDD 产出）
3. `vibeflow-feature-st` + `vibeflow-spec-review`（步骤 9-10）— **并行**（通过 Agent 工具）
**读/写：** feature-list.json、`.vibeflow/logs/session-log.md`、RELEASE_NOTES.md
