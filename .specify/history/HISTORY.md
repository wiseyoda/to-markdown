# Phase History

This file contains summaries of completed phases, archived by `specflow phase close`.

---

## 0020 - Core CLI & Pipeline

**Completed**: 2026-02-25

# Phase 0020: Core CLI & Pipeline

**Goal**: Build the complete to-markdown CLI that wraps Kreuzberg for document extraction,
composes YAML frontmatter from metadata, and outputs a single .md file. This is the MVP -
after this phase, `to-markdown file.pdf` produces a working .md file.

**Scope**:

### 1. Project Setup
- Initialize pyproject.toml with uv, Python 3.14+, all dependencies
- Configure ruff (0.15+, 2026 style guide), pytest (9.1+), syrupy
- Create project structure per coding-standards.md
- Set up .env.example, .gitignore

### 2. Kreuzberg Adapter
- `core/extraction.py`: Thin adapter around Kreuzberg's `extract_file_sync`
- Default to `output_format="markdown"` with `enable_quality_processing=True`
- Return structured result (content, metadata, tables)
- Error handling for unsupported formats, corrupted files, missing files

### 3. Frontmatter Composition
- `core/frontmatter.py`: Compose YAML frontmatter from Kreuzberg metadata
- Fields: title, author, creation date, page count, format, extraction date
- Clean, structured YAML between `---` delimiters

### 4. Pipeline
- `core/pipeline.py`: Kreuzberg extract -> frontmatter -> assemble -> output
- Handles file path resolution (input -> output .md path)
- Overwrite protection (error unless --force)

### 5. CLI
- `cli.py`: Typer-based CLI entry point
- `to-markdown <file>` - convert a file
- Flags: --version, --verbose/-v, --quiet/-q, --force/-f, -o <path>
- Proper exit codes (0 success, 1 error, 2 unsupported, 3 already exists)
- Logging setup per coding-standards.md

### 6. Tests
- test_extraction.py: Kreuzberg adapter works for basic text file
- test_frontmatter.py: YAML frontmatter composition
- test_pipeline.py: End-to-end pipeline
- test_cli.py: CLI argument parsing, exit codes, output file creation

**Deliverables**:
- [ ] pyproject.toml with all dependencies configured
- [ ] Working CLI: `uv run to-markdown <file>` produces .md with frontmatter
- [ ] Kreuzberg adapter with error handling
- [ ] Frontmatter composition from metadata
- [ ] All baseline tests passing
- [ ] `ruff check` + `ruff format --check` passing

**Verification Gate**: `to-markdown test.txt` produces valid .md with frontmatter;
`ruff check` + `pytest` pass.

**Estimated Complexity**: Medium (wrapper code, not parser development)

---

## 0010 - Research & Tooling

**Completed**: 2026-02-25

# Phase 0010: Research & Tooling

**Goal**: Deep research on every library and tool we'll use throughout the project. Verify
everything is current, maintained, and the best choice as of Feb 2026 (not stale May 2025
knowledge). Produce a research document per format/topic, get human confirmation on each
selection, then update all governance docs and future phase details with concrete choices.

**Scope**:

### 1. Core Tooling Research
- **Python version**: Confirm 3.12+ is still the right target (or 3.13?)
- **uv**: Still the standard? Version, features, any breaking changes
- **Typer**: Still maintained? Alternatives emerged? (click, cyclopts, etc.)
- **ruff**: Still the formatter/linter of choice? Config best practices
- **pytest**: Plugins we should use (pytest-cov, pytest-snapshot for golden files, etc.)

### 2. Per-Format Library Research
For each format, research the top 2-3 libraries. For each candidate evaluate:
- Last release date / commit activity
- Python version support
- Feature coverage for our needs
- Dependencies (native/C extensions vs pure Python)
- License
- Community size / issue resolution speed

Formats to research:
- **HTML**: BeautifulSoup4, lxml, markdownify, html2text, trafilatura
- **PDF**: PyMuPDF (fitz), pdfplumber, PyPDF2/pypdf, pdfminer.six, borb
- **DOCX**: python-docx, mammoth, docx2python
- **PPTX**: python-pptx (alternatives?)
- **XLSX**: openpyxl, xlrd, calamine (python bindings?), pandas
- **Images/OCR**: pytesseract, EasyOCR, PaddleOCR, docTR, Gemini vision API

### 3. LLM Integration Research
- **google-genai SDK**: Current state, Gemini 3.0 Flash availability
- **Alternative**: Should we use litellm or AI SDK for provider flexibility?
- **Vision API**: Best approach for image description (--images flag)

### 4. Human Review
- Present findings per category using AskUserQuestion
- Get explicit confirmation or override on each selection
- Document rejected alternatives with rationale

### 5. Update Everything
- Create `.specify/memory/research/{topic}.md` for each research area
- Update `tech-stack.md` with confirmed selections and versions
- Update future phase files (0025-0090) with specific library names
- Update `coding-standards.md` if any patterns change
- Update `decisions.md` with new decisions

**Research Output Location**: `.specify/memory/research/`

Each research file follows this format:
```markdown
# Research: {Format/Topic}

## Date: YYYY-MM-DD

## Candidates
### {Library A}
- Latest version:
- Last release:
- Python support:
- Pros:
- Cons:
- License:

### {Library B}
...

## Recommendation
{Library} because {reasons}

## Human Decision
- Confirmed / Overridden: {date}
- Final selection: {library}
- Notes: {any human feedback}
```

**Deliverables**:
- [ ] Research: core tooling (Python, uv, Typer, ruff, pytest)
- [ ] Research: HTML parsing libraries
- [ ] Research: PDF parsing libraries
- [ ] Research: DOCX parsing libraries
- [ ] Research: PPTX parsing libraries
- [ ] Research: XLSX parsing libraries
- [ ] Research: OCR/image libraries
- [ ] Research: LLM integration (Gemini SDK, alternatives)
- [ ] Human confirmation on all selections
- [ ] tech-stack.md updated with versions and confirmed libraries
- [ ] Future phase files updated with specific library names
- [ ] decisions.md updated with D-31+ for each selection

**Verification Gate**: **USER GATE** - All library selections confirmed by human,
research docs committed to `.specify/memory/research/`, governance docs updated
with concrete versions and library names.

**Estimated Complexity**: Medium (research-heavy, no code)

---

