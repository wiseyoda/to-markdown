# Phase 0030 Specification: Format Quality & Testing

## Overview

Establish comprehensive format-specific testing for to-markdown's Kreuzberg-based extraction
pipeline. Create programmatic test fixtures for all 6 target formats (PDF, DOCX, PPTX, XLSX,
HTML, images), build snapshot tests with syrupy, verify frontmatter composition per format,
test edge cases, and provide human testing instructions.

## Requirements

### R1: Test Fixture Generation

Create programmatic test fixtures using Python libraries (dev dependencies only).

- **R1.1**: PDF fixtures (via fpdf2): simple text, multi-page with headings, tables
- **R1.2**: DOCX fixtures (via python-docx): simple text, headings + bold/italic + lists, tables
- **R1.3**: PPTX fixtures (via python-pptx): simple slides, multi-slide with notes
- **R1.4**: XLSX fixtures (via openpyxl): single sheet, multi-sheet with headers
- **R1.5**: HTML fixtures (static strings): simple page, tables + links + headings
- **R1.6**: Image fixtures (via Pillow): PNG with text overlay (for OCR testing)
- **R1.7**: All fixtures generated via pytest fixtures in `tests/conftest.py` or
  format-specific conftest files. Fixtures cached per session (`scope="session"`).

### R2: Snapshot Tests (syrupy)

Create golden file snapshot tests that capture the full pipeline output per format.

- **R2.1**: Each format has at least 2 snapshot tests (simple case, complex case)
- **R2.2**: Snapshots capture the **complete Markdown output** (frontmatter + body)
- **R2.3**: Use `assert result == snapshot` with syrupy's default Amber extension
- **R2.4**: Snapshot names are descriptive: `test_pdf_simple`, `test_docx_with_tables`, etc.
- **R2.5**: Snapshots stored in `tests/test_formats/__snapshots__/` (syrupy default: sibling
  to test files)
- **R2.6**: `extracted_at` timestamp in frontmatter must be **excluded or normalized** before
  snapshot comparison (it changes every run). Use a helper to strip/replace it.

### R3: Frontmatter Verification Per Format

Verify that frontmatter is correctly composed from each format's metadata.

- **R3.1**: PDF frontmatter includes: format, extracted_at (always); title, author, pages,
  words (when present in metadata)
- **R3.2**: DOCX frontmatter includes: format, extracted_at; title, author, words (when present)
- **R3.3**: PPTX frontmatter includes: format, extracted_at; title, author (when present)
- **R3.4**: XLSX frontmatter includes: format, extracted_at (minimal metadata expected)
- **R3.5**: HTML frontmatter includes: format, extracted_at; title (when present)
- **R3.6**: Image frontmatter includes: format, extracted_at (minimal metadata expected)

### R4: Content Quality Assertions

Beyond snapshots, verify key quality properties per format. Passing snapshot + quality tests
constitute the "per-format quality assessment documented" deliverable — the test results
and snapshot files serve as the assessment artifact.

- **R4.1**: PDF: extracted content is non-empty, contains expected text
- **R4.2**: DOCX: headings preserved, text content complete
- **R4.3**: PPTX: slide content extracted, speaker notes included (if present)
- **R4.4**: XLSX: all sheets represented, tabular data present
- **R4.5**: HTML: heading structure preserved, link text present, table content present
- **R4.6**: Images: metadata extracted (width, height); OCR text extracted (if Tesseract
  available, tested with `@pytest.mark.ocr`)

### R5: Edge Case Tests

Test error handling for malformed, empty, and wrong-extension files.

- **R5.1**: Empty file (0 bytes) — raises `ExtractionError` or `ParsingError`
- **R5.2**: Corrupted file (random bytes with valid extension) — raises appropriate error
- **R5.3**: Wrong extension (HTML content saved as `.pdf`) — graceful handling
- **R5.4**: Unicode content (CJK characters, emoji) — extracted without corruption
- **R5.5**: All edge case errors are caught by the adapter and raised as `ExtractionError`
  or `UnsupportedFormatError` (never raw Kreuzberg exceptions)

### R6: Test Infrastructure

- **R6.1**: Add dev dependencies: `fpdf2`, `python-docx`, `openpyxl`, `python-pptx`, `Pillow`
- **R6.2**: Register `ocr` pytest mark in `pyproject.toml` to avoid warnings
- **R6.3**: Create `tests/test_formats/` directory with per-format test modules
- **R6.4**: Create shared fixture helpers in `tests/conftest.py` (timestamp normalization,
  fixture caching)
- **R6.5**: All new tests pass with `uv run pytest`; `ruff check` and `ruff format --check` clean

### R7: Human Testing Instructions

- **R7.1**: Write step-by-step instructions for testing each format with real documents
- **R7.2**: Include expected output examples
- **R7.3**: Include troubleshooting for common issues (missing Tesseract, etc.)
- **R7.4**: Instructions included in the phase completion documentation

## Out of Scope

- Format-specific ExtractionConfig tuning (D-43: measure first, tune later)
- Password-protected file handling (manual smoke test only)
- 10MB+ large file testing (manual smoke test only)
- LLM features (--summary, --images) — Phase 0040
- Batch/directory processing — Phase 0050

## Phase Goals Traceability

| Phase Goal | Requirements |
|-----------|-------------|
| Curate test fixtures for 6 formats | R1.1-R1.7 |
| Create golden file snapshot tests with syrupy | R2.1-R2.6 |
| Per-format quality assessment and configuration tuning | R3.1-R3.6, R4.1-R4.6 |
| Edge case tests for error handling | R5.1-R5.5 |
| Human testing instructions for real-world verification | R7.1-R7.4 |
