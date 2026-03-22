# UI 三层错误检测方法

本文档描述 VibeFlow TDD 流程中用于 UI 功能验证的三层错误检测方法，帮助确保 UI 功能的正确性和稳定性。

## 概述

UI 错误检测分为三个层次，从不同角度全面覆盖可能的错误：
- Layer 1: JavaScript 错误检测
- Layer 2: 快照期望/拒绝验证
- Layer 3: 控制台错误验证

三层方法相互补充，共同确保 UI 功能的正确性。

## Layer 1: JavaScript 错误检测

### 1.1 实现方式
使用 `evaluate_script` 或专门的 `error_detector` 工具执行 JavaScript 代码并捕获错误。

### 1.2 检测内容
- 未捕获的 JavaScript 异常
- 语法错误
- 运行时错误
- 引用错误（访问未定义的变量/函数）

### 1.3 示例
```javascript
// 执行脚本并捕获错误
const result = await page.evaluate(() => {
  try {
    // 你的 JavaScript 代码
    return { success: true, value: someFunction() };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

if (!result.success) {
  console.error('JavaScript Error:', result.error);
}
```

### 1.4 常见错误类型
| 错误类型 | 原因 | 解决方案 |
|----------|------|----------|
| ReferenceError | 变量未定义 | 检查变量作用域 |
| TypeError | 对象的类型不正确 | 检查对象初始化 |
| SyntaxError | JavaScript 语法错误 | 检查代码语法 |
| RangeError | 数值超出范围 | 检查数值边界 |

### 1.5 最佳实践
- 在执行复杂操作前，先用简单脚本验证基础功能
- 使用 try-catch 包装所有 evaluate_script 调用
- 记录详细的错误上下文信息

## Layer 2: 快照期望/拒绝验证

### 2.1 take_snapshot 命令
使用 `take_snapshot` 进行 UI 状态验证，支持两种模式：
- `EXPECT`: 期望特定元素或内容存在
- `REJECT`: 期望特定元素或内容不存在

### 2.2 EXPECT 模式
```json
{
  "command": "take_snapshot",
  "params": {
    "mode": "EXPECT",
    "expected": [
      {
        "type": "element",
        "selector": "#login-button",
        "description": "登录按钮存在"
      },
      {
        "type": "text",
        "content": "Welcome",
        "description": "欢迎文本显示"
      }
    ]
  }
}
```

### 2.3 REJECT 模式
```json
{
  "command": "take_snapshot",
  "params": {
    "mode": "REJECT",
    "forbidden": [
      {
        "type": "element",
        "selector": ".error-message",
        "description": "错误信息不应显示"
      },
      {
        "type": "text",
        "content": "Internal Error",
        "description": "不应显示服务器错误"
      }
    ]
  }
}
```

### 2.4 组合使用
```json
{
  "command": "take_snapshot",
  "params": {
    "mode": "EXPECT",
    "expected": [
      { "type": "element", "selector": ".main-content" }
    ],
    "forbidden": [
      { "type": "element", "selector": ".loading-spinner" }
    ]
  }
}
```

### 2.5 验证场景
| 场景 | 使用的模式 |
|------|------------|
| 验证数据加载完成 | EXPECT 加载后的内容 + REJECT 加载动画 |
| 验证表单提交成功 | EXPECT 成功消息 + REJECT 错误消息 |
| 验证错误处理 | EXPECT 错误提示 + REJECT 正常内容 |
| 验证页面初始化 | EXPECT 核心元素 + REJECT 临时占位符 |

## Layer 3: 控制台错误验证

### 3.1 list_console_messages 命令
捕获浏览器控制台的所有消息，包括：
- `console.log` 输出
- `console.warn` 警告
- `console.error` 错误
- JavaScript 运行时错误

### 3.2 使用方法
```json
{
  "command": "list_console_messages",
  "params": {
    "filter": ["error", "warn"],
    "clear": true
  }
}
```

### 3.3 响应格式
```json
{
  "messages": [
    {
      "level": "error",
      "text": "Failed to load resource: 404",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "level": "warn",
      "text": "Deprecated API usage",
      "timestamp": "2024-01-15T10:30:01Z"
    }
  ]
}
```

### 3.4 错误级别说明
| 级别 | 含义 | 是否应该失败测试 |
|------|------|------------------|
| log | 一般信息 | 否 |
| info | 信息消息 | 否 |
| warn | 警告 | 根据情况 |
| error | 错误 | 是 |

### 3.5 常见控制台错误
| 错误信息 | 含义 | 解决方案 |
|----------|------|----------|
| Failed to fetch | 网络请求失败 | 检查 API 端点、网络连接 |
| 404 Not Found | 资源不存在 | 检查 URL 路径 |
| Uncaught TypeError | 未捕获的类型错误 | 检查 JavaScript 代码 |
| Failed to load resource | 资源加载失败 | 检查静态资源路径 |

## 三层检测的协同使用

### 典型测试流程
```json
[
  {
    "step": "1. 清除控制台",
    "command": "list_console_messages",
    "params": { "action": "clear" }
  },
  {
    "step": "2. 执行操作",
    "command": "click",
    "params": { "selector": "#submit-btn" }
  },
  {
    "step": "3. Layer 1: JavaScript 错误检测",
    "command": "evaluate_script",
    "params": { "script": "window.postSubmitAction()" }
  },
  {
    "step": "4. Layer 2: 快照验证",
    "command": "take_snapshot",
    "params": {
      "mode": "EXPECT",
      "expected": [
        { "type": "element", "selector": ".success-message" }
      ]
    }
  },
  {
    "step": "5. Layer 3: 控制台错误验证",
    "command": "list_console_messages",
    "params": { "filter": ["error"] }
  }
]
```

### 检测优先级
1. **Layer 1** 首先执行，快速捕获明显的 JavaScript 错误
2. **Layer 2** 验证 UI 状态是否符合预期
3. **Layer 3** 检查是否有隐藏的错误或警告

## 测试用例示例

### 登录表单测试
```json
{
  "name": "login_form_success",
  "steps": [
    {
      "command": "list_console_messages",
      "params": { "action": "clear" }
    },
    {
      "command": "fill",
      "params": { "selector": "#username", "value": "testuser" }
    },
    {
      "command": "fill",
      "params": { "selector": "#password", "value": "password123" }
    },
    {
      "command": "click",
      "params": { "selector": "#login-btn" }
    },
    {
      "command": "evaluate_script",
      "params": {
        "script": "return { error: window.jsError || null }"
      }
    },
    {
      "command": "take_snapshot",
      "params": {
        "mode": "EXPECT",
        "expected": [
          { "type": "element", "selector": ".dashboard", "description": "仪表盘显示" },
          { "type": "text", "content": "Welcome", "description": "欢迎消息" }
        ],
        "forbidden": [
          { "type": "element", "selector": ".error-message", "description": "不应有错误" }
        ]
      }
    },
    {
      "command": "list_console_messages",
      "params": { "filter": ["error"] }
    }
  ]
}
```

## 注意事项

1. **执行顺序**: 三层检测按顺序执行，不要打乱顺序
2. **清理状态**: 每次测试前清理之前的状态
3. **超时设置**: 适当设置操作超时，防止无限等待
4. **重试机制**: 瞬态错误应设置重试机制
5. **日志记录**: 所有检测结果都应记录以便调试
