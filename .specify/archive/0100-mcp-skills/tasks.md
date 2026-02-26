# Tasks: Phase 0100 - MCP Server & AI Agent Skills

## Section 1: Pipeline Foundation

### T001: Add MCP constants to constants.py
- **Files**: `src/to_markdown/core/constants.py`
- **Action**: Add constants:
  - `MAX_MCP_OUTPUT_CHARS = 80_000` (~20K tokens, safe for agent limits)
  - `MCP_SERVER_NAME = "to-markdown"`
  - `MCP_SERVER_INSTRUCTIONS` (string describing the server for agent discovery)
  - `SUPPORTED_FORMATS_DESCRIPTION` (static string listing Kreuzberg's supported formats
    derived from Kreuzberg docs - no runtime API exists for querying formats)
- **Test**: Verify constants importable
- **Blocked by**: None

### T002: Add convert_to_string() to pipeline.py
- **Files**: `src/to_markdown/core/pipeline.py`
- **Action**: Refactor `convert_file()` to extract shared logic into `_build_content()`
  internal function. `_build_content` signature:
  ```python
  def _build_content(
      input_path: Path,
      *,
      clean: bool = False,
      summary: bool = False,
      images: bool = False,
  ) -> str:
  ```
  This does: extract -> frontmatter -> [clean] -> [images] -> [summary] -> assemble string.
  `convert_file()` calls `_build_content()` then writes to disk.
  Add public `convert_to_string()` that calls `_build_content()` and returns the string:
  ```python
  def convert_to_string(
      input_path: Path,
      *,
      clean: bool = False,
      summary: bool = False,
      images: bool = False,
  ) -> str:
  ```
  `convert_to_string` validates input exists and is a file, then delegates to `_build_content`.
  No output path, no force flag, no file writing.
- **Test**: `tests/test_pipeline.py` - add tests for convert_to_string
- **Blocked by**: None

### T003: Test convert_to_string
- **Files**: `tests/test_pipeline.py`
- **Action**: Add tests:
  - Returns string with frontmatter + content
  - Works with clean/summary/images flags (mocked)
  - Raises FileNotFoundError for missing input
  - Raises UnsupportedFormatError for bad formats
  - Does NOT write any file to disk
- **Blocked by**: T002

## Section 2: MCP Server Core

### T004: Create mcp/ subpackage structure
- **Files**: `src/to_markdown/mcp/__init__.py`, `src/to_markdown/mcp/__main__.py`
- **Action**: Create package:
  - `__init__.py`: Re-export `run_server` from `server.py` for console script entry point
  - `__main__.py`: Entry point for `python -m to_markdown.mcp`. Imports and calls
    `run_server()`. Configures logging to stderr. Suppresses stdout from imported libraries
    by redirecting sys.stdout to os.devnull during server startup if needed.
- **Blocked by**: None

### T005: Implement MCP tool handlers (tools.py)
- **Files**: `src/to_markdown/mcp/tools.py`
- **Action**: Implement four tool handler functions (pure business logic, no MCP
  decorators). All return structured text responses (R14) not just raw content:
  - `handle_convert_file(file_path, clean, summary, images) -> str`:
    Calls `convert_to_string()`. Returns structured response with source path, detected
    format, char count, any warnings, then markdown content. Truncates content at
    MAX_MCP_OUTPUT_CHARS with note about output file path if exceeded.
  - `handle_convert_batch(directory_path, recursive, clean, summary, images) -> str`:
    Calls `discover_files(Path(directory_path), recursive=recursive)` then
    `convert_batch(files, ...)`. The `recursive` param maps to `discover_files()`'s
    existing `recursive` kwarg (default True). Returns structured summary with per-file
    results.
  - `handle_list_formats() -> str`: Returns `SUPPORTED_FORMATS_DESCRIPTION` constant
    (static, derived from Kreuzberg docs since no runtime query API exists).
  - `handle_get_status() -> str`: Returns version (via `to_markdown.__version__`),
    LLM availability (check google-genai importable + GEMINI_API_KEY set), Python version.
  Each function validates inputs and raises ValueError with descriptive messages for
  invalid inputs (ToolError wrapping happens in server.py).
- **Blocked by**: T001, T002

### T006: Implement FastMCP server (server.py)
- **Files**: `src/to_markdown/mcp/server.py`
- **Action**: Create FastMCP server with:
  - `mcp = FastMCP(MCP_SERVER_NAME, instructions=MCP_SERVER_INSTRUCTIONS)`
  - Four `@mcp.tool()` decorated functions that delegate to tools.py handlers
  - Annotated parameters with `Field(description=...)` for clear agent-visible docs
  - ToolError wrapping: catch ValueError/exceptions from handlers, raise ToolError
  - `def run_server()` function called from __main__.py, runs `mcp.run(transport="stdio")`
  - Logging configured to stderr (not stdout - critical for stdio transport)
  - Ensure Rich progress bars are suppressed when called via MCP (pass `quiet=True`
    to convert_batch, verify convert_to_string doesn't trigger Rich output)
  - `mask_error_details=True` to prevent stack trace leakage
- **Blocked by**: T004, T005

## Section 3: Configuration & Integration

### T007: Add [mcp] optional extra to pyproject.toml
- **Files**: `pyproject.toml`
- **Action**: Add `[mcp]` optional dependency group with `mcp>=1.26,<2`. Add
  `to-markdown-mcp` console script entry point pointing to
  `to_markdown.mcp.server:run_server`.
- **Blocked by**: None

### T008: Create .mcp.json for Claude Code
- **Files**: `.mcp.json`
- **Action**: Create project-scope MCP config (committed to version control for automatic
  discovery by Claude Code users who clone the repo):
  ```json
  {
    "mcpServers": {
      "to-markdown": {
        "command": "uv",
        "args": ["--directory", ".", "run", "--extra", "mcp", "python", "-m", "to_markdown.mcp"]
      }
    }
  }
  ```
- **Blocked by**: T006

### T009: Update README with AI Agent Integration section
- **Files**: `README.md`
- **Action**: Add section after "Development" covering:
  - What MCP is (one sentence)
  - Claude Code setup (auto via .mcp.json, or manual `claude mcp add`)
  - Claude Desktop setup (config file path + JSON)
  - OpenAI Codex CLI setup (config.toml)
  - Google Gemini CLI setup (settings.json)
  - Available tools with brief descriptions
  - Example: how an agent would use convert_file
- **Blocked by**: T008

## Section 4: Tests

### T010: Test MCP tool handlers
- **Files**: `tests/test_mcp_tools.py`
- **Action**: Unit tests for tools.py handlers with mocked pipeline:
  - `handle_convert_file`: success with structured response, file not found, unsupported
    format, output truncation when content exceeds MAX_MCP_OUTPUT_CHARS
  - `handle_convert_batch`: success with mixed results, empty directory, structured
    per-file results
  - `handle_list_formats`: returns expected format info string
  - `handle_get_status`: returns version and LLM availability
  - Invalid parameter types produce clear ValueError messages
- **Blocked by**: T005

### T011: Test MCP server registration and stdout safety
- **Files**: `tests/test_mcp_server.py`
- **Action**: Tests for server.py:
  - Server creates successfully
  - All four tools are registered with correct names
  - Tool parameter schemas match expected types (correct required/optional params)
  - ToolError is raised for handler exceptions (not raw exceptions)
  - Verify no stdout output during tool execution (capture stdout, assert empty)
  - Server module can be imported; graceful ImportError if mcp package missing
- **Blocked by**: T006

### T012: Lint, format, and smoke test
- **Files**: All modified files
- **Action**: Run `uv run ruff check`, `uv run ruff format --check`, `uv run pytest`.
  Fix any issues. Verify `uv run python -m to_markdown.mcp` starts without error
  (quick manual check).
- **Blocked by**: T010, T011

## Section 5: Documentation Sync

### T013: Update coding-standards.md with mcp/ directory
- **Files**: `.specify/memory/coding-standards.md`
- **Action**: Add `mcp/` directory to project structure section with file descriptions.
- **Blocked by**: T006

### T014: Update tech-stack.md with mcp dependency
- **Files**: `.specify/memory/tech-stack.md`
- **Action**: Add mcp package to tech stack table. Update distribution section to
  note MCP server availability. Record decisions D-63 through D-70.
- **Blocked by**: T007

### T015: Record decisions in decisions.md
- **Files**: `.specify/discovery/decisions.md`
- **Action**: Record decisions D-63 through D-70 from the plan.
- **Blocked by**: T006

### T016: Write testing instructions
- **Files**: `README.md` (How to Test section)
- **Action**: Add "How to Test (Phase 0100: MCP Server)" section with:
  - How to install MCP extra: `uv sync --extra mcp`
  - How to start the MCP server manually: `uv run python -m to_markdown.mcp`
  - How to test from Claude Code (add server, call tool)
  - Expected output for each tool
- **Blocked by**: T012
