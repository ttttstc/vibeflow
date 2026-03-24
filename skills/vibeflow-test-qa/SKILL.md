---
name: vibeflow-test-qa
description: "系统测试通过后且工作流要求 UI QA 时使用 — 运行浏览器导向的 QA 验证并生成报告"
---

# 浏览器 QA 验证

在系统测试通过后，对含 UI 的项目运行浏览器导向的视觉和交互质量保证。此阶段关注系统测试中自动化检查可能遗漏的视觉一致性、交互细节和用户体验问题。

**启动宣告：** "正在使用 vibeflow-test-qa 运行浏览器 QA 验证。"

## 适用条件

- `.vibeflow/workflow.yaml` 中 QA 标记为 required
- 项目包含 `"ui": true` 的功能
- 系统测试已通过（`docs/changes/<change-id>/verification/system-test.md` 存在）

**如工作流标记 QA 为可选且无 UI 功能**：跳过此阶段，直接进入 `vibeflow-ship`。

## 检查清单

### 1. 准备环境

- 运行 `python scripts/get-vibeflow-paths.py --json`
- 读取 `docs/changes/<change-id>/verification/system-test.md` — 系统测试结果和已知问题
- 读取 UCD 风格指南 `docs/changes/<change-id>/ucd.md`（如存在）或 `design.md` 中的 UI/UX 章节 — 视觉基准
- 启动服务（使用 `.vibeflow/guides/services.md`）
- 验证应用在浏览器中可达

### 2. 视觉走查

使用 Chrome DevTools MCP 逐页面检查：

#### 2a. 页面级检查

对 UCD 中定义的每个页面：
1. `navigate_page` 到页面 URL
2. `take_screenshot` 捕获全页截图
3. 对照 UCD 页面提示词验证：
   - 布局结构是否匹配
   - 视觉层次是否正确
   - 响应式行为（至少检查桌面和移动两个断点）

#### 2b. 组件级检查

对关键交互组件：
1. 验证各状态（默认、悬停、激活、禁用、错误、加载）
2. 通过 `evaluate_script()` 检查 CSS 属性匹配 UCD Token：
   - 颜色值匹配调色板
   - 字体匹配排版比例
   - 间距匹配间距 Token
3. 交互反馈正确（点击、悬停、焦点状态）

#### 2c. 跨浏览器检查（如 SRS 指定）

在目标浏览器中重复关键页面检查，记录差异。

### 3. 交互流走查

对 SRS 中定义的关键用户工作流：
1. 模拟完整用户旅程（从入口到完成）
2. 验证每步的视觉反馈和状态转换
3. 检查加载状态、错误状态、空状态的视觉处理
4. 验证表单验证的视觉提示

### 4. 无障碍手工检查

自动化扫描已在系统测试中完成，此处做手工补充：
- 键盘导航流畅性（Tab 顺序合理，焦点指示器可见）
- 屏幕阅读器体验（ARIA 标签有意义）
- 色彩对比在实际内容下是否足够
- 触控目标大小足够（移动端）

### 5. 记录发现

对每个发现记录：
- **截图**：通过 `take_screenshot` 捕获
- **位置**：页面 URL + 元素定位
- **预期**：UCD 定义的外观/行为
- **实际**：当前外观/行为
- **严重度**：严重 / 重要 / 次要 / 外观

### 6. 生成 QA 报告

保存到 `docs/changes/<change-id>/verification/qa.md`：

```markdown
# QA 验证报告

**日期**：YYYY-MM-DD
**浏览器**：[测试的浏览器及版本]
**设备/视口**：[测试的断点]

## 摘要
- 检查页面数：X
- 检查组件数：Y
- 发现总数：Z
  - 严重：A
  - 重要：B
  - 次要：C
  - 外观：D

## 发现详情

### QA-001：[标题]
- **页面**：[URL]
- **严重度**：[级别]
- **预期**：[来自 UCD]
- **实际**：[当前行为]
- **截图**：[如有]
- **状态**：[待修复 / 已修复 / 推迟]

### QA-002：...

## 裁定
[PASS — 可发布 / FAIL — 需修复]
```

### 7. 处理发现

- **严重/重要**：修复后重新验证受影响区域
- **次要/外观**：与用户确认是否修复或推迟
- 最多 3 轮修复-重验循环

### 8. 清理与过渡

- 停止服务（`.vibeflow/guides/services.md`）
- Git 提交 QA 报告
- 更新 `.vibeflow/logs/session-log.md`

QA 通过后进入 `vibeflow-ship`。

## 集成

**调用者：** vibeflow-router 或 vibeflow-test-system
**依赖：** 系统测试通过、UCD 文档存在
**产出：** `docs/changes/<change-id>/verification/qa.md`
**链接到：** vibeflow-ship
