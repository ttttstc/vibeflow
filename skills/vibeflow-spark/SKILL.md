---
name: vibeflow-spark
description: "Spark 阶段 — 灵感迸发。默认先用 office-hours 做问题框定，把方向、边界、验收标准和约束想清楚；完成总结并经用户确认后再进入 Design。"
---

# Spark — 灵感迸发

合并原 Think + Plan，并吸收原 requirements 的“边界契约”职责，一次性完成问题探索、方向确定、验收标准和价值评估。

**启动输入：** 用户的功能需求描述
**启动宣告：** "正在使用 vibeflow-spark — 灵感迸发阶段。"

---

## Spark 流程

### 1. 问题框定（默认进入 Office Hours）

**输入：** 用户的功能需求描述

**如果用户没有提供有效信息：** 通过提问澄清：
- 要解决什么问题？
- 目标用户是谁？
- 核心场景是什么？

默认调用：

```
Skill: vibeflow-office-hours
```

要求：
- 先完成问题框定和范围梳理
- 在 scope 收敛时，必须让用户明确确认本次验收标准
- Office Hours 的结论要合并回当前 change 的 `brief.md`，而不是停留在独立 brainstorming 语境里

### 2. 复杂度/风险扫描

先做复杂度扫描，形成是否值得深度调研的判断依据：

```
**复杂度评估：**
- 项目类型: [工具/平台/应用/库/...]
- 预期规模: [小/中/大/企业级]
- 技术风险: [高/中/低]
- 主要风险点: [...]
```

### 3. DeepResearch 选择（用户决定）

复杂度扫描后，必须让用户决定是否进入深度调研。

评估维度：

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

### 4. 问题框定 + 确定方向

基于 Office Hours、复杂度扫描和 DeepResearch（如有）：

```markdown
## Direction

**项目方向**: [1-2 句话描述要做什么]

**差异化焦点**: [从竞品分析中发现的差异化机会]

**灵感来源**: [竞品启发/市场洞察]
```

### 4.1 圆桌会议（可选）

**提示用户：**
```
📋 在完成调研结论后，是否需要通过圆桌会议从多角色视角审视当前方向？

圆桌参与角色：产品经理、架构师、用户代表、体验代表、竞争力代表
预计耗时：3-5 分钟

选项：
- 启用圆桌会议
- 跳过，直接进入 CEO 价值评估
```

**用户选择启用时：**
Skill: `vibeflow-roundtable`

圆桌结论将追加至 `brief.md`，用户确认后继续。

**用户选择跳过时：**
直接继续步骤 5。

### 5. CEO 价值评估（关卡）

Skill: vibeflow-plan-value-review

**核心问题：**
- 这个项目值得做吗？
- 市场规模和竞争格局如何？
- 产品-市场契合度有多强？

**价值决策：**

| 结论 | 决策 | 行动 |
|------|------|------|
| EXPANSION / SELECTIVE | 通过 | 进入 Spark 总结确认 |
| HOLD | 通过+警示 | 进入 Spark 总结确认，并记录风险 |
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

## Scope Summary
[当前方向、范围边界、验收标准确认结果]

## Direction
[来自步骤 4 的方向声明]

## Roundtable 结论
[来自步骤 4.1 的圆桌结论，如有；如跳过则标注"未启用"]

## 复杂度评估
[来自步骤 2 的评估]

## 价值评估结论
[来自价值评估的核心结论]

## 决策
**是否进入 Design**: 是 / 否

## Scope And Acceptance
- Goals
- Non-goals
- Acceptance criteria
- Constraints
- Assumptions
- Open questions
```

### 7. Spark 总结确认

Spark 阶段完成后，必须向用户展示：
- 当前方向总结
- 范围边界
- 验收标准
- 是否已执行 DeepResearch
- 是否已执行 Roundtable
- CEO 价值评估结论

然后由用户明确确认：
- 是否接受本次方向与范围
- 是否进入 Design 阶段

**未确认前不得进入 Design。**

---

## 产出物

| 文件 | 内容 | 必须存在 |
|------|------|----------|
| `docs/changes/<change-id>/brief.md` | Goal + Scope + Constraints + Acceptance | ✅ |

---

## 记录到 phase-history

将结果追加到 `.vibeflow/state.json.phase_history`：

```json
{
  "timestamp": "...",
  "phase": "spark",
  "decision": "passed / rejected",
  "decision_mode": "...",
  "reason": "...",
  "roundtable_enabled": true,
  "roundtable_confirmed": true,
  "roundtable_confirmed_at": "..."
}
```

---

## 集成

**入口：** 用户输入功能需求
**产出：** `docs/changes/<change-id>/brief.md`
**Gate：** 价值评估拒绝 = 项目终止；通过后仍需完成 Spark 总结并获用户确认，才能进入 Design
**链接到：** vibeflow-design（通过时）/ 项目终止（拒绝时）
