<!-- 由 vibeflow-router SKILL.md 拆分，完整性由引用者保证 -->

## 钩子集成

会话开始钩子为常规设置任务提供自动化。

### session-start.ps1 (Windows)

位置：`.vibeflow/hooks/session-start.ps1`

**行为：**
- 在会话开始时自动执行（在阶段路由之前）
- 在Windows上运行PowerShell
- 必须在阶段路由开始之前完成
- 非阻塞失败不应阻止会话

**典型操作：**
- 从远程拉取最新更改
- 检查必需的工具有无更新
- 验证环境先决条件
- 设置特定于会话的环境变量

**示例内容：**
```powershell
# VibeFlow Session Start Hook
Write-Host "=== VibeFlow Session Start ===" -ForegroundColor Cyan

# Pull latest if on main branch
$branch = git branch --show-current
if ($branch -eq "main") {
    Write-Host "Pulling latest from main..."
    git pull
}

# Verify Python environment
python --version | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Python not found" -ForegroundColor Yellow
}

Write-Host "=== Starting Phase Routing ===" -ForegroundColor Cyan
```

### session-start.sh (Unix/Linux/macOS)

位置：`.vibeflow/hooks/session-start.sh`

**行为：**
- 在会话开始时自动执行（在阶段路由之前）
- 在POSIX shell（bash/zsh兼容）中运行
- 必须在阶段路由开始之前完成
- 非阻塞失败不应阻止会话

**典型操作：**
- 从远程拉取最新更改
- 检查必需的工具有无更新
- 验证环境先决条件
- 设置特定于会话的环境变量

**示例内容：**
```bash
#!/bin/bash
# VibeFlow Session Start Hook

echo "=== VibeFlow Session Start ==="

# Pull latest if on main branch
branch=$(git branch --show-current)
if [ "$branch" = "main" ]; then
    echo "Pulling latest from main..."
    git pull
fi

# Verify Python environment
if ! command -v python &> /dev/null; then
    echo "WARNING: Python not found"
fi

echo "=== Starting Phase Routing ==="
```

### 钩子配置

要启用钩子，请将以下内容添加到您的环境或shell配置文件中：

**Windows (PowerShell)：**
```powershell
$VIBEFLOW_HOOK_ENABLED = $true
```

**Unix：**
```bash
export VIBEFLOW_HOOK_ENABLED=true
```

### 钩子执行规则

1. 钩子在阶段确定之前运行
2. 钩子失败会产生警告但不会阻止路由
3. 钩子应该是幂等的（多次运行安全）
4. 钩子应该在<10秒内完成
5. 对于长时间运行的操作，使用后台任务
