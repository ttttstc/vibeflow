# =============================================================================
# VibeFlow 一站式安装脚本（Claude Code 内专用）
# =============================================================================
#
# 使用方法：在 Claude Code 中运行（只需要这一条命令）：
#
#   /sh irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install-all-in-one.ps1 | iex
#
# 安装程序会自动完成：
#   1. 下载 vibeflow 文件到 ~/.claude/plugins/marketplaces/vibeflow/
#   2. 注册 marketplace 到 known_marketplaces.json
#   3. 验证安装完整性
#
# 然后运行：
#   /plugin install vibeflow@vibeflow
#
# =============================================================================

param(
    [switch]$AutoPluginInstall
)

$ErrorActionPreference = "Stop"

$MarketplaceName = "vibeflow"
$Branch = "main"
$DownloadUrl = "https://github.com/ttttstc/vibeflow/archive/refs/heads/main.zip"

$ClaudePluginsDir = Join-Path $env:USERPROFILE ".claude\plugins"
$MarketplacesDir = Join-Path $ClaudePluginsDir "marketplaces"
$TargetDir = Join-Path $MarketplacesDir $MarketplaceName
$KnownMarketplacesFile = Join-Path $ClaudePluginsDir "known_marketplaces.json"

Write-Host "=== VibeFlow 一站式安装 ===" -ForegroundColor Cyan
Write-Host ""

# 1. Create directories
Write-Host "[1/5] 创建目录..." -ForegroundColor Yellow
if (-not (Test-Path $MarketplacesDir)) {
    New-Item -ItemType Directory -Force -Path $MarketplacesDir | Out-Null
}
Write-Host "  [OK]" -ForegroundColor Green

# 2. Remove existing installation
if (Test-Path $TargetDir) {
    Write-Host "[2/5] 移除旧版本..." -ForegroundColor Yellow
    Remove-Item $TargetDir -Recurse -Force
}
Write-Host "  [OK] 已移除" -ForegroundColor Green

# 3. Download and extract
Write-Host "[3/5] 下载中..." -ForegroundColor Yellow
$TempZip = Join-Path $env:TEMP "vibeflow-download.zip"
$TempExtract = Join-Path $env:TEMP "vibeflow-extract"

try {
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $TempZip -UserAgent "vibeflow-installer/1.0" -TimeoutSec 120
    $sizeMB = [math]::Round((Get-Item $TempZip).Length / 1MB, 1)
    Write-Host "  下载完成 ($sizeMB MB)" -ForegroundColor Green

    if (Test-Path $TempExtract) {
        Remove-Item $TempExtract -Recurse -Force -ErrorAction SilentlyContinue
    }
    New-Item -ItemType Directory -Force -Path $TempExtract | Out-Null

    Expand-Archive -Path $TempZip -DestinationPath $TempExtract -Force
    $ExtractedRepo = Join-Path $TempExtract "vibeflow-feat-plan-value-review"

    Move-Item -Path $ExtractedRepo -Destination $TargetDir -Force
    Write-Host "  安装到: $TargetDir" -ForegroundColor Green

    Remove-Item $TempZip -Force -ErrorAction SilentlyContinue
    Remove-Item $TempExtract -Recurse -Force -ErrorAction SilentlyContinue
} catch {
    Write-Host "  下载失败: $_" -ForegroundColor Red
    Write-Host "  请检查网络连接后重试" -ForegroundColor Yellow
    exit 1
}

# 4. Verify
Write-Host "[4/5] 验证安装..." -ForegroundColor Yellow
$MarketplaceJson = Join-Path $TargetDir ".claude-plugin\marketplace.json"
if (-not (Test-Path $MarketplaceJson)) {
    Write-Host "  [ERROR] marketplace.json 未找到 - 安装包损坏" -ForegroundColor Red
    exit 1
}
$SkillDir = Join-Path $TargetDir "skills"
$skillCount = (Get-ChildItem $SkillDir -Directory).Count -as [int]
Write-Host "  marketplace.json: OK" -ForegroundColor Green
Write-Host "  Skills: $skillCount found" -ForegroundColor Green

# 5. Register in known_marketplaces.json
Write-Host "[5/5] 注册 marketplace..." -ForegroundColor Yellow
if (-not (Test-Path $KnownMarketplacesFile)) {
    [System.IO.File]::WriteAllText($KnownMarketplacesFile, '{}', (New-Object System.Text.UTF8Encoding($false)))
}

$kmContent = Get-Content $KnownMarketplacesFile -Raw
$kmJson = $kmContent | ConvertFrom-Json
$timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.000Z")

$entry = @{
    source = @{
        source = "github"
        repo = "ttttstc/vibeflow"
    }
    installLocation = $TargetDir
    lastUpdated = $timestamp
}
$kmJson | Add-Member -MemberType NoteProperty -Name $MarketplaceName -Value $entry -Force

$compact = $kmJson | ConvertTo-Json -Depth 10 -Compress
[System.IO.File]::WriteAllText($KnownMarketplacesFile, $compact, (New-Object System.Text.UTF8Encoding($false)))

# Verify registration
$verify = (Get-Content $KnownMarketplacesFile -Raw) | ConvertFrom-Json
if (-not $verify.PSObject.Properties.Name.Contains($MarketplaceName)) {
    Write-Host "  [ERROR] 注册失败" -ForegroundColor Red
    exit 1
}
Write-Host "  注册完成" -ForegroundColor Green

# Done
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  文件安装完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "最后一步（在 Claude Code 中运行）：" -ForegroundColor Cyan
Write-Host "  /plugin install vibeflow@vibeflow" -ForegroundColor White
Write-Host ""
Write-Host "提示：也可以使用 --plugin-dir 跳过安装步骤直接加载：" -ForegroundColor Gray
Write-Host "  claude --plugin-dir ~/.claude/plugins/marketplaces/vibeflow" -ForegroundColor Gray
Write-Host ""
