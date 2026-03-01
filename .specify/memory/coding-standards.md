# Coding Standards

> **Agents**: Reference this document for code style, patterns, and conventions.

## Python Style

- **Formatter/Linter**: ruff (format + check)
- **Line length**: 100 characters
- **Quotes**: Double quotes (ruff default)
- **Type hints**: Required on all public function signatures
- **Docstrings**: Google style, only on public API and non-obvious logic
- **Max file length**: 300 lines (hard limit, excluding test files). Split if exceeded.

## Project Structure

```
to-markdown/
  src/
    to_markdown/
      __init__.py
      cli.py              # Typer CLI entry point
      core/
        __init__.py
        extraction.py      # Kreuzberg adapter interface
        frontmatter.py     # YAML frontmatter composition from metadata
        content_builder.py # Build markdown content (sync + async; used by pipeline)
        pipeline.py        # Kreuzberg extract -> frontmatter -> async LLM -> output
        constants.py       # ALL project constants (single source of truth)
        batch.py           # Batch processing: file discovery + multi-file conversion
        sanitize.py        # Content sanitization: strip non-visible Unicode chars
        cli_helpers.py     # CLI helper functions (extracted from cli.py)
        background.py      # CLI handlers for --background, --status, --cancel
        display.py         # Batch display and progress bar
        tasks.py           # SQLite task store for background processing
        worker.py          # Background worker subprocess execution
        setup.py           # Configuration wizard for --setup
      smart/               # LLM-powered features (optional)
        __init__.py
        llm.py             # Gemini client wrapper (sync + async)
        clean.py           # --clean flag: LLM artifact repair (sync + async)
        summary.py         # --summary flag: Gemini document summarization (sync + async)
        images.py          # --images flag: Gemini vision image description (sync + async)
      mcp/                 # MCP server for AI agent integration (optional)
        __init__.py
        __main__.py        # Entry point: python -m to_markdown.mcp
        server.py          # FastMCP server with tool definitions
        tools.py           # Tool handler implementations
        background_tools.py # MCP background task handlers
  tests/
    test_batch.py          # Batch processing tests
    fixtures/              # Test input files per format
      pdf/
      docx/
      pptx/
      xlsx/
      html/
      images/
    __snapshots__/         # syrupy golden file snapshots
    test_cli.py
    test_extraction.py     # Kreuzberg adapter tests
    test_frontmatter.py
    test_pipeline.py
    test_formats/          # Per-format quality tests
      test_pdf.py
      test_docx.py
      test_pptx.py
      test_xlsx.py
      test_html.py
      test_images.py
  pyproject.toml
  .env.example
  .gitignore
```

## Patterns

### Kreuzberg Adapter

All document extraction goes through the Kreuzberg adapter (`core/extraction.py`).
This isolates the project from Kreuzberg API changes.

```python
# core/extraction.py - thin adapter around Kreuzberg
from kreuzberg import extract_file_sync, ExtractionConfig

def extract(file_path: Path) -> ExtractionResult:
    """Extract content and metadata from a file via Kreuzberg."""
    result = extract_file_sync(str(file_path), config=ExtractionConfig(
        output_format="markdown",
        enable_quality_processing=True,
    ))
    return ExtractionResult(
        content=result.content,
        metadata=result.metadata,
        tables=result.tables,
    )
```

### Pipeline Flow

```
Input File -> Kreuzberg extract (via adapter) -> content + metadata
           -> Sanitize content (strip non-visible Unicode, on by default)
           -> Compose YAML frontmatter from metadata (includes sanitized: true if modified)
           -> Async LLM features: clean + images concurrent, then summary
           -> Assemble final .md (frontmatter + content)
           -> Write output file
```

### Async Pattern (smart/ modules)

Each smart module has both sync and async versions:
- `generate()` / `generate_async()` in llm.py
- `clean_content()` / `clean_content_async()` in clean.py
- `summarize_content()` / `summarize_content_async()` in summary.py
- `describe_images()` / `describe_images_async()` in images.py

Pipeline uses async internally via `build_content_async()` in `core/content_builder.py` with
`asyncio.gather()`:
- Clean + images run concurrently (independent data streams)
- Summary runs after clean completes (depends on cleaned content)
- `asyncio.Semaphore(PARALLEL_LLM_MAX_CONCURRENCY)` bounds concurrent API calls
- Single `asyncio.run()` boundary in `build_content()` — public API stays synchronous

### Frontmatter Composition

YAML frontmatter is composed from Kreuzberg's structured metadata object:
- Document metadata: title, author, created, pages, format, words
- Extraction metadata: extracted_at
- Only include fields that have values (skip None/empty)
- Structured as YAML between `---` delimiters at the top of the .md file

### No Magic Numbers - Single Constants File

Every numeric literal must be a named constant. No exceptions.

**All constants live in `src/to_markdown/core/constants.py`** - this is the single source
of truth. Never define constants inline in other modules. If you need a value, import it
from constants.py. If it doesn't exist yet, add it there.

```python
# BAD - constant defined in the module that uses it
MAX_FILE_SIZE_BYTES = 1_048_576
if len(content) > MAX_FILE_SIZE_BYTES:
    raise FileTooLargeError(...)

# GOOD - import from the one constants file
from to_markdown.core.constants import MAX_FILE_SIZE_BYTES
if len(content) > MAX_FILE_SIZE_BYTES:
    raise FileTooLargeError(...)
```

The constants file should be organized by category:

```python
# src/to_markdown/core/constants.py

# --- File Processing ---
MAX_FILE_SIZE_BYTES = 1_048_576 * 100  # 100 MB
READ_BUFFER_SIZE = 8_192  # 8 KB

# --- Timeouts ---
LLM_REQUEST_TIMEOUT_SECONDS = 30
OCR_TIMEOUT_SECONDS = 60

# --- CLI Defaults ---
DEFAULT_OUTPUT_EXTENSION = ".md"

# --- LLM ---
GEMINI_MODEL_NAME = "gemini-2.5-flash"
MAX_SUMMARY_TOKENS = 500
```

Applies to: timeouts, thresholds, retry counts, buffer sizes, indices, dimensions,
model names, default values - anything that isn't 0 or 1 in a trivially obvious context.

### No Duplication (DRY)

If two functions do the same thing, refactor immediately. When in doubt, refactor.

- Before writing a new function, check if similar logic exists
- Extract shared logic into a common helper when you see the second instance
- This applies across modules too - shared utilities go in `core/`

### Fix What You See

When working in any file, if you encounter a bug, code smell, missing type hint,
unclear variable name, or anything that doesn't meet these standards - fix it now.

- No "this isn't related to my changes"
- No "this is good enough"
- If you're in the file, you own it
- Include opportunistic fixes in the same commit with a note in the message

### Exit Codes

Defined in `core/constants.py`. Every CLI exit must use these:

| Code | Constant | Meaning |
|------|----------|---------|
| 0 | `EXIT_SUCCESS` | Conversion completed successfully |
| 1 | `EXIT_ERROR` | General error (conversion failed, file unreadable, etc.) |
| 2 | `EXIT_UNSUPPORTED` | Unsupported file format |
| 3 | `EXIT_ALREADY_EXISTS` | Output file exists and --force not passed |
| 4 | `EXIT_PARTIAL` | Batch: some files succeeded, some failed |

### Error Handling

- Use explicit exceptions, not silent failures
- Converter errors should be caught and reported clearly
- Unsupported format: clear error message with supported formats list
- Corrupted/unreadable file: graceful failure with description of what went wrong

### Overwrite Protection

When the output .md file already exists, the tool must error by default. Overwriting
requires an explicit `--force` flag. This prevents accidental data loss.

### CLI Flags (Standard)

Every build of the CLI must include these baseline flags:

- `--version` - print version and exit
- `--verbose` / `-v` - detailed output (converter selected, page count, extraction stats)
- `--quiet` / `-q` - suppress all non-error output (for piping/scripting)
- `--force` / `-f` - overwrite existing output file
- `-o <path>` - custom output path (file or directory)

### Logging

Use Python's `logging` module. Levels map to CLI verbosity:

- `--quiet`: only ERROR and above
- default: WARNING and above (e.g., "3 images skipped - use --images to describe them")
- `--verbose`: INFO and above (converter selection, page counts, timing)
- DEBUG: enabled via `--verbose --verbose` or `-vv` (full extraction details)

### CLI Output

- YAML frontmatter for document metadata
- Clean Markdown body with proper heading hierarchy
- Tables rendered as Markdown tables (pipe syntax)
- Structured data in fenced code blocks (```json, ```csv)
- Images referenced with alt text; described if --images flag used

## Naming Conventions

- **Files**: snake_case.py
- **Classes**: PascalCase
- **Functions/methods**: snake_case
- **Constants**: UPPER_SNAKE_CASE
- **CLI commands**: kebab-case (handled by Typer)

## Import Order

1. Standard library
2. Third-party packages
3. Local imports

(Enforced by ruff)

## Documentation Sync

Code and docs must never drift. When any change affects behavior:

- Update Typer docstrings / argument help text so `--help` stays accurate
- Update README usage examples
- Update memory docs (tech-stack, coding-standards, etc.) if architecture changed
- All doc updates go in the same commit as the code change

---
*Version: 3.0.0 | Last Updated: 2026-02-27*
