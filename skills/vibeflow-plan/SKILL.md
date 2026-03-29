---
name: vibeflow-plan
description: "Plan 阶段 — 承接 Think 的详细分析，进行复杂度评估、模板选择、价值判断，通过后进入 requirements 和 design 阶段"
---

# Plan — Think 简化后的详细分析阶段

Think 阶段只做"寻找灵感、确定方向"，Plan 阶段承接所有详细分析工作。

**启动宣告：** "正在使用 vibeflow-plan 运行 Plan 阶段——复杂度分析、模板选择、价值评估。"

---

## Plan 流程

### 1. 复杂度/风险扫描

基于 Think 阶段的方向声明，进行详细的复杂度评估：

```
**复杂度评估：**
- 项目类型: [工具/平台/应用/库/...]
- 预期规模: [小/中/大/企业级]
- 技术风险: [高/中/低]
- 主要风险点:
  - [...]
```

### 2. 模板选择

根据复杂度评估，从 `templates/` 中选择模板：

| 模板 | 适用场景 |
|------|----------|
| `prototype` | 快速验证、减少关卡、速度优于严格性 |
| `web-standard` | UI密集型产品或通用全栈应用 |
| `api-standard` | 后端或集成优先系统，不需要大量UI工作 |
| `enterprise` | 严格审查、可审计性和更高的质量阈值 |

### 3. 价值判断（唯一关卡）

以 CEO/Founder 视角评估商业价值：

Skill: vibeflow-plan-value-review

**核心问题：**
- 这个项目**值得做**吗？
- 市场规模和竞争格局如何？
- 产品-市场契合度有多强？
- 单位经济学是否成立？
- 战略价值 vs 执行成本的权衡？

**注意：** eng 和 design review 在 design 阶段末尾执行（详情见 vibeflow-design）。

### 4. 产出 context.md

先运行 `python scripts/get-vibeflow-paths.py --json` 确认当前工作包路径，然后编写 `docs/changes/<change-id>/context.md`：

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

## Recommended Template
[prototype | web-standard | api-standard | enterprise]
Reason: [...]
```

### 5. 价值决策 & 产出 proposal.md

将价值审查结论收敛到 `docs/changes/<change-id>/proposal.md`：

```markdown
# Proposal

**日期**：YYYY-MM-DD
**审查分支**：[branch-name]
**审查模式**：[EXPANSION / SELECTIVE / HOLD / REDUCTION]

## Summary
[这次工作包要解决什么，为什么值得做]

## 价值评估结论

[来自 vibeflow-plan-value-review 的核心结论]

## 决策

**是否进入 requirements**：是 / 否

**理由**：
- [支持的理由]
- [风险/担忧]
```

**价值决策判断：**

| vibeflow-plan-value-review 结论 | VibeFlow 决策 | 行动 |
|-----------------------|---------------|------|
| EXPANSION / SELECTIVE | **通过** | 进入 requirements |
| HOLD | **通过+警示** | 进入 requirements，记录风险 |
| REDUCTION | **条件通过** | 与用户确认缩减方案后再继续 |
| 拒绝 | **拒绝** | 项目终止 |

### 6. 创建 workflow.yaml

价值评审通过后：

- 创建 `.vibeflow/`
- 将 `templates/<template>.yaml` 复制到 `.vibeflow/workflow.yaml`
- 将 `created_at` 设置为当前日期

---

## 产出物

| 文件 | 内容 | 必须存在才进入 requirements |
|------|------|--------------------------|
| `docs/changes/<change-id>/context.md` | 完整上下文 + 复杂度 + 模板 | ✅ |
| `docs/changes/<change-id>/proposal.md` | 价值评估结论 + 决策 | ✅ |
| `.vibeflow/workflow.yaml` | 选定的模板配置 | ✅ |

---

## 记录到 phase-history

将评估结果追加到 `.vibeflow/phase-history.json`：

```json
{
  "timestamp": "...",
  "phase": "plan",
  "complexity": "...",
  "template": "...",
  "value_decision": "passed / rejected",
  "value_review_mode": "...",
  "reason": "..."
}
```

---

## 集成

**调用者：** vibeflow-router（plan 阶段）
**依赖：** Think 阶段的 Direction 声明、`docs/deepresearch/` 下相关报告（如有）
**产出：**
- `docs/changes/<change-id>/context.md`
- `docs/changes/<change-id>/proposal.md`
- `.vibeflow/workflow.yaml`
**Gate：** 价值审查失败 = 项目终止；价值评审通过 = 进入 requirements
**链接到：** vibeflow-requirements（通过时）/ 项目终止（拒绝时）
