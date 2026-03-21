---
name: vibeflow-build-work
description: Use when build initialization is done and some features are still failing.
---

# VibeFlow 构建工作编排

每次将一个特性推进到实现流水线中。每个特性遵循严格的顺序：TDD → 质量门禁 → 特性验收 → Spec审查。

**开始时宣布：** "我正在使用 vibeflow-build-work skill。让我确认当前状态。"

## 铁律

```
每次循环一个特性——不要跳过步骤
```

每个步骤都有其对应的skill。请严格按编排顺序执行。不要走捷径。

## 步骤1：定向——加载当前状态

### 1.1 读取工作配置

读取 `.vibeflow/work-config.json` 以确定启用的步骤：
```json
{
  "build": {
    "tdd": true,
    "quality": true,
    "feature_st": true,
    "spec_review": true
  }
}
```

### 1.2 读取特性列表

读取 `feature-list.json`：
- 记录所有 `"status": "failing"` 的特性
- 记录特性优先级
- 记录特性依赖关系
- 跳过 `"deprecated": true` 的特性

### 1.3 读取任务进度

读取 `task-progress.md`：
- 进度统计（X/Y 个特性通过）
- 最后完成的特性
- 下一个待处理的特性

### 1.4 选择下一个特性

**依赖关系满足检查：**
1. 按优先级从高到低选择下一个 `"status": "failing"` 的特性
2. 验证 `dependencies[]` 中的所有特性都具有 `"status": "passing"`
3. 如果任何依赖项仍为 `"failing"`：
   - 记录日志："特性 #{id} ({title}) 跳过——未满足的依赖：#{dep1}, #{dep2}"
   - 选择下一个符合条件的失败特性
4. 如果没有特性满足所有依赖关系 → 升级给用户

### 1.5 加载特性上下文

对于选定的特性，读取：
- 来自 `feature-list.json` 的特性规格
- 来自 `docs/plans/*-srs.md` 的需求部分
- 来自 `docs/plans/*-design.md` 的设计部分
- 来自 `task-progress.md` 的任何先前实现笔记

## 步骤2：TDD循环（如果在 work-config 中启用）

**调用 skill：** `vibeflow-tdd`

### 2.1 TDD 红色阶段——编写失败的测试

需要传递的上下文：
- 来自 `feature-list.json` 的特性对象
- 来自特性的 `verification_steps[]`
- 来自 `feature-list.json` 的 `tech_stack`

### 2.2 TDD 绿色阶段——最小化实现

仅实现足够使失败测试通过所需的代码。

### 2.3 TDD 重构阶段——清理

在不让绿色阶段失败的情况下清理代码。

### 2.4 验证 TDD 完成

所有测试通过。继续步骤3。

## 步骤3：质量门禁（如果在 work-config 中启用）

**调用 skill：** `vibeflow-quality`

### 3.1 门禁0：真实测试验证

验证集成测试存在并通过（或已声明豁免）。

### 3.2 门禁1：覆盖率

运行覆盖率工具。验证行覆盖率和分支覆盖率是否达到阈值。

### 3.3 门禁2：变异测试

运行变异测试。验证变异分数是否达到阈值。

### 3.4 门禁3：验证并标记

在当前会话中运行完整验证。只有所有门禁都通过时才将特性标记为通过。

### 3.5 验证质量完成

所有门禁通过。继续步骤4。

## 步骤4：特性验收测试（如果启用）

**调用 skill：** `vibeflow-feature-st`

### 4.1 创建测试用例

对于每个 `verification_step`，创建黑盒验收测试用例：
- 愉快路径测试
- 错误处理测试
- 边界测试
- UI 测试（如果 `ui: true`）

### 4.2 执行测试用例

针对运行中的系统执行所有测试用例。
将结果记录到 `docs/test-cases/feature-{id}-{slug}.md`。

### 4.3 验证全部通过

所有验收测试通过。继续步骤5。

## 步骤5：规格合规审查（如果启用）

**调用 skill：** `vibeflow-spec-review`

### 5.1 对照规格审查

验证实现是否匹配：
- SRS 需求部分
- 设计文档
- 计划文档

### 5.2 对照 UCD 审查（如果 ui: true）

验证实现是否遵循 UCD 样式指南。

### 5.3 验证合规性

规格合规性确认。继续步骤6。

## 步骤6：持久化

### 6.1 Git 提交

提交已完成的特性：
- 实现代码
- 测试
- 测试用例文档
- 更新的 `task-progress.md`

### 6.2 更新特性状态

在 `feature-list.json` 中：
```json
{
  "id": 1,
  "status": "passing",
  "completed_date": "2026-03-21"
}
```

### 6.3 更新任务进度

在 `task-progress.md` 中：
- 更新进度计数
- 记录已完成的特性
- 记录下一个特性

## 步骤7：继续或完成

### 7.1 检查剩余特性

如果仍有失败的未废弃特性 → 返回步骤1。

### 7.2 所有特性完成

如果没有失败的特性：
- 所有活跃特性都正在通过
- 调用 `vibeflow-test-system` 开始系统测试

## 检查清单

每个特性循环：

- [ ] 步骤1：定向——状态已加载，下一个特性已选择
- [ ] 步骤2：TDD 完成（如果启用）——所有测试通过
- [ ] 步骤3：质量门禁通过（如果启用）——覆盖率、变异已验证
- [ ] 步骤4：特性验收通过（如果启用）——测试用例已执行
- [ ] 步骤5：规格审查通过（如果启用）——合规性已确认
- [ ] 步骤6：持久化——git 提交，状态已更新
- [ ] 步骤7：继续或完成

## 关键规则

- **每次循环一个特性**——防止上下文耗尽
- **严格按步骤顺序**——不跳过，不重排序
- **没有新鲜证据就不标记"通过"**——运行测试，读取输出，然后标记
- **启动前检查依赖**——永远不要开发依赖项仍在失败的特性
- **计划前配置门控**——缺少必需配置时不要编码

## 集成

**被调用者：** `vibeflow` 路由器（当 feature-list.json 存在且构建处于活跃状态）
**调用（启用时按严格顺序）：**
1. `vibeflow-tdd`（步骤2）——红-绿-重构
2. `vibeflow-quality`（步骤3）——覆盖率 + 变异
3. `vibeflow-feature-st`（步骤4）——黑盒特性验收
4. `vibeflow-spec-review`（步骤5）——规格与设计合规
**读取/写入：** `feature-list.json`、`task-progress.md`
**链接到：** `vibeflow-test-system`（当所有特性通过时）
