# VibeFlow Harness Engineering 统一方案

> 日期：2026-03-27
> 状态：Unified Proposal
> 适用对象：VibeFlow 框架自身演进

## 1. 方案目标

本方案用于统一回答一个核心问题：

> 如何在不增加用户认知负担的前提下，增强 VibeFlow 的 harness 控制能力，并让实现尽可能自主闭环。

这里的重点不是把 VibeFlow 做成一个庞大的通用 agent 平台，而是把现有的 workflow、skill、packet、artifact 和 dashboard 这条主链做强，让系统更稳、更可控、更可解释。

---

## 2. 明确边界

本方案遵守以下两个硬边界：

### 2.1 不依赖工具层原生多 agent 调度能力

VibeFlow 不把 Claude / Codex / OpenCode 等宿主工具的原生多 agent 调度能力作为核心架构前提。

这意味着：

- 不建设与宿主强绑定的通用 agent runtime
- 不围绕工具层 scheduler 设计复杂 control plane
- 控制能力主要通过 `skill + hook + policy + packet + artifact + evidence` 实现
- 即使宿主不提供原生多 agent 编排，VibeFlow 也应能稳定工作

### 2.2 不过度设计

VibeFlow 的目标不是做“抽象最完整的平台”，而是做“合理完善、实现闭环”的最小充分系统。

这意味着：

- 先做最有价值的控制能力
- 先增强主链路，再考虑扩展层
- 不为未来假设做过多平台化设计
- 不引入用户当前用不到的复杂概念
- 新增持久化文件数量必须与新增能力成正比，能复用现有状态文件就不新建

---

## 3. 总体判断

当前的 VibeFlow 已经具备强 workflow 基础：

- 有 file-driven routing
- 有 spec-first 的交付前半程
- 有 `build-init` 之后的自动续跑
- 有 `feature-list.json`、packet、result、runtime、dashboard
- 有 review、system-test、QA、quality gates
- 有 `careful / freeze / guard`

但它仍然更像：

> 强 workflow、弱 control layer 的 harness

当前最需要补的，不是：

- 更多 phase
- 更多命令
- 更多技能名称
- 更复杂的多 agent 调度

而是：

- 更明确的不变量
- 更完整的证据与追踪
- 更稳定的 skill-guided execution
- 更系统的 eval 与 drift 治理

---

## 4. 统一设计目标

### 4.1 用户面目标

用户继续只需要理解四件事：

1. 开始流程
2. 在关键节点确认
3. 查看当前状态
4. 必要时介入

用户继续只需要使用：

- `/vibeflow`
- `/vibeflow-quick`
- `/vibeflow-status`
- `/vibeflow-dashboard`

### 4.2 系统面目标

系统内部逐步具备五类能力：

1. `Invariant Engine`
2. `Evidence Plane`
3. `Trace Plane`
4. `Skill-Guided Execution Control`
5. `Eval and Drift Management`

### 4.3 成功标准

如果方案做对了，用户只会感受到：

- 系统更稳
- 中断更少
- 为什么停下更清楚
- 自动推进更可信
- 失败后更容易恢复

---

## 5. 设计原则

### 5.1 Legibility First

系统必须始终可读、可恢复、可审计。

最低要求：

- 当前阶段可定位
- 阻塞原因可解释
- 执行证据可追溯
- 人类接手时不依赖聊天记忆猜上下文

### 5.2 Invariants Over Prompting

关键规则必须由 deterministic 机制 enforce，而不是仅写在 prompt 中。

最低要求：

- 阶段切换有放行条件
- 高风险操作可拦截
- 缺少必要工件时不能误推进

### 5.3 Evidence Before Autonomy

自治能力越强，证据要求越高。

最低要求：

- 自动续跑必须有完成证据
- review / test / ship 不只看文件存在
- 回退和升级路径必须可解释

### 5.4 Skill-Led Control

VibeFlow 的控制力主要体现在 skill、packet、policy、hook 和 artifact 契约上，而不是体现在工具层的底层调度特性上。

最低要求：

- packet 输入明确
- result 输出明确
- allowed tools 明确
- writable scope 明确
- failure / retry / escalation 规则明确

### 5.5 Low Cognitive Load by Default

复杂性应下沉到系统，不应抬升给普通用户。

最低要求：

- 不新增主命令
- 不新增主模式
- 不暴露大量 harness 内部术语
- 只在高价值节点打断用户

### 5.6 Continuous Garbage Collection

harness 必须持续处理熵增。

最低要求：

- 检测 stale artifact
- 检测 spec drift
- 检测 phantom completion
- 清理脏状态和错误恢复分叉

---

## 6. 当前工程基线

### 6.1 已有能力

当前仓库已经具备的关键能力包括：

1. 文件驱动 phase router
2. `Think -> Plan -> Requirements -> Design -> Build -> Review -> Test`
3. `build-init` 后自动推进
4. feature packet / result 文件分离
5. runtime、dashboard、session log
6. quality gates、mutation、review、system-test、QA
7. quick mode eligibility / rollback
8. `careful / freeze / guard`

相关代码与文档：

- [ARCHITECTURE.md](D:/AI/workspace/vibeflow/ARCHITECTURE.md)
- [VIBEFLOW-DESIGN.md](D:/AI/workspace/vibeflow/VIBEFLOW-DESIGN.md)
- [scripts/get-vibeflow-phase.py](D:/AI/workspace/vibeflow/scripts/get-vibeflow-phase.py)
- [scripts/vibeflow_paths.py](D:/AI/workspace/vibeflow/scripts/vibeflow_paths.py)
- [scripts/run-vibeflow-autopilot.py](D:/AI/workspace/vibeflow/scripts/run-vibeflow-autopilot.py)
- [scripts/vibeflow_dashboard.py](D:/AI/workspace/vibeflow/scripts/vibeflow_dashboard.py)

### 6.2 当前主要短板

当前最明显的短板有：

1. artifact presence 仍是很多阶段的主完成信号
2. phase 可见，但 run / attempt / failure trace 不完整
3. 执行约束还不够统一，更多依赖 skill 文本约定
4. eval 还不是 harness 的第一类能力
5. drift / stale / phantom completion 治理不足

---

## 7. 统一目标架构

在现有架构上，建议只增加四层，不做更大平台化扩张：

### 7.1 Phase Policy Layer

职责：

- 定义阶段不变量
- 定义放行条件
- 定义阻塞条件
- 定义需要的工件和证据

建议新增：

- `.vibeflow/policy.yaml`

说明：

- 第一阶段不拆 `.vibeflow/invariants/<phase>.yaml`
- phase invariant、allowed tools、approval rules、escalation rules 统一放进一个 `policy.yaml`

### 7.2 Evidence and Trace Layer

职责：

- 保存完成证据
- 记录执行轨迹
- 支持 dashboard 与问题定位

建议新增：

- 不新增独立目录，优先复用现有文件

第一阶段建议复用：

- `.vibeflow/runtime.json`
- `.vibeflow/logs/session-log.md`
- `docs/changes/<change-id>/verification/`

建议新增对象，但先落在 `runtime.json` 内：

- `run_id`
- `phase_run_id`
- `task_id`
- `attempt_id`
- `last_block_reason`
- `evidence_refs`

第一阶段只新增一个汇总工件：

- `docs/changes/<change-id>/verification/harness-report.md`

### 7.3 Skill-Guided Execution Layer

职责：

- 用 packet、skill contract、result contract 牵引自动执行
- 用 policy 和 scope 控制执行边界
- 在失败后实现稳定恢复

建议新增：

- 第一阶段不新增独立 policy 文件

优先复用：

- `.vibeflow/policy.yaml`
- `.vibeflow/work-config.json`
- `.vibeflow/packets/<change-id>/feature-*.json`
- `.vibeflow/subagent-results/<change-id>/feature-*.json`

### 7.4 Eval and Drift Layer

职责：

- 回归验证 harness
- 发现 spec drift
- 发现 stale artifact
- 发现 phantom completion

建议新增：

- 第一阶段不新增独立 `evals/` 目录

优先复用：

- `validation/`
- `tests/`

第二阶段再视需要引入：

- `validation/harness-scenarios/`
- `tests/test_vibeflow_harness.py`

---

## 8. 文件精简原则

为了不让 harness 增强演变成文件爆炸，本方案采用四条精简原则：

1. 配置合并
`policy` 统一进 `.vibeflow/policy.yaml`，不在第一阶段拆多个配置文件。

2. 运行时复用
`trace` 和 `evidence ref` 优先进入现有 `.vibeflow/runtime.json`，不先建新的 trace store。

3. 验证结果靠近 change
执行与验证汇总优先沉淀到当前 change 的 `verification/` 目录，不新增全局 evidence 目录。

4. 演进式分层
只有当单文件复杂度真的过高，再拆分为目录或 schema 文件。

---

## 9. 不增加认知负担的交互设计

### 8.1 继续保持现有主心智

用户继续理解为：

- 前半程做判断
- 后半程系统自动推进
- 卡住时系统清楚说明

### 8.2 用户只在四类节点被打断

1. 需求或方案待确认
2. 高风险操作待批准
3. 质量门失败
4. 回滚、切回 Full Mode、或关键升级决策

### 8.3 默认输出必须是“人话”

不建议直接对用户输出：

- invariant failed
- trace grading below threshold
- execution policy conflict

建议输出：

- 当前阶段不能继续，因为系统测试证据缺失
- 当前改动包含高风险触点，需要你确认后继续
- 当前任务执行失败，系统已保留已有结果并暂停在可恢复点

### 8.4 Progressive Disclosure

第一层界面只显示：

- 当前阶段
- 当前状态
- 风险等级
- 是否可继续
- 下一步建议

只有展开详情时才显示：

- 缺失工件
- 失败证据
- trace 明细
- 执行结果明细

---

## 10. 第一阶段最值得实现的三大模块

### 9.1 模块一：Phase Invariant Engine

为什么优先：

- 它是 harness 控制力的基础
- 可以立刻减少错误阶段切换
- 对用户完全隐形

第一版建议范围：

- 覆盖 `think / plan / requirements / design / build / review / test / ship`
- 只定义三类不变量：
  - required artifacts
  - required approvals
  - completion evidence

第一版文件新增：

- `.vibeflow/policy.yaml`

第一版验收：

- 缺少关键工件时不能误推进
- dashboard 能明确显示阻塞原因

### 9.2 模块二：Run Trace + Friendly Stop Reason

为什么优先：

- 当前 phase 可见性强，但失败路径解释不足
- trace 会直接提升恢复能力和可解释性

第一版建议范围：

- phase enter / exit
- skill execution start / end
- artifact write
- retry
- failure
- approval

第一版验收：

- 任意一次中断都能回答：
  - 在哪里停下
  - 为什么停下
  - 下一步是什么

第一版文件新增：

- `docs/changes/<change-id>/verification/harness-report.md`

第一版文件复用：

- `.vibeflow/runtime.json`
- `.vibeflow/logs/session-log.md`

### 9.3 模块三：Build Execution Policy

为什么优先：

- `build-work` 是最容易失控的阶段
- 当前已经有 packet / result 基础

第一版建议范围：

- tool allowlist
- writable scope
- timeout
- retry
- conflict domain
- result evidence requirements

第一版验收：

- 自动执行时能提前发现明显冲突
- 单个任务失败不会污染整体状态
- 不依赖宿主原生多 agent 调度，也能实现稳定闭环

第一版文件复用：

- `.vibeflow/policy.yaml`
- `.vibeflow/work-config.json`
- packet / result 现有目录结构

---

## 11. 分阶段实施路线图

### P0：Invariant Foundation

目标：

- 建立 phase invariant engine
- 把关键放行条件结构化

主要交付：

- `.vibeflow/policy.yaml`
- invariant validator
- dashboard 阻塞原因展示

### P1：Trace and Evidence Foundation

目标：

- 建立 execution trace 和 evidence plane

主要交付：

- `.vibeflow/runtime.json` 扩展字段
- `verification/harness-report.md`
- friendly stop reason

### P2：Skill-Guided Execution Control

目标：

- 强化 build 阶段的闭环执行控制

主要交付：

- `policy.yaml` / `work-config.json` 扩展规则
- packet / result contract
- retry / escalation / conflict control

### P3：Eval and Drift Management

目标：

- 让 harness 能被持续验证和持续清理

主要交付：

- `validation/` 下的 harness scenarios
- `tests/` 下的 harness regression tests
- drift / stale / phantom completion checks

---

## 12. 明确不做什么

为遵守边界，本方案明确不优先做：

1. 新增更多主命令
2. 新增更多主模式
3. 围绕宿主工具层能力去设计复杂调度平台
4. 宿主深绑定的通用 multi-agent runtime
5. 用户无感却难维护的大型抽象层
6. 在没有 invariant 和 trace 之前先盲目增强并行能力
7. 在 README 或主交互中暴露大量 harness 内部术语
8. 在第一阶段新增大量中间文件、目录和 schema
9. 在没有单文件压力之前过早拆分配置层

---

## 13. 设计验收标准

后续任何 harness 增强设计，都建议通过这五个问题验收：

1. 用户是否需要学习新概念才能用？
2. 用户是否会被更多低价值中断打扰？
3. 系统是否更容易解释为什么停下？
4. 规则是否由 deterministic 机制 enforce？
5. 出问题时是否更容易恢复？

如果答案是：

- 用户学习成本更高
- 中断更频繁
- 停止原因更模糊
- 规则仍主要靠 prompt
- 恢复更难

那么该设计就不符合本方案。

---

## 14. 最终结论

VibeFlow 下一阶段的正确方向，不是把自己做成一个复杂的 agent 平台，而是把现有 workflow 升级成一个：

- 有不变量
- 有证据
- 有追踪
- 有执行边界
- 有持续评测
- 但对用户仍然简单

的 harness。

用户应该永远只感觉到四件事：

1. 我开始流程
2. 我在关键点做判断
3. 系统自动往后推进
4. 卡住时它清楚告诉我为什么

而框架内部则逐步完成：

- invariant engine
- evidence plane
- trace plane
- skill-guided execution control
- eval and drift management

这就是 VibeFlow 在当前边界下最合理、最克制、也最可实现的 Harness Engineering 统一方案。
