# Phase 0030 Discovery: Format Quality & Testing

## Codebase Examination

### Current State

- **Pipeline**: `extract_file()` → `compose_frontmatter()` → assemble → write (all in `core/`)
- **Extraction adapter**: `core/extraction.py` wraps `kreuzberg.extract_file_sync()` with
  `ExtractionConfig(output_format="markdown", enable_quality_processing=True)`
- **Frontmatter**: Composed from metadata dict keys: title, authors, creation_date, page_count,
  word_count, format_type. Only truthy values included.
- **Test fixtures**: Empty (`tests/fixtures/.gitkeep` only)
- **Existing tests**: 44 tests across 4 files, all against plain text files
- **syrupy**: Listed in dev deps (`>=5.0`), installed as 5.1.0, but **not yet used**
- **No format-specific tests exist** — all current tests use `sample.txt`

### Kreuzberg Metadata by Format

Research verified that Kreuzberg returns **different metadata keys per format**:

| Format | Key Metadata Fields |
|--------|-------------------|
| PDF | page_count, word_count, title, authors, creation_date, format_type |
| DOCX | paragraph_count, word_count, title, authors, creation_date |
| PPTX | slide_count, title, authors, creation_date |
| XLSX | sheet_names, row_count, column_count |
| HTML | title, author, links, images, headers, meta_tags |
| Images | width, height, format, format_type("image"), exif |
| TXT | word_count, character_count, line_count, format_type("text") |

All formats include `quality_score` (float 0-1) and `output_format` (string).

### Kreuzberg Tables

`result.tables` returns `list[ExtractedTable]` where each has:
- `cells: list[list[str]]` — rows of columns
- `markdown: str` — pre-rendered Markdown table
- `page_number: int` — 1-indexed page number

Tables are returned for HTML, PDF, XLSX, and CSV formats.

### Kreuzberg Exceptions

| Exception | When Raised |
|-----------|------------|
| `ValidationError` | Unsupported MIME type, invalid config |
| `ParsingError` | Corrupted/invalid file content |
| `OCRError` | Tesseract not installed, OCR failed |
| `MissingDependencyError` | Required system dependency missing |
| `OSError` | File does not exist (pre-checked by our adapter) |

### OCR Behavior

- Images without OCR configured return basic metadata only (e.g., `"Image: PNG 800x600"`)
- OCR requires system-installed Tesseract
- Current ExtractionConfig does NOT explicitly configure OCR — Kreuzberg auto-detects
- For scanned PDFs, Kreuzberg attempts OCR automatically if Tesseract is available

### syrupy API

- Fixture: `snapshot` auto-registered by pytest plugin
- Assertion: `assert result == snapshot`
- Update: `pytest --snapshot-update`
- Storage: `tests/__snapshots__/test_file.ambr` (Amber format, default)
- Named: `assert result == snapshot(name="descriptive_name")`
- Extensions: AmberSnapshotExtension (default), JSONSnapshotExtension, SingleFileSnapshotExtension

## Key Design Decisions

### D-38: Test Fixture Creation Strategy

- **Decision**: Create test fixtures **programmatically** using Python libraries (python-docx,
  openpyxl, python-pptx, reportlab/fpdf2, Pillow) rather than committing static binary files.
  A `tests/fixtures/conftest.py` module generates all fixtures via pytest fixtures.
- **Rationale**: Programmatic fixtures are reproducible, small, self-documenting, and avoid
  licensing issues with third-party documents. They can be version-controlled as code.
- **Exception**: A small static HTML fixture is acceptable since HTML is plain text.

### D-39: Snapshot Extension Choice

- **Decision**: Use syrupy's default **AmberSnapshotExtension** (`.ambr` files) for all
  snapshot tests. Amber format stores multiple named snapshots per file, which is more compact
  than one-file-per-snapshot.
- **Rationale**: Amber is the syrupy default, requires no configuration, and stores all
  snapshots from a test file in a single `.ambr` file. Easy to review in PRs.

### D-40: OCR Testing Strategy

- **Decision**: Mark OCR-dependent tests with `@pytest.mark.ocr` and skip them if Tesseract
  is not installed. Core format tests must pass without Tesseract.
- **Rationale**: CI environments and developer machines may not have Tesseract. Core quality
  tests should not be blocked by a system dependency. OCR tests are bonus coverage.

### D-41: Edge Case Test Approach

- **Decision**: Test edge cases by creating minimal bad files in-memory (empty bytes, random
  bytes for corruption, wrong-extension files). Do NOT test password-protected PDFs or 10MB+
  files in the automated suite — document these as manual smoke test items.
- **Rationale**: Large files and password-protected files are slow/complex to generate
  programmatically. They belong in manual testing, not CI.

### D-42: Fixture Generation Dependencies

- **Decision**: Add `fpdf2`, `python-docx`, `openpyxl`, `python-pptx`, and `Pillow` as
  **dev dependencies** for generating test fixtures. These are NOT runtime dependencies.
- **Rationale**: These libraries create the test fixture files that Kreuzberg then extracts.
  They are only needed during testing, never in production.

### D-43: Format-Specific ExtractionConfig

- **Decision**: Do NOT add format-specific ExtractionConfig tuning in this phase. Use the
  existing default config for all formats. If quality issues are discovered during testing,
  document them and defer config tuning to a future iteration.
- **Rationale**: Start by measuring quality with defaults. Only tune if specific formats
  produce unacceptable output. Avoid premature configuration.
