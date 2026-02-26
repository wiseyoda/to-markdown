---
phase: 0110
name: background-processing
status: not_started
created: 2026-02-26
updated: 2026-02-26
---

# Phase 0110: Background Processing

**Goal**: Add asynchronous background processing so that long-running conversions
(especially batch + smart features) don't block the caller. Expose via both CLI flags
and MCP tools.

**Scope**:

### 1. Task Manager
- `src/to_markdown/core/tasks.py`: Task lifecycle management
- Task dataclass: id (UUID), status (pending/running/completed/failed), input,
  output_path, created_at, completed_at, error, result_summary
- SQLite-backed task store (lightweight, zero-config, file-based)
- Task store location: `~/.to-markdown/tasks.db` (configurable via env var)
- Automatic cleanup of completed tasks older than configurable retention period

### 2. CLI Background Flag
- `--background` / `--bg` flag: kicks off conversion in background, returns task ID
- Output: `Task started: abc123. Check status with: to-markdown --status abc123`
- `--status <task-id>`: show task status (pending/running/completed/failed + details)
- `--status all`: list all recent tasks with status summary
- `--cancel <task-id>`: cancel a running task
- Background execution via subprocess (fork and detach from terminal)

### 3. MCP Background Tools
- `start_conversion` tool: starts background task, returns task ID immediately
- `get_task_status` tool: check task status by ID
- `list_tasks` tool: list all tasks with status
- `cancel_task` tool: cancel a running task
- Enables AI agents to fire-and-forget long conversions and poll for results

### 4. Process Management
- Background worker process with proper signal handling
- PID file management to prevent orphan processes
- Graceful shutdown on SIGTERM/SIGINT
- Stdout/stderr redirected to log file per task

### 5. Tests
- Test task creation, status transitions, completion
- Test SQLite store CRUD operations
- Test CLI --background flag output format
- Test --status and --cancel commands
- Test MCP background tool handlers
- Test task cleanup / retention

**Deliverables**:
- [ ] Task manager with SQLite store
- [ ] --background flag for CLI (returns task ID)
- [ ] --status and --cancel CLI commands
- [ ] MCP tools: start_conversion, get_task_status, list_tasks, cancel_task
- [ ] Background process management (fork, PID, signals)
- [ ] Task retention / cleanup
- [ ] Tests for all task lifecycle scenarios
- [ ] README updated with background processing section

**Verification Gate**: **USER GATE** - `to-markdown docs/ --background` returns a task
ID immediately. `to-markdown --status <id>` shows progress. MCP `start_conversion`
tool works from an AI agent session.

**Estimated Complexity**: High
