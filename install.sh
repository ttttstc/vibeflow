#!/usr/bin/env bash
# VibeFlow installer for OpenCode (macOS / Linux)
# Usage:  curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/install.sh | bash
set -euo pipefail

INSTALL_DIR="${HOME}/.config/opencode/vibeflow"
PLUGINS_DIR="${HOME}/.config/opencode/plugins"
SKILLS_DIR="${HOME}/.config/opencode/skills"
REPO_URL="https://github.com/ttttstc/vibeflow.git"

echo "Installing vibeflow for OpenCode..."

# Clone or update
if [ -d "${INSTALL_DIR}/.git" ]; then
  echo "  → Updating existing installation..."
  git -C "${INSTALL_DIR}" pull --ff-only
else
  echo "  → Cloning repository..."
  git clone "${REPO_URL}" "${INSTALL_DIR}"
fi

# Create directories
mkdir -p "${PLUGINS_DIR}" "${SKILLS_DIR}"

# Remove stale symlinks / old copies
rm -f  "${PLUGINS_DIR}/vibeflow.js"
rm -rf "${SKILLS_DIR}/vibeflow"

# Create symlinks
ln -s "${INSTALL_DIR}/.opencode/plugins/vibeflow.js" "${PLUGINS_DIR}/vibeflow.js"
ln -s "${INSTALL_DIR}/skills"                       "${SKILLS_DIR}/vibeflow"

echo ""
echo "Done! vibeflow installed."
echo ""
echo "  Plugin : ${PLUGINS_DIR}/vibeflow.js"
echo "  Skills : ${SKILLS_DIR}/vibeflow"
echo ""
echo "Restart OpenCode to activate."
