# to-markdown

CLI file-to-Markdown converter optimized for LLM consumption. Wraps
[Kreuzberg](https://github.com/Goldziher/kreuzberg) (76+ formats) with YAML
frontmatter and a polished CLI.

## Install

```bash
uv sync
```

## Usage

### Single File

```bash
# Convert a file (creates file.md next to the input)
uv run to-markdown document.pdf

# Custom output path
uv run to-markdown document.pdf -o output/

# Overwrite existing output
uv run to-markdown document.pdf --force

# Verbose output
uv run to-markdown document.pdf -v

# Quiet mode (errors only)
uv run to-markdown document.pdf -q
```

### Batch Processing

```bash
# Convert all supported files in a directory (recursive by default)
uv run to-markdown docs/

# Non-recursive (top-level files only)
uv run to-markdown docs/ --no-recursive

# Convert files matching a glob pattern
uv run to-markdown "docs/*.pdf"

# Output to a different directory (mirrors input structure)
uv run to-markdown docs/ -o output/

# Stop on first error
uv run to-markdown docs/ --fail-fast

# Force overwrite all existing output files
uv run to-markdown docs/ --force
```

Batch mode shows a progress bar and prints a summary when done:

```
Converted 8 file(s), 2 skipped, 1 failed
```

### Smart Features

Requires `GEMINI_API_KEY` (install with `uv sync --extra llm`):

```bash
# Fix extraction artifacts via LLM
uv run to-markdown document.pdf --clean

# Generate document summary
uv run to-markdown document.pdf --summary

# Describe images via LLM vision
uv run to-markdown document.pdf --images

# Smart features work with batch mode too
uv run to-markdown docs/ --summary --clean
```

### Output

Creates a `.md` file with YAML frontmatter and extracted content:

```markdown
---
title: Example Document
author: Jane Doe
pages: 12
format: pdf
extracted_at: '2026-02-25T12:00:00Z'
---

Extracted document content in Markdown...
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (file not found, extraction failed, all files failed) |
| 2 | Unsupported file format (single file only) |
| 3 | Output file already exists (use `--force`) |
| 4 | Partial success (batch: some files succeeded, some failed) |

## AI Agent Integration (MCP)

to-markdown includes an MCP (Model Context Protocol) server so AI agents can
invoke file conversion programmatically.

### Available Tools

| Tool | Description |
|------|-------------|
| `convert_file` | Convert a single file to Markdown |
| `convert_batch` | Convert all files in a directory |
| `list_formats` | List supported file formats |
| `get_status` | Check version and feature availability |

### Claude Code

Auto-detected via `.mcp.json` in this repo. Or add manually:

```bash
claude mcp add to-markdown -- \
  uv --directory /path/to/to-markdown run --extra mcp python -m to_markdown.mcp
```

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "to-markdown": {
      "command": "uv",
      "args": ["--directory", "/path/to/to-markdown", "run", "--extra", "mcp",
               "python", "-m", "to_markdown.mcp"]
    }
  }
}
```

### OpenAI Codex CLI

Add to `.codex/config.toml` or `~/.codex/config.toml`:

```toml
[mcp_servers.to-markdown]
command = "uv"
args = ["--directory", "/path/to/to-markdown", "run", "--extra", "mcp",
        "python", "-m", "to_markdown.mcp"]
```

### Google Gemini CLI

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "to-markdown": {
      "command": "uv",
      "args": ["--directory", "/path/to/to-markdown", "run", "--extra", "mcp",
               "python", "-m", "to_markdown.mcp"]
    }
  }
}
```

## How to Test (Phase 0100: MCP Server)

1. Install MCP extra:
   ```bash
   uv sync --extra mcp
   ```

2. Verify the server starts:
   ```bash
   uv run python -m to_markdown.mcp &
   # Should start without errors (it waits for stdio input)
   kill %1
   ```

3. Add server to Claude Code:
   ```bash
   claude mcp add to-markdown -- \
     uv --directory $(pwd) run --extra mcp python -m to_markdown.mcp
   ```

4. Test from Claude Code (in a new session):
   - Ask: "Use to-markdown to convert tests/fixtures/pdf/basic.pdf"
   - Expected: Agent calls `convert_file` tool, returns markdown with frontmatter

5. Test list_formats:
   - Ask: "What formats does to-markdown support?"
   - Expected: Agent calls `list_formats` tool, returns format categories

6. Test get_status:
   - Ask: "What's the status of to-markdown?"
   - Expected: Agent calls `get_status`, shows version and LLM availability

## Development

```bash
uv sync --all-extras
uv run pytest
uv run ruff check
uv run ruff format --check
```
