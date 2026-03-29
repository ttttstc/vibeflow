---
name: vibeflow-deepresearch
description: |
  Think 阶段的深度调研引擎。系统性地分析 GitHub 同领域高星项目的
  能力分布、技术栈、产品护城河，输出结构化竞品分析报告，为差异化创新提供情报支持。
  使用场景：用户启动新项目前的竞品调研、需要了解同类项目技术选型、
  寻找差异化机会点、识别竞品护城河。
---

# DeepResearch — Think 阶段的深度调研引擎

**启动宣告：** "正在使用 vibeflow-deepresearch — 深度调研引擎启动。"

## 目标

在用户启动新项目前，系统性地分析同领域高星项目的：
- 竞品发现（GitHub 高星项目）
- 能力矩阵（功能对比）
- 技术栈分布（语言、框架、依赖）
- 产品护城河（竞品的核心壁垒）
- 差异化机会（Gap 识别）

**核心价值：** "了解已有方案"是创新的前提，不是负担。站在巨人肩膀上找差异化。

---

## 输入

- **必需**：用户提供的领域关键词或问题描述
- **可选**：已有的 `context.md`（已有项目背景）

---

## 执行流程

```
用户输入领域关键词
        │
        ├──▶ 4 Agent 并行执行
        │   ├── Agent 1: 竞品发现（GitHub Search）
        │   ├── Agent 2: 技术栈分析
        │   ├── Agent 3: 能力矩阵
        │   └── Agent 4: 护城河调研
        │
        └──▶ 聚合输出
            ├── 竞品分析报告（Markdown）
            ├── 护城河矩阵
            ├── 差异化机会矩阵
            └── 技术选型建议
```

---

## Phase 1: 并行调研（4 Agents）

### Agent 1: 竞品发现

使用 GitHub Search API 搜索同领域高星项目：

```bash
# 搜索策略
gh search repos "<领域> framework" --sort stars --limit 20
gh search repos "topic:<领域>" --sort stars --limit 20
```

**筛选条件：**
- stars > 500
- 最近更新 < 12 months
- 按 stars 降序排列

**输出：** Top 5-10 竞品列表（项目名、Stars、最新更新、简介、技术栈）

---

### Agent 2: 技术栈分析

对竞品列表中的项目，读取其依赖文件：

```bash
# 对每个竞品项目
gh repo view <owner>/<repo> --json name,primaryLanguage
# 读取依赖文件
gh repos clone <owner>/<repo> -- --depth 1
# 或使用 GitHub API 获取文件内容
gh api repos/<owner>/<repo>/contents/package.json
gh api repos/<owner>/<repo>/contents/Cargo.toml
gh api repos/<owner>/<repo>/contents/requirements.txt
gh api repos/<owner>/<repo>/contents/go.mod
```

**分析内容：**
- 主要语言（TypeScript/Python/Rust/Go 等）
- 框架（React/Vue/Express/FastAPI 等）
- 关键依赖
- 架构模式（微服务/单体/Serverless）

**输出：** 技术栈分布统计表

---

### Agent 3: 能力矩阵

对竞品列表中的项目，读取 README.md 提取功能列表：

```bash
gh api repos/<owner>/<repo>/contents/README.md
```

**分析内容：**
- Features 章节下的功能列表
- 支持的功能矩阵（认证、API、数据库、部署等维度）
- 缺失的功能（机会点）

**输出：** 功能对比矩阵表

---

### Agent 4: 产品护城河调研

分析竞品的核心壁垒和护城河：

```bash
# 获取 Stars 增长趋势
gh api repos/<owner>/<repo> --json stargazers_count,forks_count,pushedAt
# 获取贡献者数量
gh api repos/<owner>/<repo>/contributors?per_page=1 --jq '.length'
# 获取开源协议
gh repo view <owner>/<repo> --json license
# 获取 README 中的亮点描述
gh api repos/<owner>/<repo>/contents/README.md
```

**分析维度：**
1. **生态锁定**：插件数量、集成数量、SDK 支持
2. **网络效应**：贡献者数量、社区活跃度、star 趋势
3. **数据积累**：学习资源数量、文档完善度
4. **品牌先发**：开源时间、版本号、社区规模
5. **技术壁垒**：专利、独特架构、专有集成

**输出：** 护城河分析矩阵（每个竞品的核心壁垒）

---

## Phase 2: 聚合输出

将 4 个 Agent 的结果聚合为结构化报告：

**输出路径：** `docs/deepresearch/<timestamp>-<领域>.md`

**报告结构：**
```markdown
# DeepResearch Report: <领域>

**生成时间**: YYYY-MM-DD HH:mm
**调研深度**: <N> 个竞品

## 1. 竞品发现
[表格：项目名、Stars、最新更新、简介]

## 2. 能力矩阵
[功能对比矩阵表]

## 3. 技术栈分布
[语言占比、框架模式、热门依赖]

## 4. 产品护城河
[每个竞品的核心壁垒分析]

## 5. 差异化机会
[Gap 矩阵：机会 vs 竞品覆盖度]

## 6. 技术选型建议
[基于分析的建议]

---
*由 vibeflow-deepresearch 生成*
```

---

## 并行执行说明

4 个 Agent 使用 Agent 工具并行启动，每个 Agent：
- 独立运行，拥有完整上下文
- 按领域关键词执行调研
- 将结果写入临时存储或直接输出

**Agent 提示词模板** 详见 `references/analysis-prompts.md`

---

## 使用示例

### 完整流程

```
用户：我想做一个新的 CLI 工具，用于自动化部署

Assistant：
1. 理解需求：CLI 部署自动化工具
2. 调用 vibeflow-deepresearch
3. 4 个 Agent 并行调研
4. 聚合输出报告
5. 将报告作为 Think 阶段的输入
```

### 单独使用

```
用户：/vibeflow-deepresearch

Assistant：
请提供您想调研的领域或关键词：
> AI Agent 框架

正在启动 4 个并行调研 Agent...
[调研完成]
报告已保存至 docs/deepresearch/2026-03-29-ai-agent-framework.md
```

---

## 集成

**调用者：** 用户主动调用（Think 阶段前置）
**依赖：** 无强制依赖，可独立运行
**产出：** `docs/deepresearch/<timestamp>-<领域>.md`
**Gate：** 无强制 gate，用户选择是否基于报告继续
**链接到：** `vibeflow-think` / `vibeflow-brainstorming`

---

## 参考文档

- 搜索策略：`references/search-strategies.md`
- Agent 提示词模板：`references/analysis-prompts.md`
- 报告模板：`references/output-template.md`
