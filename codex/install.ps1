# =============================================================================
# VibeFlow Installer for Codex (Windows PowerShell)
# =============================================================================
#
# Usage:
#   irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/codex/install.ps1 | iex
#   $env:VIBEFLOW_VERSION="v1.0.0"; irm https://raw.githubusercontent.com/ttttstc/vibeflow/main/codex/install.ps1 | iex
#

param(
    [string]$Version = $env:VIBEFLOW_VERSION
)

$ErrorActionPreference = "Stop"

$RepoUrl = "https://github.com/ttttstc/vibeflow.git"
$RepoName = "ttttstc/vibeflow"
$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
$InstallDir = Join-Path $CodexHome "vibeflow"
$SkillsDir = Join-Path $CodexHome "skills"

function Write-Info { param($Message) Write-Host "INFO: $Message" }
function Write-Success { param($Message) Write-Host "SUCCESS: $Message" }
function Write-Err { param($Message) Write-Host "ERROR: $Message" -ForegroundColor Red }

function Normalize-Version {
    param([string]$Value)

    if ([string]::IsNullOrWhiteSpace($Value) -or $Value -eq "latest") {
        return "latest"
    }
    if ($Value -match '^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$') {
        return "v$Value"
    }
    return $Value
}

function Resolve-LatestVersion {
    try {
        $release = Invoke-RestMethod -Uri "https://api.github.com/repos/$RepoName/releases/latest" -Headers @{ "User-Agent" = "vibeflow-installer/1.0" }
        if ($release.tag_name) {
            return [string]$release.tag_name
        }
    } catch {
    }

    if (Get-Command git -ErrorAction SilentlyContinue) {
        try {
            $latestTag = git ls-remote --tags --refs --sort=-v:refname $RepoUrl 2>$null |
                ForEach-Object { ($_ -split 'refs/tags/')[-1].Trim() } |
                Where-Object { $_ -match '^(v)?[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$' } |
                Select-Object -First 1
            if ($latestTag) {
                return [string]$latestTag
            }
        } catch {
        }
    }

    return "main"
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Err "git is not installed"
    exit 1
}

$RequestedVersion = if ([string]::IsNullOrWhiteSpace($Version)) { "latest" } else { $Version }
$ResolvedRef = Normalize-Version $Version
if ($ResolvedRef -eq "latest") {
    $ResolvedRef = Resolve-LatestVersion
}

Write-Info "Installing vibeflow for Codex..."
Write-Info "Requested version: $RequestedVersion"
Write-Info "Resolved ref: $ResolvedRef"

if (-not (Test-Path $CodexHome)) {
    New-Item -ItemType Directory -Force -Path $CodexHome | Out-Null
}
if (-not (Test-Path $SkillsDir)) {
    New-Item -ItemType Directory -Force -Path $SkillsDir | Out-Null
}

if (Test-Path $InstallDir) {
    Write-Info "Removing existing installation at $InstallDir..."
    Remove-Item $InstallDir -Recurse -Force
}

Write-Info "Cloning from: $RepoUrl ($ResolvedRef)"
git clone --depth 1 --branch $ResolvedRef $RepoUrl $InstallDir 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Err "Failed to clone repository for ref $ResolvedRef"
    exit 1
}

$SourceSkillsDir = Join-Path $InstallDir "skills"
if (-not (Test-Path $SourceSkillsDir)) {
    Write-Err "skills directory not found in cloned repository"
    exit 1
}

Get-ChildItem $SourceSkillsDir -Directory | ForEach-Object {
    $SkillName = $_.Name
    $TargetPath = Join-Path $SkillsDir $SkillName
    if (Test-Path $TargetPath) {
        Remove-Item $TargetPath -Recurse -Force
    }
    New-Item -ItemType Junction -Path $TargetPath -Target $_.FullName | Out-Null
}

Write-Host ""
Write-Success "VibeFlow installed for Codex."
Write-Host ""
Write-Host "  Repo:    $InstallDir"
Write-Host "  Skills:  $SkillsDir"
if (Test-Path (Join-Path $InstallDir "VERSION")) {
    Write-Host "  Version: $((Get-Content (Join-Path $InstallDir 'VERSION') -Raw).Trim())"
}
Write-Host ""
Write-Host "Restart Codex to pick up the new skills."
