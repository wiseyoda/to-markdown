# Phase 0030 Plan: Format Quality & Testing

## Approach

This phase is testing-heavy with minimal production code changes. The work is:

1. Add dev dependencies for fixture generation
2. Build programmatic fixture factories (pytest fixtures)
3. Create per-format test modules with snapshot + quality tests
4. Add edge case tests
5. Write human testing instructions

## File Inventory

### New Files

| File | Purpose | Est. Lines |
|------|---------|-----------|
| `tests/test_formats/__init__.py` | Package marker | 1 |
| `tests/test_formats/conftest.py` | Format-specific fixture factories | ~180 |
| `tests/test_formats/test_pdf.py` | PDF snapshot + quality tests | ~80 |
| `tests/test_formats/test_docx.py` | DOCX snapshot + quality tests | ~80 |
| `tests/test_formats/test_pptx.py` | PPTX snapshot + quality tests | ~80 |
| `tests/test_formats/test_xlsx.py` | XLSX snapshot + quality tests | ~80 |
| `tests/test_formats/test_html.py` | HTML snapshot + quality tests | ~80 |
| `tests/test_formats/test_images.py` | Image snapshot + quality tests | ~70 |
| `tests/test_formats/test_edge_cases.py` | Edge case error handling tests | ~90 |

### Modified Files

| File | Changes |
|------|---------|
| `pyproject.toml` | Add dev deps (fpdf2, python-docx, openpyxl, python-pptx, Pillow); register ocr mark |
| `tests/conftest.py` | Add `normalize_timestamp()` helper for snapshot comparison |

### Unchanged Files

All `src/to_markdown/` files remain unchanged. This phase adds tests only.

## Technical Design

### Fixture Generation Pattern

All fixtures are generated programmatically via pytest session-scoped fixtures. Each format
has a factory that creates temporary files:

```python
@pytest.fixture(scope="session")
def pdf_simple(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Create a simple single-page PDF."""
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(text="Hello World")
    path = tmp_path_factory.mktemp("fixtures") / "simple.pdf"
    pdf.output(str(path))
    return path
```

Benefits:
- Reproducible across environments
- No binary files in git
- Self-documenting (fixture code IS the spec)
- Session-scoped = generated once per test run

### Timestamp Normalization

`extracted_at` changes every run, breaking snapshot comparison. Solution: a helper that
replaces the timestamp with a fixed value before comparison.

```python
import re

TIMESTAMP_PATTERN = re.compile(
    r"extracted_at: '[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z'"
)
TIMESTAMP_REPLACEMENT = "extracted_at: '2025-01-01T00:00:00Z'"  # fixed epoch for snapshots

def normalize_markdown(content: str) -> str:
    """Normalize dynamic fields for snapshot comparison."""
    return TIMESTAMP_PATTERN.sub(TIMESTAMP_REPLACEMENT, content)
```

### Snapshot Test Pattern

Each format test module follows this pattern:

```python
class TestPdfSnapshots:
    def test_simple(self, pdf_simple, snapshot):
        result = convert_file(pdf_simple)
        content = normalize_markdown(result.read_text())
        assert content == snapshot

    def test_with_tables(self, pdf_with_tables, snapshot):
        result = convert_file(pdf_with_tables)
        content = normalize_markdown(result.read_text())
        assert content == snapshot

class TestPdfQuality:
    def test_content_not_empty(self, pdf_simple):
        result = extract_file(pdf_simple)
        assert len(result.content.strip()) > 0

    def test_frontmatter_has_format(self, pdf_simple):
        result = convert_file(pdf_simple)
        content = result.read_text()
        assert "format:" in content
```

### OCR Mark Registration

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "ocr: tests requiring Tesseract OCR (skipped if not installed)",
]
```

OCR tests use:
```python
import shutil
pytestmark = pytest.mark.skipif(
    shutil.which("tesseract") is None,
    reason="Tesseract not installed",
)
```

### Edge Case Strategy

Edge cases test the adapter's error translation:

```python
class TestEdgeCases:
    def test_empty_file(self, tmp_path):
        empty = tmp_path / "empty.pdf"
        empty.write_bytes(b"")
        with pytest.raises((ExtractionError, UnsupportedFormatError)):
            extract_file(empty)

    def test_corrupted_pdf(self, tmp_path):
        bad = tmp_path / "corrupted.pdf"
        bad.write_bytes(b"not a real pdf")
        with pytest.raises(ExtractionError):
            extract_file(bad)
```

## Dependency Additions

| Package | Version | Purpose | Runtime? |
|---------|---------|---------|----------|
| fpdf2 | >=2.8 | Generate PDF test fixtures | Dev only |
| python-docx | >=1.1 | Generate DOCX test fixtures | Dev only |
| openpyxl | >=3.1 | Generate XLSX test fixtures | Dev only |
| python-pptx | >=1.0 | Generate PPTX test fixtures | Dev only |
| Pillow | >=11.0 | Generate image test fixtures | Dev only |

## Task Ordering

Tasks proceed in dependency order:

1. **Infrastructure first**: dev deps, pytest config, conftest helpers (T001-T003)
2. **Fixtures**: format-specific fixture factories (T004-T009)
3. **Snapshot tests**: per-format snapshot + quality tests (T010-T015)
4. **Edge cases**: error handling tests (T016)
5. **Verification**: run full suite, lint, update snapshots (T017)
6. **Documentation**: human testing instructions (T018)

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Kreuzberg output varies by version | Pin kreuzberg version; update snapshots intentionally |
| Tesseract not available | OCR tests skipped via pytest mark; documented in instructions |
| Fixture generation libs have API changes | Pin minimum versions; fixtures are simple API usage |
| Snapshot diffs hard to review | Use descriptive snapshot names; keep fixtures minimal |
