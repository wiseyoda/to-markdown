# Tasks: Core CLI & Pipeline

## Phase Goals Coverage

| # | Phase Goal | Spec Requirement(s) | Task(s) | Status |
|---|------------|---------------------|---------|--------|
| 1 | Project setup: pyproject.toml, ruff, pytest, syrupy | FR-001 | T001, T002, T003 | COVERED |
| 2 | Kreuzberg adapter with error handling | FR-002 | T004, T005 | COVERED |
| 3 | Frontmatter composition | FR-003 | T006, T007 | COVERED |
| 4 | Pipeline: extract -> frontmatter -> assemble -> output | FR-004 | T008, T009 | COVERED |
| 5 | Typer CLI with flags | FR-005 | T010, T011 | COVERED |
| 6 | Proper exit codes | FR-005 | T010 | COVERED |
| 7 | Build complete to-markdown CLI wrapping Kreuzberg | FR-004, FR-005 | T008-T011 | COVERED |
| 8 | Compose YAML frontmatter from Kreuzberg metadata | FR-003 | T006, T007 | COVERED |
| 9 | Baseline tests | FR-006 | T005, T007, T009, T011 | COVERED |

Coverage: 9/9 goals (100%)

---

## Progress Dashboard

> Last updated: 2026-02-25 | Run `specflow tasks sync` to refresh

| Phase | Status | Progress |
|-------|--------|----------|
| Project Setup | PENDING | 0/3 |
| Kreuzberg Adapter | PENDING | 0/2 |
| Frontmatter Composition | PENDING | 0/2 |
| Pipeline | PENDING | 0/2 |
| CLI | PENDING | 0/2 |
| Integration & Polish | PENDING | 0/4 |

**Overall**: 0/15 (0%) | **Current**: None

---

**Input**: Design documents from `specs/0020-core-cli-pipeline/`
**Prerequisites**: plan.md (required), spec.md (required)

## Phase 1: Project Setup

**Purpose**: Create the project foundation - pyproject.toml, package structure, constants

- [x] T001 [P] [FR-001] Create pyproject.toml with all dependencies, scripts, ruff config, pytest config
  - Dependencies: kreuzberg>=4.3.8, typer>=0.24.0, pyyaml>=6.0
  - Dev deps: ruff>=0.15.2, pytest>=9.1, pytest-cov>=7.0.0, syrupy>=5.1.0
  - Script entry: `to-markdown = "to_markdown.cli:app"`
  - ruff config: target-version="py314", line-length=100, select=["E","F","I","N","W","UP","B","SIM","RUF"]
  - pytest config: testpaths=["tests"]
  - Requires-python: ">=3.14"
  - Update .gitignore: add __pycache__, *.pyc, .pytest_cache, .ruff_cache, dist/, *.egg-info, .coverage, .env
- [x] T002 [P] [FR-001] Create package structure with __init__.py files
  - `src/to_markdown/__init__.py` with `__version__ = "0.1.0"`
  - `src/to_markdown/core/__init__.py`
  - `tests/__init__.py`
  - `tests/conftest.py` with shared fixtures (tmp_path helpers, sample text file creator)
  - `tests/fixtures/` directory with .gitkeep
  - `.env.example` with `# GEMINI_API_KEY=your-key-here` and `# GEMINI_MODEL=gemini-2.5-flash`
- [x] T003 [P] [FR-001, NFR-001] Create core/constants.py with all project constants
  - Exit codes: EXIT_SUCCESS=0, EXIT_ERROR=1, EXIT_UNSUPPORTED=2, EXIT_ALREADY_EXISTS=3
  - File processing: DEFAULT_OUTPUT_EXTENSION=".md"
  - Version: APP_NAME="to-markdown"
  - Verify: `uv sync` succeeds, `uv run ruff check src/` passes

**Checkpoint**: `uv sync` succeeds, empty package lints clean

---

## Phase 2: Kreuzberg Adapter

**Purpose**: Thin wrapper around Kreuzberg extraction with structured result type

- [x] T004 [S] [FR-002] Implement core/extraction.py - Kreuzberg adapter
  - **Depends on**: T001, T002, T003
  - `ExtractionResult` dataclass: content (str), metadata (dict converted from Kreuzberg metadata object), tables (list)
  - `extract_file(file_path: Path) -> ExtractionResult` function
  - Uses `extract_file_sync` with `ExtractionConfig(output_format="markdown", enable_quality_processing=True)`
  - Unsupported format strategy: delegate to Kreuzberg, catch its exceptions. Do NOT pre-check extensions.
  - Catch `kreuzberg.ExtractionError` and wrap as `UnsupportedFormatError` when error indicates format incompatibility, or `ExtractionError` for other failures
  - Custom exceptions: `UnsupportedFormatError`, `ExtractionError` defined in core/extraction.py
  - Convert Kreuzberg metadata object to plain dict (extracting title, authors, creation_date, page_count, word_count, language, mime_type)
- [x] T005 [S] [FR-002, FR-006] Write tests/test_extraction.py
  - **Depends on**: T004
  - Test: extract a simple .txt file, verify content returned
  - Test: FileNotFoundError for missing file
  - Test: ExtractionResult dataclass fields are correct types
  - Test: extraction with a real small text file (integration)
  - Test: metadata dict contains expected keys when available

**Checkpoint**: Kreuzberg adapter tests pass

---

## Phase 3: Frontmatter Composition

**Purpose**: Compose YAML frontmatter from extraction metadata

- [x] T006 [S] [FR-003] Implement core/frontmatter.py
  - **Depends on**: T003, T004
  - `compose_frontmatter(metadata: dict, source_path: Path) -> str` function
  - Fields (YAML keys): title, author, created, pages, format, words, extracted_at
  - Skip None/empty fields
  - YAML between `---` delimiters with trailing newline
  - Use PyYAML `yaml.dump(default_flow_style=False, sort_keys=False)`
- [x] T007 [S] [FR-003, FR-006] Write tests/test_frontmatter.py
  - **Depends on**: T006
  - Test: full metadata produces all fields
  - Test: partial metadata skips missing fields
  - Test: empty metadata produces minimal frontmatter (just extracted_at and format)
  - Test: special characters in title/author are properly escaped
  - Test: output starts and ends with `---`

**Checkpoint**: Frontmatter tests pass

---

## Phase 4: Pipeline

**Purpose**: End-to-end conversion orchestration

- [x] T008 [S] [FR-004] Implement core/pipeline.py
  - **Depends on**: T004, T006
  - `convert_file(input_path: Path, output_path: Path | None, force: bool) -> Path` function
  - Resolve output path: default = input dir + .md extension; -o = custom path
  - If -o is a directory, use input filename with .md extension in that directory
  - Overwrite check: raise OutputExistsError if output exists and not force
  - Flow: validate input → extract → compose frontmatter → assemble → write
  - Return the output path for confirmation message
  - `OutputExistsError` defined in core/pipeline.py
- [x] T009 [S] [FR-004, FR-006, SC-002] Write tests/test_pipeline.py
  - **Depends on**: T008
  - Test: convert text file, verify output file created with frontmatter + content
  - Test: default output path is input dir with .md extension
  - Test: custom output path via -o file
  - Test: custom output path via -o directory
  - Test: OutputExistsError when output exists without --force
  - Test: --force overwrites existing output
  - Test: missing input file raises appropriate error
  - Test: output directory does not exist raises appropriate error

**Checkpoint**: Pipeline tests pass, can convert a real text file end-to-end

---

## Phase 5: CLI

**Purpose**: Typer-based CLI with all baseline flags

- [x] T010 [S] [FR-005] Implement cli.py - Typer CLI
  - **Depends on**: T008
  - Typer app with main command
  - Positional arg: `file` (Path) - input file
  - Options: `--output/-o` (Path|None), `--force/-f` (bool), `--verbose/-v` (int, count=True), `--quiet/-q` (bool), `--version` (callback)
  - Logging setup: --quiet=ERROR, default=WARNING, --verbose=INFO, -vv=DEBUG
  - Catch all exceptions, map to exit codes (EXIT_SUCCESS, EXIT_ERROR, EXIT_UNSUPPORTED, EXIT_ALREADY_EXISTS)
  - Success message: "Converted {input} → {output}" (unless --quiet)
- [x] T011 [S] [FR-005, FR-006] Write tests/test_cli.py
  - **Depends on**: T010
  - Test: `--version` prints version and exits 0
  - Test: `--help` prints usage and exits 0
  - Test: basic conversion works via CLI runner
  - Test: `--force` flag works
  - Test: `-o` flag works (file and directory)
  - Test: missing file returns exit code 1
  - Test: output exists returns exit code 3
  - Test: `--quiet` suppresses output
  - Test: `--verbose` increases log level

**Checkpoint**: `uv run to-markdown --help` works, all CLI tests pass

---

## Phase 6: Integration & Polish

**Purpose**: Final integration, documentation, and quality checks

- [x] T012 [S] [NFR-001] Run full quality checks and fix any issues
  - **Depends on**: T011
  - `uv run ruff check src/ tests/` - fix all lint errors
  - `uv run ruff format --check src/ tests/` - fix formatting
  - `uv run pytest` - all tests pass
  - Verify no file exceeds 300 lines
  - Verify all constants are in constants.py
  - Verify .env and .env.* are in .gitignore
- [x] T013 [S] Update README and verify --help accuracy
  - **Depends on**: T012
  - Update README.md with basic usage examples (`uv run to-markdown <file>`)
  - Verify `uv run to-markdown --help` output matches implemented flags
  - Update memory docs if any decisions changed during implementation
- [x] T014 [S] Write human testing instructions in specs/0020-core-cli-pipeline/testing.md
  - **Depends on**: T013
  - Step-by-step commands to test the tool on real files
  - Expected output for each command
  - Edge cases to try manually

**Checkpoint**: All quality gates pass, human can test the tool
