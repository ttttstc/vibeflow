# VibeFlow 能力集成优先级规划

> 基于 GSD、OpenSpec、BMAD 三个项目的研究分析
> 日期：2026-03-23

---

## 评估维度

| 维度 | 说明 |
|------|------|
| **价值** | 对用户体验和项目质量的提升程度 |
| **成本** | 实现所需的工作量（低/中/高）|
| **契合度** | 与现有 7 阶段框架的契合程度（1-5 分）|
| **风险** | 对现有功能的破坏风险（低/中/高）|

---

## 能力评分表

| # | 能力 | 来源 | 价值 | 成本 | 契合度 | 风险 | 优先级 |
|---|------|------|------|------|--------|------|--------|
| 1 | 原子化 Plan 输出（PLAN.md + RESEARCH.md）| GSD | 高 | 低 | 5 | 低 | **P0** |
| 2 | Scale-Adaptive 模板系统 | BMAD | 高 | 中 | 5 | 低 | **P0** |
| 3 | 变更文件夹结构（proposal/specs/design/tasks）| OpenSpec | 高 | 低 | 5 | 低 | **P0** |
| 4 | Model Profile 配置 | GSD | 中 | 低 | 4 | 低 | **P1** |
| 5 | Quick Mode（跳过部分阶段）| GSD | 高 | 低 | 4 | 中 | **P1** |
| 6 | Party Mode（多视角 Agent 协作）| BMAD | 高 | 高 | 3 | 中 | **P2** |
| 7 | Wave 并行执行 | GSD | 高 | 高 | 3 | 中 | **P2** |
| 8 | 多运行时支持（Cursor/Copilot/etc）| GSD/OpenSpec | 中 | 高 | 2 | 低 | **P3** |
| 9 | 完整模块生态 | BMAD | 中 | 极高 | 1 | 高 | **P3** |

---

## P0 — 必须实现（当前分支可完成）

### 1. 原子化 Plan 输出
**来源**：GSD 的 `{phase_num}-{N}-PLAN.md` + `RESEARCH.md` 模式

**现状**：VibeFlow Plan 阶段输出单一 `plan.md`

**改动**：
- `vibeflow-plan` skill：调整为 RESEARCH + 原子 PLAN 输出格式
- 产出 `.vibeflow/research.md` + `.vibeflow/plan-atomic-1.md`, `plan-atomic-2.md`
- 现有 `plan.md` 作为汇总索引文件保留

**价值**：Plan 更可执行、可验证、可追溯
**风险**：低 — 仅改变产出格式，不改变路由逻辑

---

### 2. Scale-Adaptive 模板系统
**来源**：BMAD 的 "automatically adjusts planning depth based on project complexity"

**现状**：四种静态模板（prototype/web-standard/api-standard/enterprise）

**改动**：
- 模板增加 `planning_depth: auto` 选项
- `vibeflow-plan` skill 根据项目规模（代码行数、模块数、依赖数）自动调整：
  - 小项目 → quick plan
  - 中项目 → standard plan（现状）
  - 大项目 → deep plan（多轮 review + 风险分析）

**价值**：同一模板自动适配不同规模项目，减少人工判断
**风险**：低 — 新增 `auto` 选项，不影响现有 static 选项

---

### 3. 变更文件夹结构
**来源**：OpenSpec 的 `changes/{change-name}/{proposal,specs,design,tasks}`

**现状**：VibeFlow 的 `docs/plans/{name}/` 结构

**改动**：
- Design 阶段产出调整到 `docs/changes/{change-name}/`：
  - `proposal.md` — 变更动机
  - `specs/` — 需求规格
  - `design.md` — 技术设计
  - `tasks.md` — 实现清单
- `docs/plans/` 保留给长期规划文档
- Review 阶段读取变更文件夹作为输入

**价值**：清晰的变更追踪，与 OpenSpec 生态兼容
**风险**：低 — 重命名输出目录，不改变 phase 检测逻辑

---

## P1 — 应该实现（下个迭代）

### 4. Model Profile 配置
**来源**：GSD 的 model profiles（quality/balanced/budget）

**现状**：无模型选择机制

**改动**：
- 新增 `vibeflow-profile` skill 或配置选项
- 三种 Profile：
  - `quality`：Plan 用 Opus，Build 用 Sonnet
  - `balanced`：统一 Sonnet
  - `budget`：Build 用 Haiku
- 存储在 `.vibeflow/config.json` 中
- Build 阶段根据 profile 选择模型

**价值**：成本控制灵活，企业用户尤其实用
**成本**：中 — 需修改 Build 相关 skill 的模型选择逻辑

---

### 5. Quick Mode
**来源**：GSD 的 `/gsd:quick`

**现状**：所有任务都必须走完整 Think→Plan→Requirements→Design 流程

**改动**：
- 新增 `vibeflow-quick` skill
- 适用场景：bug fix、small change、hot patch
- 流程简化：`/vibeflow-quick <描述>` → 直接进入 Build（跳过 Think/Plan/Requirements/Design）
- Gate：`quick_mode` 检测到简单变更时自动推荐
- 条件：仅当 `.vibeflow/quick-mode-eligible.txt` 存在时可用

**价值**：小任务效率大幅提升
**风险**：中 — 可能绕过重要的 Design Review 环节，需要明确 eligibility 判断
**注意**：必须设置明确的 eligibility 标准，避免被滥用

---

## P2 — 可以实现（未来版本）

### 6. Party Mode
**来源**：BMAD 的多 Agent 同场协作

**现状**：Design Review 是串行的两个 skill 调用

**改动**：
- 新增 `vibeflow-party` skill
- 在 Design 阶段末，并行调用：
  - `vibeflow-plan-eng-review`
  - `vibeflow-plan-design-review`
  - `vibeflow-review`（architect persona）
- Party Mode skill 作为 orchestrator，汇总三份评审意见

**价值**：评审速度提升，多视角同时审视
**成本**：高 — 需要 skill 并行调用机制，当前 VibeFlow 无此能力

---

### 7. Wave 并行执行
**来源**：GSD 的 wave-based parallel execution

**现状**：Build 阶段顺序执行每个 feature

**改动**：
- 新增 `vibeflow-build-wave` skill（作为 build-work 的编排模式）
- feature-list.json 中支持 `wave` 字段标注并行组
- 同一 wave 的 features 并行构建
- 不同 wave 顺序执行

**价值**：多核/CI 环境构建速度大幅提升
**成本**：高 — 涉及 build-work 编排器重写，测试覆盖复杂
**前提**：需要先实现 P1-5 有稳定基础

---

## P3 — 长期规划

### 8. 多运行时支持
**来源**：GSD/OpenSpec 的 20+ AI 工具集成

**现状**：仅支持 Claude Code

**改动**：skill 安装脚本支持 OpenCode、Cursor 等
**成本**：高 — 各工具 skill 格式不同，测试成本大
**优先级理由**：VibeFlow 核心定位是 Claude Code 专用框架，多运行时是锦上添花

---

### 9. 完整模块生态
**来源**：BMAD 的模块化生态

**改动**：按需安装 BMM/BMB/TEA/BMGD/CIS 模块
**成本**：极高 — 与 VibeFlow 现有架构差异大
**优先级理由**：VibeFlow 专注工程纪律，不需要 BMAD 的全部 34+ 工作流

---

## 推荐实施路径

### 阶段 1：P0 能力落地（当前 PR 后）
```
vibeflow-plan (增强)
├── 原子化 RESEARCH + PLAN 输出
└── Scale-adaptive 自动判断

vibeflow-design (增强)
├── 变更文件夹结构 docs/changes/{name}/
└── tasks.md 生成
```

### 阶段 2：P1 能力（下一个里程碑）
```
vibeflow-profile — Model Profile 配置
viblow-quick — Quick Mode
```

### 阶段 3：P2 能力（稳定后）
```
vibeflow-party — Party Mode 多视角并行评审
vibeflow-build-wave — Wave 并行执行
```

---

## 与现有框架的集成关系

```
当前 7 阶段                    P0 增强                    P1 增强
─────────────────────────────────────────────────────────────────────
Think ──────────────────► Think ──────────────────► Think
                               │                         │
                               │ Scale-Adaptive         │
                               ▼                         ▼
Plan ───────────────────► Plan (原子化 RESEARCH+PLAN) ► Plan + Quick Mode
                               │                         │
                               │                         │ (跳过 Plan 直接 Build)
                               ▼                         ▼
Requirements ────────────► Requirements ─────────────► (Quick Mode 跳过)
                               │
                               │ 变更文件夹结构
                               ▼
Design ─────────────────► Design (docs/changes/) ──► Design + Party Mode
                               │
                               │                         │
                               ▼                         ▼
Build ──────────────────► Build ─────────────────► Build + Wave
                               │
                               │ Model Profile          │
                               ▼                         ▼
Review ─────────────────► Review ─────────────────► Review + Party
                               │
                               ▼                         ▼
Test ───────────────────► Test ───────────────────► Test
                               │
                               ▼                         ▼
Ship ───────────────────► Ship ───────────────────► Ship
                               │
                               ▼                         ▼
Reflect ─────────────────► Reflect ───────────────► Reflect
```

---

## 总结

| 优先级 | 能力数 | 核心价值 |
|--------|--------|---------|
| **P0** | 3 | 框架质量本质提升，无风险 |
| **P1** | 2 | 用户效率显著提升 |
| **P2** | 2 | 高级用户场景覆盖 |
| **P3** | 2 | 长期生态扩展 |
