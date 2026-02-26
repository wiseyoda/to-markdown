# Phase History

This file contains summaries of completed phases, archived by `specflow phase close`.

---

## 0110 - Background Processing

**Completed**: 2026-02-26

# Phase 0110: Background Processing

**Goal**: Add asynchronous background processing so that long-running conversions
(especially batch + smart features) don't block the caller. Expose via both CLI flags
and MCP tools.

**Scope**:

### 1. Task Manager
- `src/to_markdown/core/tasks.py`: Task lifecycle management
- Task dataclass: id (UUID), status (pending/running/completed/failed), input,
  output_path, created_at, completed_at, error, result_summary
- SQLite-backed task store (lightweight, zero-config, file-based)
- Task store location: `~/.to-markdown/tasks.db` (configurable via env var)
- Automatic cleanup of completed tasks older than configurable retention period

### 2. CLI Background Flag
- `--background` / `--bg` flag: kicks off conversion in background, returns task ID
- Output: `Task started: abc123. Check status with: to-markdown --status abc123`
- `--status <task-id>`: show task status (pending/running/completed/failed + details)
- `--status all`: list all recent tasks with status summary
- `--cancel <task-id>`: cancel a running task
- Background execution via subprocess (fork and detach from terminal)

### 3. MCP Background Tools
- `start_conversion` tool: starts background task, returns task ID immediately
- `get_task_status` tool: check task status by ID
- `list_tasks` tool: list all tasks with status
- `cancel_task` tool: cancel a running task
- Enables AI agents to fire-and-forget long conversions and poll for results

### 4. Process Management
- Background worker process with proper signal handling
- PID file management to prevent orphan processes
- Graceful shutdown on SIGTERM/SIGINT
- Stdout/stderr redirected to log file per task

### 5. Tests
- Test task creation, status transitions, completion
- Test SQLite store CRUD operations
- Test CLI --background flag output format
- Test --status and --cancel commands
- Test MCP background tool handlers
- Test task cleanup / retention

**Deliverables**:
- [ ] Task manager with SQLite store
- [ ] --background flag for CLI (returns task ID)
- [ ] --status and --cancel CLI commands
- [ ] MCP tools: start_conversion, get_task_status, list_tasks, cancel_task
- [ ] Background process management (fork, PID, signals)
- [ ] Task retention / cleanup
- [ ] Tests for all task lifecycle scenarios
- [ ] README updated with background processing section

**Verification Gate**: **USER GATE** - `to-markdown docs/ --background` returns a task
ID immediately. `to-markdown --status <id>` shows progress. MCP `start_conversion`
tool works from an AI agent session.

**Estimated Complexity**: High

---

## 0100 - MCP Server & AI Agent Skills

**Completed**: 2026-02-26

# Phase 0100: MCP Server & AI Agent Skills

**Goal**: Build an MCP (Model Context Protocol) server and skill definitions so that
Claude Code, Codex, Gemini, and other AI agents can invoke to-markdown programmatically
without shell scripting.

**Scope**:

### 1. MCP Server
- Implement an MCP server (`src/to_markdown/mcp/server.py`) using the MCP Python SDK
- Expose tools: `convert_file`, `convert_batch`, `list_formats`, `get_status`
- `convert_file` tool: accepts file path + options (force, clean, summary, images),
  returns converted markdown content or output path
- `convert_batch` tool: accepts directory/glob + options, returns batch result summary
- `list_formats` tool: returns supported formats (from Kreuzberg)
- `get_status` tool: returns version, available features (LLM configured or not)
- Proper error responses with structured error codes
- stdio transport (standard for local MCP servers)

### 2. MCP Configuration Files
- Generate `mcp.json` for Claude Code / Claude Desktop integration
- Document configuration for Codex and Gemini agent setups
- Include both "local development" and "installed" server configurations

### 3. Agent-Friendly Output
- MCP tool responses include structured metadata envelope (source path, format, stats)
  alongside the markdown content - not just raw markdown
- Large content returns are truncated with a pointer to the full output file
- Batch results include per-file success/failure/skip details

### 5. Tests
- Test MCP server tool handlers with mock inputs
- Test tool schema validation (correct parameters, types)
- Test error handling (missing file, unsupported format, missing API key)
- Stdout suppression verified (no library writes to stdout in MCP mode)

**Deliverables**:
- [ ] MCP server with convert_file, convert_batch, list_formats, get_status tools
- [ ] stdio transport working for local usage
- [ ] mcp.json configuration for Claude Code / Claude Desktop
- [ ] Agent setup documentation for Codex and Gemini
- [ ] Tests for all MCP tool handlers
- [ ] README updated with MCP/agent integration section

**Verification Gate**: **USER GATE** - Claude Code can invoke to-markdown via MCP
tools. `convert_file` and `convert_batch` tools work from an AI agent session.

**Estimated Complexity**: Medium-High

---

## 0050 - Batch Processing

**Completed**: 2026-02-26

# Phase 0050: Batch Processing

**Goal**: Add directory and glob pattern support for converting multiple files at once with
progress reporting.

**Scope**:

### 1. Directory Conversion
- `to-markdown path/to/directory/` converts all supported files
- Recursive by default, --no-recursive flag to disable
- Output structure mirrors input structure

### 2. Glob Pattern Support
- `to-markdown "docs/*.pdf"` converts matching files
- Standard glob patterns

### 3. Progress Reporting
- Show file count, current file, progress percentage
- Use rich or similar for terminal progress bar
- Respect --quiet flag (suppress progress output)

### 4. Error Handling
- Continue on individual file errors (log warning, skip file)
- Summary at end: X succeeded, Y failed, Z skipped
- --fail-fast flag to stop on first error

### 5. Tests
- Directory with mixed formats
- Glob pattern matching
- Error handling for individual file failures
- Progress reporting output

**Deliverables**:
- [ ] Directory conversion with recursive support
- [ ] Glob pattern support
- [ ] Progress reporting
- [ ] Error handling with continue-on-error
- [ ] All tests passing

**Verification Gate**: Directory conversion with mixed formats; progress reporting; all tests
pass.

**Estimated Complexity**: Medium

---

## 0040 - Smart Features

**Completed**: 2026-02-26

# Phase 0040: Smart Features

**Goal**: Add LLM-powered `--clean`, `--summary`, and `--images` flags using Gemini 2.5 Flash
via the google-genai SDK. These are opt-in enhancements that require a GEMINI_API_KEY.

**Motivation**: Raw extraction (Kreuzberg) captures all content but produces artifacts from PDF
layout recovery: concatenated words (`inBangkok`), decorative letter spacing
(`L E A D E R S H I P`), wall-of-text paragraphs where structured data should exist (e.g. Fast
Facts crammed into one paragraph), truncated fragments from multi-column layouts, and missing
line breaks. An LLM cleanup pass transforms this from "technically correct" to genuinely
readable for both humans and LLMs. See the YPO Thailand PDF conversion for a real-world example
of every artifact type.

**Scope**:

### 1. Gemini Client
- `smart/llm.py`: Gemini client wrapper using google-genai SDK
- API key from GEMINI_API_KEY env var (with python-dotenv)
- Model from GEMINI_MODEL env var (default: gemini-2.5-flash)
- Retry with tenacity (exponential backoff for 429/503)
- Graceful degradation: LLM failure -> warning, output without enhancement

### 2. --clean Flag (text cleanup/reflow)
- `smart/clean.py`: Fix extraction artifacts via Gemini
- This is the highest-value smart feature — it transforms raw extraction output into
  properly formatted, readable markdown
- **Artifact types to fix**:
  - Word concatenation from column/line breaks (`inBangkok` -> `in Bangkok`)
  - Decorative letter spacing (`L E A D E R S H I P` -> `LEADERSHIP`)
  - Wall-of-text restructuring: detect when a flat paragraph contains labeled data (e.g.
    "Time Zone: ... Currency: ... Weather: ...") and restructure into markdown lists or tables
  - Collapsed line breaks (`Debby CarreauYPO Global Chairman` -> two separate lines)
  - Truncated fragments from multi-column extraction (attempt recovery from context)
- **Critical constraint**: The LLM must ONLY fix formatting/structure — never add, remove,
  or rephrase content. Prompt must emphasize this is artifact repair, not rewriting
- Process in chunks if document exceeds token limits (MAX_CLEAN_TOKENS constant)
- Output replaces raw extraction content (frontmatter preserved as-is)

### 3. --summary Flag
- `smart/summary.py`: Generate document summary via Gemini
- Send extracted (or cleaned, if --clean also passed) content to Gemini for summarization
- Insert summary section after frontmatter, before main content
- Respect token limits (MAX_SUMMARY_TOKENS constant)

### 4. --images Flag
- `smart/images.py`: Describe images/charts via Gemini vision
- Extract images from document (Kreuzberg ImageExtractionConfig)
- Send each image to Gemini for description
- Insert descriptions as alt text or separate image description sections

### 5. CLI Integration
- Add --clean, --summary, and --images flags to Typer CLI
- Clear error message if flags used without GEMINI_API_KEY
- Flags work independently or in combination
- Processing order when combined: clean -> images -> summary (clean first so summary
  and images work with better content)

### 6. Prompt Engineering
- Prompts are the core IP of the smart features — invest time getting them right
- Store prompt templates as constants (not inline strings)
- **--clean prompt**: Emphasize artifact repair, not rewriting. Instruct the LLM to preserve
  all original content, fix only formatting/structural issues, and output valid markdown
- **--summary prompt**: Specify desired length, format, and that it should capture key facts
  an LLM would need to answer questions about the document
- **--images prompt**: Request detailed, factual descriptions useful for accessibility and
  LLM consumption — not artistic interpretation
- Include format-specific context in prompts when available (e.g. "this was extracted from
  a PDF with multi-column layout" helps the LLM understand why words are concatenated)

### 7. Tests
- Mock LLM responses for deterministic testing
- Test graceful degradation when LLM unavailable
- Test API key validation and error messages
- Test flag combinations (--clean + --summary, all three together)
- Test chunking behavior for documents exceeding token limits
- Real-world smoke test: YPO Thailand PDF with --clean should produce readable output

**Deliverables**:
- [ ] --clean flag fixes extraction artifacts via LLM (word concat, spacing, structure)
- [ ] --summary flag generates LLM summary in output
- [ ] --images flag describes images/charts via Gemini vision
- [ ] Flags compose correctly (--clean + --summary + --images)
- [ ] Graceful degradation when LLM unavailable
- [ ] Clear error messages for missing API key
- [ ] Prompt templates stored as constants, not inline
- [ ] All tests passing with mocked LLM responses

**Verification Gate**: **USER GATE** - `--clean`, `--summary`, and `--images` flags work
correctly with Gemini. User has tested --clean on a real PDF (YPO Thailand or equivalent)
and confirmed extraction artifacts are fixed without content loss.

**Estimated Complexity**: Medium-High

---

## 0030 - Format Quality & Testing

**Completed**: 2026-02-25

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

