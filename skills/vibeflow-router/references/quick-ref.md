<!-- 由 vibeflow-router SKILL.md 拆分，完整性由引用者保证 -->

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
