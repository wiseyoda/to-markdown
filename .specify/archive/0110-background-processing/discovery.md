# Discovery: Background Processing

**Phase**: `0110-background-processing`
**Created**: 2026-02-26
**Status**: Complete

## Phase Context

**Source**: ROADMAP Phase 0110
**Goal**: Add asynchronous background processing so long-running conversions (especially
batch + smart features) don't block the caller. Expose via both CLI flags and MCP tools.

---

## Codebase Examination

### Related Implementations

| Location | Description | Relevance |
|----------|-------------|-----------|
| `src/to_markdown/cli.py` | Typer single-command app with `main()` | Will add `--background`, `--status`, `--cancel` flags |
| `src/to_markdown/core/pipeline.py` | `convert_file()` and `convert_to_string()` | Background worker calls `convert_file()` directly |
| `src/to_markdown/core/batch.py` | `convert_batch()` with progress bar | Background supports both single and batch |
| `src/to_markdown/mcp/tools.py` | `handle_convert_file()`, `handle_convert_batch()` | New MCP tools will follow same handler pattern |
| `src/to_markdown/mcp/server.py` | FastMCP tool registration via `@mcp.tool()` | Register 4 new background tools |
| `src/to_markdown/core/constants.py` | All project constants | New constants for background processing |

### Existing Patterns & Conventions

- **Lazy imports**: Smart features and batch module use lazy imports to avoid requiring
  optional deps at startup (see `pipeline.py:84-93`, `cli.py:155-157`)
- **Optional extras**: LLM deps are `[llm]`, MCP deps are `[mcp]` - no new deps needed
  for background (SQLite is stdlib)
- **Handler pattern**: MCP tools.py has pure handler functions, server.py has thin
  `@mcp.tool()` wrappers that delegate to handlers
- **Constants-only**: All numeric values in `core/constants.py` - no inline constants
- **Exit codes**: Defined constants `EXIT_SUCCESS` through `EXIT_PARTIAL` in constants.py
- **BatchResult dataclass**: Pattern for structured results with `exit_code` property
- **Rich progress**: Batch uses `rich.progress.Progress` for feedback, suppressed with `--quiet`
- **Error hierarchy**: `ExtractionError` > `UnsupportedFormatError` in extraction.py

### Entry Points

| Entry Point | File | Registration Pattern |
|-------------|------|---------------------|
| CLI commands | `cli.py` | `@app.command()` on `main()` - single command |
| MCP tools | `mcp/server.py` | `@mcp.tool()` decorators delegating to `tools.py` |
| CLI script | `pyproject.toml` | `[project.scripts] to-markdown = "to_markdown.cli:app"` |
| MCP script | `pyproject.toml` | `to-markdown-mcp = "to_markdown.mcp.server:run_server"` |

### Integration Points

- **CLI `main()`**: Add `--background`, `--status`, `--cancel` as `Optional[str]` params
  to the existing Typer command. Early-return if `--status` or `--cancel` is provided.
- **MCP server.py**: Register 4 new tools (`start_conversion`, `get_task_status`,
  `list_tasks`, `cancel_task`) following existing pattern
- **MCP tools.py**: Add handler functions for background tools
- **pipeline.py**: No changes needed - worker process calls `convert_file()` directly
- **batch.py**: No changes needed - worker process calls `convert_batch()` directly

### Constraints Discovered

- **Synchronous codebase**: All current code is synchronous. `extract_file_sync()` is the
  Kreuzberg call. Background processing must spawn separate processes, not convert to async.
- **SQLite in stdlib**: No new dependency needed for task storage.
- **No PID file needed**: SQLite stores PID in tasks table - simpler than separate PID files.
- **stdout/stderr**: MCP uses stdout for JSON-RPC. Background worker must redirect
  stdout/stderr to log file, not terminal.
- **300-line limit**: New `core/tasks.py` and `core/worker.py` must stay under 300 lines each.
- **Typer single-command**: Current CLI is a single `@app.command()`. Adding `--status` and
  `--cancel` as flags preserves backward compatibility (no subcommand refactor).

---

## Requirements Sources

### From ROADMAP/Phase File

1. Task manager with SQLite store (lifecycle management)
2. CLI `--background`/`--bg` flag for async conversion
3. CLI `--status` and `--cancel` commands
4. MCP tools: `start_conversion`, `get_task_status`, `list_tasks`, `cancel_task`
5. Background process management (fork, PID, signals)
6. Task retention/cleanup
7. Tests for all task lifecycle scenarios
8. README updated with background processing section

### From Memory Documents

- **Constitution III**: Kreuzberg wrapper architecture - background doesn't change extraction
- **Constitution IV**: Simplicity - subprocess spawn over async refactor
- **Constitution VI**: No magic numbers, all constants in constants.py
- **Constitution VII**: Real-world smoke tests required
- **Tech Stack**: No new dependencies needed (SQLite is stdlib)
- **Coding Standards**: 300-line file limit, exit codes in constants.py

---

## Scope Clarification

### Question 1: Process Model

**Context**: Codebase is fully synchronous. Need background execution without async refactor.

**Question**: How should background tasks execute?

**Options Presented**:
- A (Recommended): Subprocess spawn with `--_worker` hidden flag
- B: multiprocessing.Process
- C: asyncio background (major refactor)

**User Answer**: Subprocess spawn (Recommended)

---

### Question 2: Task ID Format

**Context**: Phase doc says UUID but shorter IDs are more CLI-friendly.

**Question**: What format for task IDs?

**Options Presented**:
- A (Recommended): Short hex (8 chars from UUID4)
- B: Full UUID
- C: Sequential integer

**User Answer**: Short hex (8 chars)

---

### Question 3: Log Location

**Context**: Task DB at `~/.to-markdown/tasks.db`, need a place for worker logs.

**Question**: Where to store task logs?

**Options Presented**:
- A (Recommended): `~/.to-markdown/logs/<task-id>.log`
- B: Store in SQLite TEXT column
- C: Temp directory

**User Answer**: `~/.to-markdown/logs/` (Recommended)

---

### Question 4: CLI Integration

**Context**: Current CLI is single-command Typer app. Adding subcommands would break UX.

**Question**: How to integrate --status and --cancel?

**Options Presented**:
- A (Recommended): Keep flat + special flags (`--status`, `--cancel` as Optional[str])
- B: Subcommands (breaks `to-markdown file.pdf`)
- C: Hybrid (complex Typer setup)

**User Answer**: Keep flat + special flags (Recommended)

---

### Question 5: Task Retention

**Question**: Default retention period for completed/failed tasks?

**Options Presented**:
- A (Recommended): 24 hours
- B: 7 days
- C: No auto-cleanup

**User Answer**: 24 hours

---

### Confirmed Understanding

**What the user wants to achieve**:
Add background processing so long-running conversions don't block the terminal or AI agent.
Users start a conversion with `--background`, get a task ID, and check back later with
`--status`. AI agents use MCP tools (`start_conversion`, `get_task_status`) for the same
fire-and-forget pattern.

**How it relates to existing code**:
- New module `core/tasks.py` manages task lifecycle with SQLite store
- New module `core/worker.py` handles subprocess spawning and signal handling
- CLI `main()` gains `--background`, `--status`, `--cancel` flags (no subcommand refactor)
- MCP gains 4 new tools following existing handler pattern
- Pipeline and batch modules are unchanged - worker process calls them directly

**Key constraints and requirements**:
- SQLite for storage (stdlib, zero-config)
- Subprocess spawn via `subprocess.Popen` with terminal detach
- Short hex task IDs (8 chars from UUID4)
- Log files at `~/.to-markdown/logs/<task-id>.log`
- 24-hour default retention with auto-cleanup
- No new dependencies (SQLite is stdlib)

**Technical approach**:
1. `core/tasks.py` - TaskStore class with SQLite CRUD + Task dataclass
2. `core/worker.py` - spawn_worker() for background execution, signal handling
3. CLI adds `--background`, `--status <id|all>`, `--cancel <id>` flags
4. MCP adds `start_conversion`, `get_task_status`, `list_tasks`, `cancel_task` tools

**User confirmed**: Yes - 2026-02-26

---

## Recommendations for SPECIFY

### Should Include in Spec

- Task dataclass with all status fields (pending/running/completed/failed)
- SQLite schema for tasks table
- Worker subprocess lifecycle (spawn, PID tracking, signal handling, log capture)
- CLI flag behavior for --background, --status, --cancel
- MCP tool signatures and response envelopes
- Auto-cleanup on CLI startup
- Graceful handling of orphan processes (worker crashed, PID stale)

### Should Exclude from Spec (Non-Goals)

- Async refactor of existing pipeline
- Task queuing or scheduling (no cron, no priority queue)
- Remote/distributed task execution
- Web UI for task monitoring
- Task dependencies or chaining
- Persistent daemon process (each --background spawns one worker, not a long-running server)

### Potential Risks

- **Orphan processes**: Worker crashes without updating DB. Mitigation: PID check on status.
- **SQLite locking**: Concurrent writes from multiple workers. Mitigation: WAL mode, short
  transactions.
- **Platform differences**: subprocess detach differs macOS vs Linux. Mitigation: use
  `start_new_session=True` (POSIX) for process group separation.
- **File limit**: Many concurrent background tasks could exhaust file descriptors.
  Mitigation: document reasonable concurrency limits.
