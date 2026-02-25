# Discovery: Research & Tooling

**Phase**: `0010-research-tooling`
**Created**: 2026-02-25
**Status**: Complete

## Phase Context

**Source**: ROADMAP Phase 0010
**Goal**: Deep research on every library and tool for the project. Verify everything is current
and the best choice as of Feb 2026. Produce research documents, get human confirmation on each
selection, then update governance docs.

---

## Codebase Examination

### Related Implementations

| Location | Description | Relevance |
|----------|-------------|-----------|
| (none) | Greenfield project - no source code exists yet | All tooling decisions start fresh |
| `.specify/memory/tech-stack.md` | Current tech stack with TBD library slots | Will be updated with confirmed selections |
| `.specify/discovery/decisions.md` | 30 existing decisions (D-1 through D-30) | New decisions D-31+ for library selections |

### Existing Patterns & Conventions

- **Plugin Registry + Pipeline**: Architecture already decided (D-17). Parse -> Normalize -> Render.
- **Converter Module Pattern**: Each format is one module in `src/to_markdown/converters/`
- **Constants in one file**: All constants in `src/to_markdown/core/constants.py`
- **No magic numbers**: Every numeric literal gets a named constant

### Integration Points

- No existing code to integrate with - this is Phase 0010 (research only)
- Research outputs feed into all subsequent phases (0020-0090)

### Constraints Discovered

- **AGPL-3.0 acceptable**: User confirmed AGPL is fine for personal CLI tool use (pymupdf4llm)
- **System dependencies acceptable**: User OK with `brew install tesseract` for OCR
- **Python 3.14+**: User chose bleeding edge Python target

---

## Requirements Sources

### From ROADMAP/Phase File

- Research core tooling (Python, uv, Typer, ruff, pytest)
- Research per-format libraries (HTML, PDF, DOCX, PPTX, XLSX, OCR)
- Research LLM integration (Gemini SDK, alternatives)
- Human confirmation on all selections
- Update tech-stack.md with confirmed versions
- Update future phase files with specific library names
- Update decisions.md with new decisions

### From Previous Phase Handoffs

- None (first phase)

### From Memory Documents

- **Constitution**: Principles II (magic defaults), III (extensible architecture), IV (simplicity)
- **Tech Stack**: TBD slots for all format libraries need filling

---

## Scope Clarification

### Question 1: Python Version

**Context**: Python 3.14.3 is latest stable (released Feb 2026). 3.13 is mature. Project currently
targets 3.12+.

**Options Presented**:
- A: 3.13+ (Recommended) - Modern baseline, all tools support it
- B: 3.12+ (keep current) - Conservative, wider compatibility
- C: 3.14+ - Bleeding edge, t-strings, deferred annotations

**User Answer**: 3.14+ (bleeding edge)

### Question 2: PDF Library (AGPL License)

**Context**: pymupdf4llm is the best PDF-to-Markdown library but uses AGPL-3.0. pdfplumber (MIT)
is the alternative but requires building our own Markdown renderer.

**Options Presented**:
- A: pymupdf4llm (Recommended) - AGPL, best quality
- B: pdfplumber (MIT) - More work, full control
- C: Both (hybrid)

**User Answer**: pymupdf4llm - AGPL is fine for private use ("not going to sell this")

### Question 3: Default LLM Model

**Context**: Gemini 2.5 Flash is GA with free tier. Gemini 3.0 Flash is preview-only, no free tier.

**Options Presented**:
- A: 2.5 Flash default (Recommended) - GA, free tier, cheaper
- B: 3.0 Flash default - Better benchmarks, but preview

**User Answer**: 2.5 Flash default (configurable via GEMINI_MODEL env var)

### Question 4: HTML Library

**Context**: html-to-markdown (Rust, fast) vs markdownify (Python, established).

**Options Presented**:
- A: html-to-markdown (Recommended) - Rust speed, CommonMark
- B: markdownify - Pure Python, subclassable
- C: Both (evaluate in Phase 0025)

**User Answer**: Both - evaluate in Phase 0025 with real HTML files

### Question 5: OCR Approach

**Context**: pytesseract requires system Tesseract binary. Alternatives are pure-pip but heavier.

**Options Presented**:
- A: pytesseract (Recommended) - `brew install tesseract`, lightweight
- B: Skip dedicated OCR - rely on pymupdf4llm + Gemini vision
- C: EasyOCR - pip-only but 2GB PyTorch download

**User Answer**: pytesseract (system dependency acceptable)

### Question 6: Snapshot Testing

**Context**: syrupy (zero deps, MIT, active) vs custom golden file comparison.

**User Answer**: syrupy

### Question 7: Cross-Cutting All-in-One Libraries

**Context**: MarkItDown (Microsoft, 87.5k stars) and Kreuzberg (Rust core, 76+ formats) could
replace per-format libraries with less output control.

**Options Presented**:
- A: Per-format libraries (Recommended)
- B: Investigate MarkItDown
- C: Investigate Kreuzberg

**User Answer**: Investigate both (alongside per-format approach)

---

### Confirmed Understanding

**What the user wants to achieve**:
Research and confirm all library/tool selections for the to-markdown project. Update governance
documents with concrete versions and library names. Investigate MarkItDown and Kreuzberg as
potential alternatives to the per-format approach.

**How it relates to existing code**:
No existing code. Research outputs define the dependencies for Phases 0020-0090.

**Key constraints and requirements**:
- Python 3.14+ as minimum version
- AGPL-3.0 acceptable for personal CLI tool (pymupdf4llm)
- System dependencies acceptable (Tesseract for OCR)
- Gemini 2.5 Flash as default LLM, configurable via env var
- HTML library deferred to Phase 0025 evaluation
- Must investigate MarkItDown and Kreuzberg as all-in-one alternatives

**Technical approach**:
1. Create research documents per category in `.specify/memory/research/`
2. Update tech-stack.md with confirmed selections and versions
3. Update future phase files with specific library names
4. Add new decisions (D-31+) to decisions.md

**User confirmed**: Yes - 2026-02-25

---

## Research Findings Summary

### Core Tooling

| Tool | Current | Recommended | Version |
|------|---------|-------------|---------|
| Python | 3.12+ | **3.14+** | 3.14.3 |
| uv | latest | Keep | 0.10.6 |
| Typer | latest | Keep | 0.24.0 |
| ruff | latest | Keep | 0.15.2 (2026 style guide) |
| pytest | latest | Keep | 9.1 |
| pytest-cov | - | **Add** | 7.0.0 |
| syrupy | - | **Add** | 5.1.0 |
| pytest-xdist | - | Defer | 3.8.0 |

### Per-Format Libraries

| Format | Library | Version | License | Status |
|--------|---------|---------|---------|--------|
| HTML | TBD (evaluate both) | - | MIT | Deferred to Phase 0025 |
| PDF | pymupdf4llm | 0.3.4 | AGPL-3.0 | **Confirmed** |
| DOCX | python-docx | 1.2.0 | MIT | **Confirmed** |
| PPTX | python-pptx | 1.0.2 | MIT | **Confirmed** |
| XLSX | openpyxl | 3.1.3 | MIT | **Confirmed** |
| OCR | pytesseract | 0.3.13 | Apache-2.0 | **Confirmed** |

### LLM Integration

| Component | Selection | Version | Notes |
|-----------|-----------|---------|-------|
| SDK | google-genai | ~1.59.0 | GA, unified SDK |
| Default model | gemini-2.5-flash | GA | Free tier, stable ID |
| Override model | GEMINI_MODEL env var | - | Users can switch to 3.0 Flash |
| Retry | tenacity | 8.0+ | Exponential backoff |
| LLM deps | Optional extras `[llm]` | - | Core works offline |

### Cross-Cutting Alternatives to Investigate

| Library | Version | Formats | Notes |
|---------|---------|---------|-------|
| MarkItDown | 0.1.5 | All | Microsoft, 87.5k stars, pre-1.0 |
| Kreuzberg | 4.3.8 | 76+ | Rust core, MIT, very active |

---

## Recommendations for SPECIFY

### Should Include in Spec

- Research document creation for each category (8 documents)
- Human review and confirmation of each selection
- tech-stack.md update with concrete versions
- Future phase file updates with library names
- decisions.md update with D-31+ entries
- MarkItDown and Kreuzberg investigation

### Should Exclude from Spec (Non-Goals)

- Writing any application code (that's Phase 0020+)
- Installing or configuring any libraries (deferred)
- Creating pyproject.toml (Phase 0020)

### Potential Risks

- **python-pptx maintenance stalled**: No releases in 12+ months. PPTX format is stable, but
  monitor python-pptx-ng as fallback.
- **openpyxl stale releases**: No release in 20+ months. XLSX format is stable, but consider
  python-calamine for performance in future.
- **MarkItDown pre-1.0**: API may change. Evaluate but don't depend on.
