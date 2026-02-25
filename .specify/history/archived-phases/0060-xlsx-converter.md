---
phase: 0060
name: xlsx-converter
status: not_started
created: 2026-02-25
updated: 2026-02-25
---

# Phase 0060: XLSX Converter

**Goal**: Research XLSX parsing libraries, select the best one, and implement an XLSX converter
plugin that extracts spreadsheet data, formulas, and metadata.

**Scope**:
- Research XLSX parsing libraries (openpyxl, xlrd, calamine, etc.)
- Document pros/cons in a PDR
- Implement XLSX converter plugin registered with .xlsx/.xls extensions
- Extract: sheet data as Markdown tables or fenced JSON/CSV
- Handle multiple sheets: each sheet as a section
- Handle formulas: show computed values (not formula text)
- Handle merged cells, formatting hints
- YAML frontmatter: title, sheet names, row/column counts, creation date
- Golden file tests with sample spreadsheets

**Deliverables**:
- [ ] PDR: XLSX library selection with rationale
- [ ] XLSX converter plugin (registered in registry)
- [ ] Sheet data extraction as Markdown tables
- [ ] Multi-sheet support
- [ ] Metadata extraction to frontmatter
- [ ] Golden file tests (3+ test XLSX files)

**Verification Gate**: XLSX conversion produces accurate, well-structured Markdown tables.
All tests pass.

**Estimated Complexity**: Medium
