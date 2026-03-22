#!/usr/bin/env bash
# VibeFlow session start hook for macOS/Linux

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(dirname "$SCRIPT_DIR")"
PHASE_SCRIPT="$PLUGIN_ROOT/scripts/get-vibeflow-phase.py"

# Find project root by walking up from CWD until we find .vibeflow
# This handles resume/clear from subdirectories correctly, regardless of
# whether the plugin repo and target project are co-located or separate.
PROJECT_ROOT="$(pwd)"
_original_pwd="$PROJECT_ROOT"
while [ "$PROJECT_ROOT" != "/" ]; do
    if [ -d "$PROJECT_ROOT/.vibeflow" ]; then
        break
    fi
    PROJECT_ROOT="$(dirname "$PROJECT_ROOT")"
done
# Fallback to CWD if .vibeflow not found (e.g., outside any vibeflow project)
if [ ! -d "$PROJECT_ROOT/.vibeflow" ]; then
    PROJECT_ROOT="$_original_pwd"
fi

# Detect current phase
phase_json=$(python "$PHASE_SCRIPT" --project-root "$PROJECT_ROOT" --json 2>/dev/null || echo '{"phase":"think","reason":"Phase detection unavailable."}')

phase=$(echo "$phase_json" | python -c "import sys,json; print(json.load(sys.stdin).get('phase','unknown'))" 2>/dev/null || echo "unknown")
reason=$(echo "$phase_json" | python -c "import sys,json; print(json.load(sys.stdin).get('reason',''))" 2>/dev/null || echo "")

# Check for key project files
has_feature_list="false"
has_srs="false"
has_design="false"
[ -f "$PROJECT_ROOT/feature-list.json" ] && has_feature_list="true"
ls "$PROJECT_ROOT/docs/plans/"*-srs.md >/dev/null 2>&1 && has_srs="true"
ls "$PROJECT_ROOT/docs/plans/"*-design.md >/dev/null 2>&1 && has_design="true"

# Build lightweight context (no SKILL.md injection — use Skill tool instead)
python -c "
import json, sys

context = '''<EXTREMELY_IMPORTANT>
You are in a VibeFlow project.

**Current phase: ${phase}**
Reason: ${reason}

Project state: feature-list=${has_feature_list}, srs=${has_srs}, design=${has_design}

**You MUST use the Skill tool to invoke vibeflow:using-vibeflow before any response or action.**
This skill contains the full phase routing table. Do NOT read skill files directly — use the Skill tool.

Available commands: /vibeflow:work, /vibeflow:status, /vibeflow:requirements, /vibeflow:design, /vibeflow:init, /vibeflow:ucd, /vibeflow:st, /vibeflow:increment
</EXTREMELY_IMPORTANT>'''

payload = {
    'hookSpecificOutput': {
        'hookEventName': 'SessionStart',
        'additionalContext': context
    }
}
print(json.dumps(payload, ensure_ascii=False))
" 2>/dev/null || echo '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"VibeFlow session hook failed."}}'
