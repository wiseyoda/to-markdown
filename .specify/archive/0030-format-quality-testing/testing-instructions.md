# Phase 0030: Human Testing Instructions

## Prerequisites

- Python 3.14+ installed
- uv installed
- Project cloned and dependencies synced: `uv sync --extra dev`
- For OCR tests: Tesseract installed (`brew install tesseract` on macOS)

## 1. Run the Automated Test Suite

```bash
# Run all tests (102 tests expected)
uv run pytest

# Run only format-specific tests (58 tests + 1 OCR skip)
uv run pytest tests/test_formats/ -v

# Run tests with coverage
uv run pytest --cov=to_markdown

# Run lint and format checks
uv run ruff check
uv run ruff format --check
```

**Expected**: All tests pass. OCR test skipped if Tesseract not installed.

## 2. Test Each Format with Real Documents

### PDF

```bash
# Convert any PDF you have
uv run to-markdown ~/Documents/any-file.pdf

# Check the output
cat ~/Documents/any-file.md
```

**Expected output**: YAML frontmatter with `format: pdf`, `extracted_at`, and possibly
`pages`, `words`, `title`, `author`. Body contains extracted text.

### DOCX

```bash
uv run to-markdown ~/Documents/any-file.docx
cat ~/Documents/any-file.md
```

**Expected**: Frontmatter with `format: docx`. Body preserves headings (`#`, `##`),
**bold**, *italic*, and bullet lists.

### PPTX

```bash
uv run to-markdown ~/Documents/any-presentation.pptx
cat ~/Documents/any-presentation.md
```

**Expected**: Frontmatter with `format: pptx`. Body contains slide titles and content.
Speaker notes included if present.

### XLSX

```bash
uv run to-markdown ~/Documents/any-spreadsheet.xlsx
cat ~/Documents/any-spreadsheet.md
```

**Expected**: Frontmatter with `format: xlsx`. Body contains sheet names as headings
and table data in Markdown table format (`| col1 | col2 |`).

### HTML

```bash
# Create a quick test file
echo '<html><head><title>Test</title></head><body><h1>Hello</h1><p>World</p></body></html>' > /tmp/test.html
uv run to-markdown /tmp/test.html
cat /tmp/test.md
```

**Expected**: Frontmatter with `format: html`, `title: Test`. Body contains heading and
paragraph text. Note: Kreuzberg may include its own frontmatter in the body — this is
expected current behavior.

### Images

```bash
# Any PNG or JPEG
uv run to-markdown ~/Documents/any-image.png
cat ~/Documents/any-image.md
```

**Expected**: Frontmatter with `format: image` or `format: png`. Body contains image
metadata like dimensions. Without OCR/Tesseract, body is minimal (e.g., "Image: PNG 800x600").

## 3. OCR Testing (Requires Tesseract)

```bash
# Install Tesseract
brew install tesseract

# Run OCR-specific tests
uv run pytest tests/test_formats/test_images.py::TestImageOcr -v

# Test with a scanned PDF or image with text
uv run to-markdown ~/Documents/scanned-document.pdf
```

**Expected**: OCR test extracts text from the test PNG fixture. Scanned PDFs produce
extracted text in the Markdown body.

## 4. Manual Edge Case Tests

These are not in the automated suite (per D-41) and should be tested manually:

### Password-Protected PDF

```bash
# If you have a password-protected PDF:
uv run to-markdown ~/Documents/protected.pdf
```

**Expected**: Error message indicating the file cannot be processed. Should NOT crash.

### Large File (10MB+)

```bash
# Find or create a large document
uv run to-markdown ~/Documents/large-file.pdf
```

**Expected**: Completes (may take longer). Check output for completeness.

### Overwrite Protection

```bash
# Convert a file, then try again without --force
uv run to-markdown /tmp/test.html
uv run to-markdown /tmp/test.html
# Should error with "already exists"

# Now with --force
uv run to-markdown /tmp/test.html --force
# Should succeed
```

## 5. Troubleshooting

| Issue | Solution |
|-------|---------|
| `ModuleNotFoundError: kreuzberg` | Run `uv sync` to install dependencies |
| `OCR test skipped` | Install Tesseract: `brew install tesseract` |
| `fpdf2` / `python-docx` not found | Run `uv sync --extra dev` for test dependencies |
| Snapshot test fails after code change | Run `uv run pytest --snapshot-update` to regenerate |
| `Output file already exists` | Use `--force` flag or delete existing .md file |

## 6. Updating Snapshots

When Kreuzberg is upgraded or pipeline output intentionally changes:

```bash
# Regenerate all snapshots
uv run pytest --snapshot-update

# Review changes
git diff tests/test_formats/__snapshots__/

# Verify new snapshots are correct, then commit
uv run pytest  # Should all pass
git add tests/test_formats/__snapshots__/
git commit -m "test: update snapshots for Kreuzberg X.Y.Z"
```

## Quality Observations

Observed during Phase 0030 testing:

1. **PDF heading extraction**: Kreuzberg may not extract heading text from PDFs where
   headings are only distinguished by font size (no structural heading tags). Body text
   is reliably extracted.
2. **HTML double frontmatter**: Kreuzberg returns its own YAML frontmatter for HTML files.
   Our pipeline adds a second frontmatter block. Future improvement: detect and merge.
3. **Image without OCR**: Without Tesseract, image extraction returns only metadata
   (dimensions, format), not text content.
4. **XLSX formatting**: Numeric values may be formatted differently (e.g., `9.99` vs `$9.99`)
   depending on cell formatting in the source file.
