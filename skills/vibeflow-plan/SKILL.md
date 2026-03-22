---
name: vibeflow-plan
description: "Plan 阶段 — 先进行 CEO 视角的商业价值评估，再执行层面的范围审查"
---

# Plan — 价值评估 + 范围审查

在 Think 阶段完成后，以 CEO/Founder 视角评估商业价值，再以执行层面审查范围和路径。**Fail-fast：不值得做的事尽早终止，不浪费工程资源。**

**启动宣告：** "正在使用 vibeflow-plan 运行 Plan 阶段——两步审查：价值判断 → 范围确认。"

## 核心原则

### 第一关：价值判断（/plan-ceo-review）

在投入任何执行层工作之前，必须先回答：
- 这个项目**值得做**吗？
- 市场规模和竞争格局如何？
- 产品-市场契合度有多强？
- 单位经济学是否成立？
- 战略价值 vs 执行成本的权衡？

### 第二关：范围审查（执行层面）

价值通过后，审查：
- 问题定义是否抓住了根因？
- 范围是否匹配 MVP？
- 假设是否被验证？
- 风险是否被识别和排序？

## 审查模式

从 `.vibeflow/workflow.yaml` 读取 `plan.mode`：

| 模式 | 行为 | 典型模板 |
|------|------|---------|
| `reduced` | 快速检查，仅标记明显问题 | prototype |
| `hold` | 标准审查，质疑假设后推荐继续或调整 | web-standard, api-standard |
| `expansion` | 深度审查，主动探索扩大范围的机会 | enterprise |

## 两步执行流程

---

### Step 1：价值判断

#### 1.1 调用 /plan-ceo-review

使用 `Skill` 工具调用全局 `/plan-ceo-review` Skill：

```
Skill: plan-ceo-review
args: [当前 branch 名]
```

**注意**：`/plan-ceo-review` 是你全局配置的独立 Skill，不属于 VibeFlow 仓库。

#### 1.2 提取价值审查结论

从 `/plan-ceo-review` 的输出中提取关键结论，保存到 `.vibeflow/plan-value-review.md`：

```markdown
# Plan Value Review — 商业价值评估

**日期**：YYYY-MM-DD
**审查分支**：[branch-name]
**审查模式**：[EXPANSION / SELECTIVE / HOLD / REDUCTION]

## 价值评估结论

[来自 /plan-ceo-review 的核心结论]

## 决策

**是否进入 scope 审查**：是 / 否

**理由**：
- [支持的理由]
- [风险/担忧]

## 关键洞察

[来自 CEO review 的战略洞察]

## 后续行动

- [如果通过：继续 Step 2 范围审查]
- [如果拒绝：项目终止，记录原因]
```

#### 1.3 价值决策判断

| /plan-ceo-review 结论 | VibeFlow 决策 | 行动 |
|-----------------------|---------------|------|
| EXPANSION / SELECTIVE（推荐做） | **通过** | 继续 Step 2 范围审查 |
| HOLD（可以但有风险） | **通过+警示** | 继续 Step 2，记录风险 |
| REDUCTION（缩减范围后可行） | **条件通过** | 与用户确认缩减方案后再继续 |
| 拒绝（不值得做） | **拒绝** | 项目终止，不进入 Step 2 |

#### 1.4 用户确认（价值关）

通过 `AskUserQuestion` 展示价值评估结论：
- 价值评估结论是否接受
- 是否继续进入范围审查

**如果拒绝**：标记项目为 `terminated` 状态（更新 `phase-history.json`），阶段结束。

---

### Step 2：范围审查（仅在 Step 1 通过后执行）

#### 2.1 重新理解问题

不要假设 think-output.md 的问题定义是最优的：

- 问题是否抓住了**根因**而非症状？
- 是否有更深层的问题值得解决？
- 用户真正需要的是什么 vs 他们说想要的是什么？

#### 2.2 质疑范围

| 检查 | 问题 |
|------|------|
| **范围过大** | 是否包含了 MVP 不需要的功能？哪些可以推迟？ |
| **范围过小** | 是否遗漏了对用户体验至关重要的功能？ |
| **假设风险** | think-output.md 中的假设哪些最可能是错的？ |
| **技术可行性** | 选定方案的最大技术风险是什么？ |

#### 2.3 10 星产品思考

以 think-output.md 的"10x 版本"为起点：

- 如果没有任何约束，这个产品的完美版本是什么样的？
- 从完美版本中，哪些元素可以用最小成本纳入当前范围？
- 有没有一个改变能让产品价值翻倍？

#### 2.4 风险评估

识别并排序风险：

| 风险 | 可能性 | 影响 | 缓解 |
|------|--------|------|------|
| [技术风险] | 高/中/低 | 高/中/低 | [策略] |
| [市场风险] | ... | ... | ... |
| [执行风险] | ... | ... | ... |

#### 2.5 范围决策

产出三选一的决策：

**扩展（Expand）**：当发现当前范围遗漏了高价值、低成本的功能时。

**保持（Hold）**：当前范围合理。

**缩减（Reduce）**：当范围过大或风险过高时。

#### 2.6 生成范围审查记录

保存到 `.vibeflow/plan-review.md`：

```markdown
# Plan Scope Review — 执行范围审查

**日期**：YYYY-MM-DD
**审查模式**：[reduced/hold/expansion]
**价值审查结论**：[通过/拒绝/条件通过 — 附理由]

## 问题重新审视
[对问题定义的质疑和确认]

## 范围审查
[对当前范围的分析]

## 10 星思考
[理想产品的关键洞察]

## 风险评估
[排序的风险表]

## 决策
**范围决策**：[Expand / Hold / Reduce]
**理由**：[简要说明]
**调整建议**：
- [具体建议 1]
- [具体建议 2]

## 是否继续到需求
[是 / 否 — 需要先解决什么]
```

#### 2.7 用户确认（范围关）

通过 `AskUserQuestion` 展示范围审查结论：
- 范围决策是否接受
- 调整建议是否采纳
- 是否继续进入 requirements

---

## 产出物

| 文件 | 内容 | 必须存在才进入 requirements |
|------|------|--------------------------|
| `.vibeflow/plan-value-review.md` | CEO 价值评估结论 | ✅ |
| `.vibeflow/plan-review.md` | 范围审查结论 | ✅ |

两个文件都存在，才算 Plan 阶段完成。

## 记录到 phase-history

将评估结果追加到 `.vibeflow/phase-history.json`：

```json
{
  "timestamp": "...",
  "phase": "plan",
  "value_decision": "passed / rejected",
  "value_review_mode": "...",
  "scope_decision": "Expand / Hold / Reduce",
  "reason": "..."
}
```

## 红线

| 合理化借口 | 正确响应 |
|---|---|
| "Think 阶段已经评估过价值了" | Think 探索问题，Plan 的价值判断评估商业可行性——维度不同 |
| "时间紧迫，跳过价值评估" | 错误方向比速度慢更昂贵——fail-fast 是加速，不是拖延 |
| "这个想法显然有价值" | 最危险的假设是你不知道自己在假设的那些——价值需要被验证，不是被假定 |
| "价值过了直接做" | 价值判断不等于范围合理——两者都需要独立审查 |
| "需求完成后再说" | 需求完成后沉没成本更高——在需求前做价值把关 |

## 集成

**调用者：** vibeflow-router（plan 阶段）
**依赖：** `.vibeflow/think-output.md`、`.vibeflow/workflow.yaml`
**产出：**
- `.vibeflow/plan-value-review.md`（价值审查）
- `.vibeflow/plan-review.md`（范围审查）
**Gate：** 价值审查失败 = 项目终止；两者都通过 = 进入 requirements
**链接到：** vibeflow-requirements（通过时）/ 项目终止（拒绝时）
