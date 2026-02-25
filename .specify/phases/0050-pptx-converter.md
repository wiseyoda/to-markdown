---
phase: 0050
name: pptx-converter
status: not_started
created: 2026-02-25
updated: 2026-02-25
---

# Phase 0050: PPTX Converter

**Goal**: Research PPTX parsing libraries, select the best one, and implement a PPTX converter
plugin that extracts slide content, speaker notes, tables, and metadata.

**Scope**:
- Research PPTX parsing libraries (python-pptx, etc.)
- Document pros/cons in a PDR
- Implement PPTX converter plugin registered with .pptx extension
- Extract: slide titles, text boxes, bullet points, tables, speaker notes
- Represent each slide as a section (## Slide N: Title)
- Handle charts: extract data tables where possible
- Handle images: note locations for --images flag
- YAML frontmatter: title, author, slide count, creation date
- Golden file tests with sample presentations

**Deliverables**:
- [ ] PDR: PPTX library selection with rationale
- [ ] PPTX converter plugin (registered in registry)
- [ ] Slide content extraction with structure
- [ ] Speaker notes extraction
- [ ] Table extraction from slides
- [ ] Metadata extraction to frontmatter
- [ ] Golden file tests (3+ test PPTX files)

**Verification Gate**: **USER GATE**: PPTX conversion produces complete, well-structured Markdown

**Estimated Complexity**: Medium
