# TODOS

## P1 — Critical

### TODO-1: 修复 new-vibeflow-work-config.py 中 test.system 检测逻辑 bug

**问题：** `scripts/new-vibeflow-work-config.py:43` 中 `test.system` 的检测使用了 `'required: true' in content`，会匹配 YAML 中任何位置的 `required: true`，而非仅匹配 `st:` 部分。对 prototype 模板（st.required: false）会产生错误结果。同一条件还重复了两次。

**修复：** 替换为正则匹配 `re.search(r'st:[\s\S]*?required:\s+true', content) is not None`，与 `qa` 的检测方式保持一致。

**工作量：** S | **优先级：** P1 | **依赖：** 无

---

### TODO-2: 充实 14 个空壳 skill 的完整执行流程

**问题：** 18 个 skill 中有 14 个仅包含 3-7 行概要描述（vibeflow-tdd、vibeflow-quality、vibeflow-build-work、vibeflow-build-init、vibeflow-feature-st、vibeflow-spec-review、vibeflow-review、vibeflow-ship、vibeflow-reflect、vibeflow-test-system、vibeflow-test-qa、vibeflow-plan-review、vibeflow-requirements、vibeflow-design）。当前指导太模糊，AI 执行时行为不可预测。

**目标：** 参考 long-task 对应 skill 的逻辑，审视并重写为适用于 vibeflow 工作流的独立完整内容。与 long-task 完全解耦。每个 skill 应包含：明确的执行步骤、检查清单、输出格式要求、质量门禁规则。

**工作量：** XL（14 个 skill × 100-200 行） | **优先级：** P1 | **依赖：** 无

---

### TODO-3: 为框架核心脚本添加单元测试

**问题：** VibeFlow 框架本身没有任何测试。`detect_phase()` 有 16 个分支条件，是路由核心，却完全无测试覆盖。验证项目中的 6 个测试仅覆盖示例 API 业务逻辑。

**目标：** 为 `detect_phase()`（16 个分支全覆盖）、`new-vibeflow-config.py`（模板复制+日期替换）、`new-vibeflow-work-config.py`（正则解析+JSON生成）编写 Python 单元测试。

**工作量：** M | **优先级：** P1 | **依赖：** TODO-1（修复 bug 后再写测试）

---

### TODO-8: 移植 9 个验证脚本到 vibeflow

**问题：** vibeflow 的 18 个 skill 内部引用了 long-task 的验证脚本（build-work 调用 `validate_features.py`、feature-st 调用 `validate_st_cases.py`、build-init 需要 `init_project.py` 脚手架等），但这些脚本在 vibeflow 中完全不存在。没有它们，工作流在 build-init 阶段就会断裂。

**目标：** 从 long-task 移植以下 9 个脚本到 `scripts/`，调整路径约定为 vibeflow 风格（`.vibeflow/` 而非项目根目录）：
1. `init_project.py` — 项目脚手架（feature-list.json、task-progress.md、RELEASE_NOTES.md 等）
2. `validate_features.py` — feature-list.json 格式和完整性校验
3. `check_st_readiness.py` — 系统测试就绪性检查
4. `check_configs.py` — 必需配置检查（env 变量、配置文件）
5. `validate_guide.py` — vibeflow-guide.md 结构验证
6. `validate_st_cases.py` — ST 测试用例文档格式验证（ISO 29119）
7. `validate_increment_request.py` — 增量请求信号文件验证
8. `get_tool_commands.py` — tech_stack → CLI 命令查表
9. `check_devtools.py` — Chrome DevTools MCP 可用性检查

**策略：** 先直接移植 9 个脚本拿到功能对等，后续再考虑整合为统一 CLI。

**工作量：** L | **优先级：** P1 | **依赖：** 无

---

### TODO-9: 添加 3 个文档模板（SRS/Design/ST-Case）

**问题：** AI 执行 vibeflow-requirements、vibeflow-design、vibeflow-feature-st 时没有输出文档的结构参考。long-task 在 `docs/templates/` 下提供了 srs-template.md、design-template.md、st-case-template.md，确保 AI 生成的文档格式一致且可被验证脚本校验。

**目标：** 在 `docs/templates/` 下添加 3 个文档模板，中文化，适配 vibeflow 工作流。

**工作量：** M | **优先级：** P1 | **依赖：** TODO-8（验证脚本需要模板定义的结构来校验）

---

## P2 — Important

### TODO-10: 修复 session-start.sh 的 JSON 注入安全问题

**问题：** `hooks/session-start.sh` 把整个 SKILL.md 内容通过 bash 变量插值嵌入 JSON 输出，但没有转义双引号、反斜杠、换行等特殊字符。SKILL.md 包含大量 JSON 示例和代码块，导致生成的 JSON payload 损坏，会话上下文注入静默失败。long-task 用 `escape_for_json()` bash 函数解决此问题。

**修复：** 添加 JSON 转义函数，或改用 Python 生成 JSON payload（更可靠）。

**工作量：** S | **优先级：** P2 | **依赖：** 无

---

### TODO-11: 拆分 vibeflow-router SKILL.md（877 行 → ~200 行核心 + references/）

**问题：** 当前 router SKILL.md 有 877 行，包含路由逻辑、模板选择指南、feature-list.json schema、错误恢复协议、钩子集成、硬规则等所有内容。session-start hook 会把整个文件注入会话上下文，消耗约 35K token（占开发会话上下文窗口约 17%）。long-task 的 using-long-task 只有约 200 行（约 5K token），其他内容放在 references/ 子目录下按需读取。

**目标：** 拆分为 ~200 行核心路由（阶段路由表 + 硬规则）+ `skills/vibeflow-router/references/` 子目录的参考文档（模板指南、schema、恢复协议等）。

**工作量：** M | **优先级：** P2 | **依赖：** 无

---

### TODO-14: CLAUDE.md 跨会话上下文注入

**问题：** long-task 的 init_project.py 会在项目的 CLAUDE.md 中追加工作流概览段落，确保即使没有 session hook，AI 也能通过 CLAUDE.md 了解项目工作流约定。vibeflow 没有这个机制。

**修复：** 在 init_project.py（TODO-8）中添加 CLAUDE.md 注入逻辑，写入 vibeflow 工作流概览和关键文件列表。

**工作量：** S | **优先级：** P2 | **依赖：** TODO-8（init_project.py）

---

### TODO-15: 修复 VIBEFLOW-DESIGN.md 阶段列表缺失 review

**问题：** VIBEFLOW-DESIGN.md 第 76-92 行的阶段列表缺少 `review` 阶段（在 `build-work` 和 `test-system` 之间）。这是 TODO-5 的同类问题——之前修复了缺失的 plan-review，但漏了 review。

**修复：** 在 `- build-work` 和 `- test-system` 之间补充 `- review`。

**工作量：** S | **优先级：** P2 | **依赖：** 无

---

### TODO-4: 添加 bash 版 session hook

**问题：** hooks/session-start.ps1 是唯一的入口脚本，macOS/Linux 用户无法使用自动阶段上下文注入。

**目标：** 新增 hooks/session-start.sh 并更新 hooks.json 根据平台选择对应脚本。

**工作量：** S | **优先级：** P2 | **依赖：** 无

---

### TODO-5: 修复 VIBEFLOW-DESIGN.md 文档同步

**问题：** VIBEFLOW-DESIGN.md 第 77-91 行的 Detected phases 列表缺少 `plan-review`，但实际代码和其他三份文档（README、ARCHITECTURE、USAGE）都包含它。

**修复：** 在 `template-selection` 和 `requirements` 之间补充 `- plan-review`。

**工作量：** S | **优先级：** P2 | **依赖：** 无

---

### TODO-7: 让 test-vibeflow-setup.py 实际验证 skill 文件存在

**问题：** 当前脚本硬编码 18 个 skill 名称并直接输出，不检查 `skills/<name>/SKILL.md` 是否真正存在于磁盘上。如果 skill 被误删，验证脚本依然报告成功。

**修复：** 动态扫描 `skills/` 目录或逐一验证每个 SKILL.md 是否存在，并在报告中标注缺失项。

**工作量：** S | **优先级：** P2 | **依赖：** 无

---

## P3 — Nice to Have

### TODO-12: 添加用户命令（commands/）

**问题：** long-task 有 8 个用户快捷命令（/long-task:requirements、/long-task:work、/long-task:status 等），让用户可以直接键入命令进入特定阶段。vibeflow 没有任何 commands/，用户必须记住"调用 vibeflow-router"来开始。

**目标：** 添加 `commands/` 目录，包含 /vibeflow:status、/vibeflow:work、/vibeflow:init 等快捷命令。

**工作量：** S | **优先级：** P3 | **依赖：** TODO-8

---

### TODO-13: 添加 skill 参考文档（references/）

**问题：** long-task 的 skill 下有 8 个参考文档（systematic-debugging.md、plan-writing.md、ui-error-detection.md、coverage-recipes.md 等），帮助 AI 在执行具体任务时获取更深入的指导。vibeflow 没有任何 references/。不会阻塞工作流，但会降低 AI 执行质量。

**目标：** 为关键 skill（vibeflow-build-work、vibeflow-tdd、vibeflow-build-init、vibeflow-test-system）添加 references/ 子目录的参考文档。

**工作量：** M | **优先级：** P3 | **依赖：** 无

---

### TODO-6: 为 detect_phase() 添加 --verbose 调试模式

**问题：** 所有 Python 脚本在正常执行时只输出最终结果，不输出中间判断过程。用户遇到阶段路由错误时没有调试信息。

**目标：** 在 `get-vibeflow-phase.py` 中添加 `--verbose` 标志，输出每个条件的检查结果。

**工作量：** S | **优先级：** P3 | **依赖：** 无
