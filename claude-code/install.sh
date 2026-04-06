#!/usr/bin/env bash
# =============================================================================
# VibeFlow 一键安装脚本 - 在 Claude Code 内运行
# =============================================================================
#
# 使用方法：复制以下命令，粘贴到 Claude Code 对话框运行：
#
#   /sh curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.sh | bash
#
# 可选：指定版本（默认安装 latest）
#   /sh curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/main/claude-code/install.sh | VIBEFLOW_VERSION=0.8.0 bash
#
# 安装后运行：
#   /plugin install vibeflow@vibeflow
#
# =============================================================================

set -euo pipefail

MARKETPLACE_NAME="vibeflow"
MARKETPLACE_GIT_URL="https://github.com/ttttstc/vibeflow.git"
REPO_NAME="ttttstc/vibeflow"
REQUESTED_VERSION="${1:-${VIBEFLOW_VERSION:-latest}}"

CLAUDE_PLUGINS_DIR="${HOME}/.claude/plugins"
MARKETPLACES_DIR="${CLAUDE_PLUGINS_DIR}/marketplaces"
TARGET_DIR="${MARKETPLACES_DIR}/${MARKETPLACE_NAME}"
KNOWN_MARKETPLACES_FILE="${CLAUDE_PLUGINS_DIR}/known_marketplaces.json"

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
RESET='\033[0m'

info()    { echo -e "${CYAN}[INFO]${RESET} $*"; }
success() { echo -e "${GREEN}[OK]${RESET} $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; }

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
    latest_tag="$(git ls-remote --tags --refs --sort=-v:refname "$MARKETPLACE_GIT_URL" 2>/dev/null | awk -F/ '{print $3}' | grep -E '^(v)?[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$' | head -n 1 || true)"
    if [[ -n "$latest_tag" ]]; then
      printf '%s\n' "$latest_tag"
      return 0
    fi
  fi

  printf 'main\n'
}

is_version_ref() {
  [[ "${1:-}" =~ ^v?[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$ ]]
}

info "开始安装 VibeFlow..."

RESOLVED_REF="$(normalize_requested_version "$REQUESTED_VERSION")"
if [[ "$RESOLVED_REF" == "latest" ]]; then
  RESOLVED_REF="$(resolve_latest_version)"
fi

info "请求版本: ${REQUESTED_VERSION:-latest}"
info "解析版本: ${RESOLVED_REF}"

# 1. Create directories
mkdir -p "$MARKETPLACES_DIR"
success "目录就绪"

# 2. Remove existing
if [[ -d "$TARGET_DIR" ]]; then
  info "移除旧版本..."
  rm -rf "$TARGET_DIR"
fi

# 3. Download - try git first, fall back to ZIP
info "下载中..."

download_ok=false
if command -v git &>/dev/null; then
  if git clone --depth 1 --branch "$RESOLVED_REF" "$MARKETPLACE_GIT_URL" "$TARGET_DIR" 2>&1; then
    download_ok=true
    success "下载完成 (git)"
  fi
fi

if [[ "$download_ok" != "true" ]]; then
  info "git 不可用，尝试 ZIP 下载..."
  TEMP_ZIP="/tmp/vibeflow-download.zip"
  TEMP_EXTRACT="/tmp/vibeflow-extract"
  ARCHIVE_KIND="heads"
  if is_version_ref "$RESOLVED_REF"; then
    ARCHIVE_KIND="tags"
  fi

  if command -v curl &>/dev/null; then
    curl -fsSL "https://github.com/ttttstc/vibeflow/archive/refs/${ARCHIVE_KIND}/${RESOLVED_REF}.zip" -o "$TEMP_ZIP" 2>&1
  elif command -v wget &>/dev/null; then
    wget -q "https://github.com/ttttstc/vibeflow/archive/refs/${ARCHIVE_KIND}/${RESOLVED_REF}.zip" -O "$TEMP_ZIP" 2>&1
  else
    error "curl 和 wget 都不可用，无法下载"
    exit 1
  fi

  if [[ ! -f "$TEMP_ZIP" ]]; then
    error "下载失败"
    exit 1
  fi

  rm -rf "$TEMP_EXTRACT"
  mkdir -p "$TEMP_EXTRACT"
  if command -v unzip &>/dev/null; then
    unzip -q "$TEMP_ZIP" -d "$TEMP_EXTRACT"
  else
    error "unzip 不可用"
    exit 1
  fi

  # Find extracted directory (handles any branch name)
  EXTRACTED_DIR=$(find "$TEMP_EXTRACT" -maxdepth 1 -type d -name "vibeflow-*" | head -1)
  if [[ -z "$EXTRACTED_DIR" ]]; then
    error "解压失败，无法找到 vibeflow 目录"
    exit 1
  fi

  mv "$EXTRACTED_DIR" "$TARGET_DIR"
  rm -rf "$TEMP_ZIP" "$TEMP_EXTRACT"
  success "下载完成 (ZIP)"
fi

# 4. Verify
MARKETPLACE_JSON="${TARGET_DIR}/.claude-plugin/marketplace.json"
if [[ ! -f "$MARKETPLACE_JSON" ]]; then
  error "marketplace.json 未找到"
  exit 1
fi
SKILL_COUNT=$(find "${TARGET_DIR}/skills" -maxdepth 1 -type d | wc -l | xargs)
success "验证通过 (${SKILL_COUNT} skills)"

# 5. Register in known_marketplaces.json
info "注册 marketplace..."
mkdir -p "$CLAUDE_PLUGINS_DIR"

if [[ ! -f "$KNOWN_MARKETPLACES_FILE" ]]; then
  printf '{}\n' > "$KNOWN_MARKETPLACES_FILE"
fi

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")

# Use jq if available, otherwise use Python
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
  success "注册完成 (jq)"
elif command -v python3 &>/dev/null; then
  python3 - "$KNOWN_MARKETPLACES_FILE" "$MARKETPLACE_NAME" "$REPO_NAME" "$TARGET_DIR" "$TIMESTAMP" <<'PYEOF'
import json, sys
path = sys.argv[1]
name = sys.argv[2]
repo = sys.argv[3]
location = sys.argv[4]
timestamp = sys.argv[5]
with open(path) as f:
    data = json.load(f)
data[name] = {
    "source": {"source": "github", "repo": repo},
    "installLocation": location,
    "lastUpdated": timestamp
}
with open(path, 'w') as f:
    json.dump(data, f, indent=2)
PYEOF
  success "注册完成 (python3)"
elif command -v python &>/dev/null; then
  python - "$KNOWN_MARKETPLACES_FILE" "$MARKETPLACE_NAME" "$REPO_NAME" "$TARGET_DIR" "$TIMESTAMP" <<'PYEOF'
import json, sys
path = sys.argv[1]
name = sys.argv[2]
repo = sys.argv[3]
location = sys.argv[4]
timestamp = sys.argv[5]
with open(path) as f:
    data = json.load(f)
data[name] = {
    "source": {"source": "github", "repo": repo},
    "installLocation": location,
    "lastUpdated": timestamp
}
with open(path, 'w') as f:
    json.dump(data, f, indent=2)
PYEOF
  success "注册完成 (python)"
else
  error "jq 和 python 都未安装，无法注册 marketplace"
  error "请安装以下任一工具后重试："
  error "  macOS: brew install jq"
  error "  Linux: apt install jq 或 apt install python3"
  exit 1
fi

# Done
echo ""
echo -e "${GREEN}========================================${RESET}"
echo -e "${GREEN}  安装完成！${RESET}"
echo -e "${GREEN}========================================${RESET}"
echo ""
if [[ -f "${TARGET_DIR}/VERSION" ]]; then
  echo -e "已安装版本：$(<"${TARGET_DIR}/VERSION")"
fi
echo -e "下一步（在 Claude Code 中运行）："
echo -e "  ${CYAN}/plugin install vibeflow@vibeflow${RESET}"
echo ""
