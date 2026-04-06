#!/usr/bin/env bash
# VibeFlow session start hook for macOS/Linux

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(dirname "$SCRIPT_DIR")"
ROUTER_PATH="$PLUGIN_ROOT/skills/vibeflow-router/SKILL.md"
PHASE_SCRIPT="$PLUGIN_ROOT/scripts/get-vibeflow-phase.py"

router_content=$(cat "$ROUTER_PATH" 2>/dev/null || echo "Error reading vibeflow-router skill.")

phase_info=$(python "$PHASE_SCRIPT" --project-root "$PLUGIN_ROOT" --json 2>/dev/null || echo '{"phase":"spark","reason":"Phase script missing."}')

phase=$(echo "$phase_info" | python -c "import sys,json; print(json.load(sys.stdin).get('phase','unknown'))" 2>/dev/null || echo "unknown")
reason=$(echo "$phase_info" | python -c "import sys,json; print(json.load(sys.stdin).get('reason',''))" 2>/dev/null || echo "")

resume_mode=$(echo "$phase_info" | python -c "import sys,json; print(json.load(sys.stdin).get('resume_mode',''))" 2>/dev/null || echo "")
next_action=$(echo "$phase_info" | python -c "import sys,json; print(json.load(sys.stdin).get('next_action',''))" 2>/dev/null || echo "")
overview_suggestion=$(echo "$phase_info" | python -c "import sys,json; print(json.load(sys.stdin).get('overview_suggestion',''))" 2>/dev/null || echo "")
open_files=$(echo "$phase_info" | python -c "import sys,json; data=json.load(sys.stdin); print('\n- '.join(data.get('open_files',[])))" 2>/dev/null || echo "")

status_hint="
Detected phase: $phase. Reason: $reason
Resume mode: $resume_mode
Next action: $next_action"

if [ -n "$overview_suggestion" ]; then
  status_hint="$status_hint
Overview hint: $overview_suggestion"
fi

if [ -n "$open_files" ]; then
  status_hint="$status_hint
Open these first:
- $open_files"
fi

session_context="<EXTREMELY_IMPORTANT>
You are in a vibeflow project.

Use the router skill below before any phase work:

$router_content
$status_hint
</EXTREMELY_IMPORTANT>"

# Escape string for JSON using Python — avoids bash string-interpolation injection
# Use a temp file to pass session_context to Python — avoids any quote escaping issues
# caused by triple-quote sequences in SKILL.md content.
_tmpfile=$(mktemp)
echo "$session_context" > "$_tmpfile"
payload=$(python -c "
import sys, json
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    ctx = f.read()
payload = {
    'additional_context': ctx,
    'hookSpecificOutput': {
        'hookEventName': 'SessionStart',
        'additionalContext': ctx
    }
}
print(json.dumps(payload, indent=2, ensure_ascii=False))
" "$_tmpfile" 2>/dev/null || echo '{"additional_context":"Error generating context","hookSpecificOutput":{"hookEventName":"SessionStart"}}')
rm -f "$_tmpfile"

echo "$payload"
