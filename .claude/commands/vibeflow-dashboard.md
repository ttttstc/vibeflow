---
description: 启动 VibeFlow 本地看板，实时查看阶段、功能、产物和最近事件
---
运行 `python scripts/run-vibeflow-dashboard.py --project-root .`，启动当前项目的本地 live dashboard。

如果启动成功，直接把终端输出的本地地址告诉用户，并说明：

- 用浏览器打开这个地址即可查看看板
- 看板会自动刷新当前 workflow 状态
- 如果只想看一次状态摘要，也可以改用 `/vibeflow-status`
