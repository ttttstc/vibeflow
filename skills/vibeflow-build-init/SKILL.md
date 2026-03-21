---
name: vibeflow-build-init
description: Use when design exists but feature-list.json has not been initialized.
---

# VibeFlow 构建初始化

初始化构建阶段的实现工件。在需求和设计批准后运行一次。

**开始时宣布：**"我正在使用 vibeflow-build-init skill 来搭建构建阶段。"

## 目的

创建 VibeFlow 构建阶段所需的所有持久化工件：
- 带状态跟踪的功能清单
- 工作配置
- 进度跟踪

## 前置条件

运行此 skill 前：
- 需求文档存在于 `docs/plans/*-srs.md`
- 设计文档存在于 `docs/plans/*-design.md`
- Think 输出存在于 `.vibeflow/think-output.md`
- 工作流配置存在于 `.vibeflow/workflow.yaml`

## 第一步：读取输入文档

### 1.1 读取需求文档（SRS）

读取 `docs/plans/*-srs.md`：
- 功能需求（FR-xxx）
- 非功能需求（NFR-xxx）
- 约束条件（CON-xxx）
- 假设条件（ASM-xxx）
- 验收标准
- 接口需求

### 1.2 读取设计文档

读取 `docs/plans/*-design.md`：
- 技术栈
- 架构
- 数据模型
- API 设计
- 测试策略
- 任务分解

### 1.3 读取工作流配置

读取 `.vibeflow/workflow.yaml`：
- 选择的模板（prototype、web-standard、api-standard、enterprise）
- 阶段顺序
- 启用的功能

## 第二步：创建工作配置

### 2.1 创建 `.vibeflow/work-config.json`

```json
{
  "build": {
    "tdd": true,
    "quality": true,
    "feature_st": true,
    "spec_review": true
  },
  "quality": {
    "tdd": true,
    "quality_gates": {
      "line_coverage_min": 80,
      "branch_coverage_min": 70,
      "mutation_score_min": 70
    }
  }
}
```

根据以下内容调整阈值：
- 项目模板（原型可能有更低的阈值）
- 技术栈能力
- 团队偏好

### 2.2 保存工作配置

写入 `.vibeflow/work-config.json`。

## 第三步：创建功能清单

### 3.1 分解需求

从 SRS 和设计文档分解出功能：

**对于每个 FR-xxx：**
1. 创建一个或多个功能，包含：
   - `id`：顺序整数
   - `category`："core"、"backend"、"frontend"、"infrastructure"、"non-functional"
   - `title`：简洁的功能名称
   - `description`：功能作用
   - `priority`："high"、"medium"、"low"
   - `status`：初始化时始终为 `"failing"`
   - `verification_steps[]`：从 SRS 派生的验收标准
   - `dependencies[]`：必须先完成的 feature ID

### 3.2 功能 Schema

```json
{
  "id": 1,
  "category": "core",
  "title": "功能标题",
  "description": "功能作用",
  "priority": "high|medium|low",
  "status": "failing",
  "verification_steps": [
    "Given [上下文]，when [操作]，then [结果]"
  ],
  "dependencies": []
}
```

### 3.3 处理 UI 功能

对于有 UI 组件的功能（`"ui": true`）：
- 设置 `"ui": true`
- 如果适用，添加 `"ui_entry": "/可选路径"`
- 确保依赖包含后端 API 功能
- 引用 UCD 文档的样式要求

### 3.4 处理非功能需求

对于 NFR-xxx 项目：
- 使用 `category: "non-functional"` 创建功能
- 包含可测量的 `verification_steps`（例如，"响应时间 < 200ms"）
- 质量门禁（tdd、quality）可能不适用——在工作配置中相应设置

### 3.5 依赖排序

在数组中按依赖关系排序功能：
1. 基础设施/core 功能优先
2. 后端功能先于前端功能
3. 依赖的功能在其依赖之后

## 第四步：创建任务进度

### 4.1 创建 `task-progress.md`

```markdown
# 任务进度

## 当前状态

- **进度**：0/N 个功能通过
- **最后完成**：无
- **下一个功能**：#1 [功能标题]

---

## 会话日志

### 会话 0（初始化）
- 日期：YYYY-MM-DD
- 操作：构建初始化
- 已初始化的功能：N
```

## 第五步：验证

### 5.1 验证功能清单

验证 feature-list.json 是有效的 JSON：
- 所有必填字段存在
- 无循环依赖
- 所有依赖 ID 引用现有功能

### 5.2 检查文档路径

验证引用的文档存在：
- `docs/plans/*-srs.md`
- `docs/plans/*-design.md`

## 第六步：初始提交

### 6.1 Git Add

暂存所有新文件：
- `.vibeflow/work-config.json`
- `feature-list.json`
- `task-progress.md`

### 6.2 Git Commit

```
feat: initialize build stage artifacts

- Add work-config.json with quality thresholds
- Add feature-list.json with N features
- Add task-progress.md for session tracking
```

## 检查清单

在标记初始化完成前：

- [ ] 工作配置已创建于 `.vibeflow/work-config.json`
- [ ] 功能清单已创建于 `feature-list.json`
- [ ] 任务进度已创建于 `task-progress.md`
- [ ] 所有功能都有有效的 `verification_steps`
- [ ] 依赖形成 DAG（无循环）
- [ ] UI 功能标有 `"ui": true`
- [ ] NFR 功能标有 `category: "non-functional"`
- [ ] 已创建初始 git 提交
- [ ] 构建阶段已准备好进入 `vibeflow-build-work`

## 输出

| 文件 | 用途 |
|------|------|
| `.vibeflow/work-config.json` | 构建阶段配置和质量阈值 |
| `feature-list.json` | 带状态的结构化任务清单 |
| `task-progress.md` | 按会话的进度日志 |

## 集成

**调用者：** `vibeflow` 路由（当需求和设计存在，但 feature-list.json 不存在时）
**需要：**
- 需求文档位于 `docs/plans/*-srs.md`
- 设计文档位于 `docs/plans/*-design.md`
- Think 输出位于 `.vibeflow/think-output.md`
- 工作流配置位于 `.vibeflow/workflow.yaml`
**产生：** `work-config.json`、`feature-list.json`、`task-progress.md`
**链至：** `vibeflow-build-work`（第一个功能周期）
