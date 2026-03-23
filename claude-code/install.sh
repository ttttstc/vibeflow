#!/usr/bin/env bash
# =============================================================================
# VibeFlow 一键安装脚本 - 在 Claude Code 内运行
# =============================================================================
#
# 使用方法：复制以下命令，粘贴到 Claude Code 对话框运行：
#
#   /sh curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/refs/heads/feat/plan-value-review/claude-code/install.sh | bash
#
# 或者一行：
#
#   /sh bash -c "$(curl -fsSL https://raw.githubusercontent.com/ttttstc/vibeflow/refs/heads/feat/plan-value-review/claude-code/install.sh)"
#
# 安装后运行：
#   /plugin install vibeflow@vibeflow
#
# =============================================================================

set -euo pipefail

MARKETPLACE_NAME="vibeflow"
BRANCH="feat/plan-value-review"
DOWNLOAD_URL="https://github.com/ttttstc/vibeflow/archive/refs/heads/${BRANCH}.zip"
GITHUB_RAW="https://raw.githubusercontent.com/ttttstc/vibeflow/refs/heads/${BRANCH}"

MARKETPLACE_GIT_URL="https://github.com/ttttstc/vibeflow.git"
REPO_NAME="ttttstc/vibeflow"

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

# Check git
if ! command -v git &>/dev/null; then
  error "git is required but not installed"
  exit 1
fi

info "开始安装 VibeFlow..."

# 1. Create directories
mkdir -p "$MARKETPLACES_DIR"
success "目录就绪"

# 2. Remove existing
if [[ -d "$TARGET_DIR" ]]; then
  info "移除旧版本..."
  rm -rf "$TARGET_DIR"
fi

# 3. Clone
info "下载中..."
git clone --depth 1 "$MARKETPLACE_GIT_URL" "$TARGET_DIR" 2>&1
if [[ ${PIPESTATUS[0]} -ne 0 ]]; then
  error "下载失败"
  exit 1
fi
success "下载完成"

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
echo -e "下一步（在 Claude Code 中运行）："
echo -e "  ${CYAN}/plugin install vibeflow@vibeflow${RESET}"
echo ""
