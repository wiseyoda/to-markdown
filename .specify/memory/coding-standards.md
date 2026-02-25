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
        pipeline.py        # Parse -> Normalize -> Render pipeline
        registry.py        # Format plugin registry
        models.py          # Intermediate representation (IR) types
        renderer.py        # IR -> Markdown rendering
        constants.py       # ALL project constants (single source of truth)
      converters/          # One module per format
        __init__.py
        pdf.py
        docx.py
        pptx.py
        xlsx.py
        image.py
        html.py
      smart/               # LLM-powered features
        __init__.py
        summary.py
        images.py
        llm.py             # Gemini client wrapper
  tests/
    fixtures/              # Test input files per format
      pdf/
      docx/
      pptx/
      xlsx/
      images/
    golden/                # Expected output .md files
      pdf/
      docx/
      pptx/
      xlsx/
      images/
    test_cli.py
    test_pipeline.py
    test_converters/
      test_pdf.py
      test_docx.py
      ...
  pyproject.toml
  .env.example
  .gitignore
```

## Patterns

### Plugin Registration

Each converter registers itself with the central registry:

```python
from to_markdown.core.registry import register

@register(extensions=[".pdf"], mime_types=["application/pdf"])
class PdfConverter:
    def parse(self, file_path: Path) -> Document:
        ...
```

### Pipeline Flow

```
Input File -> Registry (select converter by extension/MIME)
           -> Converter.parse() -> Document IR
           -> Normalizer.normalize() -> Normalized Document
           -> Renderer.render() -> Markdown string
           -> Output (write .md file with frontmatter)
```

### Intermediate Representation

The Document IR is the shared data model between parse and render:
- Document metadata (title, author, dates, page count, etc.)
- Ordered list of content blocks (headings, paragraphs, tables, code, images)
- Each block has a type, content, and optional attributes

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
GEMINI_MODEL_NAME = "gemini-3.0-flash"
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
*Version: 1.2.0 | Last Updated: 2026-02-25*
