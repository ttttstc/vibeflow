# VibeFlow

VibeFlow 是一个仓库内本地化的软件交付工作流编排层。
它通过本地 skill、基于文件的阶段路由、静态模板和 `.vibeflow/` 运行态文件，把一个项目从 Think 一直推进到 Reflect。

## 能力概览

VibeFlow 提供：

- 统一的 `vibeflow-*` skill 命名面
- 基于仓库文件状态的确定性阶段路由
- 不同严格度的静态工作流模板
- 生成式运行态文件 `.vibeflow/`
- 使用独立样例项目进行流程验证，而不是直接拿框架仓库自证

## 生命周期

目标项目按以下阶段推进：

1. Think
2. Plan Review
3. Requirements
4. UCD（按需）
5. Design
6. Build Init
7. Build Work
8. Review
9. Test
10. Ship
11. Reflect

## 仓库结构

```text
skills/       本地工作流技能与阶段别名
scripts/      Python 路由与配置脚本
templates/    静态工作流模板
hooks/        会话上下文注入入口
validation/   用于验证工作流的独立样例项目
```

## 核心文件

目标项目的运行态文件放在 `.vibeflow/` 下，常见产物包括：

- `.vibeflow/think-output.md`
- `.vibeflow/workflow.yaml`
- `.vibeflow/work-config.json`
- `.vibeflow/plan-review.md`
- `.vibeflow/review-report.md`
- `.vibeflow/qa-report.md`
- `.vibeflow/retro-YYYY-MM-DD.md`
- `.vibeflow/increment-request.json`

交付产物保留在项目常规路径中：

- `docs/plans/*-srs.md`
- `docs/plans/*-ucd.md`
- `docs/plans/*-design.md`
- `docs/plans/*-st-report.md`
- `docs/test-cases/feature-*.md`
- `feature-list.json`
- `task-progress.md`
- `RELEASE_NOTES.md`

## 快速开始

1. 创建或选择一个目标项目。
2. 从 Think 阶段开始，先写 `.vibeflow/think-output.md`。
3. 生成 workflow 文件：

```bash
python scripts/new-vibeflow-config.py --template api-standard --project-root <target-project>
```

4. 生成 build 配置：

```bash
python scripts/new-vibeflow-work-config.py --project-root <target-project>
```

5. 检测当前阶段：

```bash
python scripts/get-vibeflow-phase.py --project-root <target-project> --json
```

6. 验证配置是否完整：

```bash
python scripts/test-vibeflow-setup.py --project-root <target-project> --json
```

## 模板

当前可用模板：

- `prototype`
- `web-standard`
- `api-standard`
- `enterprise`

模板会控制：

- 哪些阶段是必须的
- 质量门禁强度
- 是否启用 UI 专属验证路径
- 是否要求 Reflect 阶段

## 文档

- `ARCHITECTURE.md`: 实现架构与完整流程图
- `USAGE.md`: 目标项目使用说明
- `VIBEFLOW-DESIGN.md`: 精简设计说明
- `README.md`: 英文概览

## 验证项目

仓库内包含一个独立验证样例：

- `validation/sample-priority-api`

常用验证命令：

```bash
python -m unittest discover -s validation/sample-priority-api/tests -v
python scripts/get-vibeflow-phase.py --project-root validation/sample-priority-api --json
python scripts/test-vibeflow-setup.py --project-root validation/sample-priority-api --json
```
