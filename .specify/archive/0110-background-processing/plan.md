# Implementation Plan: Background Processing

**Branch**: `0110-background-processing` | **Date**: 2026-02-26 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/0110-background-processing/spec.md`

## Summary

Add background processing so long-running conversions don't block the caller. A new
`core/tasks.py` module provides SQLite-backed task lifecycle management. A new
`core/worker.py` module spawns detached subprocesses that run the existing conversion
pipeline. The CLI gains `--background`, `--status`, and `--cancel` flags. The MCP server
gains 4 new tools for AI agent fire-and-forget workflows.

## Technical Context

**Language/Version**: Python 3.14+
**Primary Dependencies**: sqlite3 (stdlib), subprocess (stdlib), signal (stdlib), os (stdlib)
**Storage**: SQLite at `~/.to-markdown/tasks.db` (WAL mode)
**Testing**: pytest with mocked subprocess calls
**Target Platform**: macOS, Linux (POSIX subprocess detach)
**Constraints**: No new third-party dependencies. 300-line file limit.

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Completeness | PASS | Background produces same output as foreground |
| II. Magic Defaults | PASS | `--background` is opt-in, default behavior unchanged |
| III. Kreuzberg Wrapper | PASS | No changes to extraction pipeline |
| IV. Simplicity | PASS | subprocess.Popen, SQLite stdlib - no new deps |
| V. Quality Testing | PASS | Tests for all lifecycle states, mocked subprocesses |
| VI. Zero Tolerance | PASS | All constants in constants.py, no duplication |
| VII. Phases Done | PASS | USER GATE with real-world smoke test |

## Project Structure

### Documentation (this feature)

```text
specs/0110-background-processing/
├── discovery.md
├── spec.md
├── requirements.md
├── plan.md
└── tasks.md
```

### Source Code (new and modified files)

```text
src/to_markdown/
├── core/
│   ├── tasks.py           # NEW: Task dataclass, TaskStatus enum, TaskStore (SQLite)
│   ├── worker.py          # NEW: spawn_worker(), _run_worker(), signal handling
│   ├── display.py         # NEW: extracted from cli.py (_run_batch helper, formatting)
│   └── constants.py       # MODIFIED: add background processing constants
├── mcp/
│   ├── server.py          # MODIFIED: register 4 new background tools
│   └── tools.py           # MODIFIED: add 4 new handler functions
└── cli.py                 # MODIFIED: add --background, --status, --cancel flags

tests/
├── test_tasks.py          # NEW: TaskStore CRUD, Task lifecycle, cleanup
├── test_worker.py         # NEW: spawn_worker(), signal handling, log capture
├── test_cli.py            # MODIFIED: add tests for new flags
├── test_mcp_tools.py      # MODIFIED: add tests for new MCP handlers
└── test_mcp_server.py     # MODIFIED: verify new tool registration
```

**Structure Decision**: Follows existing single-project layout. Two new core modules
(`tasks.py`, `worker.py`) keep concerns separated and files under 300 lines.

## Architecture

### Task Lifecycle

```
CLI --background                    MCP start_conversion
        │                                  │
        ▼                                  ▼
   TaskStore.create()  ←───────────  TaskStore.create()
   status: "pending"                 status: "pending"
        │                                  │
        ▼                                  ▼
   spawn_worker(task_id)  ←────────  spawn_worker(task_id)
        │                                  │
        ▼                                  ▼
   subprocess.Popen(                 (returns task_id
     "to-markdown --_worker <id>"     immediately)
     start_new_session=True)
        │
        ▼
   Worker process:
   1. Update status → "running"
   2. Call convert_file() or convert_batch()
   3. Update status → "completed" or "failed"
   4. Write output path / error to DB
```

### SQLite Schema

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'pending',
    input_path TEXT NOT NULL,
    output_path TEXT,
    command_args TEXT,       -- JSON-serialized conversion flags
    created_at TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    error TEXT,
    pid INTEGER
);
```

### Module Responsibilities

**`core/tasks.py` (~200 lines)**:
- `TaskStatus` enum: pending, running, completed, failed, cancelled
- `Task` dataclass: all fields from schema + computed properties (duration, is_done)
- `TaskStore` class:
  - `__init__(db_path)`: connect with WAL mode, create table
  - `create(input_path, command_args) -> Task`: insert pending task
  - `get(task_id) -> Task | None`: fetch by ID
  - `list(limit) -> list[Task]`: fetch recent tasks
  - `update(task_id, **fields)`: update specific fields
  - `delete(task_id)`: remove task and log file
  - `cleanup(max_age_hours)`: remove old completed/failed/cancelled tasks
  - `check_orphans()`: detect tasks with stale PIDs, mark as failed.
    Called by: CLI --status/--cancel/--background branches (before display/action),
    MCP get_task_status and list_tasks handlers (before returning results)
  - `_ensure_data_dir()`: create `~/.to-markdown/` and `~/.to-markdown/logs/` with
    exist_ok=True. Called by `__init__()` and `spawn_worker()`
- `get_default_store() -> TaskStore`: singleton with default DB path

**`core/worker.py` (~150 lines)**:
- `spawn_worker(task_id, store) -> int`: spawn detached subprocess, return PID
  - Builds command: `[sys.executable, "-m", "to_markdown.cli", "--_worker", task_id]`
  - `subprocess.Popen(cmd, start_new_session=True, stdout=log_fd, stderr=log_fd)`
  - Updates task PID in store
- `run_worker(task_id)`: entry point for worker subprocess
  - Register SIGTERM handler → set status to cancelled
  - Set status to running
  - Deserialize command_args from task
  - Call `convert_file()` or `convert_batch()` based on input
  - Set status to completed (with output_path) or failed (with error)
- Calls `TaskStore._ensure_data_dir()` via imported store (no duplicate helper needed)

**`cli.py` modifications (~40 lines added, after pre-refactoring)**:
- **Pre-requisite**: cli.py is currently 285 lines. Extract `_run_batch()` helper and
  display formatting into `core/display.py` (~80 lines) to create headroom. This brings
  cli.py to ~205 lines, leaving room for ~95 lines of new background code.
- Add params: `background`, `status`, `cancel`, `_worker` (hidden)
- Early return for `--status`: run check_orphans() + cleanup(), then display task info
- Early return for `--cancel`: send SIGTERM to task PID, update status
- Early return for `--_worker`: call `run_worker(task_id)` (internal only)
- If `--background`: run cleanup(), create task, spawn worker, print task ID, exit

**`mcp/tools.py` additions (~80 lines)**:
- `handle_start_conversion(file_path, *, clean, summary, images) -> str`
- `handle_get_task_status(task_id) -> str`
- `handle_list_tasks() -> str`
- `handle_cancel_task(task_id) -> str`

**`mcp/server.py` additions (~40 lines)**:
- 4 new `@mcp.tool()` wrappers delegating to handlers

### Worker Invocation

The worker is invoked as a hidden CLI flag `--_worker <task-id>`:

```bash
# Parent spawns:
python -m to_markdown.cli --_worker a1b2c3d4

# Worker process:
1. Reads task from SQLite by ID
2. Deserializes command_args (input_path, output_path, force, clean, summary, images)
3. Calls convert_file() or convert_batch()
4. Updates SQLite with result
```

This reuses the existing CLI entry point and avoids a separate worker script.

### Status Display

```
# Single task
$ to-markdown --status a1b2c3d4
Task a1b2c3d4
  Status:  completed
  Input:   /path/to/large-file.pdf
  Output:  /path/to/large-file.md
  Started: 2026-02-26 14:30:00
  Duration: 45.2s

# All tasks
$ to-markdown --status all
ID        Status     Input                     Duration
a1b2c3d4  completed  large-file.pdf            45.2s
b2c3d4e5  running    docs/ (batch)             12.1s
c3d4e5f6  failed     corrupt.pdf               2.3s
```

### MCP Response Envelopes

Following existing pattern from `handle_convert_file()`:

```markdown
# start_conversion response
**Task ID**: a1b2c3d4
**Status**: pending
**Input**: /path/to/file.pdf
**Message**: Background conversion started. Use get_task_status to check progress.

# get_task_status response
**Task ID**: a1b2c3d4
**Status**: completed
**Input**: /path/to/file.pdf
**Output**: /path/to/file.md
**Duration**: 45.2s
```

## Integration Architecture

| New Module | Caller | File | Registration Pattern |
|------------|--------|------|---------------------|
| `core/tasks.py` | `cli.py` | `src/to_markdown/cli.py` | Lazy import in `--status`/`--cancel`/`--background` branches |
| `core/worker.py` | `cli.py` | `src/to_markdown/cli.py` | Lazy import in `--background` and `--_worker` branches |
| `core/tasks.py` | `core/worker.py` | `src/to_markdown/core/worker.py` | Direct import (worker always needs task store, same pattern as batch.py per D-60) |
| `core/tasks.py` | `mcp/tools.py` | `src/to_markdown/mcp/tools.py` | Lazy import in background tool handlers |
| `core/worker.py` | `mcp/tools.py` | `src/to_markdown/mcp/tools.py` | Lazy import in `handle_start_conversion()` |
| MCP bg tools | `mcp/server.py` | `src/to_markdown/mcp/server.py` | `@mcp.tool()` decorator pattern (same as existing) |

## Complexity Tracking

No constitution violations. All new code uses stdlib (sqlite3, subprocess, signal, os).
No new third-party dependencies. Two new modules at ~150-200 lines each.
