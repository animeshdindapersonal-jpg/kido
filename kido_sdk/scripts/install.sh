#!/usr/bin/env bash
#
# KIDO Bootstrap Installer for Linux/macOS
#
# One-liner:
#   curl -fsSL https://kido.dev/install.sh | sh
#
set -euo pipefail

GITHUB_REPO="animeshdindapersonal-jpg/kido"
API_BASE="https://api.github.com/repos/${GITHUB_REPO}"
RELEASE_URL="${API_BASE}/releases/latest"
KIDO_HOME="${HOME}/.kido"
SDK_DIR="${KIDO_HOME}/sdk"
BIN_DIR="${KIDO_HOME}/bin"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

log()  { printf "${GREEN}%s${NC}\n" "$1"; }
warn() { printf "${YELLOW}%s${NC}\n" "$1"; }
err()  { printf "${RED}%s${NC}\n" "$1"; }
header() { printf "${CYAN}%s${NC}\n" "$1"; }

header "============================================================"
header "  🧒  KIDO Programming Language — Bootstrap Installer"
header "============================================================"
echo ""

# -----------------------------------------------------------
# Phase 1 — Ensure Python 3.8+
# -----------------------------------------------------------
ensure_python() {
    local python_cmd=""

    # Try python3, python, python3.11, python3.10, python3.9
    for cmd in python3 python python3.11 python3.10 python3.9; do
        if command -v "$cmd" &>/dev/null; then
            local ver
            ver=$("$cmd" --version 2>&1 | grep -oP 'Python \K\d+\.\d+') || true
            local major="${ver%.*}"
            local minor="${ver#*.}"
            if [ "$major" -ge 3 ] && [ "$minor" -ge 8 ] 2>/dev/null; then
                python_cmd="$cmd"
                break
            fi
        fi
    done

    if [ -n "$python_cmd" ]; then
        log "✅  Python found: $(command -v "$python_cmd")"
        echo "$python_cmd"
        return 0
    fi

    # Python not found — try to install it
    warn "📥  Python 3.8+ not found. Attempting to install..."

    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &>/dev/null; then
            brew install python@3.11 >/dev/null 2>&1 || true
        else
            err "❌  Homebrew not found. Please install Python 3.8+ from python.org"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &>/dev/null; then
            sudo apt-get update -qq >/dev/null 2>&1
            sudo apt-get install -y -qq python3 python3-pip >/dev/null 2>&1
        elif command -v dnf &>/dev/null; then
            sudo dnf install -y python3 python3-pip >/dev/null 2>&1
        elif command -v yum &>/dev/null; then
            sudo yum install -y python3 python3-pip >/dev/null 2>&1
        elif command -v pacman &>/dev/null; then
            sudo pacman -S --noconfirm python python-pip >/dev/null 2>&1
        else
            err "❌  No package manager found. Please install Python 3.8+ manually."
            exit 1
        fi
    else
        err "❌  Unsupported OS. Please install Python 3.8+ manually."
        exit 1
    fi

    # Verify installation
    for cmd in python3 python; do
        if command -v "$cmd" &>/dev/null; then
            python_cmd="$cmd"
            break
        fi
    done

    if [ -z "$python_cmd" ]; then
        err "❌  Python installation failed. Please install manually."
        exit 1
    fi

    log "✅  Python installed: $(command -v "$python_cmd")"
    echo "$python_cmd"
}

# -----------------------------------------------------------
# Phase 2 — Download KIDO SDK
# -----------------------------------------------------------
get_kido_sdk() {
    warn "📥  Fetching latest KIDO SDK release..."

    if ! command -v curl &>/dev/null; then
        err "❌  curl is required. Please install it."
        exit 1
    fi

    local release_json
    release_json=$(curl -sL "$RELEASE_URL") || {
        err "❌  Failed to fetch release info from GitHub."
        exit 1
    }

    local asset_url version
    if [[ "$OSTYPE" == "darwin"* ]]; then
        asset_url=$(echo "$release_json" | grep -oP '"browser_download_url":\s*"\K[^"]*kido-sdk-macos[^"]*' | head -1) || true
    else
        asset_url=$(echo "$release_json" | grep -oP '"browser_download_url":\s*"\K[^"]*kido-sdk-linux[^"]*' | head -1) || true
    fi
    version=$(echo "$release_json" | grep -oP '"tag_name":\s*"\K[^"]+' | head -1) || version="latest"

    if [ -z "$asset_url" ]; then
        err "❌  No matching SDK asset found in latest release."
        exit 1
    fi

    mkdir -p "$SDK_DIR"
    local sdk_tgz="/tmp/kido-sdk.tar.gz"
    curl -sL "$asset_url" -o "$sdk_tgz" || {
        err "❌  Failed to download SDK."
        exit 1
    }

    tar -xzf "$sdk_tgz" -C "$SDK_DIR" 2>/dev/null || {
        # If tar fails, try unzip
        unzip -o "$sdk_tgz" -d "$SDK_DIR" 2>/dev/null || true
    }
    rm -f "$sdk_tgz"

    log "✅  KIDO SDK ${version} downloaded"
    echo "$version"
}

# -----------------------------------------------------------
# Phase 3 — Bootstrap
# -----------------------------------------------------------
bootstrap() {
    local python_cmd="$1"
    local sdk_dir="$2"

    warn "📦  Setting up KIDO environment..."

    cd "$sdk_dir"

    # Create venv if it doesn't exist
    if [ ! -d ".kido-venv" ]; then
        "$python_cmd" -m venv .kido-venv 2>/dev/null || {
            # Fallback: pip install --user
            warn "  ⚠️   venv not available, using --user install"
            pip3 install -r requirements.txt 2>/dev/null || true
            return 0
        }
    fi

    # Activate venv and install deps
    if [ -f ".kido-venv/bin/python" ]; then
        .kido-venv/bin/python -m pip install -r requirements.txt --quiet 2>/dev/null || true
        .kido-venv/bin/python -m pip install -e . --quiet 2>/dev/null || true
    fi

    log "✅  Environment ready"
}

# -----------------------------------------------------------
# Phase 4 — Self-Test
# -----------------------------------------------------------
self_test() {
    local python_cmd="$1"
    local sdk_dir="$2"

    warn "🧪  Running self-test..."

    cd "$sdk_dir"

    # Determine the python to use (venv or system)
    local py="$python_cmd"
    if [ -f ".kido-venv/bin/python" ]; then
        py=".kido-venv/bin/python"
    fi

    # Smoke test
    if [ -f "examples/hello.kd" ]; then
        local out
        out=$("$py" -m kido_cli.cli run "examples/hello.kd" 2>&1 || true)
        if echo "$out" | grep -q "Hello"; then
            log "  ✅  Smoke test passed"
        else
            warn "  ⚠️   Smoke test: unexpected output"
        fi
    fi

    # Parse check on all examples
    local total=0 passed=0
    while IFS= read -r -d '' f; do
        total=$((total + 1))
        local out
        out=$("$py" -m kido_cli.cli check "$f" 2>&1 || true)
        if echo "$out" | grep -q "No problems"; then
            passed=$((passed + 1))
        fi
    done < <(find "examples" -name "*.kd" -print0 2>/dev/null)

    if [ "$total" -gt 0 ]; then
        log "  ✅  Parse check: ${passed}/${total} passed"
    fi

    # CLI check
    local v
    v=$("$py" -m kido_cli.cli version 2>&1 || true)
    if echo "$v" | grep -q "KIDO"; then
        log "  ✅  CLI version check passed"
    fi
}

# -----------------------------------------------------------
# Phase 5 — Add to PATH
# -----------------------------------------------------------
add_to_path() {
    local python_cmd="$1"
    local sdk_dir="$2"

    warn "🔧  Adding KIDO to PATH..."

    mkdir -p "$BIN_DIR"

    # Create launcher script
    cat > "$BIN_DIR/kido" << LAUNCHER
#!/usr/bin/env bash
cd "${sdk_dir}"
exec "${python_cmd}" -m kido_cli.cli "\$@"
LAUNCHER
    chmod +x "$BIN_DIR/kido"

    # Detect shell rc file
    local rc_file=""
    if [ -n "$ZSH_VERSION" ] || [ -f "$HOME/.zshrc" ]; then
        rc_file="$HOME/.zshrc"
    elif [ -n "$BASH_VERSION" ] || [ -f "$HOME/.bashrc" ]; then
        rc_file="$HOME/.bashrc"
    elif [ -f "$HOME/.bash_profile" ]; then
        rc_file="$HOME/.bash_profile"
    elif [ -f "$HOME/.profile" ]; then
        rc_file="$HOME/.profile"
    fi

    if [ -n "$rc_file" ]; then
        if ! grep -q "KIDO" "$rc_file" 2>/dev/null; then
            {
                echo ""
                echo "# KIDO Programming Language"
                echo "export PATH=\"\$PATH:${BIN_DIR}\""
            } >> "$rc_file"
            log "  ✅  Added to PATH in ${rc_file}"
            warn "  ⚠️   Run: source ${rc_file}  (or restart terminal)"
        else
            log "  ✅  Already in PATH"
        fi
    fi

    # Add to current session
    export PATH="${PATH}:${BIN_DIR}"
}

# -----------------------------------------------------------
# Report
# -----------------------------------------------------------
show_report() {
    local version="$1"

    echo ""
    header "╔═══════════════════════════════════════════════════════════╗"
    header "║       🧒  KIDO Bootstrap Complete!                        ║"
    header "╠═══════════════════════════════════════════════════════════╣"
    printf "${CYAN}║  ${NC}%-55s ${CYAN}║${NC}\n" "KIDO Home : ${KIDO_HOME}"
    printf "${CYAN}║  ${NC}%-55s ${CYAN}║${NC}\n" "Version   : ${version}"
    printf "${CYAN}║  ${NC}%-55s ${CYAN}║${NC}\n" "SDK       : ${SDK_DIR}"
    printf "${CYAN}║  ${NC}%-55s ${CYAN}║${NC}\n" "Python    : $(command -v "$PYTHON_CMD")"
    header "╠═══════════════════════════════════════════════════════════╣"
    printf "${CYAN}║  ${NC}%-55s ${CYAN}║${NC}\n" "Try:  kido run examples/hello.kd"
    printf "${CYAN}║  ${NC}%-55s ${CYAN}║${NC}\n" "Or:   kido shell"
    printf "${CYAN}║  ${NC}%-55s ${CYAN}║${NC}\n" "Help: kido help"
    header "╚═══════════════════════════════════════════════════════════╝"
    echo ""
}

# ===========================================================
# MAIN
# ===========================================================
PYTHON_CMD=$(ensure_python)
VERSION=$(get_kido_sdk)
bootstrap "$PYTHON_CMD" "$SDK_DIR"
self_test "$PYTHON_CMD" "$SDK_DIR"
add_to_path "$PYTHON_CMD" "$SDK_DIR"
show_report "$VERSION"
