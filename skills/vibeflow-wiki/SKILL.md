---
name: vibeflow-wiki
description: 维护 `docs/overview/` 轻量 RepoWiki 层，负责中文标准格式、生成区块保护、局部刷新和 freshness 检查。
---

# VibeFlow Wiki

## 目标

维护项目级长期上下文入口，使 `docs/overview/` 成为：

- 结构化
- 可持续同步
- 可提交共享
- 可局部更新
- 对后续 Design / Review / Ship 直接有用

## 作用范围

本 skill 只负责以下 3 个正式文档：

- `docs/overview/PROJECT.md`
- `docs/overview/ARCHITECTURE.md`
- `docs/overview/CURRENT-STATE.md`

以及 1 个内部状态文件：

- `.vibeflow/wiki-status.json`

`docs/overview/README.md` 不是正式必选文件，不默认生成。

## 何时使用

### 显式触发

- `/vibeflow-wiki`

### 隐式触发

当出现以下情况时，应考虑调用本 skill：

1. 项目初始化后首次建立 overview
2. brownfield 项目进入 Spark / Design 前，overview 缺失
3. 代码结构、模块边界、入口点、关键决策变化后
4. `CURRENT-STATE.md` 显示 `PROJECT.md` 或 `ARCHITECTURE.md` 已 stale
5. Review / Ship 前需要确认项目底座文档是否同步

## 核心规则

### 规则 1：overview 正文必须使用中文

`docs/overview/` 下所有人类可读正式文档内容统一使用中文。

说明：

- 文件名保留英文命名：`PROJECT.md`、`ARCHITECTURE.md`、`CURRENT-STATE.md`
- 标题、小节、说明文案、更新规则全部用中文

### 规则 2：正式核心文件只有 3 个

只认：

- `PROJECT.md`
- `ARCHITECTURE.md`
- `CURRENT-STATE.md`

不要擅自再拆出一组模块页或流程页，除非用户明确扩展这套标准。

### 规则 3：采用“人工正文 + 生成区块”模式

自动化只允许修改生成区块，例如：

```md
<!-- 生成区块:技术快照 开始 -->
...
<!-- 生成区块:技术快照 结束 -->
```

禁止：

- 重写人工正文
- 覆盖人工填写的目标、边界、关键决策、开放问题

### 规则 4：支持局部刷新

刷新策略必须满足：

- `PROJECT.md`：只更新生成区块
- `ARCHITECTURE.md`：只更新生成区块
- `CURRENT-STATE.md`：允许整篇自动刷新，因为它是纯派生快照，不承载人工正文

### 规则 5：wiki 状态必须可追踪

使用 `.vibeflow/wiki-status.json` 记录：

- 每个 overview 文档的最后刷新时间
- 源输入 hash
- stale 状态
- 生成区块 hash

字段语义：

- 顶层 `source_hash`：当前文档“上次完成同步时”的源输入组合 hash
- `generated_blocks.<区块名>.content_hash`：该生成区块渲染结果的内容 hash
- `stale` / `stale_reasons`：最近一次 freshness 检查得到的状态，而不是人工判断

## 文件职责

### `PROJECT.md`

回答：

- 项目是什么
- 项目目标和非目标是什么
- 核心概念和能力地图是什么
- 下一步设计必须继承哪些边界

### `ARCHITECTURE.md`

回答：

- 项目如何组织
- 模块职责和依赖规则是什么
- 入口与运行流是什么
- 哪些结构约束不能被破坏

### `CURRENT-STATE.md`

回答：

- 当前阶段是什么
- 当前变更是什么
- 现在进展如何
- 哪些 overview 文档可能需要同步

说明：

- 这是纯派生文档
- 允许整篇自动刷新
- 不承载需要人工长期维护的正文

## 执行流程

### 步骤 1：读取现状

读取：

- `.vibeflow/state.json`
- `feature-list.json`
- `rules/`
- 当前源码目录与测试目录
- `docs/changes/<change-id>/...`
- `.vibeflow/wiki-status.json`（如存在）

### 步骤 2：判断刷新范围

判断是：

- 首次生成
- 局部刷新
- 全量重建模板

优先做最小改动，不要默认整篇重写。

### 步骤 3：维护正式文档

确保：

- `PROJECT.md` 存在并符合中文固定结构
- `ARCHITECTURE.md` 存在并符合中文固定结构
- `CURRENT-STATE.md` 已刷新

### 步骤 4：更新 wiki 状态

更新 `.vibeflow/wiki-status.json`：

- `source_hash`
- `last_refreshed_at`
- `generated_blocks`
- `stale`

如果本次只是刷新 `CURRENT-STATE.md`，也要同步回写 `PROJECT.md` / `ARCHITECTURE.md` 的 stale 状态。

### 步骤 5：报告结果

报告应简要说明：

- 刷新了哪些文档
- 哪些文档仍需要人工补写
- 是否存在 stale 文档

## 硬规则

1. 不要把 `docs/changes/` 中的一次性推演直接复制进长期 overview。
2. 不要把根 `README.md` 的产品介绍原样复制为 `PROJECT.md`。
3. 不要新建大量 Wiki 文件增加阅读成本。
4. 不要覆盖人工正文，只能更新生成区块。
5. `CURRENT-STATE.md` 必须反映 overview 是否 stale。

## 与其他 skill 的边界

### `vibeflow-reverse-spec`

- `reverse-spec` 负责触发现有仓库的 overview 刷新
- `wiki` 负责把 overview 保持为可读、可提交、可持续同步的标准入口

具体边界：

- `wiki` 直接基于源码、规则、feature-list 和 active change 生成 overview
- `ARCHITECTURE.md` 应只沉淀长期有效的结构、边界和约束
- `CURRENT-STATE.md` 承担当前变更关注点、风险提示和建议阅读顺序

### `vibeflow-router`

- `router` 负责判断当前阶段
- `wiki` 负责保证阶段消费的 overview 是可用和够新的

### `vibeflow-design`

- `design` 消费 `PROJECT.md` 和 `ARCHITECTURE.md`
- `wiki` 负责在进入 design 前让它们保持可读、可用、不过期
