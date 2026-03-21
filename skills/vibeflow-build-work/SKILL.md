---
name: vibeflow-build-work
description: "feature-list.json 存在且部分功能仍失败时使用 — 驱动功能通过完整 TDD 管线、质量门禁和代码审查"
---

# Worker — 每次循环一个功能

通过每次循环实现一个功能来执行多会话软件项目。每个循环遵循严格管线：Orient -> Gate -> Plan -> TDD -> Quality -> ST 验收 -> Review -> Persist。

**启动宣告：** "正在使用 vibeflow-build-work。让我先定位当前状态。"

**核心原则：** 每个子步骤有其专属 skill。严格遵循编排顺序。

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
- 读取 `task-progress.md` 的 `## Current State` — 进度、上一个完成的功能、下一个功能
- 读取 `feature-list.json` — 注意 `constraints[]`、`assumptions[]`、`required_configs[]`、功能状态
- 读取 `vibeflow-guide.md` — 项目专属工作流指导
- 读取 `env-guide.md`（如存在）— 服务名、端口、健康检查 URL
- 读取设计文档**第 1 节**（`docs/plans/*-design.md`）— 项目概览和架构快照
- 运行 `git log --oneline -10` — 近期提交上下文
- 选取下一个 `"status": "failing"` 的功能，按优先级然后按数组位置（第一个合格的胜出）— **跳过 `"deprecated": true` 的功能**
- **依赖满足检查**：选择候选功能后，验证其 `dependencies[]` 中所有功能 ID 在 feature-list.json 中状态为 `"passing"`。如有依赖未满足：
  - 记录："功能 #{id}（{title}）被跳过 — 未满足依赖：#{dep1}、#{dep2}"
  - 选取下一个合格的功能
  - 如**无**功能的依赖都已满足 -> 通过 `AskUserQuestion` 警告用户
- 如目标功能有 `"ui": true` 且 UCD 文档存在，读取 UCD 风格指南

**文档查找协议：**

当需要功能的设计章节或 SRS 需求时，**不要** grep 功能标题。而是：

1. 读取设计文档的**第 4 节标题区域**，找到对应 `### 4.N` 子节
2. 读取该子节的**完整内容**（从 `### 4.N` 到 `### 4.(N+1)` 前）
3. 同理读取 SRS 的完整 FR-xxx 子节
4. 存储为 `{design_section}` 和 `{srs_section}` 供后续步骤使用

### 2. Bootstrap（引导）
- 确认开发环境就绪（如需运行 init.sh/init.ps1）
- 冒烟测试已通过的功能

### 3. Config Gate（配置门禁）
检查目标功能的 `required_configs` 是否齐备。缺失时通过 `AskUserQuestion` 向用户收集，追加到 `.env`。**配置齐备前阻塞。**

### 4. Plan（计划）
为选定功能编写逐步实现计划，保存到 `docs/plans/YYYY-MM-DD-<feature-name>.md`。

- **必须**使用文档查找协议读取完整 `{design_section}` 和 `{srs_section}`
- 计划**必须**与审批的类图、序列流和架构决策对齐
- UI 功能**必须**指定适用的 UCD 风格 Token

### 5-7. TDD 循环（Red -> Green -> Refactor）
**如 work-config.json 启用了 tdd：**
读取并遵循 `skills/vibeflow-tdd/SKILL.md`。

传递上下文：当前功能对象、quality_gates、tech_stack、计划文件路径、完整 `{srs_section}`、完整 `{design_section}`。

### 8. Quality Gates（质量门禁）
**如 work-config.json 启用了 quality_gates：**
读取并遵循 `skills/vibeflow-quality/SKILL.md`。

### 9. ST 验收测试用例
**如 work-config.json 启用了 feature_st：**
读取并遵循 `skills/vibeflow-feature-st/SKILL.md`。

产出：`docs/test-cases/feature-{id}-{slug}.md`

### 10. 规格与设计合规审查
**如 work-config.json 启用了 spec_review：**
读取并遵循 `skills/vibeflow-spec-review/SKILL.md`。

### 11. 添加示例
在 `examples/` 中创建可运行的示例展示已完成的功能。纯基础设施功能可跳过。

### 12. Persist（持久化）
- Git 提交（实现、测试、示例、测试用例文档）
- 更新 `RELEASE_NOTES.md`（Keep a Changelog 格式）
- 更新 `task-progress.md`：
  - 更新 `## Current State`：进度计数（X/Y 通过）、上一个完成的功能、下一个功能
  - 追加会话条目
- 标记功能 `"status": "passing"` 在 feature-list.json 中
- Git 再次提交（进度文件）

### 13. Continue（继续）
- 如还有失败的非废弃功能且上下文允许 -> 继续下一功能（回到步骤 1）
- 如**无失败的非废弃功能** -> 进入 `vibeflow-review`
- 如上下文耗尽 -> 结束会话（确保 task-progress.md 已更新）

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
| "端口占用，手动杀掉" | 使用 env-guide.md 的停止命令 |
| "后端没准备好先 mock" | 依赖检查存在是有原因的。先开发后端功能。 |

## 出错时

遵循系统化调试流程 — **不猜测修复**：
1. 收集证据（错误消息、堆栈跟踪、git diff）
2. 复现问题
3. 追踪根因
4. 为 bug 写失败测试
5. 单一有针对性的修改
6. 3 次尝试后放弃 -> 升级到用户

## 集成

**调用者：** vibeflow-router（feature-list.json 存在时）或 vibeflow-build-init
**调用（严格顺序）：**
1. `vibeflow-tdd`（步骤 5-7）
2. `vibeflow-quality`（步骤 8）
3. `vibeflow-feature-st`（步骤 9）
4. `vibeflow-spec-review`（步骤 10）
**读/写：** feature-list.json、task-progress.md、RELEASE_NOTES.md
