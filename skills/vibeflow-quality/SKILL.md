---
name: vibeflow-quality
description: Use for coverage and mutation quality gates during the VibeFlow build stage.
---

# VibeFlow 质量门禁

根据 `.vibeflow/work-config.json` 中的质量阈值验证当前特性。四个顺序门禁，在将特性标记为完成之前必须全部通过。

**开始时宣布：** "我正在使用 vibeflow-quality skill 运行质量门禁。"

## 铁律

```
没有新鲜的验证证据就不能声称完成
```

如果在本会话中没有运行验证命令，就不能声称它通过了。

## 步骤1：真实测试验证（门禁0）

门禁0在覆盖率之前运行。当测试套件全是 mock 时，覆盖率数据毫无意义。

### 1.1 检查真实测试存在

对于有外部依赖的特 性（DB、HTTP、文件系统）：
1. 验证至少存在一个 `[integration]` 标记的测试
2. 验证集成测试使用真实依赖（不是 mock）
3. 如果不存在集成测试 → 门禁0 失败

### 1.2 执行真实测试

运行测试套件并验证所有测试通过：
```bash
pytest tests/ -v  # 或项目特定命令
```

任何测试失败 → 门禁0 失败。继续之前先修复。

**需要的证据：**
```
门禁0 结果：
- 真实测试数量：N
- 所有测试通过：是/否
- 门禁0：通过/失败
```

## 步骤2：覆盖率门禁（门禁1）

所有测试通过后，运行覆盖率验证。

### 2.1 运行覆盖率工具

```bash
# Python
coverage run -m pytest tests/
coverage report

# Node.js
npm test -- --coverage

# Java
mvn test jacoco:report
```

### 2.2 验证阈值

读取 `.vibeflow/work-config.json` 获取阈值：
```json
{
  "quality": {
    "tdd": true,
    "quality_gates": {
      "line_coverage_min": 80,
      "branch_coverage_min": 70
    }
  }
}
```

| 指标 | 阈值 | 低于阈值时 |
|--------|-----------|----------|
| 行覆盖率 | `line_coverage_min` | 为未覆盖的行添加测试 |
| 分支覆盖率 | `branch_coverage_min` | 为未覆盖的分支添加测试 |

### 2.3 如果覆盖率失败

1. 从覆盖率报告中识别未覆盖的行/分支
2. 添加针对缺口的测试
3. 返回 TDD 循环（vibeflow-tdd）添加测试
4. 重新运行覆盖率验证
5. 不要跳过或绕过覆盖率要求

**需要的证据：**
```
门禁1 结果：
- 行覆盖率：XX%（阈值：Y%）
- 分支覆盖率：XX%（阈值：Y%）
- 门禁1：通过/失败
```

## 步骤3：变异测试门禁（门禁2）

覆盖率通过后，对更改的文件运行变异测试。

### 3.1 运行变异测试

```bash
# Python
mutmut run

# Java
mvn pitest:mutationCoverage

# Node.js
stryker
```

### 3.2 验证变异分数

检查 `.vibeflow/work-config.json` 中的变异阈值：
```json
{
  "quality": {
    "quality_gates": {
      "mutation_score_min": 70
    }
  }
}
```

| 分数 | 行动 |
|-------|--------|
| >= 阈值 | 门禁2 通过 |
| < 阈值 | 分析存活的变异体 |

### 3.3 分析存活的变异体

对于每个存活的变异体：
- **等效变异体**（代码更改没有可观察效果）→ 记录并跳过
- **真实缺口**（测试没有捕获变异）→ 添加/加强测试
- **不可达代码** → 删除死代码

分析后：
- 为真实缺口添加/加强测试
- 重新运行变异测试
- 不要跳过变异测试

**需要的证据：**
```
门禁2 结果：
- 变异分数：XX%（阈值：Y%）
- 存活变异体：N
- 等效：N，真实缺口：N，不可达：N
- 门禁2：通过/失败
```

## 步骤4：验证并标记（门禁3）

标记特性完成前的最终门禁。

### 4.1 运行完整验证

在当前会话中执行所有验证（不是缓存的）：
```bash
# 1. 所有测试通过
pytest tests/ -v

# 2. 覆盖率满足阈值
coverage run -m pytest tests/
coverage report

# 3. 变异分数满足阈值
mutmut run
mutmut results
```

### 4.2 读取所有输出

- 检查所有命令的退出码
- 统计测试的通过/失败/跳过数量
- 读取覆盖率百分比
- 读取变异分数

### 4.3 标记特性完成

只有在所有门禁都通过后：
1. 在 `feature-list.json` 中更新特性状态：`"status": "passing"`
2. 在 `task-progress.md` 中记录证据
3. 报告带证据的结果

如果任何门禁失败 → 停止。不要标记为通过。先修复问题。

## 红旗词汇

如果你发现自己使用了以下任何一个，停止并重新验证：

| 红旗 | 正确行动 |
|----------|----------------|
| "应该通过" | 立即运行测试 |
| "大概能用" | 立即执行并验证 |
| "覆盖率看起来还行" | 立即运行覆盖率工具 |
| "变异分数应该没问题" | 立即运行变异测试 |
| "已验证"（没有显示输出） | 显示实际输出 |

## 检查清单

在标记质量门禁完成之前：

- [ ] 门禁0：真实测试存在并通过（或已声明豁免）
- [ ] 门禁1：行覆盖率 >= 阈值
- [ ] 门禁1：分支覆盖率 >= 阈值
- [ ] 门禁2：变异分数 >= 阈值
- [ ] 门禁2：存活的变异体已分析并处理
- [ ] 门禁3：在当前会话中运行完整验证
- [ ] 门禁3：所有命令都已执行并捕获输出
- [ ] 特性在 `feature-list.json` 中标记为 `"status": "passing"`

## 集成

**被调用者：** `vibeflow-build-work`（步骤4——质量门禁）
**需要：**
- 特性 ID 和 `verification_steps`
- 来自 `feature-list.json` 的 `quality_gates` 阈值
- 来自 `feature-list.json` 的 `tech_stack` 工具名称
- 所有测试通过（来自 vibeflow-tdd）
**产出：** 新鲜的验证证据（测试输出、覆盖率%、变异分数）
**链接到：** `vibeflow-feature-st`（如果在 work-config 中启用）
