---
phase: 0025
name: html-converter
status: not_started
created: 2026-02-25
updated: 2026-02-25
---

# Phase 0025: HTML Converter

**Goal**: Implement the first real format converter as a proof-of-concept for the plugin
architecture. HTML is the simplest format and validates the full pipeline end-to-end.

**Scope**:
- Research HTML parsing libraries (BeautifulSoup, lxml, html2text, markdownify, etc.)
- Document pros/cons in a PDR
- Implement HTML converter plugin registered with .html/.htm extensions
- Extract: headings, paragraphs, lists, tables, links, code blocks
- Strip scripts, styles, nav/footer boilerplate (smart content extraction)
- Handle malformed HTML gracefully
- YAML frontmatter: title (from `<title>`), meta description, charset
- Golden file tests with sample HTML files
- Validates the full pipeline: registry -> parse -> normalize -> render

**Deliverables**:
- [ ] PDR: HTML library selection with rationale
- [ ] HTML converter plugin (registered in registry)
- [ ] Content extraction with structure preservation
- [ ] Table extraction as Markdown tables
- [ ] Boilerplate stripping (nav, footer, scripts, styles)
- [ ] Metadata extraction to frontmatter
- [ ] Golden file tests (3+ test HTML files)
- [ ] End-to-end pipeline validation

**Verification Gate**: HTML conversion produces clean, well-structured Markdown.
Full pipeline works end-to-end. All tests pass.

**Estimated Complexity**: Low
