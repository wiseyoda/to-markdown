# Technical Plan: Easy Install

**Phase**: `0120-easy-install`
**Created**: 2026-02-26

---

## Architecture Overview

This phase creates files at three levels:

1. **Root-level scripts** (bash/PowerShell): `install.sh`, `install.ps1`, `uninstall.sh`,
   `uninstall.ps1` - standalone, no Python dependency
2. **Python module**: `src/to_markdown/core/setup.py` - configuration wizard triggered by
   `--setup` CLI flag
3. **Documentation**: `INSTALL.md` at project root

## Technical Decisions

### Install Script Architecture (D-73)
Install scripts are pure bash (macOS) and PowerShell (Windows). They cannot depend on
Python because their job is to install Python.

### Shell Alias Strategy (D-71)
Scripts add a shell alias to the user's RC file:
```bash
# Added to ~/.zshrc or ~/.bashrc
alias to-markdown='uv run --directory /path/to/to-markdown to-markdown'
```
This approach:
- Works without PATH modifications
- Leverages uv's venv management
- Handles the `--directory` flag so the tool works from any CWD

### Configuration Wizard (D-74)
`core/setup.py` is a Python module that runs after installation. It uses Typer prompts
(via `typer.prompt()` and `typer.confirm()`) for interactive configuration. Rich is used
for formatted output.

### .env Location (D-72)
The wizard writes `.env` in the project directory (alongside pyproject.toml). python-dotenv
already loads from there.

## File Structure

### New Files

| File | Type | Purpose |
|------|------|---------|
| `install.sh` | Bash script | macOS one-command installer |
| `install.ps1` | PowerShell script | Windows one-command installer |
| `uninstall.sh` | Bash script | macOS clean removal |
| `uninstall.ps1` | PowerShell script | Windows clean removal |
| `src/to_markdown/core/setup.py` | Python module | Configuration wizard |
| `INSTALL.md` | Markdown | Step-by-step guide for non-technical users |

### Modified Files

| File | Change |
|------|--------|
| `src/to_markdown/cli.py` | Add `--setup` flag, delegate to `core/setup.py` |
| `src/to_markdown/core/constants.py` | Add setup-related constants |
| `README.md` | Add quick-start section, reference INSTALL.md |
| `tests/test_cli.py` | Add --setup flag tests |
| `tests/test_setup.py` (new) | Configuration wizard unit tests |

## Integration Architecture

### Module Registration

| New Module | Caller | Registration Point |
|------------|--------|--------------------|
| `core/setup.py` | `cli.py` | Lazy import inside `--setup` handler |

### Entry Points (unchanged)

- `to-markdown` → `to_markdown.cli:app`
- `to-markdown-mcp` → `to_markdown.mcp.server:run_server`

## install.sh Flow

```
1. Print banner ("to-markdown installer")
2. Detect OS (must be macOS)
3. Check uv:
   - If found: print version, skip
   - If missing: install via `curl -LsSf https://astral.sh/uv/install.sh | sh`
4. Check Python 3.14+:
   - If found via uv: print version, skip
   - If missing: `uv python install 3.14`
5. Offer Tesseract (optional):
   - If found: print version, skip
   - If missing: ask user, install via `brew install tesseract`
   - If declined or brew missing: print "OCR features won't work" and continue
6. Run `uv sync --all-extras`
7. Validate: `uv run to-markdown --version`
8. Add shell alias to RC file:
   - Detect shell (zsh/bash)
   - Append alias if not already present
   - Source the RC file
9. Print success message with next steps
```

## install.ps1 Flow

```
1. Print banner
2. Check uv:
   - If found: print version, skip
   - If missing: install via `irm https://astral.sh/uv/install.ps1 | iex`
3. Check Python 3.14+:
   - If found via uv: print version, skip
   - If missing: `uv python install 3.14`
4. Offer Tesseract (optional):
   - If found: print version, skip
   - If missing: ask user, install via `winget install UB-Mannheim.TesseractOCR`
   - If declined or winget missing: continue with message
5. Run `uv sync --all-extras`
6. Validate: `uv run to-markdown --version`
7. Add alias/function to PowerShell profile OR create batch wrapper
8. Print success message
```

## Configuration Wizard Flow (core/setup.py)

```
1. Print welcome banner
2. Detect existing .env file
3. Explain smart features (--clean, --summary, --images)
4. Prompt for GEMINI_API_KEY:
   - Skip if already set in .env or environment
   - Show link to get API key
   - Accept key or allow skip
5. If key provided:
   - Validate by making test API call
   - Write to .env file
6. Show summary of configuration
7. Print next steps / example commands
```

## Constants (additions to constants.py)

```python
# --- Setup / Install ---
SETUP_ENV_FILE = ".env"
SETUP_GEMINI_KEY_URL = "https://aistudio.google.com/apikey"
SETUP_VALIDATION_PROMPT = "Say 'ok' in one word."
SETUP_VALIDATION_MAX_TOKENS = 10
SHELL_ALIAS_COMMENT = "# Added by to-markdown installer"
```

## Testing Strategy

### Unit Tests (test_setup.py)
- Test wizard detects existing .env
- Test wizard writes .env correctly
- Test wizard validates API key (mock Gemini call)
- Test wizard handles skip gracefully
- Test wizard handles invalid key

### CLI Tests (test_cli.py additions)
- Test --setup flag triggers wizard
- Test --setup with --quiet skips interactive prompts

### Install Script Tests
Install scripts are bash/PowerShell - not unit-testable in pytest.
Instead: manual testing checklist in smoke-test.md.

## --quiet Mode Behavior

When `--setup --quiet` is used:
- Skip all interactive prompts
- If .env exists with GEMINI_API_KEY: validate key via test API call, report result
- If .env missing or key not set: print "API key not configured. Smart features disabled."
- Always exit with success (non-blocking)

## Error Remediation Matrix

| Error | Remediation Message |
|-------|---------------------|
| uv not found (install fails) | "Install uv manually: curl -LsSf https://astral.sh/uv/install.sh \| sh" |
| Python 3.14+ not available | "Run: uv python install 3.14 (or 3.13 if 3.14 unavailable)" |
| Homebrew not found (macOS) | "Tesseract install skipped. Install Homebrew: https://brew.sh" |
| Tesseract install fails | "OCR features won't work. Install manually: brew install tesseract" |
| winget not found (Windows) | "Tesseract install skipped. Install via: https://github.com/UB-Mannheim/tesseract/wiki" |
| uv sync fails | "Dependency install failed. Try: uv sync --all-extras --verbose" |
| Alias already exists | "Shell alias already configured. Skipping." |
| .env write fails | "Cannot write .env file. Check permissions in project directory." |
| API key validation fails | "Key invalid or network error. You can set it later in .env file." |

## PowerShell Execution Policy

Windows may block script execution. install.ps1 handles this:
1. Detect policy: `Get-ExecutionPolicy`
2. If "Restricted": print instructions to run
   `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`
3. If "RemoteSigned" or higher: proceed normally

## Output Formatting

### Colors (ANSI for bash, Write-Host for PowerShell)
- Green: success messages
- Red: error messages
- Yellow: warnings and optional steps
- Blue: info and progress

### Progress Indicators
- Step markers: `[1/7]`, `[2/7]`, etc.
- Success: checkmark or "OK"
- Error: "FAILED" with remediation

## Line Count Estimates

| Module | Estimated Lines | Limit |
|--------|-----------------|-------|
| `core/setup.py` | ~150 | 300 |
| `cli.py` additions | ~15 | N/A (existing file) |

## Constraints

- Install scripts MUST work without Python installed
- Configuration wizard requires Python (runs after install)
- Tesseract is optional - never block on it
- .env file is never committed (already in .gitignore)
- Shell alias must be idempotent (check before adding)
- Python 3.14 availability depends on uv's release schedule; fallback to 3.13 if needed
