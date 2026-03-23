# =============================================================================
# VibeFlow 启动器 - 真正的开箱即用
# =============================================================================
#
# 使用方法：下载此脚本后双击运行，或者在 PowerShell 中运行：
#   .\vibeflow-launcher.ps1
#
# 或者一行命令（推荐）：
#   irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/vibeflow-launcher.ps1 | iex
#
# 此脚本会：
#   1. 检查并安装 vibeflow（如需要）
#   2. 启动 Claude Code 并自动加载 vibeflow 插件
#   3. 无需手动运行 /plugin install
#
# 第一次运行后会记住安装状态，后续直接启动 Claude Code + vibeflow
#
# =============================================================================

$ErrorActionPreference = "Stop"

$MarketplaceName = "vibeflow"
$Branch = "main"
$DownloadUrl = "https://github.com/ttttstc/vibeflow/archive/refs/heads/main.zip"
$RawBase = "https://raw.githubusercontent.com/ttttstc/vibeflow/refs/heads/main"

$ClaudePluginsDir = Join-Path $env:USERPROFILE ".claude\plugins"
$MarketplacesDir = Join-Path $ClaudePluginsDir "marketplaces"
$TargetDir = Join-Path $MarketplacesDir $MarketplaceName
$KnownMarketplacesFile = Join-Path $ClaudePluginsDir "known_marketplaces.json"

function Write-Step($msg) {
    Write-Host "  $msg" -ForegroundColor Green
}

function Write-Info($msg) {
    Write-Host "  $msg" -ForegroundColor Yellow
}

function Write-Err($msg) {
    Write-Host "  $msg" -ForegroundColor Red
}

# Check if already installed and registered
function Test-VibeflowInstalled {
    if (-not (Test-Path (Join-Path $TargetDir ".claude-plugin\marketplace.json"))) {
        return $false
    }
    if (-not (Test-Path $KnownMarketplacesFile)) {
        return $false
    }
    $km = Get-Content $KnownMarketplacesFile -Raw | ConvertFrom-Json
    return $km.PSObject.Properties.Name.Contains($MarketplaceName)
}

# Install vibeflow
function Install-Vibeflow {
    Write-Host "[安装中] 下载 vibeflow..." -ForegroundColor Cyan

    if (-not (Test-Path $MarketplacesDir)) {
        New-Item -ItemType Directory -Force -Path $MarketplacesDir | Out-Null
    }

    if (Test-Path $TargetDir) {
        Write-Info "移除旧版本..."
        Remove-Item $TargetDir -Recurse -Force
    }

    $TempZip = Join-Path $env:TEMP "vibeflow-download.zip"
    $TempExtract = Join-Path $env:TEMP "vibeflow-extract"

    try {
        Invoke-WebRequest -Uri $DownloadUrl -OutFile $TempZip -UserAgent "vibeflow-launcher/1.0" -TimeoutSec 120
        $sizeMB = [math]::Round((Get-Item $TempZip).Length / 1MB, 1)
        Write-Step "下载完成 ($sizeMB MB)"

        if (Test-Path $TempExtract) {
            Remove-Item $TempExtract -Recurse -Force -ErrorAction SilentlyContinue
        }
        New-Item -ItemType Directory -Force -Path $TempExtract | Out-Null

        Write-Info "解压中..."
        Expand-Archive -Path $TempZip -DestinationPath $TempExtract -Force
        $ExtractedRepo = Join-Path $TempExtract "vibeflow-main"

        Move-Item -Path $ExtractedRepo -Destination $TargetDir -Force
        Write-Step "安装到: $TargetDir"

        Remove-Item $TempZip -Force -ErrorAction SilentlyContinue
        Remove-Item $TempExtract -Recurse -Force -ErrorAction SilentlyContinue
    } catch {
        Write-Err "下载失败: $_"
        throw
    }

    # Verify
    $MarketplaceJson = Join-Path $TargetDir ".claude-plugin\marketplace.json"
    if (-not (Test-Path $MarketplaceJson)) {
        Write-Err "安装包损坏，请重试"
        throw
    }
    $SkillDir = Join-Path $TargetDir "skills"
    $skillCount = (Get-ChildItem $SkillDir -Directory).Count
    Write-Step "验证通过 ($skillCount skills)"

    # Register
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
        Write-Err "注册失败"
        throw
    }
    Write-Step "注册完成"
}

# Main
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VibeFlow 启动器" -ForegroundColor White
Write-Host "  开箱即用，无需手动安装插件" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (Test-VibeflowInstalled) {
    Write-Host "[状态] vibeflow 已安装" -ForegroundColor Green
} else {
    Write-Host "[状态] 正在安装 vibeflow..." -ForegroundColor Yellow
    try {
        Install-Vibeflow
        Write-Host "[OK] 安装成功！" -ForegroundColor Green
    } catch {
        Write-Host ""
        Write-Host "安装失败，请检查网络后重试" -ForegroundColor Red
        Write-Host "或者手动下载安装："
        Write-Host "  irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install-simple.ps1 | iex" -ForegroundColor Gray
        exit 1
    }
}

Write-Host ""
Write-Host "[启动] 正在启动 Claude Code + vibeflow..." -ForegroundColor Cyan

# Find Claude Code executable
$claudeExe = $null
$searchPaths = @(
    (Join-Path $env:LOCALAPPDATA "Programs\Claude\Claude.exe"),
    "C:\Program Files\Claude\Claude.exe",
    (Join-Path $env:APPDATA "Code\User\lately\claude.exe"),
    "claude"  # in PATH
)

foreach ($path in $searchPaths) {
    if ($path -eq "claude") {
        if (Get-Command claude -ErrorAction SilentlyContinue) {
            $claudeExe = "claude"
            break
        }
    } elseif (Test-Path $path) {
        $claudeExe = $path
        break
    }
}

if (-not $claudeExe) {
    Write-Host ""
    Write-Err "未找到 Claude Code，请确保已安装 Claude Code"
    Write-Host "从以下地址下载：https://claude.com/download" -ForegroundColor Yellow
    exit 1
}

Write-Host "  找到 Claude Code: $claudeExe" -ForegroundColor Gray
Write-Host "  加载插件目录: $TargetDir" -ForegroundColor Gray
Write-Host ""

# Launch Claude Code with plugin-dir
try {
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $claudeExe
    $psi.Arguments = "--plugin-dir `"$TargetDir`""
    $psi.UseShellExecute = $true
    $psi.WorkingDirectory = $PWD
    [System.Diagnostics.Process]::Start($psi) | Out-Null

    Write-Host "[OK] Claude Code 已启动并加载 vibeflow" -ForegroundColor Green
    Write-Host ""
    Write-Host "提示：以后直接运行此脚本即可启动 vibeflow" -ForegroundColor Gray
} catch {
    Write-Err "启动失败: $_"
    Write-Host ""
    Write-Host "备选方案：在 Claude Code 中运行" -ForegroundColor Yellow
    Write-Host "  /plugin install vibeflow@vibeflow" -ForegroundColor White
}
