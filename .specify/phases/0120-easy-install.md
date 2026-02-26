---
phase: 0120
name: easy-install
status: not_started
created: 2026-02-26
updated: 2026-02-26
---

# Phase 0120: Easy Install for Non-Technical Users

**Goal**: Create a one-command install experience for non-technical users on both macOS
and Windows. Clone the repo, run one script, and everything works.

**Scope**:

### 1. macOS Install Script
- `install.sh`: Single bash script that handles everything
- Detects and installs uv (if missing) via official installer
- Detects and installs Python 3.14+ via uv
- Detects and installs Tesseract via Homebrew (for OCR support)
- Runs `uv sync --all-extras` to install all dependencies
- Creates a shell alias or symlink so `to-markdown` works globally
- Validates the installation by running `to-markdown --version`
- Colorful, friendly output with progress indicators
- Handles errors gracefully with clear remediation steps

### 2. Windows Install Script
- `install.ps1`: PowerShell script for Windows
- Detects and installs uv (if missing) via official installer
- Detects and installs Python 3.14+ via uv
- Detects and installs Tesseract via winget or choco (for OCR support)
- Runs `uv sync --all-extras`
- Adds to-markdown to PATH or creates a batch wrapper
- Validates the installation
- Clear output with progress indicators

### 3. Configuration Wizard
- Interactive first-run setup (triggered on first use or via `to-markdown --setup`)
- Prompts for GEMINI_API_KEY (optional, with explanation of what it enables)
- Creates .env file in project directory
- Tests API key if provided
- Explains core vs smart features

### 4. Quick Start Guide
- `INSTALL.md`: Step-by-step guide with screenshots/terminal output examples
- macOS section and Windows section
- Troubleshooting FAQ (common errors and fixes)
- "What to do next" section with example commands
- Written for non-technical audience (no assumed knowledge of terminals)

### 5. Uninstall
- `uninstall.sh` / `uninstall.ps1`: Clean removal scripts
- Removes symlinks/aliases, virtual environment, and config files
- Preserves any converted .md files

### 6. Tests
- Test install script logic (dependency detection, error handling) via unit tests
- Test configuration wizard flow with mocked inputs
- Test that --setup flag triggers wizard
- Manual testing checklist for both platforms

**Deliverables**:
- [ ] install.sh for macOS (one-command install)
- [ ] install.ps1 for Windows (one-command install)
- [ ] Configuration wizard (--setup flag)
- [ ] INSTALL.md with step-by-step guide for both platforms
- [ ] uninstall.sh / uninstall.ps1
- [ ] Tests for install logic and config wizard
- [ ] README updated to reference INSTALL.md for non-technical users

**Verification Gate**: **USER GATE** - Fresh macOS machine: clone repo, run
`./install.sh`, run `to-markdown test.pdf`. Fresh Windows machine: clone repo, run
`./install.ps1`, run `to-markdown test.pdf`. Both work without manual intervention.

**Estimated Complexity**: Medium
