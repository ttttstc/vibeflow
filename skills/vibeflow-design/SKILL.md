---
name: vibeflow-design
description: "以审批通过的 SRS 为输入产出架构/设计文档，回答 HOW。内置问题探索（absorbed from brainstorming）— 当问题不清晰时在设计前先厘清。"
---

# 设计文档生成

以审批通过的 SRS 为输入。提出实现方案，逐节获得设计审批，产出回答 HOW 的设计文档 — 而 SRS 回答 WHAT。

**此 skill 已吸收 brainstorming 核心行为：当无 SRS 或问题不清晰时，先进行问题探索再进入技术设计。**

**启动宣告：** "正在使用 vibeflow-design — 设计阶段（含问题探索）。"

<HARD-GATE>
在你展示设计文档并获得用户批准之前，不得调用任何实现技能、编写任何代码、搭建任何项目。此规则适用于每个项目。
</HARD-GATE>

## 反模式 A："SRS 足够详细可以直接编码了"

SRS 描述系统**做什么**。设计文档描述**怎么做**。即使需求很清晰，实现方案（架构、数据模型、技术栈选择）也需要显式决策和用户审批。

## 反模式 B："这太简单不需要设计"

每个项目都需要设计。一个 todo list、一个函数工具、一个配置变更——所有项目都需要。"简单"项目正是未经审视的假设造成最多浪费的地方。设计可以很短（真正简单的项目几句话），但你必须展示并获得批准。

## 检查清单

按顺序完成以下步骤：

0. **[问题探索]** — 如果无 SRS 或问题不清晰，先厘清问题和方向
1. **读取需求和 UCD（如需）** — 从 `docs/changes/<change-id>/`
2. **探索技术上下文** — 现有代码、框架、部署环境
3. **提出 2-3 个方案** — 带权衡和推荐
4. **逐节设计审批** — 架构、数据模型、API、UI/UX、测试、部署（用户参与式审批）
5. **AI 深度审查** — eng review + design review（用户审批后执行）
6. **范围决策** — 基于三方意见判断范围是否需要调整
7. **编写设计文档** — 保存到 `docs/changes/<change-id>/design.md` 并提交
8. **过渡到初始化** — 进入 `vibeflow-build-init`

**终止状态是进入 vibeflow-build-init。**

## 步骤 0：问题探索（仅当无 SRS 或问题不清晰时）

当存在 `docs/changes/<change-id>/requirements.md` 且问题已清晰时，**跳过此步骤**，直接进入步骤 1。

当无 SRS 或问题定义模糊时，先通过问题探索厘清方向：

### 0.1 检查 brainstorming 产物

检查是否存在 `docs/plans/*-brainstorming.md`：
- **如果存在**：读取其内容作为问题探索结论，包含 Problem Statement、Approach Chosen、Open Questions
- **如果不存在**：继续以下探索步骤

### 0.2 探索项目上下文

1. 检查当前项目状态（文件、文档、最近提交）
2. 在提问之前评估范围：如果请求描述多个独立子系统，立即标记并帮助分解
3. 如果项目范围过大（需要多个独立子系统），帮助用户分解为子项目

### 0.3 逐个提问澄清

**一次只问一个问题**。优先使用多选题。

通过 AskUserQuestion 提问，聚焦于理解：
- **目的** — 用户真正想要解决的是什么？
- **约束** — 有什么限制条件？（技术栈、时间、资源）
- **成功标准** — 怎么算"做好了"？

使用 AskUserQuestion 格式：
1. **Re-ground：** 陈述项目和当前问题。（1-2 句）
2. **Simplify：** 用普通高中生能理解的简单语言解释问题。不用行话，用具体例子。
3. **推荐：** `RECOMMENDATION: Choose [X] because [one-line reason]`
4. **选项：** 字母选项 `A) ... B) ... C) ...`

### 0.4 提出方案

展示 **2-3 个实现方案**并带有明确权衡：

```
## 方案 A：[名称]
**摘要**：[1-2 句]
** Effort**:  [S/M/L/XL]
**风险**:    [低/中/高]
**优点**:    [2-3 点]
**缺点**:    [2-3 点]
**复用**:    [现有代码/模式]
```

规则：
- 一个必须是"最小可用"（文件最少、diff 最小）
- 一个必须是"理想架构"（最佳长期轨迹）
- 一个可以是创意/差异化路径

**RECOMMENDATION:** Choose [X] because [one-line reason]

### 0.5 用户审批方案

使用 AskUserQuestion 展示方案并请求选择：
- 展示推荐的方案及理由
- 等待用户确认或选择其他方案

### 0.6 探索结论并入设计文档

将问题探索结论写入最终设计文档的"问题定义"和"方案选择"章节，不再单独产出 brainstorming 文件。

---

## 步骤 1：读取 SRS 和 UCD（如需）并提取设计输入

### 1.0 判断是否需要 UCD

1. 运行 `python scripts/get-vibeflow-paths.py --json`
2. 读取 `docs/changes/<change-id>/requirements.md`
2. 检查 SRS 中是否包含 UI 相关功能需求（FR 含用户界面、页面或组件）
3. 检查 `.vibeflow/workflow.yaml` 中的 `plan.mode`：
   - `prototype` / `api-standard` → 通常无前端 UI，**跳过 UCD**
   - `web-standard` / `enterprise` → 通常有 UI，**执行 UCD 子步骤**
4. 如判断跳过 UCD，告知用户："SRS/模板 无 UI 需求 — 跳过视觉风格定义"

### 1.1 读取现有 UCD（如存在）

- 读取 `docs/changes/<change-id>/ucd.md`（如已存在）
- 提取 UCD 风格 Token：颜色、排版、间距、组件目录
- 将 Token 注入设计文档的 UI/UX 章节

### 1.2 生成 UCD 内容（如不存在且需要 UI）

当 SRS 有 UI 需求且无现有 UCD 文档时，执行以下子步骤生成风格指南：

#### 1.2.1 定义视觉风格方向

向用户展示 **2-3 个视觉风格选项**：

```markdown
## 风格 A：[名称]
**调性**：[1-2 句描述视觉感受]
**色彩方向**：[主色调倾向 — 暖/冷/中性，高/低对比]
**排版方向**：[衬线/无衬线，几何/人文，密度]
**布局方向**：[卡片/列表，紧凑/宽松，固定/流式]
**目标用户契合**：[最适合哪些 SRS 用户画像]
```

等待用户选择或提供方向。

#### 1.2.2 生成风格 Token

定义锚定整个风格系统的具体设计 Token：

**颜色调色板：**
```markdown
| Token | Hex | 用途 | 对比度 |
|-------|-----|------|--------|
| --color-primary | #XXXXXX | 主要操作、链接 | >= 4.5:1 |
| --color-bg-primary | #XXXXXX | 主背景 | |
| --color-text-primary | #XXXXXX | 正文 | >= 4.5:1 |
```
所有对比度必须满足 WCAG AA（正文 4.5:1，大文本 3:1）。

**排版比例：** 字体族、大小、字重、行高、用途。

**间距与布局：** 间距 token（--space-xs/sm/md/lg/xl）、圆角（--radius-sm/md/lg）、阴影（--shadow-sm/md/lg）。

**图标风格：** 线框/填充/双色、图标库（如 Lucide Icons）。

#### 1.2.3 生成组件提示词（如 UI 清单存在）

对 UI 清单中的每种组件类型产出**文生图提示词**：

```markdown
### 组件：[组件名]
**变体**：默认、悬停、激活、禁用、错误、加载

#### 基础提示词
> [详细文生图提示词，引用颜色 Token、排版 Token、间距]
```

#### 1.2.4 生成页面提示词（如页面存在）

对每个关键页面/屏幕产出**整页文生图提示词**。

### 1.3 提取关键设计驱动因素

无论是否执行 UCD 子步骤，统一提取：

- **功能范围** — FR 数量、优先级分布、依赖链
- **NFR 阈值** — 影响架构的性能目标、可靠性、可扩展性
- **约束** — 限制技术/方案选择的硬限制
- **接口需求** — 外部系统、协议、数据格式
- **用户画像** — 影响 API/UI 设计决策的技术水平
- **UCD 风格 Token**（如已生成或存在）— 颜色、排版、间距、组件目录 -> 指导 UI/UX 章节

### 1.4 列出开放问题

列出必须在设计前解决的 SRS **开放问题**。

### 1.5 读取现有代码结构与本次影响面（现有项目改动）

如项目不是从空仓开始，设计阶段默认读取：
- `docs/changes/<change-id>/codebase-impact.md`

如上述影响分析文件不存在，先运行：
- `python scripts/map-change-impact.py --project-root . --source design`

设计文档必须显式吸收以下内容：
- `Relevant Modules`
- `Integration Points`
- `Risk Notes`
- `Suggested Read Order`

## 步骤 2：探索技术上下文

1. 探索项目将要构建的现有代码/仓库
2. 识别 SRS 中未提及的技术约束（如单体仓库结构、CI/CD 管线、现有库）
3. 检查设计文档模板

## 步骤 3：提出方案

展示 **2-3 个实现方案**并带有明确权衡：

```markdown
## 方案 A：[名称]
**原理**：[1-2 句]
**优点**：[要点列表]
**缺点**：[要点列表]
**最适用于**：[条件]
**NFR 影响**：[该方案如何影响 SRS NFR 阈值]
**第三方依赖**：[关键库/框架及版本]

## 推荐：方案 [X]
**理由**：[为何最适合 SRS 约束和 NFR]
```

每个方案必须对照 SRS 约束和 NFR 阈值评估。无法满足"Must" NFR 的方案被淘汰。

## 步骤 4：逐节审批

非简单项目逐节展示并获得审批：

1. **架构** — 系统组件、逻辑视图、技术栈决策
   - 必须包含 **逻辑视图**（Mermaid `graph`）显示层/包/模块及依赖方向
   - 必须包含 **组件图**（Mermaid `graph`）显示运行时组件和交互
   - 必须论证技术栈选择与 SRS 约束的关系
2. **关键功能设计** — 每个关键功能或功能组一章
   - 每章**必须**至少包含：
     - **类图**（Mermaid `classDiagram`）
     - **一个行为图**：序列图（`sequenceDiagram`）或流程图（`flowchart`）
   - 所有图表**必须**使用 **Mermaid** 格式
3. **数据模型** — 模式、关系、存储策略
   - 必须使用 Mermaid ER 图（`erDiagram`）
4. **API / 接口设计** — 端点、契约、协议
5. **UI/UX 方案**（如适用）— 布局策略、交互模式
   - 如 UCD 存在：必须引用 UCD 风格 Token 和组件目录
6. **第三方依赖** — 所有库/框架带**精确版本号**
   - 验证依赖间互相兼容
   - 验证与目标运行时版本兼容
   - 记录每个依赖的许可证类型
7. **测试策略** — 测试类型、覆盖率目标、工具
8. **部署/基础设施**（如适用）— 托管、CI/CD、环境
9. **开发计划** — 里程碑、任务分解、优先级排序
   - 必须定义有明确退出标准的里程碑
   - 必须将功能分解为优先级任务（P0-P3）
   - 必须展示依赖链（Mermaid `graph`）标识关键路径
   - 必须包含风险评估和缓解策略
   - **前后端配对排序**：当项目同时有后端和前端功能时，按后端 A -> 前端 A -> 后端 B -> 前端 B 排序

**简单项目**（< 5 个功能）：合并所有章节为单次审批步骤，但仍需包含必要图表和依赖版本。

## 步骤 5：AI 深度审查（用户审批后执行）

用户审批设计后，执行 AI 独立深度审查——这是 AI 质量把关，不重复用户审批。

### 5.1 工程审查

调用 `vibeflow-plan-eng-review` 对设计文档进行工程评审：

```
Skill: vibeflow-plan-eng-review
```

评审内容：架构设计、数据流、测试策略、性能风险、安全边界。

完成后将结论写入 `docs/changes/<change-id>/design-review.md` 的 `## Engineering Review` 小节。

### 5.2 设计审查

调用 `vibeflow-plan-design-review` 对设计文档进行七轮设计评审：

```
Skill: vibeflow-plan-design-review
```

评审内容：信息架构、交互状态、用户旅程、AI 污染风险、设计系统一致性、响应式与无障碍。

完成后将结论写入 `docs/changes/<change-id>/design-review.md` 的 `## Design Review` 小节。

### 5.3 审查结论汇总

提取两个 review 的关键发现：

```markdown
## AI 审查结论

**日期**：YYYY-MM-DD
**设计文档**：`docs/changes/<change-id>/design.md`

### 工程审查（vibeflow-plan-eng-review）
- Architecture: [N] issues
- Code Quality: [N] issues
- Test Coverage: [N] gaps
- Performance: [N] issues
- **严重问题**： [列出 critical issues，需在 scope decision 前处理]

### 设计审查（vibeflow-plan-design-review）
- Information Architecture: [N]/10
- Interaction States: [N]/10
- User Journey: [N]/10
- AI Slop Risk: [N]/10
- Design System: [N]/10
- Responsive & A11y: [N]/10
- **待解决设计问题**： [列出影响范围的问题]
```

---

## 步骤 6：范围决策

基于用户审批的设计方案 + eng review + design review 三方意见，综合判断范围是否需要调整。

### 6.1 质疑范围

| 检查 | 问题 |
|------|------|
| **范围过大** | 设计中是否有 MVP 不需要的功能？哪些可以推迟？ |
| **范围过小** | 设计是否遗漏了对目标结果至关重要的功能？ |
| **eng review 风险** | 架构或技术方案是否有重大风险影响范围？ |
| **design review 问题** | 是否有严重设计缺陷需要范围调整？ |

### 6.2 范围决策

产出三选一的决策：

**扩展（Expand）**：eng/design review 发现当前范围遗漏了高价值、低成本的功能。

**保持（Hold）**：设计合理，eng/design review 无重大问题。

**缩减（Reduce）**：eng/design review 发现范围过大或风险过高。

### 6.3 用户确认范围

通过 `AskUserQuestion` 展示 AI 审查结论和范围决策建议：

1. **Re-ground：** 陈述项目、已审批的设计、AI 审查关键发现。（1-2 句）
2. **Simplify：** 用普通高中生能理解的语言解释 eng/design review 发现了什么风险。
3. **推荐：** `RECOMMENDATION: [Expand / Hold / Reduce] — [one-line reason]`
4. **选项：** `A) 接受推荐 B) 调整范围 C) 先解决 critical issues 再决定`

### 6.4 更新设计文档

如果范围有调整，将决策记录写入设计文档末尾：

```markdown
## 范围决策

**决策**：[Expand / Hold / Reduce]
**理由**：[简要说明]
**调整**：[如范围有变化，列出具体调整内容]
**eng review 发现**：[N] issues（critical: [N]）
**design review 发现**：[N]/10 overall
```

---

## 步骤 7：编写设计文档

保存到 `docs/changes/<change-id>/design.md`。

**执行交接硬要求：**
- 设计文档必须包含且只包含一个可解析的 `Build Contract` TOML 代码块
- 每个可实施 feature 必须包含一个可解析的 `Implementation Contract` TOML 代码块
- `Implementation Contract` 至少要写出：`feature_id`、`title`、`priority`、`dependencies`、`file_scope`、`verification_commands` 或 `verification_steps`
- Build 阶段以这些 TOML 契约作为权威输入；`tasks.md` 只作为说明性索引，不再是主事实来源

## 步骤 8：过渡到初始化

设计文档保存并提交后：

1. 总结初始化需要的关键输入：
   - **来自 SRS**：约束、假设、NFR、用户画像、术语表、功能需求 -> 功能清单
   - **来自设计**：技术栈、架构决策 -> `tech_stack`、项目骨架
2. 进入 `vibeflow-build-init` 搭建项目

## 图表要求

所有架构和设计视图**必须**使用 **Mermaid** 语法。

| 章节 | 图表类型 | Mermaid 语法 | 必需？ |
|------|---------|-------------|--------|
| 架构逻辑视图 | 分层包图 | `graph TB` | 始终 |
| 架构组件 | 组件交互 | `graph LR` | 始终 |
| 关键功能 — 结构 | 类图 | `classDiagram` | 每个功能 |
| 关键功能 — 行为 | 序列图/流程图 | `sequenceDiagram`/`flowchart` | 每个功能（至少一个） |
| 数据模型 | ER 图 | `erDiagram` | 如有持久化 |
| 依赖图 | 依赖树 | `graph LR` | 如 > 3 个第三方依赖 |
| 开发计划 | 关键路径 | `graph LR` | 始终 |

## 红线

| 合理化借口 | 正确响应 |
|---|---|
| "SRS 已暗示了架构" | SRS 描述 WHAT，不是 HOW。展示选项。 |
| "只有一种方式构建" | 至少展示 2 个方案。即使显而易见的选择也需说明权衡。 |
| "用户似乎不耐烦，跳过设计" | 简要说明价值，然后高效执行 |
| "边做边设计" | 前期设计比中途纠正便宜 |

## 集成

**调用者：** vibeflow-router 或 vibeflow-requirements（步骤 8）
**依赖：** `docs/changes/<change-id>/requirements.md`；可选 `docs/changes/<change-id>/ucd.md`；可选 `docs/plans/*-brainstorming.md`（历史问题探索上下文）
**链接到：** vibeflow-build-init（scope decision 通过后）
**产出：**
- `docs/changes/<change-id>/design.md`（设计文档，含 UI/UX 章节）
- `docs/changes/<change-id>/design-review.md`（工程审查 + 设计审查结论）

**UCD 行为说明：**
- SRS 有 UI 需求 + `ucd.md` 已存在：读取 UCD 作为输入，跳过 UCD 生成
- SRS 有 UI 需求 + 无 `ucd.md`：执行 UCD 子步骤（步骤 1.2）生成风格 Token 和提示词，并保存到 `docs/changes/<change-id>/ucd.md`
- SRS 无 UI 需求或 template 为 api-standard/prototype：跳过 UCD，告知用户
- 无论 UCD 是读取还是生成，最终都内联到设计文档的 UI/UX 章节中
