---
phase: 0040
name: smart-features
status: not_started
created: 2026-02-25
updated: 2026-02-25
---

# Phase 0040: Smart Features

**Goal**: Add LLM-powered `--summary` and `--images` flags using Gemini 2.5 Flash via the
google-genai SDK. These are opt-in enhancements that require a GEMINI_API_KEY.

**Scope**:

### 1. Gemini Client
- `smart/llm.py`: Gemini client wrapper using google-genai SDK
- API key from GEMINI_API_KEY env var (with python-dotenv)
- Model from GEMINI_MODEL env var (default: gemini-2.5-flash)
- Retry with tenacity (exponential backoff for 429/503)
- Graceful degradation: LLM failure -> warning, output without enhancement

### 2. --summary Flag
- `smart/summary.py`: Generate document summary via Gemini
- Send extracted Markdown content to Gemini for summarization
- Insert summary section after frontmatter, before main content
- Respect token limits (MAX_SUMMARY_TOKENS constant)

### 3. --images Flag
- `smart/images.py`: Describe images/charts via Gemini vision
- Extract images from document (Kreuzberg ImageExtractionConfig)
- Send each image to Gemini for description
- Insert descriptions as alt text or separate image description sections

### 4. CLI Integration
- Add --summary and --images flags to Typer CLI
- Clear error message if flags used without GEMINI_API_KEY
- Flags work independently or together

### 5. Tests
- Mock LLM responses for deterministic testing
- Test graceful degradation when LLM unavailable
- Test API key validation and error messages

**Deliverables**:
- [ ] --summary flag generates LLM summary in output
- [ ] --images flag describes images/charts via Gemini vision
- [ ] Graceful degradation when LLM unavailable
- [ ] Clear error messages for missing API key
- [ ] All tests passing with mocked LLM responses

**Verification Gate**: **USER GATE** - `--summary` and `--images` flags work correctly with
Gemini. User has tested on real documents with API key.

**Estimated Complexity**: Medium
