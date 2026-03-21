---
name: vibeflow-think
description: 在VibeFlow项目中用于Think阶段，定义问题、边界、机会扫描和选择工作流程模板。
---

## 目标

产生阶段1 MVP产物：

- `.vibeflow/think-output.md`
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

## Think流程

### 1. 问题框定

推动对话朝向：

- 要解决的实际问题
- 用户是谁
- 明确不在范围内的内容
- 最小有用的第一个版本

### 2. 复杂度和风险扫描

陈述：

- 项目类型
- 预期规模
- 主要风险

### 3. 机会扫描

产生：

- 一个10倍版本
- 最小可行版本
- 一个大约30分钟能完成的快速增值

### 4. 模板推荐

从`templates/`中选择一个静态模板：

| 模板 | 使用场景 |
|------|----------|
| `prototype` | 快速验证、减少关卡、速度优于严格性 |
| `web-standard` | UI密集型产品或通用全栈应用 |
| `api-standard` | 后端或集成优先系统，不需要大量UI工作 |
| `enterprise` | 严格审查、可审计性和更高的质量阈值 |

### 5. 编写think输出

使用完全相同的结构编写`.vibeflow/think-output.md`：

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

### 6. 确认并创建工作流程

编写`think-output.md`后：

- 如果用户尚未明确选择，请请求模板确认
- 创建`.vibeflow/`
- 将`templates/<template>.yaml`复制到`.vibeflow/workflow.yaml`
- 将`created_at`设置为当前日期

## 硬规则

- 不要动态创建新的工作流程模式。
- 不要发明新的模板。
- 保持此技能薄而聚焦于编排。
- 如果仓库方向与当前推荐的模板明显冲突，在编写`workflow.yaml`之前解释冲突。
