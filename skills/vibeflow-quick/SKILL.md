---
name: vibeflow-quick
description: Quick Mode for VibeFlow - fast development without formal design. Use when user runs /vibeflow-quick or selects Quick Mode.
---

# VibeFlow Quick Mode

快速开发模式：跳过完整的设计流程，直接进入构建。

## 何时使用 Quick Mode

当用户：
- 运行 `/vibeflow-quick`
- 在 `/vibeflow` 意图确认中选择"快速任务"

## Quick Mode Eligibility

**⚠️ 风险检查：在继续之前确认**

以下情况**适合** Quick Mode：
- [ ] Bug fix 或 hot fix
- [ ] 单文件或少数文件修改
- [ ] 配置文件更新
- [ ] CLI 工具添加
- [ ] 测试文件编写
- [ ] 文档更新
- [ ] 依赖版本升级（无重大 API 变更）

以下情况**不适合** Quick Mode，请使用 Full Mode（`/vibeflow`）：
- [ ] 新功能开发
- [ ] 架构变更
- [ ] 多服务/多数据库变更
- [ ] 需要 UI/UX 设计的工作
- [ ] 首次引入新框架/库
- [ ] 涉及重要系统的变更（支付、认证等）
- [ ] 需要迁移或数据变更

**如果不确定，选择 Full Mode。**

---

## Quick Mode 流程

```
┌─────────────────────────────────────────────────────────────┐
│  Step 1: 快速评估（3-5 个问题）                              │
│  · 确认改动范围                                             │
│  · 确认不影响重要系统                                       │
│  · 确认有基本测试思路                                       │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 2: 最小化设计                                        │
│  · 生成 docs/quick-design.md（1-2 页）                      │
│  · 用户确认后再继续                                         │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 3: Build                                           │
│  · Build-init（简化）                                       │
│  · Build-work（直接实现）                                    │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 4: Review（简化版）                                  │
│  · 功能正确性检查                                          │
│  · 安全风险检查                                            │
│  · 跳过架构审查                                            │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 5: Test（冒烟测试）                                   │
│  · 快速功能验证                                            │
│  · 跳过完整 NFR                                           │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 6: Ship（可选）                                      │
│  · 如果用户要求                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 1: 快速评估

运行以下评估：

### 问题 1：改动范围

请简要描述你要做的改动（1-3 句话）：

```
回答：___
```

### 问题 2：影响范围

这个改动会影响哪些文件/模块？

```
回答：___
```

### 问题 3：测试计划

你打算如何验证这个改动正常工作？

```
回答：___
```

### 问题 4：回滚方案

如果这个改动出问题，最简单的回滚方式是什么？

```
回答：___
```

### 问题 5：风险确认

这个改动涉及以下哪些？（选择所有适用的）
- [ ] 核心业务逻辑
- [ ] 支付/财务相关
- [ ] 用户认证/授权
- [ ] 数据存储/数据库
- [ ] 外部 API 集成
- [ ] 安全相关
- [ ] 以上都不是

---

## Step 2: 最小化设计

基于快速评估，生成 `docs/quick-design.md`：

```markdown
# Quick Design: [改动名称]

## 概述
[1-2 句话描述改动]

## 改动范围
- 文件：
- 模块：

## 实现思路
[简述实现方案，1-3 点]

## 验证方式
[如何验证改动正常]

## 回滚方案
[最简单的回滚方式]
```

### 用户确认

请确认以上设计是否符合你的预期：

```
[确认] / [需要修改]
```

---

## Step 3: Build

### 3.1 初始化 build-work 需要的 artifacts

在开始实现之前，创建 build-work 期望的 artifacts：

**创建目录结构：**
```bash
mkdir -p .vibeflow docs/test-cases
```

**创建 feature-list.json：**
从 `docs/quick-design.md` 提取功能列表：

```bash
cat > feature-list.json << 'EOF'
{
  "features": [
    {
      "id": "quick-feature-1",
      "name": "Quick Mode Feature",
      "status": "failing",
      "priority": 1,
      "verification_steps": ["实现功能", "运行测试", "验证通过"]
    }
  ],
  "created_from": "quick-design.md",
  "mode": "quick"
}
EOF
```

**创建 work-config.json：**
```bash
cat > .vibeflow/work-config.json << 'EOF'
{
  "mode": "quick",
  "tdd": false,
  "quality_gates": false,
  "feature_st": true,
  "spec_review": true,
  "created_at": "DATE"
}
EOF
```

**创建 task-progress.md：**
```bash
cat > .vibeflow/task-progress.md << 'EOF'
# Task Progress

## Current State
- Progress: 0/1 features
- Current feature: None
- Last completed: None

## History
EOF
```

**更新 quick-config.json：**
```bash
cat > .vibeflow/quick-config.json << 'EOF'
{
  "mode": "quick",
  "created_at": "DATE",
  "scope": "MINIMAL",
  "design_doc": "docs/quick-design.md",
  "build_artifacts": "ready"
}
EOF
```

### 3.2 功能实现

根据 `docs/quick-design.md` 直接实现：

1. 按设计文档实现改动
2. 编写基本测试
3. 确保代码可运行

### 3.3 更新状态

```bash
cat > .vibeflow/phase-history.json << 'EOF'
[
  {
    "phase": "quick-assessment",
    "completed_at": "DATE"
  },
  {
    "phase": "quick-design",
    "completed_at": "DATE"
  },
  {
    "phase": "build-work",
    "status": "in_progress",
    "started_at": "DATE"
  }
]
EOF
```

---

## Step 4: Review（简化版）

### 重点检查

| 检查项 | 说明 |
|--------|------|
| 功能正确性 | 改动是否按设计实现？ |
| 安全风险 | 是否有 SQL注入、XSS、敏感信息暴露等？ |
| 代码质量 | 是否有明显的坏味道或问题？ |

### 不检查（跳过）

- 架构一致性（Quick Mode 跳过）
- 性能优化（Quick Mode 跳过）
- 长期可维护性（Quick Mode 跳过）

### Review 输出

```markdown
# Quick Review Report

## 功能正确性
✅/⚠️ [状态]

## 安全风险
✅/⚠️ [状态]
[问题列表，如有问题]

## 代码质量
✅/⚠️ [状态]
[问题列表，如有问题]

## 结论
- [ ] 通过，可以继续
- [ ] 需要修复后继续
```

---

## Step 5: Test（冒烟测试）

### 冒烟测试内容

1. **功能测试**：核心功能是否正常工作
2. **编译/语法检查**：代码是否可运行
3. **基本断言**：关键逻辑是否有明显错误

### 跳过

- 完整集成测试（Full Mode 才做）
- NFR 验证（性能、压力测试等）
- 探索性测试

### Test 输出

```markdown
# Quick Test Report

## 冒烟测试结果
- [ ] 功能测试通过
- [ ] 编译/语法检查通过
- [ ] 基本断言通过

## 结论
- [ ] 通过，可以发布
- [ ] 需要修复后继续
```

---

## Step 6: Ship（可选）

如果用户要求发布：

```bash
# 创建 commit
git add -A
git commit -m "quick: [改动描述]"

# 生成发布说明
cat > RELEASE_NOTES.md << 'EOF'
# Release Notes - [日期]

## Quick Mode Changes
- [改动 1]
- [改动 2]
EOF
```

---

## 升级到 Full Mode

如果在 Quick Mode 过程中发现复杂度超出预期：

1. 停止当前 Quick Mode
2. 创建新的 `/vibeflow` 会话
3. 选择 Full Mode
4. 将 Quick Mode 的产出作为参考

---

## 硬规则

1. **Eligibility 诚实**：如果改动涉及重要系统，强制使用 Full Mode
2. **最小化设计不可跳过**：即使 Quick Mode 也必须有 `docs/quick-design.md`
3. **Review 简化但不全跳过**：安全和功能正确性必须检查
4. **产出同步**：所有产物必须写入文件，不留在记忆中
