#!/usr/bin/env bash
# VibeFlow session start hook for macOS/Linux

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(dirname "$SCRIPT_DIR")"
ROUTER_PATH="$PLUGIN_ROOT/skills/vibeflow-router/SKILL.md"
PHASE_SCRIPT="$PLUGIN_ROOT/scripts/get-vibeflow-phase.py"

router_content=$(cat "$ROUTER_PATH" 2>/dev/null || echo "Error reading vibeflow-router skill.")

phase_info=$(python "$PHASE_SCRIPT" --project-root "$PLUGIN_ROOT" --json 2>/dev/null || echo '{"phase":"think","reason":"Phase script missing."}')

phase=$(echo "$phase_info" | python -c "import sys,json; print(json.load(sys.stdin).get('phase','unknown'))" 2>/dev/null || echo "unknown")
reason=$(echo "$phase_info" | python -c "import sys,json; print(json.load(sys.stdin).get('reason',''))" 2>/dev/null || echo "")

status_hint="
Detected phase: $phase. Reason: $reason"

session_context="<EXTREMELY_IMPORTANT>
You are in a vibeflow project.

Use the router skill below before any phase work:

$router_content
$status_hint
</EXTREMELY_IMPORTANT>"

payload=$(python -c "
import sys, json
payload = {
    'additional_context': '''$session_context''',
    'hookSpecificOutput': {
        'hookEventName': 'SessionStart',
        'additionalContext': '''$session_context'''
    }
}
print(json.dumps(payload, indent=2, ensure_ascii=False))
" 2>/dev/null || echo '{"additional_context":"Error generating context","hookSpecificOutput":{"hookEventName":"SessionStart"}}')

echo "$payload"
