# Browser Test Report Template

```markdown
# Browser Test Report

**日期**：YYYY-MM-DD
**URL**：http://127.0.0.1:xxxx
**执行引擎**：Playwright MCP / Chrome DevTools MCP / CLI fallback

## 范围
- 测试流：...
- 页面：...
- 视口：desktop / mobile

## 摘要
- 场景数：X
- 通过：Y
- 失败：Z
- console errors：A
- request failures：B

## 场景详情

### BT-001：场景标题
- **步骤**：...
- **预期**：...
- **实际**：...
- **截图**：...
- **console**：clean / warnings / errors
- **network**：clean / failures / 4xx / 5xx
- **a11y**：pass / concerns
- **结果**：PASS / FAIL

## 发现

### FINDING-001：标题
- **严重度**：critical / major / minor / cosmetic
- **位置**：页面 URL / 组件
- **预期**：...
- **实际**：...
- **证据**：截图 / console / network

## 裁定
- PASS：可继续
- FAIL：返回 build 修复
```
