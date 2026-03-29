---
name: vibeflow-think
description: 在VibeFlow项目中用于Think阶段，定义问题、边界、机会扫描和选择工作流程模板。
---

## 目标

产生阶段1 MVP产物：

- `docs/changes/<change-id>/context.md`
- 模板确认后的`.vibeflow/workflow.yaml`

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

### 1. 问题框定

推动对话朝向：

- 要解决的实际问题
- 用户是谁
- 明确不在范围内的内容
- 最小有用的第一个版本

### 2. DeepResearch（可选）

在进入机会扫描前，用户可选择运行深度竞品调研：

Skill: vibeflow-deepresearch

**何时使用：**
- 进入不熟悉领域时
- 需要系统性了解同领域竞品
- 需要获取技术选型参考
- 需要寻找差异化机会点

**流程：**
```
调用 vibeflow-deepresearch
  → Agent 1: 竞品发现
  → Agent 2/3/4 并行: 技术栈分析、能力矩阵、护城河调研
  → 聚合输出报告
  → 归档至 docs/deepresearch/<领域>-<timestamp>.md
```

**与机会扫描的关系：**
DeepResearch 报告为机会扫描提供竞品情报输入，帮助识别差异化机会。

**如用户跳过此步骤**，直接进入机会扫描。

### 3. 复杂度和风险扫描

陈述：

- 项目类型
- 预期规模
- 主要风险

### 4. 机会扫描

产生：

- 一个10倍版本
- 最小可行版本
- 一个大约30分钟能完成的快速增值

### 5. 模板推荐

从`templates/`中选择一个静态模板：

| 模板 | 使用场景 |
|------|----------|
| `prototype` | 快速验证、减少关卡、速度优于严格性 |
| `web-standard` | UI密集型产品或通用全栈应用 |
| `api-standard` | 后端或集成优先系统，不需要大量UI工作 |
| `enterprise` | 严格审查、可审计性和更高的质量阈值 |

### 6. 编写 think 输出

先运行 `python scripts/get-vibeflow-paths.py --json` 确认当前工作包路径，然后使用完全相同的结构编写 `docs/changes/<change-id>/context.md`：

```markdown
# Think Output

## Problem Statement
[1-3 sentences]

## Boundaries
### In Scope
- [...]

### Out of Scope
- [...]

## User Profile
- Primary user: [...]
- Usage scenario: [...]
- Success criteria: [...]

## Complexity Assessment
- Project type: [...]
- Scale: [...]
- Key risks:
  - [...]

## Opportunity Scan
- 10x version: [...]
- Minimum viable version: [...]
- Quick value add: [...]

## Recommended Template
[prototype | web-standard | api-standard | enterprise]
Reason: [...]
```

### 7. 确认并创建工作流程

编写 `context.md` 后：

- 如果用户尚未明确选择，请请求模板确认
- 创建`.vibeflow/`
- 将`templates/<template>.yaml`复制到`.vibeflow/workflow.yaml`
- 将`created_at`设置为当前日期

## 硬规则

- 不要动态创建新的工作流程模式。
- 不要发明新的模板。
- 保持此技能薄而聚焦于编排。
- 如果仓库方向与当前推荐的模板明显冲突，在编写`workflow.yaml`之前解释冲突。
