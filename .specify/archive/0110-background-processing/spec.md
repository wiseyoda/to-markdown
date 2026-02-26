# Feature Specification: Background Processing

**Feature Branch**: `0110-background-processing`
**Created**: 2026-02-26
**Status**: Draft
**Input**: ROADMAP Phase 0110 + Discovery decisions

## User Scenarios & Testing

### User Story 1 - Background Single File Conversion (Priority: P1)

A user has a large PDF with OCR + smart features that takes 30+ seconds. They want to
start the conversion and continue working, checking back when it's done.

**Why this priority**: Core use case. Without background single-file conversion, the entire
feature has no value.

**Independent Test**: Run `to-markdown large.pdf --background --clean --summary` and verify
a task ID is returned immediately. Then check `to-markdown --status <id>` to see it complete.

**Acceptance Scenarios**:

1. **Given** a valid file, **When** user runs `to-markdown file.pdf --background`,
   **Then** a task ID is printed and the terminal returns immediately
2. **Given** a running task, **When** user runs `to-markdown --status <id>`,
   **Then** status shows "running" with elapsed time
3. **Given** a completed task, **When** user runs `to-markdown --status <id>`,
   **Then** status shows "completed" with output path and duration

---

### User Story 2 - Task Status and Cancellation (Priority: P2)

A user wants to check on their background tasks or cancel one that's no longer needed.

**Why this priority**: Status checking is essential for background tasks to be useful.
Without it, users have no way to know when their conversion is done.

**Independent Test**: Start a background task, check `--status all` to see it listed,
check `--status <id>` for details, cancel with `--cancel <id>`.

**Acceptance Scenarios**:

1. **Given** multiple background tasks, **When** user runs `to-markdown --status all`,
   **Then** a summary table of all recent tasks is displayed
2. **Given** a running task, **When** user runs `to-markdown --cancel <id>`,
   **Then** the task is terminated and status shows "cancelled"
3. **Given** no tasks exist, **When** user runs `to-markdown --status all`,
   **Then** a "no tasks found" message is shown

---

### User Story 3 - Background Batch Conversion (Priority: P3)

A user wants to convert an entire directory in the background with batch processing.

**Why this priority**: Extends P1 to batch. High value but builds on single-file infrastructure.

**Independent Test**: Run `to-markdown docs/ --background` and verify task ID returned.
Check status to see batch progress.

**Acceptance Scenarios**:

1. **Given** a directory with files, **When** user runs `to-markdown docs/ --background`,
   **Then** a task ID is returned and batch conversion runs in background
2. **Given** a running batch task, **When** user runs `to-markdown --status <id>`,
   **Then** status shows "running" with elapsed time

---

### User Story 4 - MCP Background Tools (Priority: P4)

An AI agent wants to fire-and-forget a long conversion and poll for results later.

**Why this priority**: Extends background to MCP. Important for AI agent workflows but
requires all CLI infrastructure first.

**Independent Test**: Call MCP `start_conversion` tool, receive task ID. Call
`get_task_status` to poll. Call `list_tasks` to see all. Call `cancel_task` to stop one.

**Acceptance Scenarios**:

1. **Given** a file path, **When** agent calls `start_conversion`,
   **Then** a task ID and status envelope are returned immediately
2. **Given** a task ID, **When** agent calls `get_task_status`,
   **Then** full task details are returned (status, progress, output path if complete)
3. **Given** active tasks, **When** agent calls `list_tasks`,
   **Then** all tasks with summary status are returned
4. **Given** a running task, **When** agent calls `cancel_task`,
   **Then** the task is cancelled and confirmation is returned

---

### Edge Cases

- What happens when `--background` is combined with `--status` or `--cancel`?
  → Error: flags are mutually exclusive
- What happens when `--status` is given an invalid task ID?
  → Error: "Task not found: <id>"
- What happens when `--cancel` targets a completed task?
  → Message: "Task <id> already completed"
- What happens when the background worker process crashes?
  → Status check detects stale PID, marks task as failed
- What happens when the tasks.db doesn't exist yet?
  → Auto-created on first use (SQLite handles this)
- What happens when `~/.to-markdown/` directory doesn't exist?
  → Auto-created with `mkdir -p` equivalent
- What happens when two background tasks write to the same output file?
  → Second task fails with `OutputExistsError` (existing overwrite protection)

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide a `Task` dataclass with fields: id (str), status
  (pending/running/completed/failed/cancelled), input_path, output_path, command_args,
  created_at, started_at, completed_at, error, pid.
  Note: phase doc's `result_summary` field is covered by the `error` field (for failures)
  and `output_path` (for successes) — no separate field needed.
- **FR-002**: System MUST provide a `TaskStore` class backed by SQLite at
  `~/.to-markdown/tasks.db` with CRUD operations (create, get, update, list, delete)
- **FR-003**: System MUST use WAL journal mode for SQLite to support concurrent reads/writes
- **FR-004**: System MUST generate task IDs as first 8 hex chars of UUID4
- **FR-005**: CLI MUST accept `--background` / `--bg` flag that starts conversion in a
  detached subprocess and prints task ID
- **FR-006**: CLI MUST accept `--status <task-id|all>` flag to show task status
- **FR-007**: CLI MUST accept `--cancel <task-id>` flag to terminate a running task
- **FR-008**: Background worker MUST spawn via `subprocess.Popen` with `start_new_session=True`
  and redirect stdout/stderr to `~/.to-markdown/logs/<task-id>.log`
- **FR-009**: Worker MUST update task status in SQLite: pending → running → completed/failed
- **FR-010**: Worker MUST handle SIGTERM gracefully (update status to cancelled, clean up)
- **FR-011**: System MUST auto-cleanup completed/failed/cancelled tasks older than 24 hours.
  Cleanup runs at CLI startup in --status/--cancel/--background branches (not --help/--version).
  check_orphans() runs before cleanup to mark stale PIDs as failed first.
- **FR-012**: MCP MUST provide `start_conversion` tool that creates a background task
  and returns task ID immediately
- **FR-013**: MCP MUST provide `get_task_status` tool that returns task details by ID
- **FR-014**: MCP MUST provide `list_tasks` tool that returns all recent tasks
- **FR-015**: MCP MUST provide `cancel_task` tool that terminates a running task
- **FR-016**: `--status` display MUST show task ID, status, input path, output path (if
  complete), duration, and error (if failed)
- **FR-017**: `--status all` MUST show a summary table of tasks from last 24 hours,
  limited to TASK_LIST_MAX_RESULTS entries sorted by created_at DESC
- **FR-018**: `--background`, `--status`, and `--cancel` flags MUST be mutually exclusive
- **FR-019**: Worker MUST pass through all conversion flags (--clean, --summary, --images,
  --force, -o) to the underlying conversion
- **FR-020**: System MUST detect orphan tasks (PID no longer running) and mark as failed
- **FR-021**: MCP `start_conversion` MUST support both single file and directory/batch mode
- **WR-001**: `core/tasks.py` MUST be imported by CLI in `cli.py` for --status/--cancel/--background
- **WR-002**: `core/worker.py` MUST be imported by CLI in `cli.py` for --background spawn
- **WR-003**: Background MCP tools MUST be registered in `mcp/server.py` and handlers
  added to `mcp/tools.py`

### Key Entities

- **Task**: Represents a background conversion job. Fields: id, status, input_path,
  output_path, command_args, created_at, started_at, completed_at, error, pid
- **TaskStore**: Manages Task persistence in SQLite. One instance per process.
- **TaskStatus**: Enum of valid states: pending, running, completed, failed, cancelled

## Success Criteria

### Measurable Outcomes

- **SC-001**: `to-markdown file.pdf --background` returns a task ID in under 1 second
- **SC-002**: `to-markdown --status <id>` returns accurate status within 1 second
- **SC-003**: Background conversion produces identical output to foreground conversion
- **SC-004**: All 4 MCP background tools callable from Claude Code session
- **SC-005**: Orphan task detection works when worker process is killed
- **SC-006**: Auto-cleanup removes tasks older than 24 hours
- **SC-007**: All existing tests continue to pass (no regressions)
