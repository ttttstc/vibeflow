---
name: vibeflow-ship
description: Use after testing to prepare release artifacts and shipping output.
---

# VibeFlow 发布阶段

准备项目发布。创建发布制品和输出。

**开始时宣布：** "我正在使用 vibeflow-ship skill 准备发布。"

## 目的

审查批准后，准备并执行发布：
- 版本更新
- 发布说明
- 发布制品
- 部署准备

## 先决条件

运行此 skill 之前：
- `feature-list.json` 中所有功能标记为 `"status": "passing"`
- 全局变更审查通过（vibeflow-review）
- 所有测试通过
- 发布说明已起草

## 步骤 1: 加载发布上下文

### 1.1 读取功能列表

从 `feature-list.json`:
- 所有已完成的功能（status: passing）
- 功能类别
- 本版本中的新功能

### 1.2 读取任务进度

从 `task-progress.md`:
- 会话日志摘要
- 已知问题
- 开放性问题

### 1.3 读取发布说明草稿

从当前的 `RELEASE_NOTES.md`:
- 已起草的发布说明
- 列出的变更

### 1.4 确定版本

基于变更类型：
- **Major**（破坏性变更）：X.0.0
- **Minor**（新功能）：X.Y.0
- **Patch**（错误修复）：X.Y.Z

检查项目文件中的现有版本。

## 步骤 2: 更新版本

### 2.1 更新项目版本文件

更新以下内容中的版本：
- `package.json` (Node.js)
- `pyproject.toml` / `__version__` (Python)
- `pom.xml` / `build.gradle` (Java)
- 其他项目特定的版本文件

### 2.2 Git 标签

创建 git 标签：
```bash
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3
```

## 步骤 3: 定稿发布说明

### 3.1 审查草稿发布说明

验证发布说明包括：
- 所有新功能（带功能 ID）
- 所有错误修复（带问题引用）
- 所有破坏性变更（突出显示）
- 迁移说明（如果需要）
- 已知限制

### 3.2 格式化发布说明

使用 Keep a Changelog 格式：
```markdown
## [1.2.3] - YYYY-MM-DD

### Added
- Feature 1 (#1)
- Feature 2 (#2)

### Changed
- Improvement to existing feature

### Fixed
- Bug fix description

### Breaking
- Breaking change description
```

### 3.3 更新 RELEASE_NOTES.md

将新发布部分添加到 `RELEASE_NOTES.md`。

## 步骤 4: 创建发布制品

### 4.1 构建生产制品

```bash
# Node.js
npm run build
npm pack  # creates .tgz

# Python
python -m build
# or
pip wheel .

# Java
mvn clean package -DskipTests
```

### 4.2 验证制品

对于每个制品：
- [ ] 制品存在
- [ ] 制品大小合理
- [ ] 没有意外包含的文件
- [ ] 版本符合预期

### 4.3 签名制品（如果适用）

如果项目使用签名：
- 使用项目密钥签名制品
- 验证签名

## 步骤 5: 准备部署

### 5.1 创建部署包

对于可部署的项目：
- 捆绑制品
- 包含部署脚本
- 包含配置模板
- 包含回滚程序

### 5.2 记录部署步骤

创建或更新 `DEPLOY.md`：
- 部署前检查清单
- 部署步骤
- 部署后验证
- 回滚程序

## 步骤 6: Git 提交发布状态

### 6.1 暂存变更

暂存文件：
- 更新的版本文件
- 更新的 RELEASE_NOTES.md
- 任何部署制品

### 6.2 提交

```bash
git add .
git commit -m "chore: prepare release v1.2.3"
```

### 6.3 标签

```bash
git tag -a v1.2.3 -m "Release v1.2.3"
```

## 步骤 7: 验证发布

### 7.1 发布前检查清单

- [ ] 所有文件中的版本已更新
- [ ] Git 标签已创建并推送
- [ ] 发布说明已更新
- [ ] 所有测试通过
- [ ] 制品已构建并验证
- [ ] 部署包已准备（如果适用）
- [ ] 没有未提交的变更

### 7.2 冒烟测试发布

对发布制品运行冒烟测试：
```bash
# 安装/打包
# 启动应用
# 验证健康端点
# 运行关键路径测试
```

### 7.3 归档会话

更新 `task-progress.md`：
- 标记发布已准备
- 记录发布版本
- 记录创建的制品

## 检查清单

在标记发布完成之前：

- [ ] 所有项目文件中的版本已更新
- [ ] Git 标签已创建（v1.2.3）
- [ ] 发布说明已定稿
- [ ] 生产制品已构建
- [ ] 制品已验证
- [ ] 部署包已准备（如果适用）
- [ ] 发布前检查清单完成
- [ ] 冒烟测试通过
- [ ] Git 提交已创建
- [ ] 可以部署

## 输出

| 制品 | 位置 |
|----------|----------|
| Release tag | Git repository |
| Release notes | `RELEASE_NOTES.md` |
| Production artifacts | Project-specific |
| Deployment package | `dist/` or release directory |

## 集成

**调用者:** `vibeflow` 路由器（审查批准后）
**需要:**
- 所有功能通过
- 审查批准
- `RELEASE_NOTES.md` 草稿
- `feature-list.json`
- `task-progress.md`
**产出:**
- 版本更新
- Git 标签
- 定稿的发布说明
- 发布制品
**链接到:** `vibeflow-reflect`（发布后）
