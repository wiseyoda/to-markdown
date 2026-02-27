#!/usr/bin/env bash
# to-markdown installer for macOS
# Usage: ./install.sh
set -euo pipefail

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOTAL_STEPS=7
CURRENT_STEP=0

# --- Helpers ---
step() {
  CURRENT_STEP=$((CURRENT_STEP + 1))
  echo -e "\n${BLUE}[${CURRENT_STEP}/${TOTAL_STEPS}]${NC} ${BOLD}$1${NC}"
}

ok() { echo -e "  ${GREEN}OK${NC} $1"; }
warn() { echo -e "  ${YELLOW}WARNING${NC} $1"; }
fail() { echo -e "  ${RED}FAILED${NC} $1"; exit 1; }
info() { echo -e "  $1"; }

# --- Banner ---
echo -e "${BOLD}"
echo "  _____  ___        __  __    _    ____  _  ______  _____        ___   _ "
echo " |_   _|/ _ \      |  \/  |  / \  |  _ \| |/ /  _ \|  _  |      \ \ / / "
echo "   | | | | | |_____| |\/| | / _ \ | |_) | ' /| | | | | | |  _____\ V /  "
echo "   | | | |_| |_____| |  | |/ ___ \|  _ <| . \| |_| | |_| | |_____|> <   "
echo "   |_|  \___/      |_|  |_/_/   \_\_| \_\_|\_\____/|_____|      /_/ \_\  "
echo -e "${NC}"
echo -e "${BOLD}to-markdown installer for macOS${NC}"
echo ""

# --- Check OS ---
if [[ "$(uname -s)" != "Darwin" ]]; then
  fail "This script is for macOS only. Use install.ps1 for Windows."
fi

# --- Step 1: Check uv ---
step "Checking uv package manager"
if command -v uv &>/dev/null; then
  UV_VERSION=$(uv --version 2>/dev/null || echo "unknown")
  ok "uv found ($UV_VERSION)"
else
  info "uv not found. Installing..."
  if curl -LsSf https://astral.sh/uv/install.sh | sh 2>/dev/null; then
    # Source the env to pick up uv
    export PATH="$HOME/.local/bin:$PATH"
    if command -v uv &>/dev/null; then
      ok "uv installed successfully"
    else
      fail "uv installed but not found in PATH. Restart your terminal and re-run this script."
    fi
  else
    fail "Failed to install uv. Install manually: curl -LsSf https://astral.sh/uv/install.sh | sh"
  fi
fi

# --- Step 2: Check Python 3.14+ ---
step "Checking Python 3.14+"
PYTHON_OK=false
if uv python list --only-installed 2>/dev/null | grep -q "3\.1[4-9]\|3\.[2-9][0-9]"; then
  PY_VERSION=$(uv python list --only-installed 2>/dev/null | grep "3\.1[4-9]\|3\.[2-9][0-9]" | head -1 | awk '{print $1}')
  ok "Python $PY_VERSION found"
  PYTHON_OK=true
fi

if [ "$PYTHON_OK" = false ]; then
  info "Python 3.14+ not found. Installing via uv..."
  if uv python install 3.14 2>/dev/null; then
    ok "Python 3.14 installed"
  else
    warn "Python 3.14 not available. Trying 3.13..."
    if uv python install 3.13 2>/dev/null; then
      ok "Python 3.13 installed (3.14 unavailable)"
    else
      fail "Could not install Python. Run: uv python install 3.14 (or 3.13)"
    fi
  fi
fi

# --- Step 3: Check Tesseract (optional) ---
step "Checking Tesseract OCR (optional)"
if command -v tesseract &>/dev/null; then
  TESS_VERSION=$(tesseract --version 2>&1 | head -1)
  ok "Tesseract found ($TESS_VERSION)"
else
  info "Tesseract not found. It enables OCR for scanned PDFs and images."
  if command -v brew &>/dev/null; then
    echo -n "  Install Tesseract via Homebrew? [y/N] "
    read -r REPLY
    if [[ "$REPLY" =~ ^[Yy]$ ]]; then
      if brew install tesseract 2>/dev/null; then
        ok "Tesseract installed"
      else
        warn "Tesseract install failed. OCR features won't work. Install manually: brew install tesseract"
      fi
    else
      info "Skipped. OCR features won't work without Tesseract."
    fi
  else
    warn "Homebrew not found. Tesseract install skipped. Install Homebrew: https://brew.sh"
    info "Then run: brew install tesseract"
  fi
fi

# --- Step 4: Install dependencies ---
step "Installing dependencies"
cd "$SCRIPT_DIR"
if uv sync --all-extras 2>&1; then
  ok "All dependencies installed"
else
  fail "Dependency install failed. Try: uv sync --all-extras --verbose"
fi

# --- Step 5: Validate installation ---
step "Validating installation"
VERSION=$(uv run to-markdown --version 2>/dev/null || echo "")
if [ -n "$VERSION" ]; then
  ok "$VERSION"
else
  fail "Installation validation failed. Try: uv run to-markdown --version"
fi

# --- Step 6: Set up shell alias ---
step "Setting up shell alias"
ALIAS_LINE="alias to-markdown='uv run --directory ${SCRIPT_DIR} to-markdown'"
ALIAS_COMMENT="# Added by to-markdown installer"

# Detect shell config
if [ -n "${ZSH_VERSION:-}" ] || [ "$SHELL" = "/bin/zsh" ] || [ "$SHELL" = "/usr/bin/zsh" ]; then
  RC_FILE="$HOME/.zshrc"
elif [ -n "${BASH_VERSION:-}" ] || [ "$SHELL" = "/bin/bash" ] || [ "$SHELL" = "/usr/bin/bash" ]; then
  RC_FILE="$HOME/.bashrc"
else
  RC_FILE="$HOME/.zshrc"  # Default to zsh on modern macOS
fi

# Check if alias already exists
if grep -q "alias to-markdown=" "$RC_FILE" 2>/dev/null; then
  ok "Shell alias already configured in $RC_FILE"
else
  echo "" >> "$RC_FILE"
  echo "$ALIAS_COMMENT" >> "$RC_FILE"
  echo "$ALIAS_LINE" >> "$RC_FILE"
  ok "Added alias to $RC_FILE"
  info "Run: source $RC_FILE (or open a new terminal)"
fi

# --- Step 7: Success ---
step "Installation complete!"
echo ""
echo -e "${GREEN}${BOLD}to-markdown is ready to use!${NC}"
echo ""
echo "  Quick start:"
echo "    to-markdown yourfile.pdf          # Convert a file"
echo "    to-markdown docs/                 # Convert a directory"
echo "    to-markdown --setup               # Configure smart features (optional)"
echo ""
echo "  For detailed instructions, see: INSTALL.md"
echo ""
echo -e "  ${YELLOW}Note:${NC} Open a new terminal or run 'source $RC_FILE' to use the alias."
echo ""
