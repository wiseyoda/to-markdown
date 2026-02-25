---
phase: 0040
name: docx-converter
status: not_started
created: 2026-02-25
updated: 2026-02-25
---

# Phase 0040: DOCX Converter

**Goal**: Research DOCX parsing libraries, select the best one, and implement a DOCX converter
plugin that extracts text, structure, tables, image references, and metadata.

**Scope**:
- Research DOCX parsing libraries (python-docx, mammoth, docx2txt, etc.)
- Document pros/cons in a PDR
- Implement DOCX converter plugin registered with .docx extension
- Extract: headings, paragraphs, lists, tables, footnotes
- Handle images: extract alt text, note image locations for --images flag
- Handle styles: map Word styles to Markdown structure
- YAML frontmatter: title, author, creation/modification dates, word count
- Golden file tests with sample DOCX files

**Deliverables**:
- [ ] PDR: DOCX library selection with rationale
- [ ] DOCX converter plugin (registered in registry)
- [ ] Text extraction with heading/list/paragraph structure
- [ ] Table extraction as Markdown tables
- [ ] Image reference extraction
- [ ] Metadata extraction to frontmatter
- [ ] Golden file tests (3+ test DOCX files)

**Verification Gate**: **USER GATE**: DOCX conversion produces complete, well-structured Markdown

**Estimated Complexity**: Medium
