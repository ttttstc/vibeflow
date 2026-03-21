---
name: vibeflow-tdd
description: Use as the red-green-refactor step within the VibeFlow build stage.
---

# VibeFlow 测试驱动开发

对当前特性运行测试优先开发。先写测试。看它失败。写最少的代码使其通过。然后重构。

**开始时宣布：** "我正在使用 vibeflow-tdd skill 通过 TDD 实现这个特性。"

## 铁律

```
没有失败的测试就不能写实现代码
```

在测试之前写代码？删除它。重新开始。没有例外。

## 红-绿-重构循环

```
红色 → 为所有 verification_steps 编写失败的测试
绿色 → 编写最少的代码使测试通过
重构 → 在不破坏绿色阶段的情况下清理
```

## 步骤1：TDD 红色阶段——编写失败的测试

### 1.1 加载特性上下文

为当前特性读取以下制品：
- **特性规格** 来自 `feature-list.json`——ID、标题、描述、`verification_steps[]`、`dependencies[]`、`ui` 标志
- **需求文档** ——相关 FR 部分的 `docs/plans/*-srs.md`
- **设计文档** ——特性设计部分的 `docs/plans/*-design.md`
- **工作配置** ——TDD 启用情况和阈值的 `.vibeflow/work-config.json`

### 1.2 识别测试类别

对于每个 `verification_step`，派生覆盖以下内容的测试用例：

| 类别 | 测试内容 | 示例 |
|----------|-------------|---------|
| 愉快路径 | 正常操作，有效输入 | 有效输入返回预期输出 |
| 错误处理 | 已知失败，无效输入 | 无效输入返回错误 |
| 边界/边缘 | 限制、空、最大、零 | 空字符串；最大长度输入 |
| 安全 | 注入，授权 | 畸形输入被清理 |

当某个类别不适用时，在注释中明确说明。

### 1.3 编写测试（TDD 红色）

**规则1：在任何实现代码存在之前编写测试。**

对于每个 `verification_step`：
1. 编写一个或多个测试函数来执行描述的行为
2. 使用项目的测试框架（来自 `feature-list.json` 的 `tech_stack.test_framework`）
3. 将测试放置在适当的测试文件中（遵循项目约定）
4. 按层标记测试：
   ```python
   # [unit] — 内部逻辑，mock 的依赖项
   def test_feature_behavior():
       ...

   # [integration] — 真实的外部依赖（DB、API、文件系统）
   def test_feature_with_real_dependency():
       ...
   ```

**规则2：负面测试比例 >= 40%**
```
negative_test_count / total_test_count >= 0.40
```

**规则3：断言质量——低价值断言 <= 20%**
- 避免：`assert x is not None`、`assert isinstance(x, SomeType)`、`assert len(x) > 0`
- 推荐：特定值检查、状态验证、数据正确性

**规则4："错误实现"挑战**
对于每个测试，问自己："这个测试能捕获什么样的错误实现？"
- 硬编码值还能通过吗？
- 交换字段还能通过吗？
- 差一错误还能通过吗？

如果"几乎任何错误实现都能通过"→ 用更具体的断言重写。

### 1.4 验证测试失败

**按项目设置激活环境**，然后运行测试命令：
```bash
# Python
source .venv/bin/activate  # 或适当的命令
pytest tests/ -v

# Node.js
npm test

# Java
mvn test
```

**此时所有测试必须失败。** 如果任何测试通过 → 它没有测试任何有用的东西，重写它。

### 1.5 真实测试要求（如果特性有外部依赖）

对于有外部依赖的特性（DB、HTTP、文件系统）：
1. 编写至少一个使用真实依赖的 `[integration]` 测试
2. 用 `[integration]` 标签清楚地标记
3. 如果特性没有外部依赖，明确声明：
   ```python
   # [no integration test] — 纯函数，无外部 I/O
   ```

## 步骤2：TDD 绿色阶段——最小化实现

**规则：只写足够的代码使失败的测试通过。**

### 2.1 实现特性

1. 逐个读取当前失败的测试
2. 对于每个失败的测试，实现使其通过的最少更改
3. 不要实现尚未测试的功能
4. 在此步骤中不要优化或重构

### 2.2 每次更改后运行测试

实现每个测试所需更改后：
```bash
pytest tests/ -v  # 或项目特定命令
```

所有测试必须通过后才能继续。

### 2.3 服务/服务器启动（如果适用）

如果特性实现了一个服务器进程：
1. 实现必须在启动时记录：绑定端口、PID、就绪信号
2. 编写一个 TDD 红色测试，在实现服务器绑定之前验证启动输出

## 步骤3：TDD 重构阶段——清理

**规则：保持测试绿色，同时提高代码质量。**

### 3.1 重构

所有测试通过时：
1. 提取重复代码
2. 改进命名
3. 简化逻辑
4. 不要添加新功能

### 3.2 验证测试仍然通过

每次重构更改后：
```bash
pytest tests/ -v
```

如果任何测试失败 → 还原重构并尝试其他方法。

## 检查清单

在标记 TDD 完成之前：

- [ ] 所有 `verification_steps` 都有对应的测试
- [ ] 所有测试在红色阶段失败（实现之前）
- [ ] 所有测试在绿色阶段通过（实现之后）
- [ ] 负面测试比例 >= 40%
- [ ] 低价值断言比例 <= 20%
- [ ] 至少一个集成测试（如果特性有外部依赖）
- [ ] 重构后所有测试仍然通过
- [ ] 没有失败的测试就不写实现代码（铁律合规）

## 质量门禁

| 门禁 | 阈值 | 工具 |
|------|-----------|------|
| 测试通过率 | 100% | `pytest --tb=short` / `npm test` |
| 行覆盖率 | 按 `work-config.json` | `coverage report` |
| 分支覆盖率 | 按 `work-config.json` | `coverage report` |

## 集成

**被调用者：** `vibeflow-build-work`（步骤3——TDD 执行）
**调度：** 必要时调度实现子代理
**需要：**
- 来自 `feature-list.json` 的特性规格
- 特性的 `verification_steps[]`
- 来自 `docs/plans/*-srs.md` 的 SRS 需求部分
- 来自 `docs/plans/*-design.md` 的设计部分
- 来自 `feature-list.json` 的 `tech_stack` 和 `quality_gates`
**产出：** 通过的测试 + 实现代码
**链接到：** `vibeflow-quality`（TDD 完成后）
