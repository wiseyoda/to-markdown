# Tasks: Phase 0110 - Background Processing

## Phase Goals Coverage

| # | Phase Goal | Spec Requirement(s) | Task(s) | Status |
|---|------------|---------------------|---------|--------|
| 1 | Task manager with SQLite store | FR-001, FR-002, FR-003, FR-004 | T002-T006 | COVERED |
| 2 | CLI --background/--bg flag | FR-005, FR-019 | T012-T015 | COVERED |
| 3 | CLI --status and --cancel | FR-006, FR-007, FR-016, FR-017, FR-018 | T016-T018 | COVERED |
| 4 | MCP tools (start, status, list, cancel) | FR-012, FR-013, FR-014, FR-015, FR-021 | T019-T023 | COVERED |
| 5 | Background process management | FR-008, FR-009, FR-010, FR-020 | T007-T011 | COVERED |
| 6 | Task retention/cleanup | FR-011 | T006, T010 | COVERED |
| 7 | Tests for all lifecycle scenarios | SC-007 | T002-T024 (TDD) | COVERED |
| 8 | README updated | - | T025 | COVERED |
| 9 | Integration wiring | WR-001, WR-002, WR-003 | T015, T022, T024, T030 | COVERED |

Coverage: 9/9 goals COVERED

---

## Progress Dashboard

> Last updated: 2026-02-26 | Run `specflow tasks sync` to refresh

| Phase | Status | Progress |
|-------|--------|----------|
| Setup | PENDING | 0/2 |
| Foundational | PENDING | 0/9 |
| US1 - Background Conversion | PENDING | 0/4 |
| US2 - Status & Cancel | PENDING | 0/3 |
| US3 - Batch Background | PENDING | 0/1 |
| US4 - MCP Background | PENDING | 0/5 |
| Polish | PENDING | 0/6 |

**Overall**: 0/30 (0%) | **Current**: None

---

**Input**: Design documents from `specs/0110-background-processing/`
**Prerequisites**: plan.md (required), spec.md (required)

## Phase 1: Setup

**Purpose**: Add constants, refactor cli.py for headroom

- [x] T001 Refactor `src/to_markdown/cli.py` — extract `_run_batch()` helper and display formatting into `src/to_markdown/core/display.py` (~80 lines) to bring cli.py under 210 lines, creating headroom for Phase 0110 additions (300-line hard limit)
- [x] T002 [P] Add background processing constants to `src/to_markdown/core/constants.py` — TASK_ID_LENGTH, TASK_DB_FILENAME, TASK_LOG_DIR, TASK_RETENTION_HOURS, TASK_STORE_DIR, TASK_LIST_MAX_RESULTS, WORKER_FLAG, TaskStatus values, EXIT_BACKGROUND

---

## Phase 2: Foundational — Task Manager & Worker

**Purpose**: Core task lifecycle infrastructure that all user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

### Tests first

- [x] T003 [P] Write tests for Task dataclass and TaskStatus enum in `tests/test_tasks.py` — creation, field defaults, duration property, status transitions
- [x] T004 [P] Write tests for TaskStore SQLite operations in `tests/test_tasks.py` — create, get, update, list, delete, WAL mode, auto-create dirs/tables, _ensure_data_dir
- [x] T005 [P] Write tests for worker subprocess spawning in `tests/test_worker.py` — spawn_worker(), signal handling, log file creation (mock subprocess.Popen)

### Implementation

- [x] T006 Implement Task dataclass, TaskStatus enum, and TaskStore class in `src/to_markdown/core/tasks.py` — SQLite CRUD, WAL mode, _ensure_data_dir(), cleanup(), check_orphans(), get_default_store()
- [x] T007 [W] Wire tasks.py into worker.py — direct import of TaskStore and Task (same pattern as batch.py per D-60, worker always needs task store)
- [x] T008 Implement spawn_worker() in `src/to_markdown/core/worker.py` — subprocess.Popen with start_new_session=True, log file redirect, PID tracking, calls _ensure_data_dir()
- [x] T009 Implement run_worker() in `src/to_markdown/core/worker.py` — entry point for worker process, SIGTERM handler, calls convert_file()/convert_batch(), handles OutputExistsError gracefully
- [x] T010 [P] Write tests for task cleanup and orphan detection in `tests/test_tasks.py` — cleanup removes old tasks + logs, check_orphans marks stale PIDs as failed, verify check_orphans called before cleanup
- [x] T011 [P] Write tests for worker run_worker() in `tests/test_worker.py` — successful conversion, failed conversion (including OutputExistsError), SIGTERM cancellation

**Checkpoint**: Task manager and worker fully functional and tested

---

## Phase 3: User Story 1 — Background Single File Conversion (Priority: P1)

**Goal**: `to-markdown file.pdf --background` returns task ID immediately

**Independent Test**: Run with `--background`, verify task ID printed, check `--status`

### Tests first

- [x] T012 Write tests for CLI --background flag in `tests/test_cli.py` — creates task, spawns worker, prints task ID, exits with EXIT_SUCCESS, runs cleanup() at startup (mock spawn_worker)

### Implementation

- [x] T013 Add --background/--bg and --_worker flags to CLI main() in `src/to_markdown/cli.py` — early-return branch for --background (cleanup, create task, spawn worker, print ID), --_worker calls run_worker()
- [x] T014 [P] Write test for --_worker internal flag in `tests/test_cli.py` — calls run_worker with task_id, not shown in --help
- [x] T015 [W] Wire tasks.py and worker.py into cli.py — lazy import of tasks.py in --background, --status, and --cancel branches; lazy import of worker.py in --background and --_worker branches

**Checkpoint**: Single file background conversion works end-to-end

---

## Phase 4: User Story 2 — Task Status & Cancellation (Priority: P2)

**Goal**: `to-markdown --status <id>` and `to-markdown --cancel <id>` work

**Independent Test**: Start background task, check status, cancel it

### Tests first

- [x] T016 Write tests for CLI --status and --cancel flags in `tests/test_cli.py` — --status single shows details, --status all shows table (max TASK_LIST_MAX_RESULTS), --cancel sends SIGTERM, mutual exclusivity with --background, check_orphans called before display

### Implementation

- [x] T017 Add --status and --cancel handlers to CLI main() in `src/to_markdown/cli.py` — early-return branches, display formatting, mutual exclusivity validation, run check_orphans()+cleanup() before displaying status
- [x] T018 [W] Verify --status/--cancel wiring in `tests/test_cli.py` — ensure tasks.py lazy import works in --status and --cancel branches (required by WR-001)

**Checkpoint**: Full CLI background workflow works

---

## Phase 5: User Story 3 — Background Batch Conversion (Priority: P3)

**Goal**: `to-markdown docs/ --background` works for directories and globs

**Independent Test**: Run directory conversion with `--background`, verify task created

- [x] T019 Write test and implement batch background support in `src/to_markdown/core/worker.py` and `tests/test_worker.py` — run_worker detects directory/glob input, calls convert_batch() instead of convert_file()

**Checkpoint**: Both single and batch background conversions work

---

## Phase 6: User Story 4 — MCP Background Tools (Priority: P4)

**Goal**: AI agents can start background conversions and poll for results via MCP

**Independent Test**: Call all 4 MCP tools from Claude Code

### Tests first

- [x] T020 [P] Write tests for MCP background tool handlers in `tests/test_mcp_tools.py` — handle_start_conversion, handle_get_task_status (runs check_orphans before returning), handle_list_tasks (runs check_orphans before returning), handle_cancel_task

### Implementation

- [x] T021 Add handler functions to `src/to_markdown/mcp/tools.py` — handle_start_conversion (creates task + spawns worker), handle_get_task_status (check_orphans then fetch), handle_list_tasks (check_orphans then list), handle_cancel_task with structured response envelopes
- [x] T022 Register 4 new tools in `src/to_markdown/mcp/server.py` — @mcp.tool() wrappers for start_conversion, get_task_status, list_tasks, cancel_task
- [x] T023 [P] Write tests for MCP tool registration in `tests/test_mcp_server.py` — verify 4 new tools registered with correct schemas
- [x] T024 [W] Verify background MCP tool wiring — confirm handlers lazily import from core/tasks.py and core/worker.py, no circular imports

**Checkpoint**: MCP background workflow complete

---

## Phase 7: Polish & Verification

**Purpose**: Documentation, cleanup, and verification

- [x] T025 Update README.md with background processing section — --background, --status, --cancel usage, MCP background tools
- [x] T026 Update MCP_SERVER_INSTRUCTIONS constant in `src/to_markdown/core/constants.py` — mention background tools (start_conversion, get_task_status, list_tasks, cancel_task)
- [x] T027 Write human smoke test instructions in `specs/0110-background-processing/smoke-test.md` — step-by-step commands for USER GATE: start background conversion, poll --status, --cancel, --status all, MCP start_conversion from Claude Code
- [x] T028 [V] Run test suite — all tests pass (`uv run pytest`)
- [x] T029 [V] Run linter and formatter — no errors (`uv run ruff check && uv run ruff format --check`)
- [x] T030 [V] Verify all new modules wired to entry points — cli.py imports tasks+worker+display, server.py registers 4 new tools

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 constants — BLOCKS all user stories
- **US1 Background (Phase 3)**: Depends on Phase 2 (tasks.py + worker.py)
- **US2 Status/Cancel (Phase 4)**: Depends on Phase 3 (needs background tasks to check, and T015 wiring)
- **US3 Batch Background (Phase 5)**: Depends on Phase 2, can parallel with Phase 3-4
- **US4 MCP (Phase 6)**: Depends on Phase 2, can parallel with Phases 3-5
- **Polish (Phase 7)**: Depends on all user stories complete

### Parallel Opportunities

- T003, T004, T005: All test files can be written in parallel
- T010, T011: Additional tests can parallel after T006-T009
- T014: Can parallel with T013
- T020, T023: MCP tests can parallel
- Phase 5 and Phase 6 can run in parallel (different files, no deps on each other)
