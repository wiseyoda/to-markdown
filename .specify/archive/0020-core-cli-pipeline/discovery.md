# Discovery: Core CLI & Pipeline

**Phase**: 0020
**Created**: 2026-02-25
**Status**: Complete

## Codebase Examination

### Current State

No source code exists. Phase 0010 established governance, research documents, and tooling
decisions. This phase creates the first working code.

### Key Files That Will Be Created

| File | Purpose |
|------|---------|
| `pyproject.toml` | Project config: dependencies, scripts, ruff, pytest |
| `src/to_markdown/__init__.py` | Package root with `__version__` |
| `src/to_markdown/cli.py` | Typer CLI entry point |
| `src/to_markdown/core/__init__.py` | Core package |
| `src/to_markdown/core/constants.py` | ALL project constants |
| `src/to_markdown/core/extraction.py` | Kreuzberg adapter |
| `src/to_markdown/core/frontmatter.py` | YAML frontmatter composition |
| `src/to_markdown/core/pipeline.py` | Extract -> frontmatter -> output |
| `tests/conftest.py` | Shared fixtures |
| `tests/test_extraction.py` | Kreuzberg adapter tests |
| `tests/test_frontmatter.py` | Frontmatter composition tests |
| `tests/test_pipeline.py` | End-to-end pipeline tests |
| `tests/test_cli.py` | CLI argument and behavior tests |

### Existing Infrastructure

- `.gitignore` - exists, may need additions for Python artifacts
- `CLAUDE.md` - project instructions (already references src/ structure)
- `.specify/memory/` - all governance docs established

### Dependencies to Install

From tech-stack.md (D-19, D-31, D-34):

| Package | Version | Purpose |
|---------|---------|---------|
| kreuzberg | >=4.3.8 | Extraction backend |
| typer | >=0.24.0 | CLI framework |
| pyyaml | >=6.0 | YAML frontmatter serialization |
| ruff | >=0.15.2 | Linting + formatting (dev) |
| pytest | >=9.1 | Test framework (dev) |
| pytest-cov | >=7.0.0 | Coverage reporting (dev) |
| syrupy | >=5.1.0 | Snapshot testing (dev) |

### Kreuzberg API Surface (from research/kreuzberg.md)

```python
from kreuzberg import extract_file_sync, ExtractionConfig

result = extract_file_sync("file.pdf", config=ExtractionConfig(
    output_format="markdown",
    enable_quality_processing=True,
))
result.content    # str - Markdown text
result.metadata   # Metadata object
result.tables     # List[ExtractedTable]
```

Metadata fields available: title, authors, creation_date, modification_date, page_count,
word_count, language, mime_type.

### Unsupported Format Behavior

Kreuzberg raises `kreuzberg.ExtractionError` (or a subclass) when it cannot process a file.
The adapter strategy is:

1. **Delegate to Kreuzberg** - do NOT pre-check extensions. Kreuzberg supports 76+ formats
   and knows more about what it can handle than a static extension list.
2. **Catch Kreuzberg exceptions** - wrap `kreuzberg.ExtractionError` in our custom
   `UnsupportedFormatError` when the error indicates format incompatibility.
3. **Map to exit code** - `UnsupportedFormatError` → exit code 2; other extraction errors → exit code 1.

This avoids maintaining a separate format list and lets Kreuzberg be the authority on what
it supports.

## Clarified Intent

### What This Phase Produces

A working CLI: `uv run to-markdown <file>` that:
1. Accepts a file path argument
2. Extracts content via Kreuzberg
3. Composes YAML frontmatter from metadata
4. Writes `<filename>.md` next to the input file
5. Handles errors gracefully (missing file, unsupported format, output exists)

### What This Phase Does NOT Include

- Smart features (--summary, --images) - Phase 0040
- Golden file testing per format - Phase 0030
- Batch/directory processing - Phase 0050
- LLM dependencies - Phase 0040

### Open Questions Resolved

| Question | Resolution |
|----------|-----------|
| Which YAML library? | PyYAML - standard, well-maintained |
| How to handle Kreuzberg async? | Use `extract_file_sync` - no async needed for single file |
| Output path with -o flag? | If -o is a directory, place file there; if a file, use as-is |
| Version source of truth? | `src/to_markdown/__init__.py` with `__version__` |
