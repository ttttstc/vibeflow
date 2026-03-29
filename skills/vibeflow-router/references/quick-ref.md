<!-- 由 vibeflow-router SKILL.md 拆分，完整性由引用者保证 -->

## 快速参考卡

### 会话开始检查表

- [ ] 运行`python scripts/get-vibeflow-phase.py`
- [ ] 读取`.vibeflow/phase-history.json`
- [ ] 读取`.vibeflow/work-config.json`
- [ ] 读取`feature-list.json`
- [ ] 检查`.vibeflow/increments/queue.json`
- [ ] 注入会话上下文摘要
- [ ] 如果存在，处理增量
- [ ] 路由到适当的阶段处理器

### 阶段路由图

```
increment --> increment-handler
spark --> vibeflow-spark (问题框定 + DeepResearch + 复杂度扫描 + CEO价值评估)
requirements --> vibeflow-requirements
design --> vibeflow-design (UCD + user approval + eng review + design review + scope decision)
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
| `feature-list.json` | 功能清单和状态 |
| `.vibeflow/increments/queue.json` | 待处理的增量更改 |
| `.vibeflow/workflow.yaml` | 批准的项目计划 |
| `.vibeflow/hooks/session-start.ps1` | Windows会话开始钩子 |
| `.vibeflow/hooks/session-start.sh` | Unix会话开始钩子 |
