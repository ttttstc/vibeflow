---
name: vibeflow-spark
description: "Spark 阶段 — 灵感迸发。将灵感、想法、价值和方向彻底想清楚，通过价值评估后自动进入 Requirements。"
---

# Spark — 灵感迸发

合并原 Think + Plan 阶段，一次性完成问题探索、方向确定和价值评估。

**启动输入：** 用户的功能需求描述
**启动宣告：** "正在使用 vibeflow-spark — 灵感迸发阶段。"

---

## Spark 流程

### 1. 需求理解

**输入：** 用户的功能需求描述

**如果用户没有提供有效信息：** 通过提问澄清：
- 要解决什么问题？
- 目标用户是谁？
- 核心场景是什么？

### 2. DeepResearch 评估（按需）

评估是否需要深度调研：

| 维度 | 问题 | 结果 |
|------|------|------|
| 话题熟悉度 | 用户对领域是否熟悉？ | 不熟悉 → 推荐 DR |
| 需求规模 | 是新领域还是增量？ | 新领域 → 推荐 DR |
| 现有情报 | 是否有相关报告？ | 无 → 推荐 DR |

**推荐 DR 时：**
```
📊 DeepResearch 推荐评估：
- 话题熟悉度: ...
- 需求规模: ...
- 现有情报: ...
- 推荐结论: [强烈推荐/建议/可跳过]

[推荐] 建议运行 DeepResearch...
```

Skill: vibeflow-deepresearch（如评估通过）

### 3. 问题框定 + 确定方向

基于需求理解和 DeepResearch（如有）：

```markdown
## Direction

**项目方向**: [1-2 句话描述要做什么]

**差异化焦点**: [从竞品分析中发现的差异化机会]

**灵感来源**: [竞品启发/市场洞察]
```

### 4. 复杂度/风险扫描

```
**复杂度评估：**
- 项目类型: [工具/平台/应用/库/...]
- 预期规模: [小/中/大/企业级]
- 技术风险: [高/中/低]
- 主要风险点: [...]
```

### 5. CEO 价值评估（关卡）

Skill: vibeflow-plan-value-review

**核心问题：**
- 这个项目值得做吗？
- 市场规模和竞争格局如何？
- 产品-市场契合度有多强？

**价值决策：**

| 结论 | 决策 | 行动 |
|------|------|------|
| EXPANSION / SELECTIVE | 通过 | 进入 Requirements |
| HOLD | 通过+警示 | 进入 Requirements，记录风险 |
| REDUCTION | 条件通过 | 与用户确认缩减方案 |
| 拒绝 | 拒绝 | 项目终止 |

### 6. 产出 Spark 结果

先运行 `python scripts/get-vibeflow-paths.py --json` 确认当前工作包路径，然后生成：

```markdown
# Spark Result

**日期**: YYYY-MM-DD
**模式**: [EXPANSION / SELECTIVE / HOLD / REDUCTION / 拒绝]

## Summary
[要解决什么，为什么值得做]

## Direction
[来自步骤 3 的方向声明]

## 复杂度评估
[来自步骤 4 的评估]

## 价值评估结论
[来自价值评估的核心结论]

## 决策
**是否进入 Requirements**: 是 / 否
```

### 7. 自动进入 Requirements

价值评估通过后：
- 自动进入 Requirements 阶段
- 无需用户额外确认

---

## 产出物

| 文件 | 内容 | 必须存在 |
|------|------|----------|
| `docs/changes/<change-id>/context.md` | Direction + 复杂度评估 + Proposal | ✅ |

---

## 记录到 phase-history

将结果追加到 `.vibeflow/phase-history.json`：

```json
{
  "timestamp": "...",
  "phase": "spark",
  "decision": "passed / rejected",
  "decision_mode": "...",
  "reason": "..."
}
```

---

## 集成

**入口：** 用户输入功能需求
**产出：** `docs/changes/<change-id>/context.md`
**Gate：** 价值评估拒绝 = 项目终止；通过 = 自动进入 Requirements
**链接到：** vibeflow-requirements（通过时）/ 项目终止（拒绝时）
