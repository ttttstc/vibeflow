---
name: vibeflow-status
description: 查看 VibeFlow 项目当前状态（阶段、进度、待处理项）。
allowed-tools: [Read, Bash]
---

# VibeFlow Status

这是 VibeFlow 的插件可见状态入口。运行时请直接执行：

```bash
python scripts/get-vibeflow-phase.py --project-root . --verbose
```

## 结果要求

- 输出当前 `phase`
- 说明是否存在可恢复的中断点
- 给出建议下一步
- 如果脚本报错，直接展示关键信息并说明缺少什么文件或环境

## 说明

- 这是 marketplace plugin 的正式命令入口，供 `/vibeflow-status` 发现与加载
- 它属于用户可调用 skill，不是内部 skill
