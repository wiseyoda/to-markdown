# Tasks: Batch Processing

## Progress Dashboard

> Last updated: 2026-02-26 | Run `specflow tasks sync` to refresh

| Phase | Status | Progress |
|-------|--------|----------|
| Setup | PENDING | 0/3 |
| Core Batch Module | PENDING | 0/6 |
| CLI Integration | PENDING | 0/5 |
| Progress Reporting | PENDING | 0/3 |
| Error Handling | PENDING | 0/3 |
| Polish | PENDING | 0/6 |

**Overall**: 0/26 (0%) | **Current**: None

---

## Phase 1: Setup

**Purpose**: Add dependencies and constants needed for batch processing.

- [x] T001 [P] Add `rich>=13.0` to core dependencies in `pyproject.toml`
- [x] T002 [P] Add batch constants to `src/to_markdown/core/constants.py`: EXIT_PARTIAL=4, GLOB_CHARS frozenset
- [x] T003 [P] Add batch test fixtures to `tests/conftest.py`: mixed-format directory, empty directory, directory with hidden files

**Checkpoint**: Dependencies installed, constants defined, test infrastructure ready.

---

## Phase 2: Core Batch Module (US1, US2)

**Goal**: Implement file discovery and batch conversion loop.

**Independent Test**: `discover_files()` and `convert_batch()` work correctly in isolation.

### Tests

- [x] T004 [P] Write tests for `discover_files()` in `tests/test_batch.py`: directory scanning (recursive/non-recursive), hidden file skipping, extensionless file skipping, empty directory, glob pattern resolution
- [x] T005 [P] Write tests for `convert_batch()` in `tests/test_batch.py`: successful batch, mixed results, all failures, fail-fast behavior, output directory mirroring, skip on existing output, force overwrite

### Implementation

- [x] T006 Implement `discover_files()` in `src/to_markdown/core/batch.py`: walk directory with Path.rglob/glob, skip hidden files and extensionless files, sort for deterministic order
- [x] T007 Implement `resolve_glob()` in `src/to_markdown/core/batch.py`: resolve glob pattern to list of file paths, handle no-match case
- [x] T008 Implement `BatchResult` dataclass in `src/to_markdown/core/batch.py`: succeeded/failed/skipped lists, total property, exit_code property
- [x] T009 Implement `convert_batch()` in `src/to_markdown/core/batch.py`: iterate files calling convert_file(), classify errors (UnsupportedFormat->skip, OutputExists->skip, other->fail), fail-fast support, output directory path resolution

**Checkpoint**: Batch module works end-to-end with mocked pipeline calls.

---

## Phase 3: CLI Integration (US1, US2, US4)

**Goal**: Wire batch processing into the Typer CLI.

**Independent Test**: `to-markdown docs/` and `to-markdown "*.pdf"` work from command line.

### Tests

- [x] T010 [P] Write CLI tests for batch mode in `tests/test_cli.py`: directory input, glob input, --no-recursive flag, --fail-fast flag, batch exit codes (SUCCESS, PARTIAL, ERROR)

### Implementation

- [x] T011 Change CLI `file` argument from `Path` to `str` in `src/to_markdown/cli.py`, add input type detection (file/dir/glob), dispatch to single-file or batch path
- [x] T012 Add `--no-recursive` and `--fail-fast` flags to `src/to_markdown/cli.py`
- [x] T013 Implement batch dispatch in CLI main(): call discover_files/resolve_glob, call convert_batch, print summary, exit with batch result exit code
- [x] T014 Update `--help` text in `src/to_markdown/cli.py`: update argument help from "File to convert" to "File, directory, or glob pattern to convert", document new flags

**Checkpoint**: Full CLI batch workflow functional.

---

## Phase 4: Progress Reporting (US3)

**Goal**: Add rich progress bar for batch conversions.

**Independent Test**: Progress bar appears during batch conversion, respects --quiet.

### Tests

- [x] T015 Write tests for progress reporting in `tests/test_batch.py`: progress callback invoked per-file, quiet mode suppresses output

### Implementation

- [x] T016 Add rich Progress bar to `convert_batch()` in `src/to_markdown/core/batch.py`: show file count, current filename, percentage; suppress when quiet=True
- [x] T017 Implement summary output in `src/to_markdown/cli.py`: print "Converted X files (Y skipped, Z failed)" after batch, print individual failure details with --verbose

**Checkpoint**: Progress bar and summary work correctly in all modes.

---

## Phase 5: Error Handling Refinement (US4)

**Goal**: Ensure robust error handling for all batch edge cases.

**Independent Test**: Batch handles corrupted files, missing directories, and edge cases gracefully.

### Tests

- [x] T018 [P] Write edge case tests in `tests/test_batch.py`: corrupted file in batch, batch with all unsupported files, batch with existing outputs (skip vs force), symlink directory

### Implementation

- [x] T019 Handle edge cases in batch module: empty directory error message, no-match glob error message, all-skipped-no-succeeded result
- [x] T020 Handle edge case in CLI: `-o` points to existing file during batch (error), input path doesn't exist (error with clear message)

**Checkpoint**: All error scenarios handled with clear messages and correct exit codes.

---

## Phase 6: Polish & Documentation

**Purpose**: Documentation, coding standards compliance, final verification.

- [x] T021 Update `README.md` with batch processing usage examples and new flags
- [x] T022 Update `--help` output verification test in `tests/test_cli.py` to include batch flags
- [x] T023 Update `.specify/memory/coding-standards.md`: add batch.py to project structure, document batch exit code
- [x] T024 Update `.specify/memory/tech-stack.md`: add rich dependency
- [x] T025 Run full test suite (`uv run pytest`), `ruff check`, `ruff format --check` - fix any issues
- [x] T026 [P] Write human testing instructions in README.md "How to Test" section: step-by-step copy-paste commands for directory conversion, glob patterns, progress bar, error handling (corrupted file, empty dir), and exit codes with expected outputs for each scenario

**Checkpoint**: All tests pass, docs current, human verification steps documented, ready for verification.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - all tasks are parallel
- **Phase 2 (Core Batch)**: Depends on Phase 1 (constants, fixtures)
  - Tests (T004, T005) can be written in parallel
  - Implementation (T006-T009): T008 first (BatchResult), then T006/T007 parallel, then T009
- **Phase 3 (CLI)**: Depends on Phase 2 (batch module exists)
  - T010 (tests) can be written parallel with T011-T014
  - T011 first (argument change), then T012 (flags), T013 (dispatch), T014 (help)
- **Phase 4 (Progress)**: Depends on Phase 2 (convert_batch exists)
  - Can run parallel with Phase 3 CLI tests (but implementation touches same files)
- **Phase 5 (Error Handling)**: Depends on Phase 2 and 3
- **Phase 6 (Polish)**: Depends on all above

### Parallel Opportunities

- All Phase 1 tasks (T001-T003) can run in parallel
- Phase 2 tests (T004, T005) can be written in parallel with each other
- Phase 2: T006 and T007 can be implemented in parallel (after T008)
- Phase 3 tests (T010) can be written parallel with implementation
- Phase 5 tests (T018) can be written parallel with other Phase 5 work

---

## Notes

- [P] tasks = different files, no dependencies
- Total: 26 tasks across 6 phases
- Existing 170+ tests must continue passing (no regression)
- All constants in constants.py, no magic numbers
- Files must stay under 300 lines (batch.py, cli.py)
