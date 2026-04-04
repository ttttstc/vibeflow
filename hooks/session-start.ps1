$ErrorActionPreference = 'Stop'

$pluginRoot = Split-Path -Parent $PSScriptRoot
$routerPath = Join-Path $pluginRoot 'skills\vibeflow-router\SKILL.md'

if (Test-Path $routerPath) {
    $routerContent = Get-Content $routerPath -Raw
} else {
    $routerContent = 'Error reading vibeflow-router skill.'
}

$phaseScript = Join-Path $pluginRoot 'scripts\get-vibeflow-phase.py'
$phaseInfo = if (Test-Path $phaseScript) {
    python $phaseScript --project-root $pluginRoot --json | ConvertFrom-Json
} else {
    [pscustomobject]@{ phase = 'spark'; reason = 'Phase script missing.' }
}

$openFiles = ""
if ($phaseInfo.open_files) {
    $openFiles = ($phaseInfo.open_files -join "`n- ")
    if ($openFiles) {
        $openFiles = "`nOpen these first:`n- $openFiles"
    }
}

$statusHint = "`n`nDetected phase: $($phaseInfo.phase). Reason: $($phaseInfo.reason)`nResume mode: $($phaseInfo.resume_mode)`nNext action: $($phaseInfo.next_action)$openFiles"

$sessionContext = @"
<EXTREMELY_IMPORTANT>
You are in a vibeflow project.

Use the router skill below before any phase work:

$routerContent
$statusHint
</EXTREMELY_IMPORTANT>
"@

$payload = @{
    additional_context = $sessionContext
    hookSpecificOutput = @{
        hookEventName = 'SessionStart'
        additionalContext = $sessionContext
    }
}

$payload | ConvertTo-Json -Depth 6 -Compress
