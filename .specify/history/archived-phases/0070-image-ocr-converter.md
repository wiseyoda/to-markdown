---
phase: 0070
name: image-ocr-converter
status: not_started
created: 2026-02-25
updated: 2026-02-25
---

# Phase 0070: Image & OCR Converter

**Goal**: Research OCR libraries, select the best one, and implement an image converter plugin
that extracts text from images (PNG, JPG, TIFF, etc.) and scanned documents.

**Scope**:
- Research OCR libraries (pytesseract, EasyOCR, PaddleOCR, Gemini vision, etc.)
- Document pros/cons in a PDR
- Implement image converter plugin registered with .png/.jpg/.jpeg/.tiff/.bmp extensions
- Extract text from images via OCR
- Support scanned PDFs (integrate with PDF converter's fallback path)
- Auto-detect whether OCR is needed (text layer vs image-only)
- YAML frontmatter: image dimensions, format, OCR confidence score
- Golden file tests with sample images (text photos, screenshots, scanned docs)

**Deliverables**:
- [ ] PDR: OCR library selection with rationale
- [ ] Image converter plugin (registered in registry)
- [ ] OCR text extraction
- [ ] PDF converter OCR fallback integration
- [ ] Auto-detection of OCR need
- [ ] Metadata extraction to frontmatter
- [ ] Golden file tests (3+ test images)

**Verification Gate**: **USER GATE**: Image/OCR conversion produces accurate text extraction

**Estimated Complexity**: High
