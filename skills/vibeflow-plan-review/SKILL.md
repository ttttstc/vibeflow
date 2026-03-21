---
name: vibeflow-plan-review
description: 在Plan期间用于在规范编写之前运行执行范围审查。
---

# VibeFlow计划审查

在需求和设计继续编写之前，执行VibeFlow计划审查。

**开始时宣布：** "我正在使用vibeflow-plan-review skill来运行计划审查。"

## 目的

在编写需求和设计之前，验证：
- 问题框定是正确的
- 范围层级是适当的
- 主要风险已识别
- 推荐的路径是合理的

##何时运行

- Think阶段之后（vibeflow-think）
- Requirements阶段之前（vibeflow-requirements）
- 由`vibeflow`路由器调用

## 输入

- `VIBEFLOW-DESIGN.md`（如果存在）
- `.vibeflow/think-output.md` — Think阶段输出
- `.vibeflow/workflow.yaml` — 选择的模板配置（如果存在）

## 步骤1：加载审查上下文

### 1.1 阅读Think输出

从`.vibeflow/think-output.md`：
- 问题陈述
- 提出的解决方案
- 成功标准
- 初始范围评估

### 1.2 阅读工作流程配置

从`.vibeflow/workflow.yaml`：
- 选择的模板
- 阶段序列
- 启用的功能

### 1.3 阅读设计文档（如果存在）

从`VIBEFLOW-DESIGN.md`或`docs/plans/*-design.md`：
- 先前的设计工作
- 架构决策

## 步骤2：挑战问题框定

### 2.1 问题验证

审查问题陈述：
- [ ] 问题已清晰陈述
- [ ] 问题实际上是根本原因
- [ ] 问题值得解决
- [ ] 问题范围适当

### 2.2 解决方案验证

审查提出的解决方案：
- [ ] 解决方案解决根本原因
- [ ] 解决方案在技术上是可行的
- [ ] 解决方案具有成本效益
- [ ] 已考虑替代解决方案

### 2.3 成功标准验证

审查成功标准：
- [ ] 标准是可衡量的
- [ ] 标准是可实现的
- [ ] 标准验证问题已解决
- [ ] 标准没有遗漏重要结果

## 步骤3：范围层级审查

### 3.1 评估范围层级

根据问题和解决方案，推荐范围层级：

| 层级 | 特点 | 何时使用 |
|------|------|----------|
| **Prototype** | 快速验证、最少功能 | 探索性、学习 |
| **Web Standard** | 完整Web应用、无复杂集成 | 标准Web产品 |
| **API Standard** | 后端API、可能有多个客户端 | API优先产品 |
| **Enterprise** | 复杂集成、高可靠性 | 任务关键型 |

### 3.2 确认层级适当性

- [ ] 模板与范围复杂度匹配
- [ ] 工作流程步骤适合层级
- [ ] 质量关卡适合层级

### 3.3 记录层级决策

```markdown
## Scope Tier Recommendation

**Recommended tier**: [Tier name]
**Rationale**: Why this tier is appropriate
**Alternative considered**: [Tier name] — why not chosen
```

## 步骤4：风险评估

### 4.1 产品风险

| 风险 | 可能性 | 影响 | 缓解策略 |
|------|--------|------|----------|
| Risk 1 | High/Medium/Low | High/Medium/Low | Mitigation strategy |

### 4.2 技术风险

| 风险 | 可能性 | 影响 | 缓解策略 |
|------|--------|------|----------|
| Risk 1 | High/Medium/Low | High/Medium/Low | Mitigation strategy |

### 4.3 交付风险

| 风险 | 可能性 | 影响 | 缓解策略 |
|------|--------|------|----------|
| Risk 1 | High/Medium/Low | High/Medium/Low | Mitigation strategy |

## 步骤5：审查建议

### 5.1 继续进行需求

**推荐** — 问题框定正确，风险可管理

**有条件** — 带修改继续：
- [ ] Modification 1
- [ ] Modification 2

**不推荐** — 重大问题：
- [ ] Issue 1
- [ ] Issue 2

### 5.2 范围调整

如果需要范围调整：
```
## Scope Adjustments

**Expand**:
- [Item to add to scope]

**Reduce**:
- [Item to remove from scope]

**Defer**:
- [Item to defer to later iteration]
```

## 步骤6：记录审查

### 6.1 创建审查笔记

保存到`.vibeflow/plan-review.md`或`docs/plans/YYYY-MM-DD-plan-review.md`：

```markdown
# Plan Review — YYYY-MM-DD

## Summary
- **Review date**: YYYY-MM-DD
- **Think output**: `.vibeflow/think-output.md`
- **Workflow**: [template] — [stage sequence]

## Problem Framing
[Assessment of problem statement]

## Solution Validation
[Assessment of proposed solution]

## Scope Tier
**Recommended**: [Tier]
**Rationale**: [Why appropriate]

## Risk Assessment

### Product Risks
[Risks table]

### Technical Risks
[Risks table]

### Delivery Risks
[Risks table]

## Recommendations

**Decision**: Proceed | Conditional | Not Recommended

### Modifications (if conditional)
- [Modification 1]
- [Modification 2]

### Scope Adjustments (if any)
[Expand/Reduce/Defer items]

## Next Steps
- [ ] Proceed to Requirements (vibeflow-requirements)
- [ ] Address modifications before proceeding
```

### 6.2 保存审查笔记

将审查笔记写入适当位置。

## 检查表

完成计划审查之前：

- [ ] 问题框定已验证
- [ ] 解决方案方法已验证
- [ ] 成功标准已验证
- [ ] 范围层级已推荐
- [ ] 产品风险已识别
- [ ] 技术风险已识别
- [ ] 交付风险已识别
- [ ] 建议已记录
- [ ] 审查笔记已保存
- [ ] 决定：继续 / 有条件 / 不推荐

## 预期输出

| 输出 | 位置 | 目的 |
|------|------|------|
| Scope decision | Review notes | Expand / Hold / Reduce |
| Review notes | `.vibeflow/plan-review.md` or `docs/plans/` | 决定文档 |
| Risk assessment | Review notes | 风险意识 |
| Recommendation | Review notes | Go/No-go指导 |

## 集成

**由以下调用：** `vibeflow`路由器（Think之后，Requirements之前）
**需要：**
- Think输出在`.vibeflow/think-output.md`
- 工作流程配置在`.vibeflow/workflow.yaml`（如果存在）
- 设计文档（如果存在）
**产生：**
- 带范围决定的审查笔记
- 风险评估
- Go/No-go建议
**链接到：** `vibeflow-requirements`（如果批准）
