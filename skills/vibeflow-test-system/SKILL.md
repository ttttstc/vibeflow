---
name: vibeflow-test-system
description: "所有活跃功能通过且全局审查完成后使用 — 发布前运行全面系统测试，对齐 IEEE 829 和 ISTQB"
---

# 系统测试 — 跨功能与系统级发布前验证

在所有功能实现并通过后运行跨功能和系统级测试。每个功能的 ST 测试用例已在构建循环中通过 `vibeflow-feature-st` 执行。此阶段关注功能级测试**无法**覆盖的：跨功能交互、多功能 E2E 工作流、系统级 NFR 验证、兼容性和探索性测试。

**启动宣告：** "正在使用 vibeflow-test-system。所有功能已通过 — 开始跨功能系统测试。"

<HARD-GATE>
不得跳过任何适用的测试类别。"Go" 裁定需要每个适用类别的证据。"可能可以"不是证据。
</HARD-GATE>

## 检查清单

### 1. ST 就绪门禁

- 所有功能 `"status": "passing"` — 如有失败则返回 vibeflow-build-work
- SRS 和设计文档存在
- 启动服务（如适用），使用 `.vibeflow/guides/services.md` 命令
- 运行 `python scripts/get-vibeflow-paths.py --json`
- 读取 feature-list.json、`brief.md`、`design.md`、`ucd.md`（如有 UI）、`.vibeflow/logs/session-log.md`

### 2. ST 计划

创建 `docs/changes/<change-id>/verification/system-test-plan.md`：

#### 2a. 测试范围

| 类别 | 适用条件 | 跳过条件 |
|------|---------|---------|
| 回归 | 始终 | 从不 |
| 集成 | 2+ 功能共享数据/状态/API | 单个隔离功能 |
| E2E 场景 | SRS 有多步用户工作流 | 纯库/工具项目 |
| 浏览器运行时验证 | 存在页面交互、表单、路由、前端 API、状态切换 | 无浏览器运行时 |
| 性能 | SRS 有响应时间/吞吐量 NFR | 无性能 NFR |
| 安全 | 安全 NFR 或处理用户输入/认证 | 隔离离线工具 |
| 无障碍 | 存在 UI 功能 | 无 UI 功能 |
| 兼容性 | SRS 指定平台/浏览器/运行时目标 | 单平台 CLI 工具 |
| 探索性 | 始终 | 从不 |

#### 2b. 需求追溯矩阵（RTM）

将**每个** SRS 需求映射到 ST 测试方法：

```markdown
| 需求 ID | 需求 | 功能 ST 状态 | 系统 ST 类别 | 测试方法 | 优先级 |
|---------|------|-------------|-------------|---------|--------|
```

每个 FR-xxx、NFR-xxx、IFR-xxx 必须出现在 RTM 中。无测试方法的需求 = **缺口**。

#### 2c. 入口/退出标准

**入口**：所有功能 passing，环境就绪，所有配置齐备。
**退出**：所有测试通过，NFR 阈值达标（有度量证据），无严重/重要缺陷，RTM 100% 覆盖。

### 3. 回归测试（阻塞门禁 — 必须先通过）

1. 运行完整项目测试套件
2. 验证所有测试通过 — 零失败
3. 验证覆盖率阈值全项目达标
4. 任何失败 -> **停止** — 这是回归。先诊断。

**回归测试是阻塞门禁**：必须通过后才能启动后续并行测试类别。

### 4-8. 多类别并行测试

回归测试通过后，以下测试类别**互不依赖**，使用 Agent 工具**并行**执行：

```
回归测试通过（阻塞门禁）
        │
        ├──▶ Agent 1: 集成测试
        │         跨功能数据流、API 契约、依赖链
        │
        ├──▶ Agent 2: E2E 场景测试
        │         跨功能用户工作流（正常路径 + 错误恢复）
        │
        ├──▶ Agent 3: 浏览器运行时验证
        │         真实页面交互、console、network、截图、a11y
        │
        ├──▶ Agent 4: NFR 验证
        │         性能/安全/无障碍/可靠性
        │
        └──▶ Agent 5: 兼容性 + 探索性测试
                  跨平台兼容 + 章程式探索
        │
        ├── 所有 Agent 返回 ──▶ 合并到 ST 报告
        └── 任一发现严重/重要缺陷 ──▶ 缺陷分诊
```

**执行方式：**

在**同一条消息**中发起多个 Agent 调用（仅发起 ST 计划中标记为"适用"的类别）。每个 Agent 的提示词包含：feature-list.json、需求文档、设计文档、`.vibeflow/guides/services.md`、RTM 相关需求。

**Agent 1 — 集成测试**（适用条件：2+ 功能共享数据/状态/API）：

- **数据流**：功能 A 产生数据 -> 功能 B 消费 -> 验证端到端数据完整性
- **API 契约**：模块间内部 API 调用 — 验证请求/响应模式
- **依赖链**：遍历 feature-list.json 中 `dependencies[]` 图
- 返回格式：每个集成点的 PASS/FAIL + 证据

**Agent 2 — E2E 场景测试**（适用条件：SRS 有多步用户工作流）：

- 对 SRS 中每个用户画像提取跨功能边界的主要工作流
- 创建 E2E 场景（正常路径 + 错误恢复）
- 涉及 UI 的 E2E，必须调用 `vibeflow-browser-testing`
- 返回格式：每个场景的 PASS/FAIL + 执行证据

**Agent 3 — 浏览器运行时验证**（适用条件：存在浏览器运行时）：

- 调用 `skills/vibeflow-browser-testing/SKILL.md`
- 生成 `browser-test-plan.md`
- 对关键页面/流程执行真实浏览器验证
- 采集 screenshot、console、network、a11y 证据
- 对涉及页面交互的功能，浏览器验证是**硬门禁**，不得用“代码看起来没问题”替代
- 返回格式：每个场景的 PASS/FAIL + 证据链接 + 发现摘要

**Agent 4 — NFR 验证**（适用条件：SRS 有 NFR-xxx）：

对 SRS 中每个 NFR-xxx，用**度量证据**验证：
- **性能**：度量 p50/p95/p99，吞吐量，内存/CPU
- **安全**：输入验证审计、认证/授权、依赖漏洞扫描、OWASP Top 10
- **无障碍**（仅 UI）：WCAG 2.1 AA 自动扫描、键盘导航、ARIA/语义 HTML；浏览器运行时证据优先来自 `vibeflow-browser-testing`
- **可靠性**：错误处理产生有意义消息、优雅降级
- 返回格式：每个 NFR 的度量值 vs 阈值 + PASS/FAIL

**Agent 5 — 兼容性 + 探索性测试**：

兼容性（如 SRS 未指定平台/浏览器/运行时目标则跳过）：
- 跨浏览器（仅 UI）、跨平台、运行时版本

探索性（始终执行）：
基于章程、限时的会话，发现脚本测试遗漏的问题：

```
章程：探索 [功能领域]
      使用 [技术：压力/边界/滥用/工作流变体]
      以发现 [bug/可用性问题/未文档行为]
```

每个章程限时 15-30 分钟。

返回格式：兼容性矩阵 + 探索性发现列表。

**结果合并：** 收集所有 Agent 的返回结果，统一进入缺陷分诊流程。

**回退规则：** 如 Agent 工具不可用或执行异常，回退为顺序执行。

### 9. 缺陷分诊

| 严重度 | 定义 | 行动 |
|--------|------|------|
| **严重** | 系统崩溃、数据丢失、安全漏洞 | 阻塞发布 — 立即修复 |
| **重要** | 核心工作流中断、NFR 阈值未达 | 阻塞发布 — 发布前修复 |
| **次要** | 非核心受影响、有变通方案 | 记录 — 立即修复或推迟 |
| **外观** | 视觉/文本问题、无功能影响 | 记录 — 推迟到下一发布 |

严重/重要缺陷：标记受影响功能为 failing -> 返回 vibeflow-build-work 修复 -> 重新运行受影响 ST 类别。

### 10. ST 报告

生成 `docs/changes/<change-id>/verification/system-test.md`：
1. **执行摘要** — 1-3 句：整体质量评估和发布建议
2. **需求追溯矩阵** — 完整 RTM
3. **测试执行摘要** — 按类别：运行数、通过、失败、跳过
4. **缺陷摘要** — 按严重度：描述、状态、修复引用
5. **质量指标** — 覆盖率、测试总数
6. **风险评估** — 残余风险及缓解
7. **建议** — 发布后监控、已知限制

### 11. 持久化

- Git 提交 ST 工件
- 更新 RELEASE_NOTES.md
- 更新 `.vibeflow/logs/session-log.md`
- **强制清理**：停止步骤 1 启动的服务

### 12. 裁定

通过 `AskUserQuestion` 向用户展示 ST 报告摘要和 Go/No-Go 建议：
- **Go**：所有退出标准达标，无严重/重要缺陷，RTM 100% 覆盖
- **有条件 Go**：次要/外观缺陷推迟，所有关键路径验证
- **No-Go**：有严重/重要缺陷，NFR 阈值未达，或 RTM 缺口

裁定通过后：
- 如 `.vibeflow/workflow.yaml` 要求 QA -> 进入 `vibeflow-test-qa`
- 否则 -> 进入 `vibeflow-ship`

## 集成

**调用者：** vibeflow-router 或 vibeflow-review
**读取：** feature-list.json、`docs/changes/<change-id>/brief.md`、`docs/changes/<change-id>/design.md`、可选 legacy `docs/changes/<change-id>/requirements.md`、可选 `docs/changes/<change-id>/ucd.md`、功能级测试用例文档、`.vibeflow/logs/session-log.md`
**可调用：** vibeflow-build-work（如发现严重/重要缺陷）、vibeflow-browser-testing（如存在 UI / 页面交互）
**产出：** `docs/changes/<change-id>/verification/system-test-plan.md`、`docs/changes/<change-id>/verification/system-test.md`、适用时 `docs/changes/<change-id>/verification/browser-test-plan.md` 与 `docs/changes/<change-id>/verification/browser-test.md`
**链接到：** vibeflow-test-qa 或 vibeflow-ship
