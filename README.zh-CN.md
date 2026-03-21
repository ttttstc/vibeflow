# VibeFlow

VibeFlow 是一个基于仓库驱动的开发工作流框架，通过结构化的 skill 定义和文件驱动的阶段路由，实现项目从 Think 到 Reflect 的完整生命周期管理。

## 框架简介

VibeFlow 提供：

- 统一的 `vibeflow-*` skill 命令规范
- 基于仓库文件状态确定当前阶段路由
- 不同粒度的精细化项目模板配置
- 结构化的动态文件 `.vibeflow/`
- 使用多层次验证的项目生命周期管理，支持仓库级别和项目级别验证

## 七阶段流程

项目的核心生命周期：

1. Think（思考）
2. Plan Review（计划评审）
3. Requirements（需求）
4. UCD（用例设计）
5. Design（设计）
6. Build（构建）
7. Review（评审）
8. Test（测试）
9. Ship（发布）
10. Reflect（复盘）

## 仓库结构

```text
skills/       核心流程和检查点定义
scripts/      Python 项目管理脚本
templates/    动态配置模板
hooks/        会话管理和注册钩子
validation/   项目验证和示例项目
```

## 运行时文件

项目运行时的动态文件位于 `.vibeflow/` 下，包括：

- `.vibeflow/think-output.md` - 思考阶段输出
- `.vibeflow/workflow.yaml` - 工作流配置
- `.vibeflow/work-config.json` - 构建配置
- `.vibeflow/plan-review.md` - 计划评审记录
- `.vibeflow/review-report.md` - 评审报告
- `.vibeflow/qa-report.md` - QA 报告
- `.vibeflow/retro-YYYY-MM-DD.md` - 复盘记录
- `.vibeflow/increment-request.json` - 增量请求

项目文档保存在项目目录下：

- `docs/plans/*-srs.md` - 需求规格说明
- `docs/plans/*-ucd.md` - 用例设计文档
- `docs/plans/*-design.md` - 设计文档
- `docs/plans/*-st-report.md` - 系统测试报告
- `docs/test-cases/feature-*.md` - 功能测试用例
- `feature-list.json` - 特性列表
- `task-progress.md` - 任务进度
- `RELEASE_NOTES.md` - 发布说明

## 快速开始

1. 在目标项目目录初始化 VibeFlow
2. 从 Think 阶段开始，编写 `.vibeflow/think-output.md`
3. 生成工作流配置

```bash
python scripts/new-vibeflow-config.py --template api-standard --project-root <target-project>
```

4. 生成构建配置

```bash
python scripts/new-vibeflow-work-config.py --project-root <target-project>
```

5. 检测当前阶段

```bash
python scripts/get-vibeflow-phase.py --project-root <target-project> --json
```

6. 验证设置是否正确

```bash
python scripts/test-vibeflow-setup.py --project-root <target-project> --json
```

## 模板说明

当前支持的模板类型：

- `prototype` - 原型项目
- `web-standard` - Web 标准项目
- `api-standard` - API 标准项目
- `enterprise` - 企业级项目

模板配置决定：

- 哪些阶段是必需的
- 是否强制检查点验证
- 是否包含 UI 相关验证路径
- 是否需要 Reflect 阶段

## 文档

- `ARCHITECTURE.md`: 框架架构和技术架构图
- `USAGE.md`: 项目使用说明
- `VIBEFLOW-DESIGN.md`: 设计理念说明
- `README.md`: 英文概述

## 验证项目

仓库包含一个完整的验证项目：

- `validation/sample-priority-api`

运行验证命令：

```bash
python -m unittest discover -s validation/sample-priority-api/tests -v
python scripts/get-vibeflow-phase.py --project-root validation/sample-priority-api --json
python scripts/test-vibeflow-setup.py --project-root validation/sample-priority-api --json
```
