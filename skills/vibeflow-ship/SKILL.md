---
name: vibeflow-ship
description: "测试通过后使用 — 准备发布工件、版本管理和发布输出"
---

# 发布准备

在所有测试通过（系统测试 + QA 如需要）后，准备项目发布。

**启动宣告：** "正在使用 vibeflow-ship 准备发布。"

## 前置条件

- 系统测试报告存在且裁定为 Go 或 Conditional-Go
- QA 报告存在且通过（如工作流要求 QA）
- 无严重/重要缺陷未修复

## 检查清单

### 1. 发布前检查

- [ ] 读取 ST 报告确认 Go/Conditional-Go 裁定
- [ ] 读取 QA 报告确认通过（如适用）
- [ ] 运行完整测试套件 — 最后一次确认零失败
- [ ] 验证 feature-list.json 中所有活跃功能为 passing
- [ ] 读取 `.vibeflow/workflow.yaml` 确认发布配置

### 2. 版本管理

从 `.vibeflow/workflow.yaml` 读取 `ship` 配置：

- **version_bump**：如启用，更新项目版本号
  - 读取当前版本（`VERSION` 文件、`package.json`、`pyproject.toml` 等）
  - 根据变更范围确定版本号（major/minor/patch）
  - 更新所有版本引用
- **tag**：如启用，创建 git tag

### 3. 完善 RELEASE_NOTES.md

读取现有 `RELEASE_NOTES.md`，确保：

- `[Unreleased]` 章节包含所有已交付功能的变更记录
- 将 `[Unreleased]` 重命名为 `[版本号] - YYYY-MM-DD`
- 添加新的空 `[Unreleased]` 章节
- 格式遵循 Keep a Changelog

```markdown
# Changelog

## [Unreleased]

## [X.Y.Z] - YYYY-MM-DD

### Added
- [功能描述]（对应 FR-xxx）

### Changed
- [变更描述]

### Fixed
- [修复描述]
```

### 4. 更新文档

- 确保 README.md 反映当前功能集和使用方式
- 确保 examples/ 可运行
- 如有 API 文档，确保与实现同步

### 5. 创建发布提交

```
git add -A
git commit -m "release: vX.Y.Z

- [功能摘要]
- ST report: Go
- QA report: Pass (如适用)"
```

### 6. 创建 Tag（如工作流配置启用）

```
git tag -a vX.Y.Z -m "Release vX.Y.Z"
```

### 7. 创建 PR（如工作流配置启用）

#### 7a. 确认 PR 配置

从 `.vibeflow/workflow.yaml` 读取 ship 配置：
```yaml
ship:
  version_bump: true|false
  tag: true|false
  pr: true|false
  release_docs: true|false
  pr_draft: true|false        # 默认 true
  pr_reviewer: ""             # 可选，如 "owner1,owner2"
  pr_milestone: ""            # 可选，如 "v1.0.0"
```

#### 7b. 构建 PR 正文

生成包含完整测试结果和变更摘要的 PR body：

```markdown
## 发布摘要

**版本**：vX.Y.Z
**日期**：YYYY-MM-DD

### 测试结果
| 检查项 | 结果 |
|--------|------|
| 单元测试 | PASS |
| 覆盖率 | XX% 行 / XX% 分支 |
| 变异得分 | XX% |
| 系统测试 | Go |
| QA | Pass（如适用）|

### 关键交付
- [功能 1]
- [功能 2]

### 变更统计
- 文件变更：X 个
- 新增行：+XXX
- 删除行：-XXX

### 关联 Issues
- 总需求 Issue: #X
- 子任务 Issues: #Y1, #Y2

---
*由 VibeFlow 自动生成*
```

#### 7c. 执行 PR 创建

```bash
# 基本 PR 创建（draft 默认开启）
gh pr create \
  --title "Release vX.Y.Z" \
  --body "## 发布摘要
..." \
  --draft

# 带 reviewer（从 workflow.yaml 读取）
gh pr create \
  --title "Release vX.Y.Z" \
  --body "..." \
  --reviewer owner1,owner2 \
  --draft

# 带 milestone
gh pr create \
  --title "Release vX.Y.Z" \
  --body "..." \
  --milestone "v1.0.0" \
  --draft

# 完整命令示例
gh pr create \
  --title "Release vX.Y.Z" \
  --body "$(cat <<'EOF'
## 发布摘要
...
EOF
)" \
  --reviewer "${PR_REVIEWER}" \
  --milestone "${PR_MILESTONE}" \
  --draft
```

#### 7d. 展示 PR 链接

PR 创建后展示链接供用户确认：
```bash
gh pr view --json 'url,number,title'
```

#### 7e. 询问用户是否立即合并

```
PR #X 已创建：https://github.com/owner/repo/pull/X

是否现在合并？（输入 "y" 合并，"n" 仅创建，稍后手动合并）
```

如用户选择合并：
```bash
gh pr merge --squash --delete-branch
```

### 8. 发布摘要

向用户展示发布摘要：

```markdown
## 发布摘要

**版本**：vX.Y.Z
**功能数**：X 个活跃功能
**测试**：
- 单元测试：XXX 通过
- 覆盖率：XX% 行 / XX% 分支
- 变异得分：XX%
- 系统测试：Go
- QA：Pass（如适用）

**关键交付**：
- [功能 1]
- [功能 2]
- ...

**已知限制**：
- [如有]
```

### 9. 过渡

发布完成后进入 `vibeflow-reflect`。

## 工作流配置参考

`.vibeflow/workflow.yaml` 中 `ship` 章节完整配置：

```yaml
ship:
  version_bump: true|false   # 是否自动更新版本号
  tag: true|false           # 是否创建 git tag
  pr: true|false           # 是否创建 PR
  pr_draft: true|false     # 默认创建 draft PR
  pr_reviewer: ""           # PR reviewers（如 "owner1,owner2"）
  pr_milestone: ""          # PR milestone（如 "v1.0.0"）
  release_docs: true|false  # 是否更新发布文档
```

按配置跳过不需要的步骤（如 prototype 模板可能不创建 tag 和 PR）。

## 集成

**调用者：** vibeflow-router 或 vibeflow-test-system/vibeflow-test-qa
**依赖：** 系统测试 Go + QA 通过（如需要）
**产出：** 发布提交、RELEASE_NOTES.md、可选 tag 和 PR
**关联：** vibeflow-repo-sync（Issue 同步由 Tasks 阶段处理）

**链接到：** vibeflow-reflect
