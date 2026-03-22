#!/usr/bin/env bash
# =============================================================================
# Claude Code Marketplace Installer (macOS / Linux)
# =============================================================================
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.sh | bash
#
# After installation, use Claude Code to install plugins:
#   /plugin install vibeflow@vibeflow
#
set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================

MARKETPLACE_GIT_URL="https://github.com/ttttstc/vibeflow.git"
MARKETPLACE_NAME="vibeflow"

# =============================================================================
# Paths
# =============================================================================

CLAUDE_PLUGINS_DIR="${HOME}/.claude/plugins"
MARKETPLACES_DIR="${CLAUDE_PLUGINS_DIR}/marketplaces"
TARGET_DIR="${MARKETPLACES_DIR}/${MARKETPLACE_NAME}"
KNOWN_MARKETPLACES_FILE="${CLAUDE_PLUGINS_DIR}/known_marketplaces.json"

# =============================================================================
# Color Output
# =============================================================================

if [[ -t 1 ]]; then
  GREEN='\033[0;32m'
  BLUE='\033[0;34m'
  YELLOW='\033[0;33m'
  BOLD='\033[1m'
  RESET='\033[0m'
else
  GREEN=''
  BLUE=''
  YELLOW=''
  BOLD=''
  RESET=''
fi

info()    { echo -e "${BLUE}ℹ${RESET} $*"; }
warn()    { echo -e "${YELLOW}⚠${RESET} $*"; }
success() { echo -e "${GREEN}✓${RESET} $*"; }

# =============================================================================
# Pre-flight Check
# =============================================================================

if ! command -v git &>/dev/null; then
  echo "Error: git is not installed" >&2
  exit 1
fi

# =============================================================================
# Install
# =============================================================================

info "Installing marketplace: $MARKETPLACE_NAME"

# Remove existing if present
if [[ -d "$TARGET_DIR" ]]; then
  info "Removing existing installation..."
  rm -rf "$TARGET_DIR"
fi

# Clone repository
info "Cloning from: $MARKETPLACE_GIT_URL"
mkdir -p "$MARKETPLACES_DIR"
git clone --depth 1 "$MARKETPLACE_GIT_URL" "$TARGET_DIR"

# Update known_marketplaces.json
info "Registering marketplace..."
mkdir -p "$CLAUDE_PLUGINS_DIR"

if [[ ! -f "$KNOWN_MARKETPLACES_FILE" ]]; then
  echo '{}' > "$KNOWN_MARKETPLACES_FILE"
fi

# Update known_marketplaces.json using jq
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")
REPO_NAME="${MARKETPLACE_GIT_URL#https://github.com/}"
REPO_NAME="${REPO_NAME%.git}"

if command -v jq &>/dev/null; then
  jq --arg name "$MARKETPLACE_NAME" \
     --arg repo "$REPO_NAME" \
     --arg location "$TARGET_DIR" \
     --arg timestamp "$TIMESTAMP" \
     '.[$name] = {
       "source": {"source": "github", "repo": $repo},
       "installLocation": $location,
       "lastUpdated": $timestamp
     }' "$KNOWN_MARKETPLACES_FILE" > "${KNOWN_MARKETPLACES_FILE}.tmp" && \
  mv "${KNOWN_MARKETPLACES_FILE}.tmp" "$KNOWN_MARKETPLACES_FILE"
else
  warn "jq not found, skipping known_marketplaces.json update"
fi

# =============================================================================
# Success
# =============================================================================

echo ""
echo -e "${BOLD}${GREEN}✓ Marketplace installed successfully!${RESET}"
echo ""
echo "  Name: $MARKETPLACE_NAME"
echo "  Path: $TARGET_DIR"
echo ""
echo -e "${BOLD}To install plugins, use Claude Code:${RESET}"
echo "  /plugin install vibeflow@$MARKETPLACE_NAME"
echo ""
