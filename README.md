# to-markdown

[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/wiseyoda/to-markdown/actions/workflows/ci.yml/badge.svg)](https://github.com/wiseyoda/to-markdown/actions/workflows/ci.yml)

CLI file-to-Markdown converter optimized for LLM consumption. Convert PDF, DOCX,
PPTX, XLSX, HTML, images, and 70+ other formats into clean Markdown with YAML
frontmatter metadata.

## What It Does

to-markdown wraps [Kreuzberg](https://github.com/Goldziher/kreuzberg) (Rust-based
extraction for 76+ formats) with an LLM-optimized output layer:

- **YAML frontmatter** with document metadata (title, author, pages, format, timestamps)
- **Smart features** via Google Gemini — automatic content cleaning, document summaries,
  and image descriptions
- **Content sanitization** strips non-visible Unicode (zero-width, control, directional
  chars) to prevent prompt injection
- **Batch processing** with glob patterns, progress bars, and partial-success reporting
- **Background processing** for large files via detached subprocesses
- **MCP server** for AI agent integration (Claude Code, Claude Desktop, Codex CLI,
  Gemini CLI)

## Quick Start

```bash
git clone https://github.com/wiseyoda/to-markdown.git
cd to-markdown
uv sync                   # Core only
uv run to-markdown document.pdf
```

For step-by-step installation (including non-technical users), see **[INSTALL.md](INSTALL.md)**.

To enable smart features (cleaning, summaries, image descriptions):

```bash
uv sync --extra llm
export GEMINI_API_KEY=your-key-here
```

## Usage

### Single File

```bash
uv run to-markdown document.pdf            # Creates document.md
uv run to-markdown document.pdf -o output/ # Custom output path
uv run to-markdown document.pdf --force    # Overwrite existing
uv run to-markdown document.pdf -v         # Verbose output
uv run to-markdown document.pdf -q         # Quiet (errors only)
```

### Batch Processing

```bash
uv run to-markdown docs/                   # All files in directory (recursive)
uv run to-markdown docs/ --no-recursive    # Top-level only
uv run to-markdown "docs/*.pdf"            # Glob pattern
uv run to-markdown docs/ -o output/        # Output to different directory
uv run to-markdown docs/ --fail-fast       # Stop on first error
```

### Smart Features

Content cleaning runs automatically when `GEMINI_API_KEY` is set. Use `--no-clean`
to disable.

```bash
uv run to-markdown doc.pdf --summary       # Generate document summary
uv run to-markdown doc.pdf --images        # Describe images via LLM vision
uv run to-markdown doc.pdf --no-clean      # Disable automatic cleaning
uv run to-markdown doc.pdf --no-sanitize   # Disable Unicode sanitization
```

### Background Processing

```bash
uv run to-markdown large.pdf --bg          # Returns task ID immediately
uv run to-markdown --status <task-id>      # Check task status
uv run to-markdown --status all            # List all recent tasks
uv run to-markdown --cancel <task-id>      # Cancel a running task
```

### Output Format

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
| 1 | Error (file not found, extraction failed) |
| 2 | Unsupported file format |
| 3 | Output file already exists (use `--force`) |
| 4 | Partial success (batch: some files failed) |

## AI Agent Integration (MCP)

to-markdown includes an MCP server for AI agent integration via stdio transport.

**Available tools**: `convert_file`, `convert_batch`, `start_conversion`,
`get_task_status`, `list_tasks`, `cancel_task`, `list_formats`, `get_status`

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

### Codex CLI / Gemini CLI

See [MCP setup docs](https://modelcontextprotocol.io/) for your tool's configuration
format. The server command is the same:

```bash
uv --directory /path/to/to-markdown run --extra mcp python -m to_markdown.mcp
```

## Development

```bash
uv sync --all-extras          # Install everything (dev, llm, mcp)
uv run pytest                 # Run tests (505+)
uv run ruff check             # Lint
uv run ruff format --check    # Format check
uv run pytest --cov=to_markdown --cov-fail-under=80  # Coverage
```

## License

[MIT](LICENSE)
