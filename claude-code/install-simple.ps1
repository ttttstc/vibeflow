# =============================================================================
# VibeFlow Simple Installer - No Git Required
# =============================================================================
#
# Usage:
#   irm https://raw.githubusercontent.com/ttttstc/vibeflow/refs/heads/feat/plan-value-review/claude-code/install-simple.ps1 | iex
#
# Or download and run manually:
#   Invoke-WebRequest -Uri "https://raw.githubusercontent.com/ttttstc/vibeflow/refs/heads/feat/plan-value-review/claude-code/install-simple.ps1" -OutFile install-simple.ps1
#   .\install-simple.ps1
#

$ErrorActionPreference = "Stop"

$MarketplaceName = "vibeflow"
$RepoUrl = "https://github.com/ttttstc/vibeflow"
$Branch = "refs/heads/feat/plan-value-review"
$DownloadUrl = "https://github.com/ttttstc/vibeflow/archive/refs/heads/feat/plan-value-review.zip"

$ClaudePluginsDir = Join-Path $env:USERPROFILE ".claude\plugins"
$MarketplacesDir = Join-Path $ClaudePluginsDir "marketplaces"
$TargetDir = Join-Path $MarketplacesDir $MarketplaceName
$KnownMarketplacesFile = Join-Path $ClaudePluginsDir "known_marketplaces.json"

Write-Host "=== VibeFlow Installer (Simple - No Git Required) ===" -ForegroundColor Cyan
Write-Host ""

# 1. Create directories
Write-Host "[1/5] Creating directories..." -ForegroundColor Yellow
if (-not (Test-Path $MarketplacesDir)) {
    New-Item -ItemType Directory -Force -Path $MarketplacesDir | Out-Null
    Write-Host "  Created: $MarketplacesDir" -ForegroundColor Green
}

# 2. Remove existing installation
if (Test-Path $TargetDir) {
    Write-Host "[2/5] Removing existing installation..." -ForegroundColor Yellow
    Remove-Item $TargetDir -Recurse -Force
    Write-Host "  Removed: $TargetDir" -ForegroundColor Green
}

# 3. Download and extract
Write-Host "[3/5] Downloading vibeflow..." -ForegroundColor Yellow
$TempZip = Join-Path $env:TEMP "vibeflow-download.zip"
$TempExtract = Join-Path $env:TEMP "vibeflow-extract"

try {
    Invoke-WebRequest -Uri "https://github.com/ttttstc/vibeflow/archive/refs/heads/feat/plan-value-review.zip" -OutFile $TempZip -UserAgent "vibeflow-installer/1.0"
    Write-Host "  Downloaded ($((Get-Item $TempZip).Length / 1MB) MB)" -ForegroundColor Green

    # Extract
    Write-Host "  Extracting..." -ForegroundColor Green
    Expand-Archive -Path $TempZip -DestinationPath $TempExtract -Force
    $ExtractedRepo = Join-Path $TempExtract "vibeflow-feat-plan-value-review"

    # Move to final location
    Move-Item -Path $ExtractedRepo -Destination $TargetDir -Force
    Write-Host "  Installed to: $TargetDir" -ForegroundColor Green

    # Cleanup
    Remove-Item $TempZip -Force -ErrorAction SilentlyContinue
    Remove-Item $TempExtract -Recurse -Force -ErrorAction SilentlyContinue
} catch {
    Write-Host "  Download failed: $_" -ForegroundColor Red
    Write-Host "  Falling back to git clone..." -ForegroundColor Yellow

    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Host "  ERROR: git is not installed and download failed" -ForegroundColor Red
        Write-Host "  Please install git or use GitHub Desktop" -ForegroundColor Red
        exit 1
    }

    git clone --depth 1 "https://github.com/ttttstc/vibeflow.git" $TargetDir
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: git clone failed" -ForegroundColor Red
        exit 1
    }
    Write-Host "  Cloned via git" -ForegroundColor Green
}

# 4. Verify marketplace.json
Write-Host "[4/5] Verifying installation..." -ForegroundColor Yellow
$MarketplaceJson = Join-Path $TargetDir ".claude-plugin\marketplace.json"
if (-not (Test-Path $MarketplaceJson)) {
    Write-Host "  ERROR: marketplace.json not found at $MarketplaceJson" -ForegroundColor Red
    exit 1
}
Write-Host "  marketplace.json: OK" -ForegroundColor Green

$SkillDir = Join-Path $TargetDir "skills"
if (-not (Test-Path $SkillDir)) {
    Write-Host "  ERROR: skills directory not found" -ForegroundColor Red
    exit 1
}
$skillCount = (Get-ChildItem $SkillDir -Directory).Count
Write-Host "  Skills: $skillCount found" -ForegroundColor Green

# 5. Register in known_marketplaces.json
Write-Host "[5/5] Registering marketplace..." -ForegroundColor Yellow
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
    Write-Host "  ERROR: Registration failed" -ForegroundColor Red
    exit 1
}
Write-Host "  Registered as '$MarketplaceName' in known_marketplaces.json" -ForegroundColor Green

# Done
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  SUCCESS! VibeFlow is installed." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Marketplace key: $MarketplaceName" -ForegroundColor White
Write-Host "  Install path:    $TargetDir" -ForegroundColor White
Write-Host ""

# Try to find and signal Claude Code to reload plugins
$claudeProcesses = Get-Process -Name "claude" -ErrorAction SilentlyContinue
if ($claudeProcesses) {
    Write-Host "Detected running Claude Code instance(s)." -ForegroundColor Cyan
    Write-Host "Please restart Claude Code (close and reopen) for changes to take effect." -ForegroundColor Yellow
    Write-Host "Then run: /plugin install vibeflow@vibeflow" -ForegroundColor White
} else {
    Write-Host "NEXT STEP:" -ForegroundColor Cyan
    Write-Host "  1. Open Claude Code" -ForegroundColor White
    Write-Host "  2. Run: /plugin install vibeflow@vibeflow" -ForegroundColor White
}
Write-Host ""
