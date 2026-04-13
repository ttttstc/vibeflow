---
name: vibeflow-repo-sync
description: "将 Tasks 阶段产出的任务同步到 GitHub Issues，支持总需求 issue 和子任务 issue 的层级结构；也用于 Review 完成后同步检视意见到 PR comment"
---

# 仓库同步

将 VibeFlow 产出的设计文档和任务计划同步到 GitHub Issues 和 PR Comments。

**启动宣告：** "正在使用 vibeflow-repo-sync 同步到 GitHub。"

## 两种模式

### 模式 A：Issue 同步（Tasks 阶段）

**触发时机**：Tasks 阶段完成后，用户确认要将任务同步到 GitHub Issues

**前置条件**：
- `design.md` 存在
- `tasks.md` 存在
- `gh` CLI 已登录（`gh auth status`）

### 模式 B：PR Comment 同步（Review 阶段）

**触发时机**：Review 完成后，用户确认要将检视意见同步到 PR

**前置条件**：
- `docs/changes/<change-id>/verification/review.md` 存在
- 当前分支有对应的 open PR

---

## 模式 A：Issue 同步

### 前置准备

1. 运行 `python scripts/get-vibeflow-paths.py --json`，获取：
   - `design_path`: design.md 路径
   - `tasks_path`: tasks.md 路径
   - `change_id`: 变更 ID

2. 确认 GitHub 仓库：
   ```bash
   git remote get-url origin
   ```
   从中提取 `owner/repo`。

### 步骤 1：解析 design.md，提取功能领域

读取 `design.md`，提取所有二级标题（`## <N>. <Title>` 格式）作为功能领域：

```python
import re

def parse_design_sections(design_path):
    """提取 design.md 中的功能领域"""
    content = Path(design_path).read_text(encoding='utf-8')
    sections = {}
    # 匹配 ## 4.1 xxx 或 ## 4. xxx 格式
    pattern = r'^##\s+(\d+(?:\.\d+)?)\s+(.+)$'
    for match in re.finditer(pattern, content, re.MULTILINE):
        section_num = match.group(1)
        section_title = match.group(2).strip()
        sections[section_num] = {
            'title': section_title,
            'description': extract_section_description(content, match.start())
        }
    return sections
```

### 步骤 2：解析 tasks.md，提取任务列表

读取 `tasks.md`，支持两种格式：

**格式 1：简单列表**
```markdown
- [ ] Task description 1
- [ ] Task description 2
```

**格式 2：结构化模板**
```markdown
### Task <task-id>

- `feature_id`: <id>
- `goal`: <one-sentence goal>
- `change_type`: <code|test|config|docs|migration|qa>
- `design_section`: <for example 4.1>
- `exact_file_paths`:
  - <repo-relative-path>
- `depends_on`:
  - <task-id or none>
- `steps`:
  - <ordered implementation step>
```

```python
def parse_tasks(tasks_path):
    """解析 tasks.md，提取所有任务"""
    content = Path(tasks_path).read_text(encoding='utf-8')
    tasks = []

    # 格式 2：结构化模板
    task_pattern = r'^### Task (.+?)$(.*?)(?=^### Task |^## |\Z)'
    for match in re.finditer(task_pattern, content, re.MULTILINE | re.DOTALL):
        task_id = match.group(1).strip()
        task_body = match.group(2)

        task = {'id': task_id, 'format': 'structured'}

        # 提取字段
        feature_id = re.search(r'`feature_id`:\s*(.+)', task_body)
        goal = re.search(r'`goal`:\s*(.+)', task_body)
        change_type = re.search(r'`change_type`:\s*(.+)', task_body)
        design_section = re.search(r'`design_section`:\s*(.+)', task_body)
        file_paths = re.findall(r'^\s*-\s*(.+)', task_body, re.MULTILINE)
        depends_on = re.findall(r'^\s*-\s*`?(.+?)`?\s*$', task_body, re.MULTILINE)

        if feature_id:
            task['feature_id'] = feature_id.group(1).strip()
        if goal:
            task['goal'] = goal.group(1).strip()
        if change_type:
            task['change_type'] = change_type.group(1).strip()
        if design_section:
            task['design_section'] = design_section.group(1).strip()
        if file_paths:
            task['file_paths'] = [f.strip() for f in file_paths if f.strip()]

        tasks.append(task)

    # 格式 1：简单列表
    for match in re.finditer(r'^-\s+\[.\]\s+(.+)$', content, re.MULTILINE):
        tasks.append({
            'id': f"task-{len(tasks)+1}",
            'title': match.group(1).strip(),
            'format': 'simple'
        })

    return tasks
```

### 步骤 3：分组任务到功能领域

```python
def group_tasks_by_section(tasks, sections):
    """将任务按功能领域分组"""
    grouped = {sec_num: [] for sec_num in sections}

    for task in tasks:
        if task.get('format') == 'structured' and 'design_section' in task:
            sec = task['design_section'].split('.')[0]  # 取主要章节号
            if sec in grouped:
                grouped[sec].append(task)
            else:
                # 放到第一个未分组
                for sec_num in sorted(grouped.keys()):
                    if not grouped[sec_num]:
                        grouped[sec_num].append(task)
                        break
        else:
            # 简单格式的任务放到第一个领域
            for sec_num in sorted(grouped.keys()):
                if not grouped[sec_num]:
                    grouped[sec_num].append(task)
                    break

    return grouped
```

### 步骤 4：展示 Issue 创建预览

向用户展示将创建的 Issue 结构：

```markdown
## 将创建的 Issues

### 功能领域 Issues（Parent）

| # | 功能领域 | 任务数 |
|---|---------|--------|
| 1 | 3.1 Packet layer becomes optional | 3 |
| 2 | 3.2 Build execution uses normalized feature artifacts | 2 |

### 子任务 Issues（Child）

每个 Parent Issue 下将创建对应的子任务 Issue。
```

### 步骤 5：确认并执行

询问用户：
```
是否确认创建这些 Issues？
- 输入 "y" 确认
- 输入 "n" 取消
- 输入 "d" 仅显示预览，不创建
```

### 步骤 6：创建 Issues

```bash
# 创建功能领域（Parent）Issues
gh issue create \
  --title "[Feature] Packet layer becomes optional" \
  --body "**功能领域**: 3.1 Packet layer becomes optional
**设计依据**: design.md#3.1
**概述**: 将 packet 层从必选降级为可选，解除 build-init 对 packet 的强依赖。

**关联任务**: 3 个子任务" \
  --label "feature"

# 保存返回的 issue 编号
PARENT_NUM=$(gh issue create ... --json 'number' | jq -r '.number')

# 创建子任务 Issue
gh issue create \
  --title "[Task] Deprecate packet-required flag in build-init" \
  --body "**Task ID**: task-1
**Parent Issue**: #${PARENT_NUM}
**变更类型**: refactor
**文件范围**: scripts/vibeflow_build_init.py
**依赖**: 无" \
  --label "task"
```

### Issue 标签规范

| 标签 | 用途 |
|------|------|
| `feature` | 功能领域 parent issue |
| `task` | 子任务 issue |
| `bug` | 缺陷追踪 |
| `enhancement` | 改进项 |
| `question` | 问题 |

---

## 模式 B：PR Comment 同步

### 前置准备

1. 确认当前分支有对应的 open PR：
   ```bash
   gh pr view --json 'number,title,state'
   ```

2. 读取 Review 报告：
   ```bash
   cat docs/changes/<change-id>/verification/review.md
   ```

### 步骤 1：生成 PR Comment 摘要

从 review.md 提取关键结论，生成格式化的 comment：

```markdown
## Review 结论

**日期**: YYYY-MM-DD
**审查范围**: <change-id>

### 结构审查
| 检查项 | 结果 |
|--------|------|
| 架构一致性 | PASS |
| SQL 安全 | PASS |
| 竞态条件 | PASS |

### 回归检查
| 检查项 | 结果 |
|--------|------|
| 全套测试 | PASS |
| 覆盖率 | 85% |
| 安全审计 | PASS |

### 完整性检查
| 检查项 | 结果 |
|--------|------|
| RELEASE_NOTES | PASS |
| 文档同步 | PASS |

### 裁定
**[PASS] — 可进入系统测试**

---
*此评论由 VibeFlow 自动生成*
```

### 步骤 2：展示并确认

向用户展示将提交的 comment 内容，确认后执行：

```bash
gh pr comment create \
  --body "## Review 结论
...
*此评论由 VibeFlow 自动生成*"
```

---

## 集成

**调用者**：
- vibeflow-tasks（Tasks 阶段完成后的 Issue 同步）
- vibeflow-review（Review 完成后的 PR Comment 同步）
- vibeflow-ship（PR 提交，由 Ship 阶段处理）

**依赖**：
- `gh` CLI 已登录
- `jq`（用于 JSON 解析）
- Python 3（用于 Markdown 解析）

**产出**：
- 多个 GitHub Issues（带层级关系）
- PR Comment（如适用）

**不创建 PR**：PR 创建由 vibeflow-ship 负责。
