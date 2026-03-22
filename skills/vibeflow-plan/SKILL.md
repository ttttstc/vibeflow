---
name: vibeflow-plan
description: "Plan 阶段 — CEO/Founder 视角的价值评估通过后，进入 requirements 和 design 阶段（eng/design review 在 design 阶段末尾执行）"
---

# Plan — 价值评估（唯一关卡）

在 Think 阶段完成后，以 CEO/Founder 视角评估商业价值。**Fail-fast：不值得做的事尽早终止，不浪费工程资源。**

eng 和 design review 在 design 阶段末尾执行（详情见 vibeflow-design）。

**启动宣告：** "正在使用 vibeflow-plan 运行 Plan 阶段——价值评估（唯一关卡）。eng/design review 在 design 阶段末尾执行。"

## 核心原则

### 第一关：价值判断（CEO 视角）

在投入任何执行层工作之前，必须先回答：
- 这个项目**值得做**吗？
- 市场规模和竞争格局如何？
- 产品-市场契合度有多强？
- 单位经济学是否成立？
- 战略价值 vs 执行成本的权衡？

**注意：** eng 和 design review 不在 plan 阶段执行。设计文档存在之前，这些 review 只能评审抽象方向而非具体实现。因此 plan 阶段只做价值判断，eng/design review 移到 design 阶段末尾（有具体 design doc 可审时再执行）。

---

## Step 1：价值判断

### 1.1 调用 vibeflow-plan-value-review

使用 `Skill` 工具调用：

```
Skill: vibeflow-plan-value-review
```

---

### 1.2 提取价值审查结论

保存到 `.vibeflow/plan-value-review.md`：

```markdown
# Plan Value Review — 商业价值评估

**日期**：YYYY-MM-DD
**审查分支**：[branch-name]
**审查模式**：[EXPANSION / SELECTIVE / HOLD / REDUCTION]

## 价值评估结论

[来自 vibeflow-plan-value-review 的核心结论]

## 决策

**是否进入 requirements**：是 / 否

**理由**：
- [支持的理由]
- [风险/担忧]

## 后续行动

- [如果通过：进入 requirements 和 design 阶段（eng/design review 在 design 末尾执行）]
- [如果拒绝：项目终止，记录原因]
```

### 1.3 价值决策判断

| vibeflow-plan-value-review 结论 | VibeFlow 决策 | 行动 |
|-----------------------|---------------|------|
| EXPANSION / SELECTIVE（推荐做） | **通过** | 进入 requirements |
| HOLD（可以但有风险） | **通过+警示** | 进入 requirements，记录风险 |
| REDUCTION（缩减范围后可行） | **条件通过** | 与用户确认缩减方案后再继续 |
| 拒绝（不值得做） | **拒绝** | 项目终止，不进入 requirements |

### 1.4 用户确认（价值关）

通过 `AskUserQuestion` 展示价值评估结论：
- 价值评估结论是否接受
- 是否继续进入 requirements

**如果拒绝**：标记项目为 `terminated` 状态（更新 `phase-history.json`），阶段结束。

### 1.5 写入 plan.md 完成标记

价值评审通过后，写入 `.vibeflow/plan.md`：

```markdown
# Plan 完成

**日期**：YYYY-MM-DD
**价值审查**：通过（模式：XXX）
**进入 requirements**：是

**说明**：eng/design review 在 design 阶段末尾执行（见 vibeflow-design）
```

此文件的存在即标记 Plan 阶段完成，触发 phase detector 进入 requirements。

---

## 产出物

| 文件 | 内容 | 必须存在才进入 requirements |
|------|------|--------------------------|
| `.vibeflow/plan-value-review.md` | CEO 价值评估结论 | ✅ |
| `.vibeflow/plan.md` | Plan 阶段完成标记（价值评审通过后写入） | ✅ |

## 记录到 phase-history

将评估结果追加到 `.vibeflow/phase-history.json`：

```json
{
  "timestamp": "...",
  "phase": "plan",
  "value_decision": "passed / rejected",
  "value_review_mode": "...",
  "reason": "..."
}
```

---

## 红线

| 合理化借口 | 正确响应 |
|---|---|
| "Think 阶段已经评估过价值了" | Think 探索问题，Plan 的价值判断评估商业可行性——维度不同 |
| "时间紧迫，跳过价值评估" | 错误方向比速度慢更昂贵——fail-fast 是加速，不是拖延 |
| "这个想法显然有价值" | 最危险的假设是你不知道自己在假设的那些——价值需要被验证，不是被假定 |
| "eng/design review 应该在 plan 阶段" | 在无具体设计稿时这些 review 只能评审抽象方向，在 design 末尾执行才能审具体实现 |

---

## 集成

**调用者：** vibeflow-router（plan 阶段）
**依赖：** `.vibeflow/think-output.md`、`.vibeflow/workflow.yaml`
**产出：**
- `.vibeflow/plan-value-review.md`（CEO 价值审查）
- `.vibeflow/plan.md`（阶段完成标记，价值评审通过后写入）
**Gate：** 价值审查失败 = 项目终止；价值评审通过 = 进入 requirements
**链接到：** vibeflow-requirements（通过时）/ 项目终止（拒绝时）
