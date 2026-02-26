# Plan: Phase 0100 - MCP Server & AI Agent Skills

## Architecture

### New Module: `src/to_markdown/mcp/`

```
src/to_markdown/
  mcp/
    __init__.py        # Package marker with __main__ support
    __main__.py        # Entry point: python -m to_markdown.mcp
    server.py          # FastMCP server with tool definitions
    tools.py           # Tool handler implementations (business logic)
```

### Modified Files

| File | Change |
|------|--------|
| `src/to_markdown/core/pipeline.py` | Add `convert_to_string()` function |
| `src/to_markdown/core/constants.py` | Add MCP-related constants |
| `pyproject.toml` | Add `[mcp]` optional extra, add `to-markdown-mcp` script |
| `.mcp.json` | New file - Claude Code MCP config |
| `README.md` | Add AI Agent Integration section |

### New Test Files

| File | Purpose |
|------|---------|
| `tests/test_mcp_tools.py` | Unit tests for MCP tool handlers |
| `tests/test_mcp_server.py` | Server initialization and tool registration |
| `tests/test_convert_to_string.py` | Pipeline string output tests |

## Technical Decisions

### D-63: Official mcp package over standalone fastmcp
The official `mcp` package (by Anthropic, v1.26.0) includes FastMCP and is the reference
implementation. Standalone `fastmcp` v3.0 has extra features but adds a separate dependency.
Official package is more stable and better documented for our agents.

### D-64: stdio transport only
All four target agents (Claude Code, Claude Desktop, Codex CLI, Gemini CLI) support stdio.
It requires no persistent server process - the agent spawns the server on demand.

### D-65: Pin mcp>=1.26,<2
The mcp package v2 is in pre-alpha. Pinning to v1.x avoids breaking changes.

### D-66: Return content directly for single files
MCP `convert_file` returns markdown content as a string (not a file path). This is more
useful for agents who want to reason about the content. For large files, truncate with
a pointer to the full output file.

### D-67: Always force=True for MCP single-file conversion
MCP tools can't prompt for interactive confirmation. For `convert_file`, we skip file
writing entirely (use `convert_to_string`). For `convert_batch`, we use `force=True`
since the agent explicitly requested conversion.

### D-68: convert_to_string() in pipeline.py
New function that does extract -> frontmatter -> [smart features] -> assemble, returning
the string. Shares 95% of logic with `convert_file()` via a shared `_build_content()`
internal function.

### D-69: mcp/ subpackage (not single file)
Follows the same pattern as `smart/` - subpackage with clear module boundaries.
Separates server setup (server.py) from tool logic (tools.py).

### D-70: [mcp] optional extra
The `mcp` dependency is only needed if running the MCP server. Core CLI and smart
features work without it. Pattern matches `[llm]` extras.

## Implementation Order

1. **Constants & pipeline changes** (foundation)
   - Add MCP constants to constants.py
   - Add `convert_to_string()` to pipeline.py
   - Tests for convert_to_string

2. **MCP server & tools** (core feature)
   - Create mcp/ subpackage
   - Implement tool handlers in tools.py
   - Set up FastMCP server in server.py
   - __main__.py entry point

3. **Configuration & documentation** (integration)
   - .mcp.json for Claude Code
   - pyproject.toml updates
   - README agent integration section

4. **Tests** (verification)
   - Tool handler unit tests
   - Server registration tests
   - Error path tests

## Risks

1. **Python 3.14 + mcp SDK**: The mcp package lists support for 3.10-3.13. May need
   workaround if 3.14 causes issues. Mitigation: test early, file issue if needed.

2. **stdout leakage**: Rich progress bars default to stderr but should be verified.
   Kreuzberg's internal logging needs checking. Mitigation: redirect stdout in server
   startup if needed.

3. **Large output truncation**: Need to balance between returning useful content and
   staying within agent token limits. Mitigation: configurable MAX_MCP_OUTPUT_CHARS
   constant with sensible default.

## Constitution Compliance

- **Principle I (Completeness)**: MCP tools expose all conversion options available in CLI
- **Principle II (Magic Defaults)**: Tools work with zero optional params; smart features opt-in
- **Principle III (Kreuzberg Wrapper)**: MCP wraps the same pipeline, no new extraction logic
- **Principle IV (Simplicity)**: Thin MCP layer over existing pipeline functions
- **Principle V (Testing)**: All tool handlers have unit tests
- **Principle VI (No Sloppiness)**: Constants in constants.py, no duplication
