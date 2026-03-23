# VibeFlow 安装指南

## 方法一：一键安装（推荐）

在 Claude Code 对话框中运行：

```
/sh curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.sh | bash
```

安装完成后激活：

```
/plugin install vibeflow@vibeflow
```

---

## 方法二：让 Claude Code 自行下载安装

复制以下内容，粘贴到 Claude Code 对话框：

```
帮我安装 VibeFlow 插件。

执行以下步骤：

1. 下载仓库（选一种方式）：

   方式A - git clone：
   git clone --depth 1 https://github.com/ttttstc/vibeflow.git ~/.claude/plugins/marketplaces/vibeflow

   方式B - 如果 git 不可用，用 curl 下载 ZIP：
   curl -fsSL https://github.com/ttttstc/vibeflow/archive/refs/heads/main.zip -o /tmp/vibeflow.zip
   unzip /tmp/vibeflow.zip -d /tmp/
   rm -rf ~/.claude/plugins/marketplaces/vibeflow
   mv /tmp/vibeflow-main ~/.claude/plugins/marketplaces/vibeflow

2. 确保目录是 ~/.claude/plugins/marketplaces/vibeflow/

3. 在 ~/.claude/plugins/known_marketplaces.json 注册（如果文件不存在则创建）：
   使用 jq 或 python3 更新 JSON，添加：
   "vibeflow": {
     "source": {"source": "github", "repo": "ttttstc/vibeflow"},
     "installLocation": "~/.claude/plugins/marketplaces/vibeflow/",
     "lastUpdated": "2026-03-23T00:00:00.000Z"
   }

4. 完成后报告
```

---

## 方法三：本地已有 vibeflow 仓库

如果你本地已经有 vibeflow 仓库（例如 D:\AI\workspace\vibeflow），可以快速从本地安装：

```
帮我把 D:\AI\workspace\vibeflow 安装为 Claude Code 插件：

1. 复制整个目录到 ~/.claude/plugins/marketplaces/vibeflow/
2. 在 ~/.claude/plugins/known_marketplaces.json 中添加 vibeflow 条目：
   - key: vibeflow
   - source.source: "github"
   - source.repo: "ttttstc/vibeflow"
   - installLocation: ~/.claude/plugins/marketplaces/vibeflow/
   - lastUpdated: 当前 UTC 时间（格式：2026-03-23T00:00:00.000Z）
3. 完成后运行 /plugin install vibeflow@vibeflow 激活插件
```

（把路径改成你本地仓库的实际路径）

---

## 激活

无论用哪种方法安装，最后都需要在 Claude Code 中激活插件：

```
/plugin install vibeflow@vibeflow
```

激活成功后试试 `/vibeflow` 或 `/vibeflow-status`。

---

## 诊断

如果遇到问题，运行诊断脚本：

```
/sh curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/debug-install.ps1 | iex
```
