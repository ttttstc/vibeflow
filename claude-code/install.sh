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
REPO_NAME="ttttstc/vibeflow"

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
  RED='\033[0;31m'
  BOLD='\033[1m'
  RESET='\033[0m'
else
  GREEN=''
  BLUE=''
  YELLOW=''
  RED=''
  BOLD=''
  RESET=''
fi

info()    { echo -e "${BLUE}[INFO]${RESET} $*"; }
success() { echo -e "${GREEN}[SUCCESS]${RESET} $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; }

# =============================================================================
# Pre-flight Check
# =============================================================================

if ! command -v git &>/dev/null; then
  error "git is not installed"
  exit 1
fi

info "Installing vibeflow marketplace..."

# =============================================================================
# Clone or Update
# =============================================================================

mkdir -p "$MARKETPLACES_DIR"

if [[ -d "$TARGET_DIR" ]]; then
  info "Removing existing installation at $TARGET_DIR..."
  rm -rf "$TARGET_DIR"
fi

info "Cloning from: $MARKETPLACE_GIT_URL"
git clone --depth 1 "$MARKETPLACE_GIT_URL" "$TARGET_DIR"

# Verify marketplace.json exists
if [[ ! -f "$TARGET_DIR/.claude-plugin/marketplace.json" ]]; then
  error "marketplace.json not found in cloned repository"
  exit 1
fi

# =============================================================================
# Register in known_marketplaces.json
# =============================================================================

info "Registering marketplace..."
mkdir -p "$CLAUDE_PLUGINS_DIR"

if [[ ! -f "$KNOWN_MARKETPLACES_FILE" ]]; then
  echo '{}' > "$KNOWN_MARKETPLACES_FILE"
fi

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")

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
  error "jq is not installed - cannot update known_marketplaces.json"
  error "Install jq: brew install jq (macOS) or apt install jq (Linux)"
  exit 1
fi

# =============================================================================
# Verify
# =============================================================================

if ! jq -e ".$MARKETPLACE_NAME" "$KNOWN_MARKETPLACES_FILE" &>/dev/null; then
  error "Marketplace registration failed"
  exit 1
fi

# =============================================================================
# Success
# =============================================================================

echo ""
success "VibeFlow marketplace installed successfully!"
echo ""
echo "  Marketplace key: $MARKETPLACE_NAME"
echo "  Install path:    $TARGET_DIR"
echo "  Git repo:       $MARKETPLACE_GIT_URL"
echo ""
echo "To activate the plugin, run in Claude Code:"
echo "  /plugin install vibeflow@vibeflow"
echo ""
