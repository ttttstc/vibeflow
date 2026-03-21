---
name: vibeflow-router
description: 在此仓库中用于在会话开始时路由整个VibeFlow生命周期的工作。
---

<EXTREMELY-IMPORTANT>
如果此仓库包含`VIBEFLOW-DESIGN.md`，在执行阶段工作之前必须使用此路由器。
</EXTREMELY-IMPORTANT>

## 会话开始协议

在每个会话的**开始**，无例外地遵循此序列：

### 步骤1：确定当前阶段

运行阶段检测脚本来确定当前会话阶段：

```bash
python scripts/get-vibeflow-phase.py
```

脚本返回以下之一：`increment`、`think`、`template-selection`、`plan-review`、`requirements`、`ucd`、`design`、`build-init`、`build-config`、`build-work`、`review`、`test-system`、`test-qa`、`ship`、`reflect`、`done`

### 步骤2：注入会话上下文

读取以下文件以将上下文注入会话：

1. **`.vibeflow/phase-history.json`** — 已完成阶段和时间戳的历史记录
2. **`.vibeflow/work-config.json`** — 当前工作配置和活动功能
3. **`.vibeflow/feature-list.json`** — 带有构建状态的功能主列表
4. **`VIBEFLOW-DESIGN.md`** — 项目级设计文档（如果存在）

将上下文格式化为清晰的摘要给自己：

```
=== Session Context ===
Current Phase: <phase>
Completed Phases: <list from phase-history.json>
Active Features: <count from feature-list.json>
Pending Actions: <from work-config.json>
====================
```

### 步骤3：检查增量请求

在继续任何计划阶段工作之前，始终检查增量请求：

```bash
cat .vibeflow/increment-queue.txt 2>/dev/null || echo "No pending increments"
```

如果返回`increment`阶段或队列中有待处理的增量，先处理增量，然后再处理其他工作。

### 步骤4：路由到阶段处理器

根据检测到的阶段，调用阶段路由表下方定义的相关技能或脚本。

---

## 阶段路由表

路由器是**文件驱动的**。阶段仅从`scripts/get-vibeflow-phase.py`确定。绝不从内存或对话历史推断阶段。

### 阶段：`increment`

**条件**：有待处理的增量更改请求或用户明确请求增量。

**所需操作：**
1. 读取`.vibeflow/increment-queue.txt`获取待处理增量列表
2. 读取`scripts/increment-handler.py`获取增量处理协议
3. 按队列顺序处理每个增量：
   - 验证增量目标（哪个功能/阶段）
   - 将增量应用到适当的产物
   - 更新`feature-list.json`以反映更改的范围
   - 将增量记录到`phase-history.json`
4. 处理完所有排队的增量后，重新运行`get-vibeflow-phase.py`以确定会话是否应该继续或结束

**退出**：应用所有增量后，重新评估阶段并相应继续。

---

### 阶段：`think`

**条件**：项目需要探索、问题分解或初始概念分析。

**所需操作：**
1. 使用`skills/vibeflow-think/SKILL.md`
2. think阶段的输出应该写入`.vibeflow/think-output.md`
3. think完成后，阶段应该推进到`template-selection`

**关键产出物**：`.vibeflow/think-output.md` — 包含初始项目分析和方向性决策

---

### 阶段：`template-selection`

**条件**：Think阶段完成且必须选择项目模板。

**所需操作：**
1. 彻底阅读`.vibeflow/think-output.md`
2. 阅读`.vibeflow/feature-list.json`以了解初始功能范围
3. 参考模板选择指导（下方第3节）推荐模板
4. 向用户展示推荐及理由
5. 用户确认后：
   - 运行：`python scripts/new-vibeflow-config.py --template <template>`
   - 然后运行：`python scripts/new-vibeflow-work-config.py`
6. 将选定的模板写入`.vibeflow/selected-template.txt`

**退出**：配置生成后，推进到`plan-review`

---

### 阶段：`plan-review`

**条件**：模板已选择且工作流程计划需要审查/批准。

**所需操作：**
1. 使用`skills/vibeflow-plan-review/SKILL.md`
2. plan-review技能将：
   - 读取生成的workflow.yaml
   - 评估完整性和序列合理性
   - 推荐调整或按原样批准
3. 用户必须明确批准计划后才能继续
4. 批准后，更新`.vibeflow/phase-history.json`

**关键产出物**：`.vibeflow/workflow.yaml` — 批准的项目计划

---

### 阶段：`requirements`

**条件**：计划已批准且必须开始需求收集。

**所需操作：**
1. 使用`skills/vibeflow-requirements/SKILL.md`
2. 需求输出应填充：
   - `.vibeflow/requirements.md`
   - 更新`.vibeflow/feature-list.json`
3. 每个需求必须可追溯到`feature-list.json`中的功能

**关键产出物**：`.vibeflow/requirements.md` — 详细需求文档

---

### 阶段：`ucd`（用例设计）

**条件**：需求已完成且必须设计用例。

**所需操作：**
1. 使用`skills/vibeflow-ucd/SKILL.md`
2. UCD输出应填充：
   - `.vibeflow/use-cases.md`
   - 更新`.vibeflow/feature-list.json`将功能链接到用例
3. 每个用例必须引用它满足的需求

**关键产出物**：`.vibeflow/use-cases.md` — 用例规范

---

### 阶段：`design`

**条件**：用例已完成且必须开始技术设计。

**所需操作：**
1. 使用`skills/vibeflow-design/SKILL.md`
2. 设计输出应填充：
   - `.vibeflow/design.md` — 技术架构和设计决策
   - `.vibeflow/feature-list.json` — 更新每个功能的设计状态
3. 设计必须涵盖：
   - 组件架构
   - 数据模型
   - API契约（如适用）
   - 技术选型（供应商中立的命名）

**关键产出物**：`.vibeflow/design.md` — 技术设计规范

---

### 阶段：`build-init`

**条件**：设计已完成且必须发生构建初始化。

**所需操作：**
1. 使用`skills/vibeflow-build-init/SKILL.md`
2. build-init应该：
   - 初始化项目结构
   - 设置依赖
   - 创建初始构建配置
   - 在`feature-list.json`中将功能标记为`init-started`
3. 此阶段创建物理项目脚手架

**关键产出物**：工作目录中的项目脚手架

---

### 阶段：`build-config`

**条件**：build-init已完成且需要特定于功能的配置。

**所需操作：**
1. 运行：`python scripts/new-vibeflow-work-config.py`
2. 此脚本读取`feature-list.json`并生成：
   - `.vibeflow/work-config.json` — 特定于功能的构建裁剪
   - 每个功能的配置文件
3. 审查生成的配置的完整性
4. 如果配置不完整，标记错误并不继续

**关键产出物**：`.vibeflow/work-config.json` — 工作裁剪配置

---

### 阶段：`build-work`

**条件**：build-config已完成且实际功能实现开始。

**所需操作：**
1. 使用`skills/vibeflow-build-work/SKILL.md`
2. build-work遍历`feature-list.json`中的功能：
   - 根据规范实现每个功能
   - 更新功能状态：`in-progress`、`built`、`blocked`
   - 将构建进度记录到`.vibeflow/build-log.json`
3. 如果一个功能被阻塞，在`feature-list.json`中记录阻塞者并继续处理未阻塞的功能

**关键产出物**：项目结构中已实现的功能

---

### 阶段：`review`

**条件**：所有可构建的功能已完成且需要代码审查。

**所需操作：**
1. 使用`skills/vibeflow-review/SKILL.md`
2. 审查应该：
   - 根据规范检查所有已构建的功能
   - 验证feature-list.json的准确性
   - 识别缺陷或缺失的功能
   - 将功能状态更新为`review-passed`或`review-failed`
3. 如果审查失败，为受影响的功能路由回`build-work`

**关键产出物**：`.vibeflow/review-report.md`中的审查报告

---

### 阶段：`test-system`

**条件**：审查已通过且需要系统级测试。

**所需操作：**
1. 使用`skills/vibeflow-test-system/SKILL.md`
2. 系统测试应该：
   - 在所有已构建的功能上运行集成测试
   - 验证端到端工作流
   - 将功能状态更新为`system-test-passed`或`system-test-failed`
3. 将测试结果记录到`.vibeflow/test-results/system-tests.json`

**关键产出物**：`.vibeflow/test-results/`中的系统测试结果

---

### 阶段：`test-qa`

**条件**：系统测试已通过且需要QA验证。

**所需操作：**
1. 使用`skills/vibeflow-test-qa/SKILL.md`
2. QA测试应该：
   - 执行手动或自动化QA验证
   - 根据requirements.md验证
   - 确认功能完整性
   - 将功能状态更新为`qa-passed`或`qa-failed`
3. 将QA结果记录到`.vibeflow/test-results/qa-tests.json`

**关键产出物**：`.vibeflow/test-results/`中的QA测试结果

---

### 阶段：`ship`

**条件**：所有测试已通过且项目已准备好部署。

**所需操作：**
1. 使用`skills/vibeflow-ship/SKILL.md`
2. Ship应该：
   - 定稿所有交付物
   - 创建发布产物
   - 将feature-list.json更新为`shipped`
   - 归档项目会话
3. 如果尚不存在，生成`VIBEFLOW-DESIGN.md`

**关键产出物**：发布产物和归档会话

---

### 阶段：`reflect`

**条件**：项目会话已结束且需要回顾性分析。

**所需操作：**
1. 使用`skills/vibeflow-reflect/SKILL.md`
2. 反思应该：
   - 审查phase-history.json中的模式
   - 识别做得好的和做得不好的
   - 用发现的模式更新`tasks/lessons.md`
   - 生成改进建议
3. 反思输出到`.vibeflow/retro.md`

**关键产出物**：`.vibeflow/retro.md` — 回顾笔记

---

### 阶段：`done`

**条件**：所有阶段已完成且不需要进一步工作。

**所需操作：**
1. 生成完成摘要：
   - 完成的总阶段数
   - 已发布的功能数
   - 用时（从phase-history.json）
   - 指向retro.md的链接（如果执行了反思）
2. 向用户展示摘要
3. 报告任何剩余的开放项或推荐的 next steps

**摘要格式：**
```
=== Project Complete ===
Phases Completed: <list>
Features Shipped: <count>/<total>
Total Duration: <time>
Retro: <link or "not performed">
Next Steps: <optional recommendations>
====================
```

---

## 模板选择指导

使用以下决策框架来推荐适当的模板。将项目特征与模板配置文件进行匹配。

### 模板配置文件

#### `prototype`

**最适合**：快速探索、概念验证、MVP验证、学习实验

**特点**：
- 速度优于结构
- 最小的测试要求
- 小团队（1-3人）
- 对返工的高容忍度
- 范围可能大幅变化

**推荐prototype的指标**：
- 用户想要"尝试"一个想法
- 需求模糊或预期会演变
- 时间约束是首要考虑
- 为了学习而构建，而不是为了发布
- 单个开发者或非常小的团队

#### `web-standard`

**最适合**：标准Web应用程序、CRUD应用程序、仪表板、内容网站

**特点**：
- 平衡的结构和速度
- 标准Web技术栈（前端+后端）
- 典型关系型数据库
- 标准测试金字塔
- 团队规模2-5人

**推荐web-standard的指标**：
- 具有用户和数据的典型Web应用程序
- 标准请求/响应范式
- 没有专门的集成要求
- 中等复杂度
- 常规Web应用

#### `api-standard`

**最适合**：后端API、微服务、集成层、数据管道

**特点**：
- API优先设计
- 没有前端（或最少）
- 可能涉及多个服务
- 契约测试很重要
- 团队规模2-6人

**推荐api-standard的指标**：
- 主要输出是API
- 其他系统将消费输出
- 复杂数据处理或转换
- 高集成要求
- 面向服务的架构

#### `enterprise`

**最适合**：大规模系统、任务关键型应用程序、多团队项目

**特点**：
- 完整的治理和合规性
- 多个集成点
- 全面测试（单元、集成、e2e、性能）
- 正式审查关卡
- 团队规模6人以上

**推荐enterprise的指标**：
- 正式合规要求
- 多个团队贡献
- 需要任务关键型可靠性
- 复杂的利益相关者管理
- 预期的长期维护

### 决策流程图

```
START: 阅读think-output.md
  |
  v
速度是首要考虑吗？
  |-- 是 --> 这是学习/探索项目吗？
  |           |-- 是 --> 推荐：prototype
  |           |-- 否 --> 团队规模 <= 3？
  |                     |-- 是 --> 推荐：prototype
  |                     |-- 否 --> 推荐：web-standard
  |
  v (否)
这主要是API或后端服务吗？
  |-- 是 --> 团队规模 >= 6 或任务关键型？
  |           |-- 是 --> 推荐：enterprise
  |           |-- 否 --> 推荐：api-standard
  |
  v (否)
这是标准Web应用程序吗？
  |-- 是 --> 团队规模 >= 6？
  |           |-- 是 --> 推荐：enterprise
  |           |-- 否 --> 推荐：web-standard
  |
  v (否)
这是探索性或POC吗？
  |-- 是 --> 推荐：prototype
  |
  v (否)
默认 --> 推荐：web-standard
```

### 模板确认问题

在最终确定模板推荐之前，与用户确认：

1. "推荐的是[recommended template]正确吗？您说这是一个[from think-output的简要描述]。"

2. "这些因素中有改变决定的吗？"（展示关键决策因素）

3. "准备好用--template [template]生成配置了吗？"

---

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

---

## 错误恢复

当产物不一致时，遵循此恢复协议。

### 检测：产物不一致

当发生以下情况时，存在产物不一致：
- 阶段表示已完成但缺少必需的产物
- `feature-list.json`中的功能状态与物理状态不匹配
- `work-config.json`引用了`feature-list.json`中不存在的功能
- `phase-history.json`有间隙或顺序错误的条目
- 当前阶段缺少必需的文件（requirements.md、design.md等）

### 恢复协议

#### 步骤1：评估不一致

读取受影响的产物并确定：
- 哪个阶段记录了不一致
- 受影响的功能是哪些
- 问题是否可恢复或需要重新开始

#### 步骤2：对问题进行分类

**类型A — 缺少可选产物**
- 该产物对于推进不是严格必需的
- 操作：记录差距，创建占位符，继续
- 示例：reflect完成时缺少`retro.md`

**类型B — 缺少必需产物**
- 该产物是下一阶段必需的
- 操作：确定是否可以从前身产物重建
- 示例：缺少`design.md`但`requirements.md`和`use-cases.md`存在

**类型C — 状态不匹配**
- 功能状态与物理状态不匹配
- 操作：根据物理状态纠正状态，而不是反过来
- 示例：功能标记为`shipped`但代码不在发布位置

**类型D — 结构损坏**
- JSON文件格式错误或不可读
- 操作：尝试解析和修复，如果不可能，从最后一个有效状态重建
- 示例：`feature-list.json`被截断

#### 步骤3：执行恢复

**对于类型A：**
```
1. 将缺失的产物创建为存根
2. 记录："已恢复：在<date>创建了占位符<artifact>"
3. 继续阶段
```

**对于类型B：**
```
1. 检查产物是否可以重建
2. 如果可以：重建并记录恢复
3. 如果不可以：确定最后一个有效阶段，提供用户选择：
   a) 从最后一个有效阶段重建
   b) 手动创建产物
4. 在phase-history.json中记录差距
```

**对于类型C：**
```
1. 不要更改物理文件以匹配状态
2. 更新feature-list.json以反映物理现实
3. 记录："已恢复：在<date>将<feat-id>的状态纠正为<actual-status>"
4. 如果这影响构建顺序，重新生成work-config.json
5. 根据更正后的状态继续
```

**对于类型D：**
```
1. 尝试带错误恢复的JSON解析
2. 如果不可恢复，读取最后一个有效备份（如果存在）
3. 如果没有备份，从phase-history.json记录重建
4. 记录损坏事件
5. 通知用户数据丢失程度
```

#### 步骤4：记录恢复

对于任何恢复操作（类型B、C、D），添加到phase-history.json的条目：

```json
{
  "event": "recovery",
  "date": "<ISO-8601>",
  "type": "<A|B|C|D>",
  "description": "<what was wrong>",
  "resolution": "<what was done>",
  "artifacts-affected": ["<list>"]
}
```

---

## 钩子集成

会话开始钩子为常规设置任务提供自动化。

### session-start.ps1 (Windows)

位置：`.vibeflow/hooks/session-start.ps1`

**行为：**
- 在会话开始时自动执行（在阶段路由之前）
- 在Windows上运行PowerShell
- 必须在阶段路由开始之前完成
- 非阻塞失败不应阻止会话

**典型操作：**
- 从远程拉取最新更改
- 检查必需的工具有无更新
- 验证环境先决条件
- 设置特定于会话的环境变量

**示例内容：**
```powershell
# VibeFlow Session Start Hook
Write-Host "=== VibeFlow Session Start ===" -ForegroundColor Cyan

# Pull latest if on main branch
$branch = git branch --show-current
if ($branch -eq "main") {
    Write-Host "Pulling latest from main..."
    git pull
}

# Verify Python environment
python --version | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Python not found" -ForegroundColor Yellow
}

Write-Host "=== Starting Phase Routing ===" -ForegroundColor Cyan
```

### session-start.sh (Unix/Linux/macOS)

位置：`.vibeflow/hooks/session-start.sh`

**行为：**
- 在会话开始时自动执行（在阶段路由之前）
- 在POSIX shell（bash/zsh兼容）中运行
- 必须在阶段路由开始之前完成
- 非阻塞失败不应阻止会话

**典型操作：**
- 从远程拉取最新更改
- 检查必需的工具有无更新
- 验证环境先决条件
- 设置特定于会话的环境变量

**示例内容：**
```bash
#!/bin/bash
# VibeFlow Session Start Hook

echo "=== VibeFlow Session Start ==="

# Pull latest if on main branch
branch=$(git branch --show-current)
if [ "$branch" = "main" ]; then
    echo "Pulling latest from main..."
    git pull
fi

# Verify Python environment
if ! command -v python &> /dev/null; then
    echo "WARNING: Python not found"
fi

echo "=== Starting Phase Routing ==="
```

### 钩子配置

要启用钩子，请将以下内容添加到您的环境或shell配置文件中：

**Windows (PowerShell)：**
```powershell
$VIBEFLOW_HOOK_ENABLED = $true
```

**Unix：**
```bash
export VIBEFLOW_HOOK_ENABLED=true
```

### 钩子执行规则

1. 钩子在阶段确定之前运行
2. 钩子失败会产生警告但不会阻止路由
3. 钩子应该是幂等的（多次运行安全）
4. 钩子应该在<10秒内完成
5. 对于长时间运行的操作，使用后台任务

---

## 硬规则

这些规则是**不可协商的**。违反可能导致路由到错误的阶段或数据损坏。

### 规则1：供应商中立命名

始终使用VibeFlow别名名称而不是底层基础名称。

| 使用这个 | 不是那个 |
|----------|----------|
| Vector store | Chroma, Pinecone, Weaviate |
| LLM | GPT-4, Claude, Gemini |
| Embedding model | text-embedding-ada-002, bge-large |
| Framework | LangChain, LlamaIndex |
| Runtime | Docker, Kubernetes |

**理由：** 项目不应与特定供应商紧密耦合。如果供应商更改定价、功能或可用性，迁移应该只需要最少的代码更改。

**例外：** 在`design.md`和技术规范中，当您**明确要求**特定供应商时，您可以引用特定供应商。

### 规则2：文件驱动优于记忆

阶段必须从`scripts/get-vibeflow-phase.py`读取。绝不：

- 从对话上下文推断阶段
- 根据经过的时间假设阶段
- 在没有验证的情况下信任前一会话的阶段
- 使用"上次我们在做什么"的记忆

**如果`get-vibeflow-phase.py`缺失或损坏：**
1. 尝试从`phase-history.json`重建阶段
2. 将重建呈现给用户确认
3. 在阶段确认之前不要继续

### 规则3：功能列表是事实来源

所有功能相关决策必须引用`feature-list.json`：

- 构建顺序来自`build-order`数组
- 功能状态来自各个功能条目
- 依赖从`depends-on`数组解析
- 阻塞从`blocked-by`字段确定

**绝不：**
- 在不检查状态的情况下假设功能已完成
- 在带有非空`blocked-by`的功能上开始工作
- 在不更新依赖项的情况下重新排序`build-order`

### 规则4：阶段历史是仅追加的

`phase-history.json`中的条目记录发生的事情。它们不应在事后修改：

- 不要编辑过去的阶段条目
- 不要删除阶段条目
- 不要重新排序阶段条目
- 恢复事件是**添加的**，不是插入过去的

**理由：** 阶段历史提供审计跟踪。修改它会破坏跟踪项目演变的目的。

### 规则5：未经用户同意不得阶段回归

阶段应该向前推进（think -> template-selection -> plan-review -> ... -> done）。回归（向后）只应在以下情况下发生：

- 用户明确要求时
- 恢复协议识别出必要的回滚时
- 审查/测试失败并需要返工时

**绝不回归阶段：**
- 只是因为当前阶段感觉困难
- 为了"再次检查"已经完成的事情
- 因为不同的方法"看起来更好"

### 规则6：产物保持同步

所有相关产物必须一起更新：

- 完成设计 -> 更新`feature-list.json` **并且**写`design.md`
- 完成build-work -> 更新功能状态**并且**物理文件存在
- 完成ship -> 标记功能为`shipped` **并且**发布产物存在

**如果您更新了一个但没有更新另一个，这是一个必须恢复的不一致。**

### 规则7：增量队列是FIFO

增量按先进先出顺序处理：

- 首先处理最旧的增量
- 不要跳过队列中的下一步
- 不要同时处理多个增量
- 处理完所有增量后，重新评估阶段

**理由：** 保留更改的逻辑顺序。用户可能在增量之间有依赖关系。

---

## 快速参考卡

### 会话开始检查表

- [ ] 运行`python scripts/get-vibeflow-phase.py`
- [ ] 读取`.vibeflow/phase-history.json`
- [ ] 读取`.vibeflow/work-config.json`
- [ ] 读取`.vibeflow/feature-list.json`
- [ ] 检查`.vibeflow/increment-queue.txt`
- [ ] 注入会话上下文摘要
- [ ] 如果存在，处理增量
- [ ] 路由到适当的阶段处理器

### 阶段路由图

```
increment --> increment-handler
think --> vibeflow-think
template-selection --> new-vibeflow-config.py + new-vibeflow-work-config.py
plan-review --> vibeflow-plan-review
requirements --> vibeflow-requirements
ucd --> vibeflow-ucd
design --> vibeflow-design
build-init --> vibeflow-build-init
build-config --> new-vibeflow-work-config.py
build-work --> vibeflow-build-work
review --> vibeflow-review
test-system --> vibeflow-test-system
test-qa --> vibeflow-test-qa
ship --> vibeflow-ship
reflect --> vibeflow-reflect
done --> (generate summary)
```

### 关键文件位置

| 文件 | 目的 |
|------|------|
| `.vibeflow/phase-history.json` | 阶段完成审计跟踪 |
| `.vibeflow/work-config.json` | 当前工作配置 |
| `.vibeflow/feature-list.json` | 功能清单和状态 |
| `.vibeflow/increment-queue.txt` | 待处理的增量更改 |
| `.vibeflow/workflow.yaml` | 批准的项目计划 |
| `.vibeflow/hooks/session-start.ps1` | Windows会话开始钩子 |
| `.vibeflow/hooks/session-start.sh` | Unix会话开始钩子 |
