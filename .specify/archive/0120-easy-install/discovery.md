# Discovery: Easy Install

**Phase**: `0120-easy-install`
**Created**: 2026-02-26
**Status**: Complete

## Phase Context

**Source**: ROADMAP Phase 0120
**Goal**: Create a one-command install experience for non-technical users on both macOS
and Windows. Clone the repo, run one script, and everything works.

---

## Codebase Examination

### Related Implementations

| Location | Description | Relevance |
|----------|-------------|-----------|
| `pyproject.toml` | Entry points: `to-markdown`, `to-markdown-mcp` | Install scripts run `uv sync` |
| `src/to_markdown/cli.py` | Typer CLI with --version flag | Will add --setup flag |
| `src/to_markdown/core/constants.py` | APP_NAME, GEMINI_API_KEY_ENV, etc. | Config wizard constants |
| `.env.example` | Template for API key config | Wizard creates .env from this pattern |
| `.gitignore` | .env excluded, .env.example tracked | Config file safety |
| `README.md` | Current install: just `uv sync` | Will reference INSTALL.md |

### Existing Patterns & Conventions

- **Constants-only**: All values in `core/constants.py`
- **Lazy imports**: Optional deps imported only when needed
- **Exit codes**: EXIT_SUCCESS through EXIT_PARTIAL in constants.py
- **Typer CLI**: Single command with many flags, version callback
- **python-dotenv**: Already loads .env from project directory for LLM features
- **~/.to-markdown/**: Data directory for background tasks (tasks.db, logs/)

### Entry Points

| Entry Point | File | Registration Pattern |
|-------------|------|---------------------|
| CLI main | `cli.py` | `@app.command()` on `main()` |
| --version | `cli.py` | `typer.Option(callback=_version_callback)` |
| --setup | `cli.py` (planned) | New flag triggering config wizard |

### Dependencies for Install

| Dependency | Detection | Install Method |
|-----------|-----------|----------------|
| uv | `command -v uv` / `Get-Command uv` | Official installer (curl/irm) |
| Python 3.14+ | `uv python list` | `uv python install 3.14` |
| Tesseract | `command -v tesseract` / `Get-Command tesseract` | Homebrew (macOS) / winget (Windows) |
| Project deps | `uv sync` exit code | `uv sync --all-extras` |

---

## Design Decisions

### D-71: Shell alias for global CLI access
**Decision**: Add shell alias `alias to-markdown='uv run --directory /path to-markdown'` to
user's shell config (~/.zshrc or ~/.bashrc).
**Rationale**: Simplest approach - no PATH changes, no symlinks, works with uv's venv management.

### D-72: .env file in project directory
**Decision**: Configuration wizard writes .env alongside pyproject.toml.
**Rationale**: python-dotenv already loads from CWD/project root. Visible, simple, consistent
with existing LLM feature configuration.

### D-73: Install scripts are standalone (no Python dependency)
**Decision**: install.sh is pure bash, install.ps1 is pure PowerShell. Neither requires Python.
**Rationale**: Can't assume Python exists before the install script runs - that's what the
script installs.

### D-74: Configuration wizard is a Python module
**Decision**: `--setup` flag triggers `core/setup.py` which handles interactive prompts.
**Rationale**: After install, Python is available. Typer/rich provide good interactive UX.

### D-75: Tesseract is optional with clear messaging
**Decision**: Install scripts detect and offer Tesseract but don't fail without it.
**Rationale**: OCR is nice-to-have. Core conversion works without Tesseract.
