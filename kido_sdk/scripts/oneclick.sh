#!/usr/bin/env bash
#
# KIDO One-Click Bootstrap (Linux/macOS)
# User runs ONE command — does everything.
#
# Usage:
#   chmod +x kido-install.sh && ./kido-install.sh
#   OR just:  bash kido-install.sh
#
set -euo pipefail

GITHUB_REPO="animeshdindapersonal-jpg/kido"
API_BASE="https://api.github.com/repos/${GITHUB_REPO}"
KIDO_HOME="${HOME}/.kido"
SDK_DIR="${KIDO_HOME}/sdk"
BIN_DIR="${KIDO_HOME}/bin"

RED='\033[0;31m'; GREEN='\033[0;32m'
YELLOW='\033[1;33m'; CYAN='\033[0;36m'
NC='\033[0m'
log()  { printf "${GREEN}%s${NC}\n" "$1"; }
warn() { printf "${YELLOW}%s${NC}\n" "$1"; }
err()  { printf "${RED}%s${NC}\n" "$1"; }
header() { printf "${CYAN}%s${NC}\n" "$1"; }

header "============================================================"
header "  🧒  KIDO Programming Language — One-Click Setup"
header "============================================================"
header "  This will install KIDO on your system."
header "  Internet connection required."
header "============================================================"
echo ""

# -----------------------------------------------------------
# Phase 1 — Ensure Python 3.8+
# -----------------------------------------------------------
echo "[1/5] Checking Python..."
PYTHON_CMD=""
for cmd in python3 python python3.11 python3.10 python3.9; do
    if command -v "$cmd" &>/dev/null; then
        ver=$("$cmd" --version 2>&1 | grep -oP 'Python \K\d+\.\d+') || true
        major="${ver%.*}"; minor="${ver#*.}"
        if [ "$major" -ge 3 ] && [ "$minor" -ge 8 ] 2>/dev/null; then
            PYTHON_CMD="$cmd"
            break
        fi
    fi
done

if [ -n "$PYTHON_CMD" ]; then
    log "  [OK] Python found: $(command -v "$PYTHON_CMD")"
else
    warn "  [..] Python 3.8+ not found. Attempting to install..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &>/dev/null; then
            brew install python@3.11 >/dev/null 2>&1 || true
        else
            err "  [ERROR] Install Python from python.org first, then re-run this script."
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &>/dev/null; then
            sudo apt-get update -qq >/dev/null 2>&1
            sudo apt-get install -y -qq python3 python3-pip >/dev/null 2>&1
        elif command -v dnf &>/dev/null; then
            sudo dnf install -y python3 python3-pip >/dev/null 2>&1
        elif command -v pacman &>/dev/null; then
            sudo pacman -S --noconfirm python python-pip >/dev/null 2>&1
        else
            err "  [ERROR] No package manager found. Install Python 3.8+ manually."
            exit 1
        fi
    else
        err "  [ERROR] Unsupported OS. Install Python 3.8+ manually."
        exit 1
    fi
    PYTHON_CMD=$(command -v python3 || command -v python)
    log "  [OK] Python installed: ${PYTHON_CMD}"
fi

# -----------------------------------------------------------
# Phase 2 — Download KIDO SDK
# -----------------------------------------------------------
echo "[2/5] Downloading KIDO SDK..."

if ! command -v curl &>/dev/null; then
    err "  [ERROR] curl is required. Please install it."
    exit 1
fi

release_json=$(curl -sL "$API_BASE/releases/latest") || {
    err "  [ERROR] Failed to fetch release info from GitHub."
    exit 1
}

# Determine platform-specific asset
if [[ "$OSTYPE" == "darwin"* ]]; then
    asset_url=$(echo "$release_json" | grep -oP '"browser_download_url":\s*"\K[^"]*kido-sdk-macos[^"]*' | head -1) || true
else
    asset_url=$(echo "$release_json" | grep -oP '"browser_download_url":\s*"\K[^"]*kido-sdk-linux[^"]*' | head -1) || true
fi
version=$(echo "$release_json" | grep -oP '"tag_name":\s*"\K[^"]+' | head -1) || version="latest"

if [ -z "$asset_url" ]; then
    err "  [ERROR] No SDK asset found in latest release."
    exit 1
fi

mkdir -p "$SDK_DIR"
sdk_tgz="/tmp/kido-sdk.tar.gz"
curl -sL "$asset_url" -o "$sdk_tgz" || {
    err "  [ERROR] Failed to download SDK."
    exit 1
}

# Extract (try tar.gz first, fallback to zip)
if tar -xzf "$sdk_tgz" -C "$SDK_DIR" 2>/dev/null; then
    # Move contents from subdirectory up
    subdir=$(ls "$SDK_DIR" 2>/dev/null | head -1)
    if [ -n "$subdir" ] && [ -d "$SDK_DIR/$subdir" ]; then
        shopt -s dotglob
        mv "$SDK_DIR/$subdir"/* "$SDK_DIR/" 2>/dev/null || true
        rmdir "$SDK_DIR/$subdir" 2>/dev/null || true
        shopt -u dotglob
    fi
else
    unzip -o "$sdk_tgz" -d "$SDK_DIR" >/dev/null 2>&1 || true
fi
rm -f "$sdk_tgz"

log "  [OK] KIDO SDK ${version} downloaded"

# -----------------------------------------------------------
# Phase 3 — Install Dependencies
# -----------------------------------------------------------
echo "[3/5] Installing dependencies..."

cd "$SDK_DIR"
if [ -f "requirements.txt" ]; then
    # Try venv first
    if ! command -v "$PYTHON_CMD" -m venv &>/dev/null; then
        "$PYTHON_CMD" -m pip install -r requirements.txt --quiet 2>/dev/null || true
    else
        if [ ! -d ".kido-venv" ]; then
            "$PYTHON_CMD" -m venv .kido-venv
        fi
        .kido-venv/bin/python -m pip install -r requirements.txt --quiet 2>/dev/null || true
        .kido-venv/bin/python -m pip install -e . --quiet 2>/dev/null || true
    fi
fi
log "  [OK] Dependencies installed"

# -----------------------------------------------------------
# Phase 4 — Self-Test
# -----------------------------------------------------------
echo "[4/5] Running self-test..."

# Use venv python if available, else system python
if [ -f ".kido-venv/bin/python" ]; then
    PY="${SDK_DIR}/.kido-venv/bin/python"
else
    PY="$PYTHON_CMD"
fi

# Smoke test
if [ -f "examples/hello.kd" ]; then
    out=$("$PY" -m kido_cli.cli run "examples/hello.kd" 2>&1 || true)
    if echo "$out" | grep -q "Hello"; then
        log "  [OK] Smoke test passed"
    else
        warn "  [--] Smoke test: unexpected output"
    fi
fi

# Parse check
total=0; passed=0
while IFS= read -r -d '' f; do
    total=$((total + 1))
    out=$("$PY" -m kido_cli.cli check "$f" 2>&1 || true)
    echo "$out" | grep -q "No problems" && passed=$((passed + 1))
done < <(find "examples" -name "*.kd" -print0 2>/dev/null)
[ "$total" -gt 0 ] && log "  [OK] Parse check: ${passed}/${total} passed"

# CLI check
ver_out=$("$PY" -m kido_cli.cli version 2>&1 || true)
echo "$ver_out" | grep -q "KIDO" && log "  [OK] CLI version check passed"

# -----------------------------------------------------------
# Phase 5 — Add to PATH + Create Launcher
# -----------------------------------------------------------
echo "[5/5] Setting up KIDO launcher..."

mkdir -p "$BIN_DIR"

cat > "$BIN_DIR/kido" << LAUNCHER
#!/usr/bin/env bash
SDK_DIR="${SDK_DIR}"
if [ -f "\${SDK_DIR}/.kido-venv/bin/python" ]; then
    exec "\${SDK_DIR}/.kido-venv/bin/python" -m kido_cli.cli "\$@"
else
    exec "$PYTHON_CMD" -m kido_cli.cli "\$@"
fi
LAUNCHER
chmod +x "$BIN_DIR/kido"

# Detect shell rc
rc_file=""
[ -n "$ZSH_VERSION" ] || [ -f "$HOME/.zshrc" ] && rc_file="$HOME/.zshrc"
[ -z "$rc_file" ] && { [ -n "$BASH_VERSION" ] || [ -f "$HOME/.bashrc" ]; } && rc_file="$HOME/.bashrc"
[ -z "$rc_file" ] && [ -f "$HOME/.bash_profile" ] && rc_file="$HOME/.bash_profile"
[ -z "$rc_file" ] && [ -f "$HOME/.profile" ] && rc_file="$HOME/.profile"

if [ -n "$rc_file" ]; then
    if ! grep -q "KIDO" "$rc_file" 2>/dev/null; then
        { echo ""; echo "# KIDO Programming Language"; echo "export PATH=\"\$PATH:${BIN_DIR}\""; } >> "$rc_file"
        log "  [OK] Added to PATH in ${rc_file}"
        warn "  [!!] Run: source ${rc_file}  (or restart terminal)"
    else
        log "  [OK] Already in PATH"
    fi
fi

export PATH="${PATH}:${BIN_DIR}"

# -----------------------------------------------------------
# Report
# -----------------------------------------------------------
echo ""
header "============================================================"
header "     🧒  KIDO Bootstrap Complete!"
header "============================================================"
echo "  Version   : ${version}"
echo "  Install   : ${KIDO_HOME}"
echo "  Python    : ${PYTHON_CMD}"
echo "  SDK       : ${SDK_DIR}"
header "============================================================"
echo "  Try:  kido run examples/hello.kd"
echo "  Or:   kido shell"
echo "  Help: kido help"
header "============================================================"
echo ""
