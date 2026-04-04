# VibeFlow Workflow Enhancement Plan

**Date:** 2026-04-04  
**Scope:** 基于当前 `vision.md`，参考最新公开的 `gstack` 与 `Superpowers` 能力，对 VibeFlow 交付工作流各阶段的 skill 与流程进行增强规划。  
**Positioning:** 这是一份 control plane 强化方案，不是另一个 agent runtime 设计。

## 1. 背景

VibeFlow 当前已经具备较强的交付骨架：

- 文件驱动 phase router
- spec-driven delivery artifacts
- feature contract
- build / review / test / ship / reflect 全链路
- dashboard、overview、rules、phase invariant

但按最新 `gstack` 与 `Superpowers` 的公开能力对照，VibeFlow 仍存在一个明显特征：

- **规划层和交付编排层相对成熟**
- **执行层、真实 QA、发布闭环仍偏薄**

因此，下一轮增强不应继续扩张 phase 数量，也不应重造 runtime，而应聚焦在：

1. 让计划更可执行  
2. 让实现更隔离、更稳定  
3. 让 QA 更真实  
4. 让发布更完整  
5. 让 skill 设计和 automation 实现保持一致

## 2. 约束与原则

本规划遵守根目录 [vision.md](../../../vision.md) 中的原则：

- 只把 100% 可机械化的东西写成脚本
- 只把必须稳定复现的东西固化成状态机
- 只把经常忘、忘了就出事的东西做成 gate
- 其他尽量留给 agent runtime + skill 提示词 + 项目产物

结论上，VibeFlow 要继续做 **control plane**：

- 负责 phase、contracts、gates、artifacts、recovery、observability
- 不负责重写通用 planner、通用 executor、通用 multi-agent runtime

## 3. 当前工作流评估

### 3.1 探索阶段：`office-hours / brainstorming / spark`

**当前判断：较强**

已有能力：

- `vibeflow-office-hours` 能进行需求澄清、场景压缩、价值判断
- `vibeflow-brainstorming` 与 `vibeflow-design` 已经吸收问题探索逻辑
- 设计前探索与正式设计之间已有衔接

主要问题：

- 触发条件仍偏“可选”
- router 对“需求模糊、范围大、产品不清晰”的自动引导不够积极

增强方向：

- 强化 router 的前置判别逻辑
- 当输入属于模糊需求、产品探索、架构方向选择时，优先引导到 `office-hours` 或 `brainstorming`

### 3.2 计划与设计阶段：`plan / requirements / design / plan-eng-review`

**当前判断：强，但执行粒度不够硬**

已有能力：

- spec-driven 设计与评审
- `requirements.md`、`design.md`、`design-review.md`、`tasks.md`
- 设计阶段已能引入 `rules/` 和工程审查

主要问题：

- `tasks.md` 的执行粒度未被框架强制收紧
- 缺少“执行级 plan validator”
- 任务常常只有意图，没有精确到文件、验证、回滚和依赖
- `tasks.md` 更像说明性清单，还没有达到 `writing-plans` 那种 executor-facing 质量

增强方向：

- 新增计划质量约束，要求任务具备：
  - exact file paths
  - verification steps
  - rollback note
  - dependency note
  - 2-5 分钟级粒度的实施单位
- 将 plan 质量纳入 design 通过前的检查项
- 将 `tasks.md` 从“人类阅读清单”提升为“human-readable + agent-consumable task contract”

建议的任务最低字段：

- `task_id`
- `goal`
- `exact_file_paths`
- `change_type`
- `depends_on`
- `steps`
- `verification_steps`
- `rollback_note`
- `expected_duration_min`

建议的任务质量标准：

- 一个 task 只覆盖一个明确动作
- 一个 task 尽量只触及 1-3 个文件
- `exact_file_paths` 不能为空，禁止使用“相关文件”“必要时修改”这类模糊描述
- `verification_steps` 必须是可执行检查，不接受“人工确认即可”
- `rollback_note` 必须说明最小撤销路径
- `expected_duration_min` 默认控制在 2-5 分钟，超过 10 分钟应强制拆分

建议的 `tasks.md` 风格示例：

```md
### Task T-03 - Normalize feature contract loading

- goal: Ensure build-work always reads normalized feature contracts before task notes
- exact_file_paths:
  - scripts/vibeflow_automation.py
  - scripts/vibeflow_feature_contracts.py
- change_type: behavior-tightening
- depends_on:
  - T-02
- steps:
  - Update build-work entry path to load normalized contract first
  - Preserve backward compatibility for missing contract fields
- verification_steps:
  - Run `python scripts/run_vibeflow_repo_tests.py tests/test_vibeflow_autopilot.py`
  - Confirm failing features still execute with legacy payloads
- rollback_note:
  - Revert contract-first loading path and restore previous payload fallback
- expected_duration_min: 5
```

### 3.3 Build Init 阶段

**当前判断：明显可增强**

已有能力：

- `build-init` 能生成 feature-list、work-config，并进入自动续跑
- 已有 feature contract、project rules、build guide 等输入

主要问题：

- 没有正式的 worktree / isolated workspace 模式
- 对中高风险改动缺少隔离执行策略
- setup 与 baseline smoke check 没有被提升为显式交付能力

增强方向：

- 将 `worktree mode` 升级为正式能力，而不是临时调试手段
- 增加 build-init checklist：
  - baseline branch / diff sanity check
  - isolated workspace creation
  - env/bootstrap validation
  - smoke run before build continuation

### 3.4 Build Work 阶段

**当前判断：最值得优先增强**

已有能力：

- `vibeflow-build-work` 的 skill 设计已经明确了：
  - sequential / parallel
  - subagent per feature
  - per-feature contract execution
  - ST / spec review 并行

主要问题：

- automation 实现仍主要是基于 feature contract 跑命令
- skill 文档中的“subagent-driven development”与实际执行器能力存在落差
- 当前 parallel 更像线程级命令并发，不是真正的 agent orchestration

增强方向：

- 在不重造 runtime 的前提下，补一个更薄的 execution backend 抽象：
  - `command-runner` backend
  - `agent-runner` backend
- feature 执行由“仅命令驱动”升级为：
  - contract-aware
  - verification-aware
  - failure-handling-aware
- 保持 VibeFlow 只负责 orchestration contract，不直接实现通用 agent runtime

### 3.5 TDD / Quality / Debugging

**当前判断：原则强，默认动作还不够硬**

已有能力：

- `vibeflow-quality` 强调新鲜验证证据
- 具备 coverage / mutation / executable rules 的门禁意识

主要问题：

- 失败后的标准动作不够明确
- “系统化调试”存在于文档和引用里，但没有提升成一等执行路径
- 缺少失败分类和重试策略约束

增强方向：

- 把 failure handling 变成 build-work 的正式子流程：
  - reproduce
  - isolate
  - root-cause hypothesis
  - targeted fix
  - re-verify
- 新增调试失败升级规则：
  - 同类失败重复 N 次后停止自动挣扎
  - 自动建议切换为单 feature / 单 worktree / 单阶段修复模式

### 3.6 Review 阶段

**当前判断：检查面强，但节奏仍偏后置**

已有能力：

- 全局 review 的检查面非常完整
- 已包含结构、回归、完整性、critical issue 检查

主要问题：

- review 更偏最后总审查
- 任务之间缺少更细粒度的 review 节点
- 接 review finding 后的标准修复流程没有框架化

增强方向：

- 把 review 拆成两个层次：
  - feature-level review continuity
  - holistic review gate
- 定义 review finding 处理协议：
  - classify
  - assign fix owner
  - selective rerun
  - update evidence

### 3.7 QA 阶段

**当前判断：skill 强，automation 弱**

已有能力：

- `vibeflow-test-qa` 已定义浏览器走查、截图、UCD 对照、交互流、a11y 补充检查

主要问题：

- automation 实现当前仍是执行 `qa_command`
- 文档中的真实浏览器 QA 与系统能力不一致

增强方向：

- 将 QA 接到正式浏览器执行层
- 对 UI 项目默认支持：
  - URL reachability check
  - screenshot capture
  - key path walk
  - issue evidence collection
- 保持浏览器 skill / MCP 为宿主能力调用，不把浏览器 runtime 内嵌进 VibeFlow

### 3.8 Ship 阶段

**当前判断：skill 明显强于 automation**

已有能力：

- ship skill 已覆盖：
  - 版本 bump
  - changelog
  - tag
  - PR
  - 文档同步

主要问题：

- automation 目前更接近“生成 RELEASE_NOTES”
- release checklist 执行不足

增强方向：

- 将 ship automation 升级为 checklist executor：
  - final verification pass
  - version detection and bump
  - release notes materialization
  - optional tag / PR generation
  - publish summary generation

### 3.9 Reflect 阶段

**当前判断：当前够用**

已有能力：

- retro
- 增量请求
- 下轮迭代输入

当前策略：

- 暂不引入 compound / learning engine
- 只补结构化指标与回顾模板质量即可

## 4. 值得优先增强的能力

综合评估后，当前最值得增强的不是更多 phase，而是以下 5 项：

### P0-1. Execution-Grade Planning

目标：

- 让 `tasks.md` 和 feature contract 真正成为“可执行计划”
- 引入 `writing-plans` 风格的执行级任务化能力

需要补的能力：

- 计划粒度约束
- exact file path requirement
- file scope completeness check
- verification step completeness check
- rollback note requirement
- task complexity smell check
- expected duration constraint（2-5 分钟默认粒度）
- machine-consumable task schema

建议产物：

- `tasks.md`：保留人类可读性，但每个任务块必须包含结构化字段
- `task validator`：检查字段完整性、路径存在性、粒度和模糊描述
- `design gate`：当任务不满足执行级要求时，不允许进入 build-init

建议 validator 至少检查：

- 是否存在 `exact_file_paths`
- 路径是否为仓库内可解析路径
- 是否包含至少一个可执行 `verification_step`
- 是否包含 `rollback_note`
- 是否出现模糊词：`相关文件`、`必要时`、`视情况`、`等`
- 是否存在单任务涉及过多文件或过长执行时长

### P0-2. Worktree-Aware Build Init

目标：

- 对中高风险实施默认提供隔离执行场地

需要补的能力：

- build-init 风险等级判断
- isolated workspace / worktree creation policy
- baseline smoke validation
- worktree cleanup / merge handoff policy

### P0-3. Real Subagent Build Work

目标：

- 让 build-work 的真实执行模式与 skill 设计一致

需要补的能力：

- agent-runner backend abstraction
- per-feature execution envelope
- selective parallelism
- failure-aware fallback to sequential

### P1-4. Browser-Native QA

目标：

- 让 QA 从“命令接口”升级成“真实浏览器验证阶段”

需要补的能力：

- browser session orchestration
- screenshot evidence path convention
- key flow QA template
- QA severity + rerun protocol

### P1-5. Real Release Executor

目标：

- 让 ship 成为完整发布闭环，而不是 changelog step

需要补的能力：

- pre-release final checks
- versioning adapter
- release note assembler
- optional tag / PR adapter
- publish summary output

## 5. 分期路线

### Phase A：先补执行内核，不加新 phase

范围：

- execution-grade planning
- worktree-aware build-init
- build-work backend 对齐

交付标准：

- `tasks.md` 可被稳定消费，且达到 `writing-plans` 风格的执行级质量
- 中高风险改动具备隔离执行路径
- build-work 不再只是命令并发器

### Phase B：补末端闭环

范围：

- browser-native QA
- release executor

交付标准：

- UI 项目 QA 真正进入浏览器层
- ship 能完成版本、release 和交付摘要

### Phase C：统一体验与守卫

范围：

- plan validator
- rerun / fallback protocol
- design-to-build continuity guard
- review-to-fix protocol

交付标准：

- 各阶段之间输入输出边界更清晰
- skill 设计与 automation 行为差距显著缩小

## 6. 明确不做什么

为了避免过度设计，本轮增强明确**不做**以下事情：

- 不新增新的顶层 workflow phases
- 不实现一个新的通用 agent runtime
- 不实现一个新的通用 planner
- 不把所有执行细节下沉成脚本
- 不引入 compound / self-improving memory engine
- 不为了“自动化更多”而牺牲 skill 与 runtime 的自然协作

## 7. 成功标准

本规划完成后的判断标准：

- 计划文档能更稳定地驱动执行，而不是只作为阅读材料
- build-init 和 build-work 的风险控制更强
- QA 与 ship 的真实能力与 skill 文档对齐
- 各阶段 automation 只承接可机械化部分，没有滑向 another runtime
- skill、state machine、gate、artifacts 的职责边界更清晰

## 8. 下一步建议

建议按以下顺序继续落地：

1. 先输出 `Execution-Grade Planning` 的设计稿
2. 再输出 `Worktree-Aware Build Init + Build Work Backend` 设计稿
3. 然后补 `Browser-Native QA` 与 `Release Executor`

这是一个“先补执行、再补末端”的路线，而不是“先扩 workflow、后想怎么执行”。
