# VibeFlow 安装提示词

复制以下内容发送给 Claude Code，让它自行完成安装：

---

## 安装命令（一键）

在 Claude Code 对话框中运行：

```
/sh curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/refs/heads/feat/plan-value-review/claude-code/install.sh | bash
```

安装完成后运行：

```
/plugin install vibeflow@vibeflow
```

---

## 安装提示词（让 Claude Code 自主完成）

复制以下内容，粘贴到 Claude Code 对话框：

---

**提示词开始：**

```
帮我安装 VibeFlow 插件到当前机器。

步骤：
1. 下载安装文件到 ~/.claude/plugins/marketplaces/vibeflow/
   - 如果 git 可用：用 git clone https://github.com/ttttstc/vibeflow.git --depth 1 到目标目录
   - 如果 git 不可用：从 https://github.com/ttttstc/vibeflow/archive/refs/heads/feat/plan-value-review.zip 下载并解压

2. 在 ~/.claude/plugins/known_marketplaces.json 中注册 marketplace（如果没有这个文件则创建）：
   - marketplace 名称（key）：vibeflow
   - source.source: "github"
   - source.repo: "ttttstc/vibeflow"
   - installLocation: 实际安装路径（~/.claude/plugins/marketplaces/vibeflow/）
   - lastUpdated: 当前 UTC 时间，格式如 2026-03-23T00:00:00.000Z

3. 完成后报告安装结果

注意：
- 目标目录：~/.claude/plugins/marketplaces/vibeflow/
- 安装完成后需要你手动运行：/plugin install vibeflow@vibeflow 来激活插件
```

**提示词结束**

---

## 验证安装

安装完成后，在 Claude Code 中运行诊断：

```
/sh curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/refs/heads/feat/plan-value-review/claude-code/debug-install.ps1 | iex
```

或者（如果系统是 bash）：

```
/sh curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/refs/heads/feat/plan-value-review/claude-code/debug-install.ps1 | iex
```

---

## 常见问题

| 问题 | 解决方法 |
|------|---------|
| `jq: command not found` | macOS: `brew install jq` / Linux: `apt install jq` |
| `git clone 失败` | 检查网络，或使用 ZIP 下载方式 |
| `plugin not found` | 确保运行了 `/plugin install vibeflow@vibeflow` |
| 仍报 not found | 重启 Claude Code 后再试 |
