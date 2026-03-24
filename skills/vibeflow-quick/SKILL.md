---
name: vibeflow-quick
description: Quick Mode for VibeFlow. Use when the work is small, bounded, low-risk, and easy to verify or roll back.
---

# VibeFlow Quick Mode

Quick Mode 是“小改动快速交付模式”，不是“低质量模式”。

它会：
- 压缩前置分析
- 保留最小设计和任务清单
- 保留 Review 和 Test
- 在风险超出边界时，强制升级到 Full Mode

## 适用场景

适合：
- bug fix / hot fix
- 小范围现有功能修正
- 配置更新
- 文档、测试、脚手架修补
- 小型依赖升级，且无重大 API 变化

不适合：
- 新功能开发
- 架构调整
- 多服务或多数据库变更
- UI 方案需要重新设计
- 权限、安全、支付、认证、数据迁移
- 范围不明确、回滚不明确

如果不确定，进入 Full Mode。

## Quick Mode 最小契约

Quick Mode 在进入 Build 之前，必须同时满足：

1. `.vibeflow/state.json`
   - `mode = "quick"`
   - `checkpoints.quick_ready = true`
   - `quick_meta.decision = "approved"`

2. `quick_meta` 至少写清：
   - `category`
   - `scope`
   - `touchpoints`
   - `validation_plan`
   - `rollback_plan`
   - `risk_flags`
   - `promote_to_full_if`

3. 最小产物存在：
   - `docs/changes/<change-id>/design.md`
   - `docs/changes/<change-id>/tasks.md`

## Quick Mode 流程

```text
Quick Assessment
  -> Minimal Design
  -> Build
  -> Review
  -> Test
  -> Ship? / Reflect?
```

## 第一步：快速准入评估

先运行：

```bash
python scripts/get-vibeflow-paths.py --json
```

然后把这次改动压缩成一组最小结论：

- 这次属于什么类型：`bugfix / small-change / config / docs / tests / dependency`
- 范围有多大
- 会碰到哪些文件或模块
- 怎么验证
- 怎么回滚
- 有哪些风险标记

风险标记里，只要出现下面任意一类，就不应该继续走 Quick：

- `core-logic`
- `payment`
- `auth`
- `data`
- `external-api`
- `security`
- `multi-service`
- `multi-database`
- `ui-redesign`
- `migration`
- `new-feature`
- `architecture`

## 第二步：写入 Quick 状态

在 `.vibeflow/state.json` 里补齐 `quick_meta`，推荐结构：

```json
{
  "mode": "quick",
  "quick_meta": {
    "decision": "approved",
    "category": "bugfix",
    "scope": "Fix a small bounded issue in one module.",
    "touchpoints": ["src/example.py"],
    "risk_flags": [],
    "validation_plan": "Run the targeted regression test.",
    "rollback_plan": "Revert the single quick-mode commit.",
    "promote_to_full_if": [
      "scope grows beyond a small bounded change",
      "risk touches auth, payment, security, or data migration",
      "work spans multiple services, databases, or ownership boundaries",
      "design decisions are no longer obvious"
    ]
  },
  "checkpoints": {
    "quick_ready": true
  }
}
```

如果 Quick 不合适，就把：

- `quick_meta.decision = "rejected"`
- `quick_meta.rejected_reasons = [...]`

此时路由会停留在 `quick` 阶段，并提示升级到 Full Mode。

## 第三步：最小设计

写：

- `docs/changes/<change-id>/design.md`
- `docs/changes/<change-id>/tasks.md`

`design.md` 至少写清：
- 这次改什么
- 改到哪里
- 怎么验证
- 怎么回滚

`tasks.md` 至少写清：
- 实现步骤
- 验证步骤
- 收尾步骤

## 第四步：进入 Build

Quick Mode 不再手工硬写一堆旧状态文件。

进入 Build 前，优先使用现有脚本和既有约定：

- `feature-list.json` 继续作为 Build 的事实来源
- `.vibeflow/work-config.json` 继续由脚本生成
- `docs/changes/<change-id>/design.md` 和 `tasks.md` 作为 Quick 输入

Quick 就绪后，路由会直接进入：

```text
build-work -> review -> test-system -> ship? -> reflect?
```

## 升级到 Full Mode

如果在 Quick 过程中发现复杂度超出预期，不要硬撑。

直接执行：

```bash
python scripts/promote-vibeflow-quick.py --reason "Scope is no longer safe for Quick Mode."
```

这个脚本会：
- 把 `mode` 改成 `full`
- 清掉 `quick_ready`
- 保留现有 `design.md` 作为草稿
- 把路由切回 Full Mode 的最早缺失阶段

通常会回到：
- `think`
- 或 `plan / requirements / design`

具体取决于哪些 Full 产物还没补齐。

## 硬规则

1. Quick 只适合小范围、低风险、可快速回滚的工作。
2. `design.md` 和 `tasks.md` 不能省。
3. Review 和 Test 不能省。
4. 只要风险碰到核心链路，必须升级到 Full。
5. 所有结论必须写进文件，不留在聊天记忆里。
