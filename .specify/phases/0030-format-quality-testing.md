---
phase: 0030
name: format-quality-testing
status: not_started
created: 2026-02-25
updated: 2026-02-25
---

# Phase 0030: Format Quality & Testing

**Goal**: Establish golden file tests for each target format (PDF, DOCX, PPTX, XLSX, HTML,
images) to verify Kreuzberg's output quality meets the completeness principle. Tune extraction
configuration per format where needed.

**Scope**:

### 1. Test Fixtures
- Curate 2-3 test files per format (simple, complex, edge case)
- Files should be small (<1MB), representative of real-world documents
- Include: tables, headings, lists, images, mixed content

### 2. Golden File Tests (syrupy)
- Create snapshot tests for each format
- Compare Kreuzberg Markdown output against known-good baselines
- Verify frontmatter is correctly composed per format

### 3. Per-Format Quality Assessment
- PDF: Verify heading detection, table extraction, OCR for scanned pages
- DOCX: Verify structure preservation, bold/italic, lists, tables
- PPTX: Verify slide content, speaker notes, image alt text
- XLSX: Verify multi-sheet handling, table formatting
- HTML: Verify DOM structure, table handling, link preservation
- Images: Verify OCR text extraction (pytesseract via Kreuzberg)

### 4. Format-Specific Configuration
- If Kreuzberg output needs tuning for a format, configure via ExtractionConfig
- Document any format-specific workarounds or post-processing

### 5. Edge Case Tests
- Empty files (0 bytes)
- Corrupted files
- Very large files (10MB+)
- Password-protected PDFs
- Files with wrong extensions
- Mixed-language content (Unicode, CJK)

**Deliverables**:
- [ ] Test fixtures for all 6 formats
- [ ] Golden file snapshot tests passing
- [ ] Per-format quality assessment documented
- [ ] Edge case tests for error handling
- [ ] Human testing instructions for real-world verification

**Verification Gate**: **USER GATE** - Golden file tests pass for PDF, DOCX, PPTX, XLSX,
HTML, images. User has tested on real documents.

**Estimated Complexity**: Medium (testing-heavy, minimal code)
