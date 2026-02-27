# Testing Strategy

> **Agents**: Reference this document for testing approach and requirements.

## Framework

- **Test runner**: pytest
- **Assertions**: pytest built-in assert
- **Fixtures**: pytest fixtures for test file management

## Test Categories

### 1. Golden File Tests (Output Quality)

Compare converter output against curated, known-good .md reference files.

- Location: `tests/golden/{format}/`
- One golden file per test input file
- Tests fail if output differs from golden file
- Golden files are manually reviewed and committed
- Update golden files intentionally when output format changes

```python
def test_pdf_basic(golden_compare):
    result = convert("tests/fixtures/pdf/basic.pdf")
    golden_compare(result, "tests/golden/pdf/basic.md")
```

### 2. Format Coverage Tests

Every supported format converts a representative sample file without errors.

- At least 3 test files per format (simple, complex, edge case)
- Tests verify: no exceptions, non-empty output, valid Markdown structure
- Cover format-specific features (e.g., PDF with tables, DOCX with images)

### 3. Edge Case Tests

- Empty files (0 bytes)
- Corrupted files (invalid format data)
- Very large files (10MB+ documents)
- Scanned PDFs (image-only, no text layer)
- Mixed-language content (Unicode, CJK, RTL)
- Password-protected files (should fail gracefully)
- Files with wrong extensions (e.g., .pdf that's actually .docx)

### 4. CLI Tests

- Argument parsing (input file, -o flag, smart flags)
- Exit codes (0 success, 1 error, 2 unsupported format, 3 output exists)
- Error messages (clear, actionable)
- Output file creation (correct path, correct content)

### 5. Pipeline Tests

- Kreuzberg adapter returns content and metadata for supported formats
- Frontmatter is composed correctly from extraction metadata
- Pipeline orchestrates extract -> frontmatter -> assemble -> write correctly
- Output file path resolution works for all cases (default, -o file, -o directory)
- Overwrite protection errors when output exists without --force

## Test Fixtures

- `tests/fixtures/` contains real-world sample files for each format
- Files should be small (under 1MB) for fast tests
- Include attribution/license if using third-party test documents
- Never commit files containing sensitive or personal data

## Coverage Requirements

- No hard coverage percentage target (internal tool)
- Every converter must have golden file tests
- Every public function in core/ must have tests
- Smart features (--summary, --images) tested with mocked LLM responses

## Phase Completion: Real-World Smoke Tests

Automated tests (`pytest`) are the minimum bar, not the finish line. Every phase must include
real-world verification before it can be marked complete.

### Requirements

1. **Actually run the tool** on real documents, not just test fixtures
2. **Inspect the output** - open the .md file and verify it looks correct
3. **Document the results** - record what was tested and what the output looked like
4. **Provide human testing instructions** - every completed phase must include a
   "How to Test" section with:
   - Exact commands to copy-paste
   - What input files to use (provide samples or tell the human where to get them)
   - What the expected output looks like
   - What to look for to confirm it's working

### Example Phase Completion Checklist

```markdown
## How to Test (Phase 0030: PDF Converter)

1. Convert a simple PDF:
   ```bash
   to-markdown ~/path/to/any-document.pdf
   ```
   Expected: Creates `any-document.md` next to the PDF.

2. Check the output:
   ```bash
   cat ~/path/to/any-document.md
   ```
   Expected: YAML frontmatter with title/author/pages, then clean Markdown body.

3. Convert with custom output:
   ```bash
   to-markdown ~/path/to/any-document.pdf -o ./output/
   ```
   Expected: Creates `./output/any-document.md`.

4. Try an edge case (scanned PDF, large file, etc.) and verify graceful handling.
```

### What "Done" Means

- [ ] `uv run pytest` passes with zero failures
- [ ] `ruff check` passes with zero errors
- [ ] `ruff format --check` passes
- [ ] Real-world smoke test performed on 2+ real documents
- [ ] Output manually inspected and verified
- [ ] Human testing instructions written and included in phase completion
- [ ] `--help` output matches current feature set
- [ ] Memory docs updated if any decisions changed

## Keeping Docs in Sync

When code changes affect behavior, the following must be updated in the same commit:

- `--help` output (Typer docstrings and argument descriptions)
- README usage examples
- Memory documents (tech-stack.md, coding-standards.md) if architecture changed
- Phase detail files if scope changed

No drift. Ever.

## Phase 0125 Additions

Phase 0125 brought the test suite to **505 tests** (143 new + 362 existing) with the following
testing patterns:

- **Async pattern testing**: pytest-asyncio (`asyncio_mode = "auto"`) enables native async test
  functions for testing `generate_async()`, `clean_content_async()`, `describe_images_async()`,
  and the `_build_content_async()` pipeline orchestrator
- **Sanitization test coverage**: Frozen character sets (SANITIZE_ZERO_WIDTH_CHARS,
  SANITIZE_CONTROL_CHARS, SANITIZE_DIRECTIONAL_CHARS) tested for completeness and immutability;
  SanitizeResult dataclass fields (content, chars_removed, was_modified) verified for all code paths
- **Parallel LLM test strategies**: Concurrent chunk dispatch tested with mocked
  `asyncio.Semaphore` to verify max concurrency limits; single-chunk optimization path tested
  separately; `asyncio.gather()` for clean+images parallelism tested with controlled mock ordering

## Running Tests

```bash
# All tests (505 tests)
uv run pytest

# Specific module
uv run pytest tests/test_pipeline.py

# With coverage
uv run pytest --cov=to_markdown
```

---
*Version: 1.2.0 | Last Updated: 2026-02-27*
