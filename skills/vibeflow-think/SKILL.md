---
name: vibeflow-think
description: Think 阶段用于寻找灵感和确定方向。通过问题框定和 DeepResearch 竞品调研，明确项目方向后进入 Plan 阶段进行详细分析。
---

## 目标

产出 Think 阶段的简洁方向声明：

- `docs/deepresearch/<领域>-<timestamp>.md`（如执行了 DeepResearch）
- 方向声明（内嵌于 Plan 阶段的 context.md）

## 首先重用

在提问或写作之前：

1. 阅读`VIBEFLOW-DESIGN.md`
2. 重用工作空间中已有的产品发现基础

使用该基础来指导提问风格和问题重构思维。不要在此处复制其更广泛的设置行为。

## 必需输入

从以下来源收集足够的上下文：

- 用户的请求
- `VIBEFLOW-DESIGN.md`
- 仓库中现有的根文档

## Office Hours（可选前置）

在开始问题框定之前，用户可选择先运行 YC Office Hours 风格的头脑风暴：

Skill: vibeflow-office-hours

这会帮助从战略层面验证想法是否值得投入，而非直接进入执行规划。

**何时使用：**
- 用户有模糊的想法但不确定是否值得做
- 需要在投入工程资源前验证需求真实性
- 用户要求"先聊聊这个想法"

**如用户跳过此步骤**，直接进入标准 Think 流程。

## Think流程

Think 阶段的核心目标是**寻找灵感、确定方向**。其他分析工作放到 Plan 阶段。

### 1. 问题框定

推动对话朝向：

- 要解决的实际问题
- 用户是谁
- 明确不在范围内的内容

### 2. DeepResearch（可选）

运行深度竞品调研，寻找灵感和差异化方向：

Skill: vibeflow-deepresearch

**何时使用：**
- 进入不熟悉领域时
- 需要灵感时
- 需要寻找差异化机会点

**流程：**
```
调用 vibeflow-deepresearch
  → Agent 1: 竞品发现
  → Agent 2/3/4 并行: 技术栈分析、能力矩阵、护城河调研
  → 聚合输出报告
  → 归档至 docs/deepresearch/<领域>-<timestamp>.md
```

### 3. 确定方向

基于问题框定和 DeepResearch（如有），产出简短的**方向声明**：

```markdown
## Direction

**项目方向**: [1-2 句话描述要做什么]

**差异化焦点**: [从竞品分析中发现的差异化机会]

**灵感来源**: [竞品启发/市场洞察]
```

### 4. 进入 Plan

完成方向确定后，调用 `vibeflow-plan` 进入 Plan 阶段。

Plan 阶段负责：
- 复杂度/风险扫描
- 价值评估
- 模板选择
- 完整的需求和设计文档

## 硬规则

- Think 阶段保持轻量，只做灵感寻找和方向确定
- 其他分析工作留给 Plan 阶段
