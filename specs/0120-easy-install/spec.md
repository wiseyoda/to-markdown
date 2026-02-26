# Specification: Easy Install

**Phase**: `0120-easy-install`
**Created**: 2026-02-26

---

## Overview

Create a one-command install experience for non-technical users on both macOS and Windows.
Clone the repo, run one script, and `to-markdown` works globally.

## User Stories

### US1: macOS First-Time Install
**As a** non-technical macOS user,
**I want to** clone the repo and run one script,
**So that** `to-markdown` works from any directory without understanding Python/uv.

**Acceptance Criteria**:
- `./install.sh` detects and installs uv if missing
- `./install.sh` installs Python 3.14+ via uv if missing
- `./install.sh` offers Tesseract install via Homebrew (optional, non-blocking)
- `./install.sh` runs `uv sync --all-extras`
- `./install.sh` adds shell alias so `to-markdown` works globally
- `./install.sh` validates installation with `to-markdown --version`
- Script shows colorful progress with clear success/failure messages
- Script handles errors gracefully with remediation steps

### US2: Windows First-Time Install
**As a** non-technical Windows user,
**I want to** clone the repo and run one script,
**So that** `to-markdown` works from any directory.

**Acceptance Criteria**:
- `./install.ps1` detects and installs uv if missing
- `./install.ps1` installs Python 3.14+ via uv if missing
- `./install.ps1` offers Tesseract install via winget (optional, non-blocking)
- `./install.ps1` runs `uv sync --all-extras`
- `./install.ps1` adds shell alias or batch wrapper for global access
- `./install.ps1` validates installation
- Script shows clear progress with success/failure messages
- Script handles errors gracefully with remediation steps

### US3: Configuration Wizard
**As a** user who wants smart features,
**I want to** run `to-markdown --setup` and be guided through configuration,
**So that** I can set up my API key without editing files manually.

**Acceptance Criteria**:
- `--setup` flag triggers interactive configuration wizard
- Wizard explains what smart features are (--clean, --summary, --images)
- Wizard prompts for GEMINI_API_KEY (optional, can skip)
- Wizard writes .env file in project directory
- Wizard validates API key if provided (test call to Gemini)
- Wizard shows what was configured and next steps
- Works with --quiet flag (non-interactive, just validates existing config)

### US4: Installation Guide
**As a** non-technical user,
**I want** step-by-step instructions with examples,
**So that** I can install and use to-markdown even if something goes wrong.

**Acceptance Criteria**:
- INSTALL.md with macOS and Windows sections
- Terminal output examples showing expected output at each step
- Troubleshooting FAQ covering common errors
- "What to do next" section with example commands
- Written for non-technical audience (no assumed terminal knowledge)

### US5: Clean Uninstall
**As a** user who wants to remove to-markdown,
**I want to** run one script to cleanly uninstall,
**So that** nothing is left behind (except my converted files).

**Acceptance Criteria**:
- `uninstall.sh` / `uninstall.ps1` remove shell alias
- Scripts remove .venv directory
- Scripts remove ~/.to-markdown/ data directory
- Scripts preserve any .md files the user created
- Scripts confirm before removing (with --yes flag to skip)

---

## Functional Requirements

### FR-001: macOS Install Script
The `install.sh` script MUST handle the complete macOS installation flow:
dependency detection, installation, project setup, global alias, and validation.

### FR-002: Windows Install Script
The `install.ps1` script MUST handle the complete Windows installation flow:
dependency detection, installation, project setup, global access, and validation.

### FR-003: Configuration Wizard
The `--setup` CLI flag MUST trigger an interactive wizard that configures
GEMINI_API_KEY in a .env file with validation and clear explanations.

### FR-004: Installation Documentation
INSTALL.md MUST provide platform-specific step-by-step instructions with
terminal examples and troubleshooting for non-technical users.

### FR-005: Uninstall Scripts
`uninstall.sh` and `uninstall.ps1` MUST cleanly remove all to-markdown artifacts
while preserving user-created .md files.

### FR-006: README Update
README.md MUST reference INSTALL.md for non-technical users and include a
quick-start section.

## Non-Functional Requirements

### NFR-001: No Python Dependency for Install Scripts
Install scripts (bash/PowerShell) MUST NOT require Python to run - they install it.

### NFR-002: Idempotent Installation
Running install scripts multiple times MUST be safe and produce the same result.

### NFR-003: Graceful Degradation
Tesseract unavailability MUST NOT block installation. Smart features unavailability
(no API key) MUST NOT block core usage.

### NFR-004: Error Messages
All error conditions MUST produce clear, actionable messages explaining what went
wrong and how to fix it.

## Success Criteria

### SC-001: Fresh macOS Install
Clone repo on fresh macOS, run `./install.sh`, run `to-markdown test.pdf` - works.

### SC-002: Fresh Windows Install
Clone repo on fresh Windows, run `./install.ps1`, run `to-markdown test.pdf` - works.

### SC-003: Setup Wizard
Run `to-markdown --setup`, enter API key, run `to-markdown file.pdf --summary` - works.

## Wiring Requirements

### WR-001: --setup flag wired in cli.py
The `--setup` flag MUST be registered in `cli.py` and delegate to `core/setup.py`.

### WR-002: Setup constants in constants.py
All setup-related constants MUST be defined in `core/constants.py`.
