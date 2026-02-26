# Discovery: Phase 0100 - MCP Server & AI Agent Skills

## Date: 2026-02-26

## Codebase Examination

### Current Architecture

to-markdown is a CLI file-to-Markdown converter wrapping Kreuzberg (Rust-based, 76+ formats).
The codebase has clean module boundaries:

- **cli.py**: Typer CLI entry point with all flags
- **core/pipeline.py**: `convert_file()` - the main conversion function
- **core/batch.py**: `convert_batch()`, `discover_files()`, `resolve_glob()`
- **core/extraction.py**: Kreuzberg adapter (`extract_file()`, `ExtractionResult`)
- **core/frontmatter.py**: YAML frontmatter composition
- **core/constants.py**: All constants (single source of truth)
- **smart/**: LLM features (clean, summary, images via Gemini)

### Key Interfaces for MCP Wrapping

**convert_file** (pipeline.py):
```python
def convert_file(
    input_path: Path,
    output_path: Path | None = None,
    *,
    force: bool = False,
    clean: bool = False,
    summary: bool = False,
    images: bool = False,
) -> Path  # Returns output file path
```

**convert_batch** (batch.py):
```python
def convert_batch(
    files: list[Path],
    output_dir: Path | None = None,
    *,
    batch_root: Path | None = None,
    force: bool = False,
    clean: bool = False,
    summary: bool = False,
    images: bool = False,
    fail_fast: bool = False,
    quiet: bool = False,
) -> BatchResult
```

**BatchResult** (batch.py):
```python
@dataclass
class BatchResult:
    succeeded: list[Path]
    failed: list[tuple[Path, str]]
    skipped: list[tuple[Path, str]]
    exit_code: int  # property
```

### Exceptions to Handle
- `FileNotFoundError`: Input file doesn't exist
- `UnsupportedFormatError(ExtractionError)`: Format not supported
- `OutputExistsError`: Output exists without --force
- `ExtractionError`: Base extraction error

### Constraints Discovered

1. **convert_file writes to disk**: Returns a Path, not content. MCP tools need to either
   read the output file back, or we need a separate code path that returns content directly.
2. **stdout corruption risk**: Rich progress bars and Typer echo write to stdout. MCP stdio
   transport uses stdout for JSON-RPC. Must ensure no stdout leakage.
3. **LLM features are optional**: `google-genai` is in `[llm]` extras. MCP server needs
   graceful handling when LLM deps aren't installed.
4. **Large output**: Claude Code has a ~25K token limit for MCP tool output. Large documents
   could exceed this. Need truncation strategy.

## Research Summary

### MCP Python SDK

- **Package**: `mcp` on PyPI (v1.26.0, by Anthropic)
- **API**: `FastMCP` from `mcp.server.fastmcp` - decorator-based tool definitions
- **Transport**: stdio (universal across all agents)
- **Error handling**: `ToolError` from `mcp.server.fastmcp.exceptions`
- **Python 3.14**: Not officially listed in classifiers but likely works (pure Python SDK)

### Agent Configuration

| Agent | Config Format | Config Location |
|-------|--------------|-----------------|
| Claude Code | JSON | `.mcp.json` (project) or `~/.claude.json` (user) |
| Claude Desktop | JSON | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| OpenAI Codex | TOML | `.codex/config.toml` or `~/.codex/config.toml` |
| Google Gemini CLI | JSON | `~/.gemini/settings.json` |

All use stdio transport with identical `command` + `args` pattern.

### Key Design Decisions

- **D-63**: Use official `mcp` package (not standalone `fastmcp`) for stability
- **D-64**: stdio transport only (universal, no persistent server needed)
- **D-65**: Pin `mcp>=1.26,<2` to avoid v2 breaking changes
- **D-66**: MCP tools return markdown content directly (not file paths) for single files;
  return structured summaries for batch operations
- **D-67**: Always `force=True` internally for MCP single-file conversion (no interactive
  overwrite prompts in MCP context)
- **D-68**: Create `convert_to_string()` helper in pipeline.py that returns content instead
  of writing to disk, to avoid unnecessary I/O for MCP use case
- **D-69**: MCP server lives at `src/to_markdown/mcp/server.py` as a subpackage (consistent
  with smart/ pattern), runnable via `python -m to_markdown.mcp`
- **D-70**: Add `[mcp]` optional extra in pyproject.toml for the mcp dependency
