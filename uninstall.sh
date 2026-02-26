#!/usr/bin/env bash
# to-markdown uninstaller for macOS
# Usage: ./uninstall.sh [--yes]
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BOLD='\033[1m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTO_YES=false

# Parse arguments
for arg in "$@"; do
  case "$arg" in
    --yes|-y) AUTO_YES=true ;;
  esac
done

echo -e "${BOLD}to-markdown uninstaller${NC}\n"

confirm() {
  if [ "$AUTO_YES" = true ]; then
    return 0
  fi
  echo -n "$1 [y/N] "
  read -r REPLY
  [[ "$REPLY" =~ ^[Yy]$ ]]
}

# --- Remove shell alias ---
echo -e "${YELLOW}1.${NC} Shell alias"
for rc_file in "$HOME/.zshrc" "$HOME/.bashrc"; do
  if [ -f "$rc_file" ] && grep -q "alias to-markdown=" "$rc_file"; then
    if confirm "  Remove to-markdown alias from $rc_file?"; then
      # Remove the alias line and the comment above it
      sed -i '' '/# Added by to-markdown installer/d' "$rc_file"
      sed -i '' '/alias to-markdown=/d' "$rc_file"
      echo -e "  ${GREEN}Removed alias from $rc_file${NC}"
    else
      echo "  Skipped"
    fi
  fi
done

# --- Remove virtual environment ---
echo -e "${YELLOW}2.${NC} Virtual environment"
VENV_DIR="$SCRIPT_DIR/.venv"
if [ -d "$VENV_DIR" ]; then
  if confirm "  Remove virtual environment ($VENV_DIR)?"; then
    rm -rf "$VENV_DIR"
    echo -e "  ${GREEN}Removed .venv${NC}"
  else
    echo "  Skipped"
  fi
else
  echo "  No .venv found"
fi

# --- Remove data directory ---
echo -e "${YELLOW}3.${NC} Data directory"
DATA_DIR="$HOME/.to-markdown"
if [ -d "$DATA_DIR" ]; then
  if confirm "  Remove data directory ($DATA_DIR)?"; then
    rm -rf "$DATA_DIR"
    echo -e "  ${GREEN}Removed $DATA_DIR${NC}"
  else
    echo "  Skipped"
  fi
else
  echo "  No data directory found"
fi

# --- Remove .env file ---
echo -e "${YELLOW}4.${NC} Configuration"
ENV_FILE="$SCRIPT_DIR/.env"
if [ -f "$ENV_FILE" ]; then
  if confirm "  Remove configuration file ($ENV_FILE)?"; then
    rm "$ENV_FILE"
    echo -e "  ${GREEN}Removed .env${NC}"
  else
    echo "  Skipped"
  fi
else
  echo "  No .env file found"
fi

echo ""
echo -e "${GREEN}${BOLD}Uninstall complete.${NC}"
echo "  Converted .md files have been preserved."
echo "  To fully remove, delete the project directory: rm -rf $SCRIPT_DIR"
