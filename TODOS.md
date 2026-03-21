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

## P2 — Important

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

### TODO-6: 为 detect_phase() 添加 --verbose 调试模式

**问题：** 所有 Python 脚本在正常执行时只输出最终结果，不输出中间判断过程。用户遇到阶段路由错误时没有调试信息。

**目标：** 在 `get-vibeflow-phase.py` 中添加 `--verbose` 标志，输出每个条件的检查结果。

**工作量：** S | **优先级：** P3 | **依赖：** 无
