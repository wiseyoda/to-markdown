# Smoke Test: Background Processing (Phase 0110)

## Prerequisites

```bash
uv sync --all-extras
```

## Test 1: Background Single File

```bash
# Create a test file
echo "Hello background world" > /tmp/bg-test.txt

# Start background conversion
uv run to-markdown /tmp/bg-test.txt --background
# Expected: prints a hex task ID (e.g., a1b2c3d4)

# Check status (use the task ID from above)
uv run to-markdown --status <task-id>
# Expected: shows "completed" with output path

# Verify output exists
cat /tmp/bg-test.md
# Expected: markdown with YAML frontmatter
```

## Test 2: Status All

```bash
# List all tasks
uv run to-markdown --status all
# Expected: table with at least the task from Test 1
```

## Test 3: Cancel

```bash
# Start a background conversion
TASK_ID=$(uv run to-markdown /tmp/bg-test.txt --bg --force)

# Cancel it (may already be completed for small files)
uv run to-markdown --cancel $TASK_ID
# Expected: "Cancelled task <id>" or "Task <id> already completed"
```

## Test 4: Background Batch

```bash
# Create test directory
mkdir -p /tmp/bg-batch
echo "File A" > /tmp/bg-batch/a.txt
echo "File B" > /tmp/bg-batch/b.txt

# Start background batch
uv run to-markdown /tmp/bg-batch --bg
# Expected: prints task ID

# Check status
uv run to-markdown --status <task-id>
# Expected: shows "completed"
```

## Test 5: Short Flag

```bash
uv run to-markdown /tmp/bg-test.txt --bg --force
# Expected: same as --background
```

## Test 6: MCP Background Tools

```bash
# Ensure MCP server is registered
claude mcp add to-markdown -- \
  uv --directory $(pwd) run --extra mcp python -m to_markdown.mcp

# In a new Claude Code session:
# Ask: "Use to-markdown start_conversion to convert /tmp/bg-test.txt"
# Expected: Agent calls start_conversion, returns task ID

# Ask: "Check the status of task <id>"
# Expected: Agent calls get_task_status, shows completed

# Ask: "List all to-markdown tasks"
# Expected: Agent calls list_tasks, shows recent tasks
```

## Test 7: Mutual Exclusivity

```bash
# These should all fail with error
uv run to-markdown /tmp/bg-test.txt --background --status all
uv run to-markdown /tmp/bg-test.txt --background --cancel abc
uv run to-markdown /tmp/bg-test.txt --status all --cancel abc
# Expected: error about mutually exclusive flags
```

## Cleanup

```bash
rm -f /tmp/bg-test.txt /tmp/bg-test.md
rm -rf /tmp/bg-batch
```
