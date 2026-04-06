---
name: vibeflow-dashboard
description: 启动 VibeFlow 本地看板，实时查看阶段、功能、产物和最近事件。
allowed-tools: [Read, Bash]
---

# VibeFlow Dashboard

这是 VibeFlow 的插件可见 dashboard 入口。运行时请直接执行：

```bash
python scripts/run-vibeflow-dashboard.py --project-root .
```

## 成功后要做什么

- 把终端输出的本地地址告诉用户
- 说明用浏览器打开即可查看看板
- 说明看板会刷新 workflow 状态、feature 状态、关键产物和最近事件
- 补充一句：如果只想看一次状态摘要，可以改用 `/vibeflow-status`

## 失败时

- 直接说明缺少的依赖、端口占用或项目状态问题
- 告诉用户可先运行 `python scripts/run-vibeflow-dashboard.py --snapshot-json` 或 `/vibeflow-status` 做退路检查

## 说明

- 这是 marketplace plugin 的正式命令入口，供 `/vibeflow-dashboard` 发现与加载
- 它属于用户可调用 skill，不是内部 skill
