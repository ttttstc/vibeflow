# =============================================================================
# Claude Code Marketplace Installer (Windows PowerShell)
# =============================================================================
#
# Usage:
#   irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.ps1 | iex
#
# After installation, use Claude Code to install plugins:
#   /plugin install vibeflow@vibeflow
#

$ErrorActionPreference = "Stop"

# =============================================================================
# Configuration
# =============================================================================

$MarketplaceGitUrl = "https://github.com/ttttstc/vibeflow.git"
$MarketplaceName = "vibeflow"
$RepoName = "ttttstc/vibeflow"

# =============================================================================
# Paths
# =============================================================================

$ClaudePluginsDir = Join-Path $env:USERPROFILE ".claude\plugins"
$MarketplacesDir = Join-Path $ClaudePluginsDir "marketplaces"
$TargetDir = Join-Path $MarketplacesDir $MarketplaceName
$KnownMarketplacesFile = Join-Path $ClaudePluginsDir "known_marketplaces.json"

# =============================================================================
# Helper Functions
# =============================================================================

function Write-Info { param($Message) Write-Host "INFO: $Message" }
function Write-Success { param($Message) Write-Host "SUCCESS: $Message" }
function Write-Err { param($Message) Write-Host "ERROR: $Message" -ForegroundColor Red }

# =============================================================================
# Pre-flight Check
# =============================================================================

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Err "git is not installed"
    exit 1
}

Write-Info "Installing vibeflow marketplace..."

# =============================================================================
# Clone or Update
# =============================================================================

if (-not (Test-Path $MarketplacesDir)) {
    New-Item -ItemType Directory -Force -Path $MarketplacesDir | Out-Null
}

if (Test-Path $TargetDir) {
    Write-Info "Removing existing installation at $TargetDir..."
    Remove-Item $TargetDir -Recurse -Force
}

Write-Info "Cloning from: $MarketplaceGitUrl"
git clone --depth 1 $MarketplaceGitUrl $TargetDir 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Err "Failed to clone repository"
    exit 1
}

# Verify marketplace.json exists
$MarketplaceJson = Join-Path $TargetDir ".claude-plugin\marketplace.json"
if (-not (Test-Path $MarketplaceJson)) {
    Write-Err "marketplace.json not found in cloned repository"
    exit 1
}

# =============================================================================
# Register in known_marketplaces.json
# =============================================================================

Write-Info "Registering marketplace..."

if (-not (Test-Path $ClaudePluginsDir)) {
    New-Item -ItemType Directory -Force -Path $ClaudePluginsDir | Out-Null
}

if (-not (Test-Path $KnownMarketplacesFile)) {
    [System.IO.File]::WriteAllText($KnownMarketplacesFile, '{}', (New-Object System.Text.UTF8Encoding($false)))
}

$jsonContent = Get-Content $KnownMarketplacesFile -Raw
$json = $jsonContent | ConvertFrom-Json

$timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.000Z")

# Add marketplace entry
$marketplaceEntry = @{
    source = @{
        source = "github"
        repo = $RepoName
    }
    installLocation = $TargetDir
    lastUpdated = $timestamp
}
$json | Add-Member -MemberType NoteProperty -Name $MarketplaceName -Value $marketplaceEntry -Force

# Write back with formatting
$compact = $json | ConvertTo-Json -Depth 10 -Compress
[System.IO.File]::WriteAllText($KnownMarketplacesFile, $compact, (New-Object System.Text.UTF8Encoding($false)))

# =============================================================================
# Verify
# =============================================================================

$verifyContent = Get-Content $KnownMarketplacesFile -Raw | ConvertFrom-Json
if (-not $verifyContent.PSObject.Properties.Name.Contains($MarketplaceName)) {
    Write-Err "Marketplace registration failed"
    exit 1
}

# =============================================================================
# Success
# =============================================================================

Write-Host ""
Write-Success "VibeFlow marketplace installed successfully!"
Write-Host ""
Write-Host "  Marketplace key: $MarketplaceName"
Write-Host "  Install path:    $TargetDir"
Write-Host "  Git repo:       $MarketplaceGitUrl"
Write-Host ""
Write-Host "To activate the plugin, run in Claude Code:"
Write-Host "  /plugin install vibeflow@vibeflow"
Write-Host ""
