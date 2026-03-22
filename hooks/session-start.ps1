$ErrorActionPreference = 'Stop'

$pluginRoot = Split-Path -Parent $PSScriptRoot
$phaseScript = Join-Path $pluginRoot 'scripts\get-vibeflow-phase.py'

# Detect current phase
$phaseInfo = if (Test-Path $phaseScript) {
    python $phaseScript --project-root . --json 2>$null | ConvertFrom-Json
} else {
    [pscustomobject]@{ phase = 'think'; reason = 'Phase detection unavailable.' }
}

$phase = $phaseInfo.phase
$reason = $phaseInfo.reason

# Check for key project files
$hasFeatureList = Test-Path 'feature-list.json'
$hasSrs = (Get-ChildItem 'docs/plans/*-srs.md' -ErrorAction SilentlyContinue).Count -gt 0
$hasDesign = (Get-ChildItem 'docs/plans/*-design.md' -ErrorAction SilentlyContinue).Count -gt 0

# Build lightweight context (no SKILL.md injection — use Skill tool instead)
$sessionContext = @"
<EXTREMELY_IMPORTANT>
You are in a VibeFlow project.

**Current phase: $phase**
Reason: $reason

Project state: feature-list=$hasFeatureList, srs=$hasSrs, design=$hasDesign

**You MUST use the Skill tool to invoke vibeflow:using-vibeflow before any response or action.**
This skill contains the full phase routing table. Do NOT read skill files directly - use the Skill tool.

Available commands: /vibeflow:work, /vibeflow:status, /vibeflow:requirements, /vibeflow:design, /vibeflow:init, /vibeflow:ucd, /vibeflow:st, /vibeflow:increment
</EXTREMELY_IMPORTANT>
"@

$payload = @{
    hookSpecificOutput = @{
        hookEventName = 'SessionStart'
        additionalContext = $sessionContext
    }
}

$payload | ConvertTo-Json -Depth 6 -Compress
