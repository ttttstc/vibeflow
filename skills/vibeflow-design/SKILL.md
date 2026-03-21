---
name: vibeflow-design
description: Use when VibeFlow needs a technical design document before initialization.
---

# VibeFlow 技术设计

在 `docs/plans/*-design.md` 中生成技术设计文档。

**开始时宣布：**"我正在使用 vibeflow-design skill 来编写技术设计文档。"

## 目的

基于以下内容创建完整的技术设计：
- 批准的需求规格说明书（SRS）
- Plan 审查范围层级
- 技术约束和决策

## 前置条件

运行此 skill 前：
- 需求阶段完成（SRS 存在于 `docs/plans/*-srs.md`）
- Plan 审查已批准

## 第一步：加载输入上下文

### 1.1 读取需求文档

从 `docs/plans/*-srs.md` 获取：
- 所有功能需求（FR-xxx）
- 所有非功能需求（NFR-xxx）
- 所有接口需求（IFR-xxx）
- 验收标准

### 1.2 读取 Plan 审查

从 `.vibeflow/plan-review.md` 或 `docs/plans/YYYY-MM-DD-plan-review.md` 获取：
- 范围层级
- 风险评估
- 修改内容

### 1.3 读取工作流配置

从 `.vibeflow/workflow.yaml` 获取：
- 选择的模板
- 阶段顺序
- 启用的功能

## 第二步：定义架构

### 2.1 架构概述

```markdown
## 1. 架构概述

### 高层架构
[架构图或描述]

### 设计原则
- [原则1]
- [原则2]
```

### 2.2 技术栈

根据模板层级和需求：

**对于 Web Standard：**
```markdown
## 1.x 技术栈

| 组件 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 前端 | React/Vue/Svelte | x.y | UI 框架 |
| 后端 | Node/Python/Go | x.y | API 服务器 |
| 数据库 | PostgreSQL/MongoDB | x.y | 数据存储 |
| ... | ... | ... | ... |
```

**对于 API Standard：**
```markdown
## 1.x 技术栈

| 组件 | 技术 | 版本 | 用途 |
|------|------|------|------|
| API | Node/Python/Go | x.y | REST API |
| 数据库 | PostgreSQL/MongoDB | x.y | 数据存储 |
| 缓存 | Redis/Memcached | x.y | 缓存 |
```

**对于 Enterprise：**
- 更详细的技术决策
- 集成中间件
- 企业消息传递
- 安全基础设施

### 2.3 组件架构

对于每个主要组件：
```markdown
## 1.x [组件名称]

**职责**： [此组件的作用]
**依赖**： [它依赖什么]
**公共 API**： [关键接口]
```

## 第三步：设计数据模型

### 3.1 实体关系

```markdown
## 2. 数据模型

### 实体关系图
[ER 图或描述]

### 核心实体
```

### 3.2 实体定义

对于每个实体：
```markdown
### [实体名称]

| 字段 | 类型 | 约束 | 描述 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| name | string | NOT NULL | 实体名称 |
| ... | ... | ... | ... |
```

### 3.3 数据库 Schema（如适用）

```markdown
## 2.x 数据库 Schema

### [表名称]
```sql
CREATE TABLE [table_name] (
  ...
);
```
```

## 第四步：设计 API

### 4.1 API 概述

```markdown
## 3. API 设计

### API 风格
REST | GraphQL | gRPC

### 基础 URL
`/api/v1`
```

### 4.2 端点定义

对于每个端点：
```markdown
### [METHOD] /api/v1/[resource]

**描述**： [此端点的作用]

**请求**：
```json
{
  "field": "type — description"
}
```

**响应** (200)：
```json
{
  "field": "type — description"
}
```

**错误响应**：
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
```

### 4.3 认证（如适用）

```markdown
## 3.x 认证

**方法**：JWT | OAuth | API Key

**流程**：
[认证流程描述]
```

## 第五步：设计模块结构

### 5.1 目录结构

```markdown
## 4. 模块结构

```
project/
├── src/
│   ├── [module1]/
│   │   ├── index.ts
│   │   ├── [module1].ts
│   │   └── types.ts
│   ├── [module2]/
│   └── ...
├── tests/
├── docs/
└── ...
```
```

### 5.2 模块职责

对于每个模块：
```markdown
## 4.x [模块名称]

**位置**：`src/[module]/`
**职责**： [此模块的作用]
**公共 API**：
- `functionName(params): returnType` — [描述]

**依赖**：
- [此模块依赖的其他模块]
```

## 第六步：设计安全性

### 6.1 认证与授权

```markdown
## 5. 安全设计

### 认证
[用户如何认证]

### 授权
[权限如何强制执行]

### 数据保护
[敏感数据如何保护]
```

### 6.2 安全控制

```markdown
### 输入验证
[如何验证输入]

### 输出编码
[如何编码输出]

### 审计日志
[记录什么]
```

## 第七步：设计测试策略

### 7.1 测试类型

```markdown
## 6. 测试策略

### 单元测试
**框架**：[Jest/Pytest/JUnit]
**覆盖率目标**：[X%]

### 集成测试
**范围**： [测试什么]
**环境**： [如何设置环境]

### 端到端测试
**框架**：[Playwright/Cypress]
**范围**： [测试什么]
```

### 7.2 质量门禁

```markdown
### 质量门禁

| 门禁 | 阈值 |
|------|------|
| 行覆盖率 | 80% |
| 分支覆盖率 | 70% |
| 变异分数 | 70% |
```

## 第八步：设计部署

### 8.1 部署架构

```markdown
## 7. 部署设计

### 基础设施
[部署基础设施描述]

### 配置
[环境配置]
```

### 8.2 环境配置

```markdown
### [环境名称]
**URL**：[URL]
**用途**：[用途]
**配置**：[关键配置值]
```

## 第九步：记录设计决策

### 9.1 关键决策

```markdown
## 8. 设计决策

### DEC-xxx: [标题]
**日期**：YYYY-MM-DD
**状态**：已接受

**上下文**：
[需要解决的问题或决策]

**决策**：
[决定了什么]

**后果**：
[这影响什么]
```

## 第十步：创建功能设计

### 10.1 功能概述

对于每个 FR 需求：
```markdown
## 9.x FR-xxx: [功能名称]

### 概述
[此功能的作用]

### 类图
[适用时的 UML 类图]

### 时序图
[关键交互的时序图]

### 数据流
[数据流描述]
```

### 10.2 接口契约

对于每个功能接口：
```markdown
### 接口契约

| 方法 | 参数 | 返回 | 描述 |
|------|------|------|------|
| methodName | Type | Type | 描述 |
```

### 10.3 边界情况

```markdown
### 边界情况
- [边界情况1]
- [边界情况2]
```

## 第十一步：审查并定稿

### 11.1 自我审查清单

- [ ] 架构支持所有需求
- [ ] 技术栈选择合适
- [ ] 数据模型完整
- [ ] API 设计覆盖所有接口
- [ ] 安全需求已解决
- [ ] 测试策略已定义
- [ ] 部署架构已定义
- [ ] 设计决策已记录

### 11.2 一致性检查

- [ ] 所有 FR 都有相应的设计
- [ ] 所有 NFR 都已处理
- [ ] 所有接口都已设计
- [ ] 无冲突决策

### 11.3 保存文档

文件：`docs/plans/YYYY-MM-DD-<topic>-design.md`

```bash
git add docs/plans/YYYY-MM-DD-<topic>-design.md
git commit -m "docs: add technical design for [project name]"
```

## 检查清单

在标记设计完成前：

- [ ] 架构概述已完成
- [ ] 技术栈已定义
- [ ] 数据模型已设计
- [ ] API 端点已设计
- [ ] 模块结构已定义
- [ ] 安全已设计
- [ ] 测试策略已定义
- [ ] 部署架构已定义
- [ ] 设计决策已记录
- [ ] 所有 FR 都有功能设计
- [ ] 自我审查已通过
- [ ] 文档已保存至 `docs/plans/*-design.md`
- [ ] 文档已提交至 git

## 输出

| 输出 | 位置 | 格式 |
|------|------|------|
| 设计文档 | `docs/plans/YYYY-MM-DD-<topic>-design.md` | Markdown |

## 集成

**调用者：** `vibeflow` 路由（在需求批准后）
**需要：**
- SRS 位于 `docs/plans/*-srs.md`
- Plan 审查位于 `.vibeflow/plan-review.md`
- 工作流配置位于 `.vibeflow/workflow.yaml`
**产生：**
- 设计文档位于 `docs/plans/YYYY-MM-DD-<topic>-design.md`
**链至：** `vibeflow-build-init`（设计批准后）
