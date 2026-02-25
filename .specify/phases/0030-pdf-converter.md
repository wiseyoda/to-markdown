---
phase: 0030
name: pdf-converter
status: not_started
created: 2026-02-25
updated: 2026-02-25
---

# Phase 0030: PDF Converter

**Goal**: Research PDF parsing libraries, select the best one, and implement a PDF converter
plugin that extracts text, structure, tables, and metadata into the Document IR.

**Scope**:
- Research PDF parsing libraries (PyMuPDF, pdfplumber, PyPDF2, pdfminer.six, etc.)
- Document pros/cons in a PDR (Project Decision Record)
- Implement PDF converter plugin registered with .pdf extension
- Extract: text with structure (headings, paragraphs), tables, metadata
- Handle scanned PDFs: auto-detect text layer, fall back to OCR hints
- YAML frontmatter: title, author, creation date, page count, file size
- Golden file tests with sample PDFs (simple, tables, multi-page)

**Deliverables**:
- [ ] PDR: PDF library selection with rationale
- [ ] PDF converter plugin (registered in registry)
- [ ] Text extraction with heading/paragraph structure
- [ ] Table extraction as Markdown tables
- [ ] Metadata extraction to frontmatter
- [ ] Golden file tests (3+ test PDFs)
- [ ] Edge case tests (empty, corrupted, scanned)

**Verification Gate**: **USER GATE**: PDF conversion produces complete, well-structured Markdown

**Estimated Complexity**: High
