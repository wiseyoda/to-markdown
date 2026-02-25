# Tasks: Format Quality & Testing

## Progress Dashboard

| Phase | Status | Progress |
|-------|--------|----------|
| Infrastructure | IN_PROGRESS | 0/3 |
| Fixture Factories | PENDING | 0/6 |
| Snapshot & Quality Tests | PENDING | 0/6 |
| Edge Cases | PENDING | 0/1 |
| Verification & Docs | PENDING | 0/2 |

**Overall**: 0/18 (0%) | **Current**: Infrastructure

---

**Input**: Design documents from `/specs/0030-format-quality-testing/`
**Prerequisites**: plan.md (required), spec.md (required)

## Phase 1: Infrastructure

**Purpose**: Dev dependencies, pytest config, shared test helpers

- [x] T001 [P] Add fixture generation dev deps (fpdf2, python-docx, openpyxl, python-pptx, Pillow) to pyproject.toml `[project.optional-dependencies] dev`. Verify: `uv sync --extra dev` succeeds. Spec: R6.1
- [x] T002 [P] Register OCR pytest mark in pyproject.toml `[tool.pytest.ini_options]` markers. Verify: `uv run pytest --markers` shows ocr mark. Spec: R6.2
- [x] T003 [P] Add `normalize_markdown()` helper to tests/conftest.py. Replaces `extracted_at` timestamps with fixed value for snapshot stability. Uses re module with named constants. Spec: R2.6, R6.4

**Checkpoint**: All fixture libs importable, pytest config ready, helper available

---

## Phase 2: Fixture Factories

**Purpose**: Programmatic test fixture generation via session-scoped pytest fixtures

- [x] T004 [P] Create tests/test_formats/__init__.py and tests/test_formats/conftest.py with session-scoped PDF fixtures: `pdf_simple` (single page, "Hello World"), `pdf_with_headings` (multi-page, H1/H2 text), `pdf_with_table` (3x3 table). Uses fpdf2. Spec: R1.1, R6.3
- [x] T005 [P] Add DOCX fixtures to tests/test_formats/conftest.py: `docx_simple` (single paragraph), `docx_with_formatting` (H1, H2, bold, italic, bullet list), `docx_with_table` (3-col table with headers). Uses python-docx. Spec: R1.2
- [x] T006 [P] Add PPTX fixtures to tests/test_formats/conftest.py: `pptx_simple` (single slide, title + body), `pptx_multi_slide` (3 slides, speaker notes on slide 2). Uses python-pptx. Spec: R1.3
- [x] T007 [P] Add XLSX fixtures to tests/test_formats/conftest.py: `xlsx_simple` (single sheet, header + 3 data rows), `xlsx_multi_sheet` (two sheets "Sales"/"Expenses" with headers + data). Uses openpyxl. Spec: R1.4
- [x] T008 [P] Add HTML fixtures to tests/test_formats/conftest.py: `html_simple` (title, heading, paragraph), `html_with_table` (heading, 3-col table, links, list). Static HTML strings written to files. Spec: R1.5
- [x] T009 [P] Add image fixtures to tests/test_formats/conftest.py: `image_png_simple` (200x100 white PNG with "Test Image" text via Pillow), `image_jpg_simple` (200x100 colored JPEG). Spec: R1.6

**Checkpoint**: All fixtures generate valid files extractable by Kreuzberg

---

## Phase 3: Snapshot & Quality Tests

**Purpose**: Per-format snapshot tests with syrupy + quality assertions

- [x] T010 [P] Create tests/test_formats/test_pdf.py with: TestPdfSnapshots (snapshot tests for pdf_simple, pdf_with_headings, pdf_with_table using normalize_markdown), TestPdfQuality (content non-empty, expected text present), TestPdfFrontmatter (format field present). Spec: R2.1-R2.5, R3.1, R4.1
- [x] T011 [P] Create tests/test_formats/test_docx.py with: TestDocxSnapshots (snapshots for docx_simple, docx_with_formatting, docx_with_table), TestDocxQuality (content non-empty, headings preserved), TestDocxFrontmatter (format field present). Spec: R2.1-R2.5, R3.2, R4.2
- [x] T012 [P] Create tests/test_formats/test_pptx.py with: TestPptxSnapshots (snapshots for pptx_simple, pptx_multi_slide), TestPptxQuality (slide content extracted), TestPptxFrontmatter (format field present). Spec: R2.1-R2.5, R3.3, R4.3
- [x] T013 [P] Create tests/test_formats/test_xlsx.py with: TestXlsxSnapshots (snapshots for xlsx_simple, xlsx_multi_sheet), TestXlsxQuality (all sheets represented, tabular data present), TestXlsxFrontmatter (format field present). Spec: R2.1-R2.5, R3.4, R4.4
- [x] T014 [P] Create tests/test_formats/test_html.py with: TestHtmlSnapshots (snapshots for html_simple, html_with_table), TestHtmlQuality (headings preserved, links present, table content present), TestHtmlFrontmatter (format + title fields). Spec: R2.1-R2.5, R3.5, R4.5
- [x] T015 [P] Create tests/test_formats/test_images.py with: TestImageSnapshots (snapshot for image_png_simple), TestImageQuality (metadata extracted, frontmatter has format), TestImageOcr (@pytest.mark.ocr, skip if no Tesseract, verify "Test Image" text extracted). Spec: R2.1-R2.5, R3.6, R4.6

**Checkpoint**: All format tests pass, snapshots generated

---

## Phase 4: Edge Cases

**Purpose**: Error handling for malformed, empty, and wrong-extension files

- [x] T016 [P] Create tests/test_formats/test_edge_cases.py with: TestEmptyFiles (0-byte .pdf, .docx, .html raise ExtractionError/UnsupportedFormatError), TestCorruptedFiles (random bytes with .pdf/.docx extensions raise appropriate error), TestWrongExtension (HTML content as .pdf), TestUnicodeContent (HTML with CJK/emoji extracted without corruption). Spec: R5.1-R5.5

**Checkpoint**: All edge case errors caught by adapter, no raw Kreuzberg exceptions leak

---

## Phase 5: Verification & Documentation

**Purpose**: Final suite run, lint check, human testing instructions

- [x] T017 Run `uv run pytest --snapshot-update` to generate snapshots, then `uv run pytest` to verify, then `uv run ruff check` and `uv run ruff format --check`. Fix any issues. Spec: R6.5
- [x] T018 Write human testing instructions: how to run suite, test each format with real docs, expected output, OCR testing, manual edge cases (password-protected PDFs, 10MB+ files per D-41), troubleshooting, snapshot update process. Spec: R7.1-R7.4

---

## Dependencies & Execution Order

- **Phase 1 (T001-T003)**: No dependencies, all parallel
- **Phase 2 (T004-T009)**: T004-T007, T009 depend on T001 (libs); T008 has no deps; all parallel within phase
- **Phase 3 (T010-T015)**: Each depends on its format fixture + T003; all parallel within phase
- **Phase 4 (T016)**: No deps on fixture libs (creates in-memory); parallel with Phase 3
- **Phase 5 (T017-T018)**: Sequential; T017 after all tests written; T018 after T017
