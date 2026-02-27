# Tasks: Phase 0120 - Easy Install

## Phase Goals Coverage

| # | Phase Goal | Spec Requirement(s) | Task(s) | Status |
|---|------------|---------------------|---------|--------|
| 1 | One-command macOS install (install.sh) | FR-001 | T002-T004 | COVERED |
| 2 | One-command Windows install (install.ps1) | FR-002 | T005-T007 | COVERED |
| 3 | Interactive configuration wizard (--setup) | FR-003, WR-001, WR-002 | T008-T014 | COVERED |
| 4 | Step-by-step INSTALL.md for non-technical users | FR-004 | T018-T019 | COVERED |
| 5 | Clean uninstall scripts | FR-005 | T015-T017 | COVERED |
| 6 | Tests for install logic and config wizard | - | T008, T010, T012 | COVERED |

Coverage: 6/6 goals (100%)

---

## Progress Dashboard

| Section | Total | Done | Blocked |
|---------|-------|------|---------|
| 1. Setup & Constants | 1 | 0 | 0 |
| 2. macOS Install Script | 3 | 0 | 0 |
| 3. Windows Install Script | 3 | 0 | 0 |
| 4. Configuration Wizard | 7 | 0 | 0 |
| 5. Uninstall Scripts | 3 | 0 | 0 |
| 6. Documentation | 4 | 0 | 0 |
| 7. Verification | 4 | 0 | 0 |
| **Total** | **25** | **0** | **0** |

---

## 1. Setup & Constants

- [x] T001 Add setup/install constants to `src/to_markdown/core/constants.py` (SETUP_ENV_FILE, SETUP_GEMINI_KEY_URL, SETUP_VALIDATION_PROMPT, SETUP_VALIDATION_MAX_TOKENS, SHELL_ALIAS_COMMENT)

## 2. macOS Install Script

- [x] T002 [P] Create `install.sh` with dependency detection (uv, Python 3.14+, Tesseract) and `uv sync --all-extras`
- [x] T003 [P] Add shell alias setup to `install.sh` (detect shell, idempotent append, source RC)
- [x] T004 [P] Add error handling, colorful output, and install validation to `install.sh`

## 3. Windows Install Script

- [x] T005 [P] Create `install.ps1` with dependency detection (uv, Python 3.14+, Tesseract) and `uv sync --all-extras`
- [x] T006 [P] Add PowerShell function/alias setup and validation to `install.ps1`
- [x] T007 [P] Add error handling, formatted output, and execution policy check to `install.ps1`

## 4. Configuration Wizard

- [x] T008 Write tests for configuration wizard in `tests/test_setup.py` (detect .env, write .env, skip flow)
- [x] T009 Create `src/to_markdown/core/setup.py` — detect existing .env, explain features, prompt for API key
- [x] T010 Write tests for API key validation in `tests/test_setup.py` (valid key, invalid key, network error)
- [x] T011 Add API key validation (mock Gemini test call) and .env writing to `core/setup.py`
- [x] T012 Write tests for --setup CLI flag in `tests/test_cli.py` (triggers wizard, --quiet mode)
- [x] T013 [W] Wire --setup flag in `cli.py` to `core/setup.py` (lazy import, early return)
- [x] T014 Add --quiet mode to setup wizard — non-interactive, validate existing config only

## 5. Uninstall Scripts

- [x] T015 [P] Create `uninstall.sh` for macOS (remove alias, .venv, ~/.to-markdown data dir)
- [x] T016 [P] Create `uninstall.ps1` for Windows (remove function, .venv, data dir)
- [x] T017 Add confirmation prompt and --yes flag to uninstall scripts

## 6. Documentation

- [x] T018 Create `INSTALL.md` with macOS and Windows sections (step-by-step, terminal examples)
- [x] T019 Add troubleshooting FAQ and "what to do next" sections to `INSTALL.md`
- [x] T020 Update `README.md` with quick-start section referencing `INSTALL.md`
- [x] T021 Write smoke test instructions in `specs/0120-easy-install/smoke-test.md`

## 7. Verification

- [x] T022 [V] Run test suite — all tests pass
- [x] T023 [V] Run linter — no errors
- [x] T024 [V] Run format check — no errors
- [x] T025 [V] [W] Verify --setup flag wired and working end-to-end
