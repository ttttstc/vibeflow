<!-- 由 vibeflow-router SKILL.md 拆分，完整性由引用者保证 -->

## 功能列表管理

`feature-list.json`是构建清单的**事实来源**。所有阶段转换必须正确更新它。

### 功能列表模式

```json
{
  "version": "1.0",
  "project": "<project-name>",
  "template": "<prototype|web-standard|api-standard|enterprise>",
  "features": [
    {
      "id": "feat-<number>",
      "name": "<feature-name>",
      "description": "<brief-description>",
      "phase-added": "<think|requirements|ucd|design>",
      "status": "<not-started|in-progress|built|review-passed|review-failed|system-test-passed|system-test-failed|qa-passed|qa-failed|shipped>",
      "owner": "<optional-owner>",
      "depends-on": ["<feat-id>", "..."],
      "blocked-by": "<blocker-description or null>",
      "notes": "<optional-notes>"
    }
  ],
  "build-order": ["feat-1", "feat-2", "..."]
}
```

### 更新规则

#### 规则1：阶段推进更新状态

当一个阶段完成时，更新受影响功能的状态：

| 阶段 | 要设置的状态 |
|------|-------------|
| requirements | `not-started`（功能已定义）|
| design | `not-started`（设计完成）|
| build-init | `not-started`（脚手架就绪）|
| build-work | `in-progress` -> `built` |
| review | `review-passed` 或 `review-failed` |
| test-system | `system-test-passed` 或 `system-test-failed` |
| test-qa | `qa-passed` 或 `qa-failed` |
| ship | `shipped` |

#### 规则2：阻塞规则

- 带有`blocked-by`的功能在阻塞者解决之前不得处理
- 阻塞者应该是具体的和可操作的
- 解决阻塞者后，将`blocked-by`设置为`null`

#### 规则3：依赖规则

- `depends-on`定义构建顺序约束
- 禁止循环依赖
- 如果功能A依赖B，B必须先于A构建

#### 规则4：会话期间添加功能

会话中途发现的新功能：
1. 用`phase-added`设置为当前阶段添加到`feature-list.json`
2. 根据当前阶段进度设置状态
3. 在`build-order`中的适当位置插入
4. 通知用户添加

#### 规则5：会话期间修改功能

如果现有功能的范围更改：
1. 不要修改原始功能条目
2. 创建新的功能条目，ID递增（例如feat-1 -> feat-1-v2）
3. 将原始标记为`superseded`
4. 在phase-history.json中记录更改
