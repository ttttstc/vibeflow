---
name: vibeflow-review
description: "所有活跃功能通过后使用 — 在最终测试和发布前运行全变更审查"
---

# 全局变更审查

在所有活跃功能通过后、系统测试前运行。审查整个交付物的结构完整性、一致性和质量。

当前实现保持**单一 Review 阶段**，但报告会固定拆成两组结果：
- `Spec Compliance`
- `Code Quality`

这样可以把“是否按需求/设计做对了”和“代码及实施证据是否站得住”分开表达，而不增加新的用户阶段概念。

**启动宣告：** "正在使用 vibeflow-review 运行全局变更审查。"

## 运行时机

- 所有活跃功能（非废弃）在 feature-list.json 中状态为 "passing"
- 在 vibeflow-test-system 之前
- 此阶段关注跨功能问题，而非单个功能（那是 vibeflow-spec-review 的工作）

## 安全护栏（可选激活）

在执行审查前，用户可选择激活安全护栏：

**启用 careful（危险命令警告）：**
Skill: vibeflow-careful

**启用 freeze（编辑边界保护）：**
Skill: vibeflow-freeze

**同时启用 guard（最大安全模式）：**
Skill: vibeflow-guard

安全护栏**默认不启用**。如用户未主动调用上述 skill，审查将以正常权限执行。

## 检查清单

### 1. 准备
- 读取 `feature-list.json` — 确认所有活跃功能为 passing
- 读取 `.vibeflow/logs/session-log.md` — 会话历史
- 运行 `python scripts/get-vibeflow-paths.py --json`，读取设计文档 — 架构和全局约束
- 运行 `git diff main...HEAD`（或对应基线分支）获取完整变更

### 2-4. 三维度并行审查

结构审查、回归检查、完整性检查**互不依赖**，使用 Agent 工具**并行**执行：

```
准备完成（diff + 文档已读取）
        │
        ├──▶ Agent 1: 结构审查（R1-R5）
        │         检查架构/依赖/API/数据模型一致性
        │
        ├──▶ Agent 2: 回归检查（G1-G4）
        │         运行测试套件 + 覆盖率 + lint + 安全审计
        │
        └──▶ Agent 3: 完整性检查（C1-C4）
                  检查文档/进度/示例一致性
        │
        ├── 三个 Agent 都返回 ──▶ 合并结果到审查报告
        └── 任一发现问题 ──▶ 按严重度处理
```

**执行方式：**

在**同一条消息**中发起三个 Agent 调用。每个 Agent 的提示词包含：feature-list.json 内容、设计文档路径、git diff 输出、quality_gates 阈值。

**Agent 1 — 结构审查（含深度代码审查）：**

| # | 检查项 | 描述 | 类型 |
|---|--------|------|------|
| R1 | **架构一致性** | 所有模块遵循设计文档定义的层次和边界 | 架构 |
| R2 | **依赖一致性** | 实际使用的依赖版本与设计文档依赖表匹配 | 架构 |
| R3 | **API 契约一致性** | 实际 API 端点、参数、响应与设计文档 API 章节匹配 | 架构 |
| R4 | **数据模型一致性** | 实际数据结构与设计文档 ER 图匹配 | 架构 |
| R5 | **无孤立代码** | 没有未被任何功能引用的死代码模块 | 架构 |
| R6 | **SQL 安全** | 无 SQL 字符串拼接，使用参数化查询 | Critical |
| R7 | **竞态条件** | check-then-set 模式使用原子操作；状态转换使用 atomic WHERE | Critical |
| R8 | **LLM 输出信任边界** | LLM 生成值写入 DB 前有格式验证 | Critical |
| R9 | **Enum 完整性** | 新增 enum 值时，trace 所有消费者是否处理该值 | Critical |
| R10 | **条件副作用** | 分支路径无遗漏的副作用应用 | Informational |
| R11 | **魔法数字** | 无 bare numeric literals，多文件共享值应为命名常量 | Informational |
| R12 | **Dead Code** | 无未使用变量、无过时注释 | Informational |
| R13 | **测试覆盖缺口** | 负面路径测试覆盖了副作用而不仅是类型断言 | Informational |

**两阶段审查流程：**

1. **Pass 1（Critical）— 必须先执行：** SQL & 数据安全 → 竞态条件 → LLM 信任边界 → Enum 完整性
2. **Pass 2（Informational）— Pass 1 完成后执行：** 条件副作用 → 魔法数字 → Dead Code → 测试覆盖缺口

**Fix-First 分类规则：**

| AUTO-FIX（直接修复） | ASK（需用户确认） |
|---------------------|------------------|
| Dead code / 未使用变量 | 安全问题（Auth、XSS、注入） |
| N+1 查询（缺 eager loading） | 竞态条件 |
| 过时注释与代码矛盾 | 设计决策 |
| 魔法数字 → 命名常量 | 大型修复（>20行） |
| 变量赋值但从未读取 | Enum 完整性 |
| 测试覆盖缺口（边界情况） | 移除功能 |

**Scope Drift 检测（审查前必做）：**
- 读取 `TODOS.md`（如存在）和 commit messages
- 对比 git diff --stat 与需求是否匹配
- 检测：范围蔓延（无关文件变更）、需求遗漏（应做未做）
- 输出格式：
  ```
  Scope Check: [CLEAN / DRIFT DETECTED / REQUIREMENTS MISSING]
  Intent: <1行描述请求内容>
  Delivered: <1行描述实际变更>
  ```

**Enum & Value Completeness 特别规则（Diff 新增 enum 值时）：**
使用 Grep 找到所有引用同级值的文件，Read 每个文件确认新值被正确处理：
- 检查 switch/if-elsif 链：新值是否落入错误 default？
- 检查 allowlist 数组：新值是否在所有需要的地方添加？
- 检查 frontend dropdown/backend model：两端是否一致？

返回格式：
```
结构审查：N issues (X critical, Y informational)
**AUTO-FIXED:**
- [file:line] Problem → fix applied
**NEEDS INPUT:**
- [file:line] Problem description
  Recommended fix: suggested fix
  → A) Fix  B) Skip
```

**Agent 2 — 回归检查：**

| # | 检查项 | 描述 |
|---|--------|------|
| G1 | **全套测试通过** | 运行完整测试套件，零失败 |
| G2 | **覆盖率未下降** | 全项目覆盖率 >= feature-list.json 中 quality_gates 阈值 |
| G3 | **无新警告** | 编译/lint 无新增警告或弃用通知 |
| G4 | **无安全漏洞** | 依赖安全审计通过（npm audit / pip-audit 等） |

返回格式：每个检查项的 PASS/FAIL + 实际输出证据。

**Agent 3 — 完整性检查：**

| # | 检查项 | 描述 |
|---|--------|------|
| C1 | **RELEASE_NOTES.md 完整** | 每个通过的功能都有对应变更记录 |
| C2 | **session-log 一致** | Current State 与 feature-list.json 功能计数一致 |
| C3 | **文档同步** | README / 使用说明反映当前功能集 |
| C4 | **示例覆盖** | examples/ 目录覆盖关键功能用法 |
| C5 | **文档陈旧性** | 代码变更涉及的 .md 文档是否同步更新 |

**文档陈旧性检查规则：**
- 检查 diff 中变更的文件是否被 README.md、ARCHITECTURE.md、CONTRIBUTING.md 等文档描述
- 如文档未更新但代码已变更，标记为 INFORMATIONAL：
  > "Documentation may be stale: [file] describes [feature] but code changed in this branch."

返回格式：每个检查项的 PASS/FAIL + 备注。

**结果合并：** 收集三个 Agent 的返回结果，合并到统一的审查报告中。

**回退规则：** 如 Agent 工具不可用或执行异常，回退为顺序执行（结构 → 回归 → 完整性）。

### 5. 生成审查报告

保存到 `docs/changes/<change-id>/verification/review.md`：

```markdown
# 全局变更审查报告

**日期**：YYYY-MM-DD
**功能总数**：X 活跃 / Y 废弃
**审查范围**：git diff main...HEAD

## 结构审查
| 检查 | 结果 | 备注 |
|------|------|------|
| R1-R5 | PASS/FAIL | 架构/依赖/API/数据模型/孤立代码 |
| R6-R9 | PASS/FAIL | Critical: SQL安全/竞态/LLM信任/Enum完整性 |
| R10-R13 | PASS/FAIL | Informational: 条件副作用/魔法数字/DeadCode/测试缺口 |

## 回归检查
| 检查 | 结果 | 备注 |
|------|------|------|
| G1-G4 | PASS/FAIL | 测试/覆盖率/lint/安全审计 |

## 完整性检查
| 检查 | 结果 | 备注 |
|------|------|------|
| C1-C4 | PASS/FAIL | 变更记录/进度/文档/示例 |
| C5 | PASS/FAIL | 文档陈旧性 |

## Scope Drift 检测
[审查前执行：对比 Intent vs Delivered]

## 发现的问题
| # | 严重度 | 描述 | 建议 |
|---|--------|------|------|

## 裁定
[PASS — 可进入系统测试 / FAIL — 需修复]
```

当前自动执行链路会把这些内容收敛成更紧凑的结构：

```markdown
# Review

## Summary
## Spec Compliance
### Feature Contract Validation
### Implementation Delivery Consistency
### System Test Readiness

## Code Quality
### Required Config Checks
### Implementation Evidence Quality

## Verdict
```

### 6. 处理发现

- **严重/重要问题**：修复后重新运行受影响检查
- **次要问题**：记录，可推迟到下一迭代
- 最多 3 轮修复-重审循环，然后升级到用户

### 7. 过渡

审查通过后进入 `vibeflow-test-system`。

## 集成

**调用者：** vibeflow-router 或 vibeflow-build-work（步骤 13 当无失败功能时）
**依赖：** 所有活跃功能 passing
**产出：** `docs/changes/<change-id>/verification/review.md`
**链接到：** vibeflow-test-system
