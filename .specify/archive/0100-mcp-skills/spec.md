# Specification: Phase 0100 - MCP Server & AI Agent Skills

## Overview

Add an MCP (Model Context Protocol) server so that Claude Code, Codex, Gemini CLI, and
other AI agents can invoke to-markdown's file conversion programmatically via standardized
tool calls over stdio transport.

## Requirements

### R1: MCP Server Module
The project must provide an MCP server as a Python subpackage at `src/to_markdown/mcp/`
that can be run via `python -m to_markdown.mcp` or `uv run python -m to_markdown.mcp`.

### R2: convert_file Tool
The MCP server must expose a `convert_file` tool that accepts a file path and optional
flags (force, clean, summary, images), converts the file to markdown, and returns the
markdown content directly as a string response.

### R3: convert_batch Tool
The MCP server must expose a `convert_batch` tool that accepts a directory path or glob
pattern and optional flags, converts matching files, and returns a structured summary
(succeeded count, failed files with errors, skipped files with reasons).

### R4: list_formats Tool
The MCP server must expose a `list_formats` tool that returns a description of supported
file formats (based on Kreuzberg's capabilities).

### R5: get_status Tool
The MCP server must expose a `get_status` tool that returns the tool version, whether
LLM features are available (google-genai installed + API key configured), and basic
system information.

### R6: Pipeline String Output
A new function `convert_to_string()` must be added to `core/pipeline.py` that performs
the same conversion as `convert_file()` but returns the markdown content as a string
instead of writing to disk. This avoids unnecessary file I/O for the MCP use case.

### R7: Error Handling
All MCP tools must translate to-markdown exceptions into `ToolError` responses with
clear, actionable error messages. Unhandled exceptions must not leak stack traces.

### R8: Claude Code Configuration
The project must include a `.mcp.json` file at the project root for Claude Code
project-scope MCP server discovery.

### R9: Agent Configuration Documentation
The README must include an "AI Agent Integration" section documenting MCP server setup
for Claude Code, Claude Desktop, OpenAI Codex CLI, and Google Gemini CLI.

### R10: Output Size Safety
For single-file conversions, if the output exceeds a configurable token limit
(MAX_MCP_OUTPUT_CHARS constant), the tool must write the full output to a file and return
a truncated preview with the output file path.

### R11: No stdout Leakage
The MCP server must ensure no library (Rich, Typer, Kreuzberg) writes to stdout, which
would corrupt the stdio JSON-RPC transport. Logging must go to stderr. The server entry
point must suppress stdout from any imported library.

### R14: Structured Response Envelope
MCP tool responses must include structured metadata alongside content:
- `convert_file`: Response includes source path, detected format, word/char count,
  warnings (if any), and then the markdown content
- `convert_batch`: Response includes per-file results (succeeded with paths, failed
  with error messages, skipped with reasons), plus aggregate counts
- `list_formats`: Structured list of format categories and extensions
- `get_status`: Structured key-value pairs for version, LLM availability, etc.

### R12: Optional Dependency
The `mcp` package must be an optional dependency under a `[mcp]` extra in pyproject.toml,
so core CLI functionality is unaffected.

### R13: Tests
All MCP tool handlers must have unit tests with mocked pipeline calls. Tests must cover
success paths, error paths (missing file, unsupported format, missing API key), and
output size truncation.

## Out of Scope

- HTTP/SSE transport (stdio only for this phase)
- Background/async task processing (Phase 0110)
- MCP resources or prompts (tools only)
- Claude Code skill definitions (MCP tools provide equivalent agent access)
- Publishing to MCP registries

## Acceptance Criteria

1. `uv run python -m to_markdown.mcp` starts the MCP server on stdio
2. Claude Code can discover and call `convert_file` via `.mcp.json`
3. `convert_file` returns markdown content for a valid file
4. `convert_batch` returns structured results for a directory
5. `list_formats` returns supported format information
6. `get_status` returns version and LLM availability
7. Errors return `ToolError` with clear messages
8. All tests pass (`uv run pytest`)
9. Lint clean (`uv run ruff check`)
