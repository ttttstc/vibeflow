#!/usr/bin/env bash
# VibeFlow installer for OpenCode (macOS / Linux)
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/opencode/install.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/opencode/install.sh | VIBEFLOW_VERSION=v1.0.0 bash
set -euo pipefail

INSTALL_DIR="${HOME}/.config/opencode/vibeflow"
PLUGINS_DIR="${HOME}/.config/opencode/plugins"
SKILLS_DIR="${HOME}/.config/opencode/skills"
REPO_URL="https://github.com/ttttstc/vibeflow.git"
REPO_NAME="ttttstc/vibeflow"
REQUESTED_VERSION="${1:-${VIBEFLOW_VERSION:-latest}}"

normalize_requested_version() {
  local value="${1:-latest}"
  if [[ -z "$value" || "$value" == "latest" ]]; then
    printf 'latest\n'
    return 0
  fi
  if [[ "$value" =~ ^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$ ]]; then
    printf 'v%s\n' "$value"
    return 0
  fi
  printf '%s\n' "$value"
}

extract_tag_name_from_json() {
  local json="${1:-}"
  if [[ -z "$json" ]]; then
    return 0
  fi
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$json" | jq -r '.tag_name // empty'
    return 0
  fi
  if command -v python3 >/dev/null 2>&1; then
    python3 -c 'import json,sys; print(json.loads(sys.stdin.read()).get("tag_name",""))' <<<"$json" 2>/dev/null || true
    return 0
  fi
  if command -v python >/dev/null 2>&1; then
    python -c 'import json,sys; print(json.loads(sys.stdin.read()).get("tag_name",""))' <<<"$json" 2>/dev/null || true
    return 0
  fi
  sed -nE 's/.*"tag_name"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/p' <<<"$json" | head -n 1
}

resolve_latest_version() {
  local latest_tag=""
  local release_json=""

  if command -v curl >/dev/null 2>&1; then
    release_json="$(curl -fsSL "https://api.github.com/repos/${REPO_NAME}/releases/latest" 2>/dev/null || true)"
  elif command -v wget >/dev/null 2>&1; then
    release_json="$(wget -qO- "https://api.github.com/repos/${REPO_NAME}/releases/latest" 2>/dev/null || true)"
  fi

  latest_tag="$(extract_tag_name_from_json "$release_json")"
  if [[ -n "$latest_tag" && "$latest_tag" != "null" ]]; then
    printf '%s\n' "$latest_tag"
    return 0
  fi

  if command -v git >/dev/null 2>&1; then
    latest_tag="$(git ls-remote --tags --refs --sort=-v:refname "$REPO_URL" 2>/dev/null | awk -F/ '{print $3}' | grep -E '^(v)?[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$' | head -n 1 || true)"
    if [[ -n "$latest_tag" ]]; then
      printf '%s\n' "$latest_tag"
      return 0
    fi
  fi

  printf 'main\n'
}

if ! command -v git >/dev/null 2>&1; then
  echo "ERROR: git is required to install vibeflow for OpenCode." >&2
  exit 1
fi

RESOLVED_REF="$(normalize_requested_version "$REQUESTED_VERSION")"
if [[ "$RESOLVED_REF" == "latest" ]]; then
  RESOLVED_REF="$(resolve_latest_version)"
fi

TMP_DIR="${INSTALL_DIR}.tmp.$$"
cleanup() {
  if [[ -d "$TMP_DIR" ]]; then
    rm -rf "$TMP_DIR"
  fi
}
trap cleanup EXIT

echo "Installing vibeflow for OpenCode..."
echo "  -> Requested version: ${REQUESTED_VERSION:-latest}"
echo "  -> Resolved ref: ${RESOLVED_REF}"
echo "  -> Downloading repository..."

if ! git clone --depth 1 --branch "$RESOLVED_REF" "$REPO_URL" "$TMP_DIR"; then
  echo "ERROR: Failed to download ref '${RESOLVED_REF}' from ${REPO_URL}" >&2
  exit 1
fi

rm -rf "${INSTALL_DIR}"
mv "$TMP_DIR" "${INSTALL_DIR}"

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
if [[ -f "${INSTALL_DIR}/VERSION" ]]; then
  echo "  Version: $(<"${INSTALL_DIR}/VERSION")"
fi
echo ""
echo "Restart OpenCode to activate."
