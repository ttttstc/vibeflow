# Browser Testing Tooling Setup

## Preferred Setup

### Playwright MCP

优先用 Playwright MCP 执行真实交互和断言。

### Chrome DevTools MCP

用 Chrome DevTools MCP 做运行时诊断：

- screenshot
- console
- network
- DOM
- styles
- accessibility

## CLI Fallback

当当前宿主没有 MCP，或只想先做最小 smoke verification 时：

```bash
python scripts/browser_verify.py --url http://127.0.0.1:4317 --out-dir .tmp/browser-verify
```

## Recommended Evidence

至少保留：

- 一张成功页面截图
- console 摘要
- network 摘要
- 如适用，a11y snapshot 摘要
