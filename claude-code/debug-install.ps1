# VibeFlow Installation Diagnostic Script
# Run this in PowerShell to diagnose plugin installation issues

$ErrorActionPreference = "Continue"

Write-Host "=== VibeFlow Installation Diagnostic ===" -ForegroundColor Cyan
Write-Host ""

$ClaudePluginsDir = Join-Path $env:USERPROFILE ".claude\plugins"
$MarketplacesDir = Join-Path $ClaudePluginsDir "marketplaces"
$TargetDir = Join-Path $MarketplacesDir "vibeflow"
$KnownMarketplacesFile = Join-Path $ClaudePluginsDir "known_marketplaces.json"

# 1. Check known_marketplaces.json
Write-Host "1. Checking known_marketplaces.json..." -ForegroundColor Yellow
if (Test-Path $KnownMarketplacesFile) {
    Write-Host "   FOUND: $KnownMarketplacesFile" -ForegroundColor Green
    try {
        $kmContent = Get-Content $KnownMarketplacesFile -Raw
        $kmJson = $kmContent | ConvertFrom-Json
        $entries = $kmJson.PSObject.Properties.Name -join ", "
        Write-Host "   Entries: $entries" -ForegroundColor Green

        if ($kmJson.PSObject.Properties.Name.Contains("vibeflow")) {
            Write-Host "   [OK] vibeflow entry found" -ForegroundColor Green
            $vfEntry = $kmJson.vibeflow
            Write-Host "   installLocation: $($vfEntry.installLocation)"
            Write-Host "   repo: $($vfEntry.source.repo)"
        } else {
            Write-Host "   [FAIL] vibeflow NOT in known_marketplaces.json" -ForegroundColor Red
        }
    } catch {
        Write-Host "   [FAIL] JSON parse error: $_" -ForegroundColor Red
    }
} else {
    Write-Host "   [FAIL] known_marketplaces.json NOT FOUND" -ForegroundColor Red
}
Write-Host ""

# 2. Check marketplace directory
Write-Host "2. Checking marketplace directory..." -ForegroundColor Yellow
if (Test-Path $TargetDir) {
    Write-Host "   FOUND: $TargetDir" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] Marketplace directory NOT FOUND: $TargetDir" -ForegroundColor Red
}
Write-Host ""

# 3. Check marketplace.json
Write-Host "3. Checking marketplace.json..." -ForegroundColor Yellow
$MarketplaceJson = Join-Path $TargetDir ".claude-plugin\marketplace.json"
if (Test-Path $MarketplaceJson) {
    Write-Host "   FOUND: $MarketplaceJson" -ForegroundColor Green
    try {
        $mpContent = Get-Content $MarketplaceJson -Raw
        $mpJson = $mpContent | ConvertFrom-Json
        Write-Host "   Marketplace name: $($mpJson.name)"
        $pluginCount = $mpJson.plugins.Count
        Write-Host "   Plugin count: $pluginCount"
        $pluginNames = $mpJson.plugins | ForEach-Object { $_.name } | Sort-Object
        Write-Host "   Plugins: $($pluginNames -join ", ")"
        if ($pluginNames -contains "vibeflow") {
            Write-Host "   [OK] Plugin 'vibeflow' found in marketplace.json" -ForegroundColor Green
        } else {
            Write-Host "   [FAIL] Plugin 'vibeflow' NOT in plugins array" -ForegroundColor Red
        }
    } catch {
        Write-Host "   [FAIL] JSON parse error: $_" -ForegroundColor Red
    }
} else {
    Write-Host "   [FAIL] marketplace.json NOT FOUND: $MarketplaceJson" -ForegroundColor Red
}
Write-Host ""

# 4. Check plugin.json
Write-Host "4. Checking plugin.json..." -ForegroundColor Yellow
$PluginJson = Join-Path $TargetDir ".claude-plugin\plugin.json"
if (Test-Path $PluginJson) {
    Write-Host "   FOUND: $PluginJson" -ForegroundColor Green
    try {
        $plContent = Get-Content $PluginJson -Raw
        $plJson = $plContent | ConvertFrom-Json
        Write-Host "   Plugin name: $($plJson.name)"
        Write-Host "   Plugin version: $($plJson.version)"
    } catch {
        Write-Host "   [FAIL] JSON parse error: $_" -ForegroundColor Red
    }
} else {
    Write-Host "   [FAIL] plugin.json NOT FOUND: $PluginJson" -ForegroundColor Red
}
Write-Host ""

# 5. Check skills directory
Write-Host "5. Checking skills..." -ForegroundColor Yellow
$SkillsDir = Join-Path $TargetDir "skills"
if (Test-Path $SkillsDir) {
    $skillCount = (Get-ChildItem $SkillsDir -Directory).Count
    Write-Host "   FOUND: $SkillsDir ($skillCount skills)" -ForegroundColor Green
    $coreSkills = @("vibeflow", "vibeflow-router", "vibeflow-spark", "vibeflow-design", "vibeflow-tasks")
    foreach ($skill in $coreSkills) {
        $skillPath = Join-Path $SkillsDir $skill
        if (Test-Path $skillPath) {
            $hasSkillet = Test-Path (Join-Path $skillPath "SKILL.md")
            if ($hasSkillet) {
                Write-Host "   [OK] $skill/SKILL.md exists" -ForegroundColor Green
            } else {
                Write-Host "   [WARN] $skill exists but no SKILL.md" -ForegroundColor Yellow
            }
        } else {
            Write-Host "   [FAIL] $skill NOT FOUND" -ForegroundColor Red
        }
    }
} else {
    Write-Host "   [FAIL] skills directory NOT FOUND: $SkillsDir" -ForegroundColor Red
}
Write-Host ""

# 5b. Check plugin-visible command skills
Write-Host "5b. Checking plugin-visible command skills..." -ForegroundColor Yellow
$EntryCommandSkills = @("vibeflow-status", "vibeflow-dashboard")
if (Test-Path $SkillsDir) {
    foreach ($skill in $EntryCommandSkills) {
        $skillPath = Join-Path $SkillsDir $skill
        $skillMd = Join-Path $skillPath "SKILL.md"
        if (Test-Path $skillMd) {
            Write-Host "   [OK] $skill/SKILL.md exists" -ForegroundColor Green
        } else {
            Write-Host "   [FAIL] $skill/SKILL.md NOT FOUND" -ForegroundColor Red
        }
    }
} else {
    Write-Host "   [FAIL] skills directory missing, cannot verify command skills" -ForegroundColor Red
}
Write-Host ""

# 6. Summary
Write-Host "=== Summary ===" -ForegroundColor Cyan
$issues = 0

if (-not (Test-Path $KnownMarketplacesFile)) { $issues++; Write-Host "  - known_marketplaces.json missing" -ForegroundColor Red }
else {
    try {
        $kmJson2 = (Get-Content $KnownMarketplacesFile -Raw) | ConvertFrom-Json
        if (-not $kmJson2.PSObject.Properties.Name.Contains("vibeflow")) { $issues++; Write-Host "  - vibeflow not registered" -ForegroundColor Red }
    } catch { $issues++; Write-Host "  - known_marketplaces.json invalid" -ForegroundColor Red }
}

if (-not (Test-Path $TargetDir)) { $issues++; Write-Host "  - marketplace directory missing" -ForegroundColor Red }
if (-not (Test-Path $MarketplaceJson)) { $issues++; Write-Host "  - marketplace.json missing" -ForegroundColor Red }
if (-not (Test-Path $PluginJson)) { $issues++; Write-Host "  - plugin.json missing" -ForegroundColor Red }
if (-not (Test-Path $SkillsDir)) { $issues++; Write-Host "  - skills directory missing" -ForegroundColor Red }
if (-not (Test-Path (Join-Path $SkillsDir "vibeflow-status\\SKILL.md"))) { $issues++; Write-Host "  - vibeflow-status plugin-visible command skill missing" -ForegroundColor Red }
if (-not (Test-Path (Join-Path $SkillsDir "vibeflow-dashboard\\SKILL.md"))) { $issues++; Write-Host "  - vibeflow-dashboard plugin-visible command skill missing" -ForegroundColor Red }

if ($issues -eq 0) {
    Write-Host "  All checks passed! Run Claude Code and try:" -ForegroundColor Green
    Write-Host "    /plugin install vibeflow@vibeflow" -ForegroundColor Cyan
} else {
    Write-Host "  $issues issue(s) found. Fix these before installing." -ForegroundColor Red
}

Write-Host ""
Write-Host "If all checks pass but /plugin install still fails:" -ForegroundColor Yellow
Write-Host "  1. Restart Claude Code completely" -ForegroundColor White
Write-Host "  2. Check Claude Code logs for detailed errors" -ForegroundColor White
Write-Host "  3. Try: /plugin install vibeflow@vibeflow --verbose" -ForegroundColor White
