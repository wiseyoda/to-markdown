---
phase: 0040
name: smart-features
status: not_started
created: 2026-02-25
updated: 2026-02-25
---

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
