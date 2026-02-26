# Requirements Checklist: Background Processing

**Purpose**: Track implementation status of all requirements from spec.md
**Created**: 2026-02-26
**Feature**: [spec.md](spec.md)

## Functional Requirements

- [ ] CHK001 FR-001 Task dataclass with all required fields (id, status, input_path, output_path, command_args, created_at, started_at, completed_at, error, pid)
- [ ] CHK002 FR-002 TaskStore class with SQLite CRUD operations
- [ ] CHK003 FR-003 WAL journal mode for concurrent access
- [ ] CHK004 FR-004 Short hex task IDs (8 chars from UUID4)
- [ ] CHK005 FR-005 CLI --background/--bg flag starts detached subprocess
- [ ] CHK006 FR-006 CLI --status shows task status (single or all)
- [ ] CHK007 FR-007 CLI --cancel terminates running task
- [ ] CHK008 FR-008 Worker subprocess with start_new_session and log redirect
- [ ] CHK009 FR-009 Worker updates task status through lifecycle
- [ ] CHK010 FR-010 Worker handles SIGTERM gracefully
- [ ] CHK011 FR-011 Auto-cleanup of tasks older than 24 hours (runs at CLI startup, check_orphans first)
- [ ] CHK012 FR-012 MCP start_conversion tool
- [ ] CHK013 FR-013 MCP get_task_status tool
- [ ] CHK014 FR-014 MCP list_tasks tool
- [ ] CHK015 FR-015 MCP cancel_task tool
- [ ] CHK016 FR-016 --status displays full task details
- [ ] CHK017 FR-017 --status all shows summary table (max TASK_LIST_MAX_RESULTS, last 24h)
- [ ] CHK018 FR-018 Mutually exclusive background/status/cancel flags
- [ ] CHK019 FR-019 Worker passes through all conversion flags
- [ ] CHK020 FR-020 Orphan task detection (stale PID)
- [ ] CHK021 FR-021 MCP start_conversion supports single and batch

## Wiring Requirements

- [ ] CHK022 WR-001 tasks.py imported by cli.py (--status, --cancel, --background branches)
- [ ] CHK023 WR-002 worker.py imported by cli.py (--background, --_worker branches)
- [ ] CHK024 WR-003 Background MCP tools registered in server.py + tools.py

## Success Criteria

- [ ] CHK025 SC-001 --background returns task ID in under 1 second
- [ ] CHK026 SC-002 --status returns accurate status within 1 second
- [ ] CHK027 SC-003 Background output identical to foreground
- [ ] CHK028 SC-004 All 4 MCP background tools callable from Claude Code
- [ ] CHK029 SC-005 Orphan detection works on killed worker
- [ ] CHK030 SC-006 Auto-cleanup removes old tasks
- [ ] CHK031 SC-007 All existing tests pass (no regressions)
