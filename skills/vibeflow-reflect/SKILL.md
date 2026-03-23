---
name: vibeflow-reflect
description: "发布后使用 — 创建回顾、总结经验教训、生成下一迭代输入"
---

# 发布后回顾

在发布完成后关闭循环。总结本次交付的经验，识别改进机会，为下一迭代提供输入。

**启动宣告：** "正在使用 vibeflow-reflect 进行发布后回顾。"

## 前置条件

- 发布已完成（RELEASE_NOTES.md 已更新，可选 tag/PR 已创建）
- `.vibeflow/workflow.yaml` 中 `reflect.required` 为 true（某些模板如 prototype 可能标记为 false）

**如 reflect 不是必需的**：宣布"回顾为可选 — 跳过"，将阶段标记为完成。

## 检查清单

### 1. 收集数据

读取以下工件以收集回顾数据：

- `.vibeflow/logs/session-log.md` — 逐会话进度和遇到的问题
- `feature-list.json` — 功能总数、废弃功能、优先级分布
- `RELEASE_NOTES.md` — 实际交付内容
- `docs/changes/<change-id>/verification/system-test.md` — 测试结果和缺陷摘要
- `docs/changes/<change-id>/verification/qa.md`（如存在）— QA 发现
- `docs/changes/<change-id>/verification/review.md` — 全局审查发现
- `docs/changes/<change-id>/proposal.md` — Plan 阶段完成标记（含 scope decision）
- `docs/changes/<change-id>/design-review.md` — 工程审查和设计审查发现
- `docs/changes/<change-id>/context.md` — 初始问题定义
- `git log` — 提交历史和时间线

### 2. 分析

#### 2a. 交付分析

- **计划 vs 实际**：context.md 定义的范围 vs RELEASE_NOTES.md 实际交付
- **功能完成率**：活跃功能中 passing 的比例
- **废弃功能**：哪些功能被废弃？为什么？
- **范围变化**：过程中添加或移除了哪些需求？

#### 2b. 质量分析

- **缺陷密度**：ST 和 QA 发现的缺陷数量 vs 功能数量
- **缺陷分布**：按严重度、按功能、按类型（前端/后端/集成）
- **返工率**：有多少功能在审查中被打回重做？
- **测试覆盖率趋势**：最终覆盖率 vs 门禁阈值

#### 2c. 流程分析

- **瓶颈**：哪个阶段花费时间最多？
- **阻塞**：什么原因导致了阻塞？
- **工具问题**：哪些工具或配置造成了摩擦？
- **文档质量**：SRS、设计、UCD 在实现中是否足够清晰？

### 3. 经验总结

从分析中提取：

#### 什么做得好
- [具体的成功实践和决策]

#### 什么可以改进
- [具体的问题和改进建议]

#### 关键教训
- [跨项目可复用的洞察]

### 4. 下一迭代输入

基于回顾识别下一步：

#### 4a. 已知改进
从 ST 报告的建议、QA 报告的推迟项、审查报告的次要问题中收集。

#### 4b. 新机会
从 context.md 的"10x 版本"和 design-review.md 的扩展建议中回顾。

#### 4c. 技术债
从代码审查和测试过程中识别的技术债。

### 5. 生成回顾文档

保存到 `.vibeflow/logs/retro-YYYY-MM-DD.md`：

```markdown
# 回顾 — [项目名] vX.Y.Z

**日期**：YYYY-MM-DD

## 交付摘要
- 计划功能：X
- 实际交付：Y（Z 个废弃）
- 范围变化：[描述]

## 质量摘要
- 测试覆盖率：XX% 行 / XX% 分支 / XX% 变异
- ST 缺陷：A 严重 / B 重要 / C 次要
- QA 发现：D（如适用）
- 返工功能数：E

## 什么做得好
- [项 1]
- [项 2]

## 什么可以改进
- [项 1]
- [项 2]

## 关键教训
- [教训 1]
- [教训 2]

## 下一迭代建议
### 改进项
- [来自 ST/QA/Review 的推迟项]

### 新机会
- [来自 Think 和 Plan Review]

### 技术债
- [识别的技术债]
```

### 6. 生成增量请求（可选）

如果回顾中识别了明确的下一迭代工作：

通过 `AskUserQuestion` 询问用户是否要启动下一迭代。如是：

生成 `.vibeflow/increments/requests/<increment-id>.json`，并将其加入 `.vibeflow/increments/queue.json`：

```json
{
  "reason": "回顾中识别的改进和新功能",
  "scope": "来自回顾的简要范围描述",
  "items": [
    {"type": "new", "description": "新功能描述"},
    {"type": "improvement", "description": "改进描述"},
    {"type": "tech_debt", "description": "技术债描述"}
  ],
  "source": "retro-YYYY-MM-DD"
}
```

这将触发 router 在下次会话中进入增量流程。

### 7. 最终更新

- 更新 `.vibeflow/logs/session-log.md` — 记录回顾会话
- Git 提交回顾工件

## 集成

**调用者：** vibeflow-router 或 vibeflow-ship
**依赖：** 发布完成
**产出：** `.vibeflow/logs/retro-YYYY-MM-DD.md`，可选 `.vibeflow/increments/requests/<increment-id>.json`
**链接到：** done（项目完成）或通过 `.vibeflow/increments/queue.json` 触发增量流程
