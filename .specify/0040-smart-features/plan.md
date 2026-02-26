# Implementation Plan: Smart Features

**Phase**: `0040-smart-features` | **Date**: 2026-02-25 | **Spec**: `spec.md`
**Input**: Phase spec, discovery findings, existing codebase analysis

## Summary

Add three LLM-powered enhancement flags (--clean, --summary, --images) to the existing
Kreuzberg wrapper pipeline. A shared Gemini client module handles authentication, retry,
and error mapping. Each smart feature is an independent module that plugs into the pipeline
between frontmatter composition and file write. The google-genai SDK and tenacity are
already declared as `[llm]` optional extras.

## Technical Context

**Language/Version**: Python 3.14+
**Primary Dependencies**: google-genai 1.59.0+, tenacity 8.0+, python-dotenv (new)
**Storage**: N/A (file I/O only)
**Testing**: pytest 9.0+, syrupy 5.0+ (mocked LLM responses)
**Target Platform**: macOS / Linux CLI
**Project Type**: Single project (src/to_markdown)
**Constraints**: No file over 300 lines, all constants in constants.py, core works offline

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Completeness Over Brevity | PASS | --images adds image descriptions to output |
| II. Magic Defaults, Flags for Edge Cases | PASS | Smart features are opt-in flags |
| III. Kreuzberg Wrapper Architecture | PASS | Extends wrapper with LLM features |
| IV. Simplicity and Maintainability | PASS | One module per feature, shared client |
| V. Quality Through Testing | PASS | Mocked LLM tests, real-world smoke tests |
| VI. Zero Tolerance for Sloppiness | PASS | Constants centralized, DRY, fix-what-you-see |
| VII. Phases Are Done When Actually Done | PASS | Real-world testing with --clean on PDF |

## Project Structure

### New Files

```text
src/to_markdown/
  smart/
    __init__.py          # Package init, exports
    llm.py               # Gemini client wrapper, retry logic, error types
    clean.py             # --clean: artifact repair via LLM
    summary.py           # --summary: document summarization via LLM
    images.py            # --images: image description via Gemini vision
```

### Modified Files

```text
src/to_markdown/
  cli.py                 # Add --clean, --summary, --images flags + API key validation
  core/
    constants.py         # Add LLM constants, token limits, prompt templates
    pipeline.py          # Add smart feature orchestration to convert_file()
    extraction.py        # Add optional image extraction support

tests/
  conftest.py            # Add LLM mock fixtures
  test_cli.py            # Add tests for new flags, API key validation
  test_pipeline.py       # Add tests for smart feature integration
  test_smart/
    __init__.py
    test_llm.py          # Gemini client wrapper tests
    test_clean.py        # --clean module tests
    test_summary.py      # --summary module tests
    test_images.py       # --images module tests

pyproject.toml           # Add python-dotenv to [llm] extras
.env.example             # Add GEMINI_API_KEY and GEMINI_MODEL examples
```

---

## Architecture

### Pipeline Extension

Current pipeline:
```
Input -> extract -> compose frontmatter -> assemble (frontmatter + content) -> write
```

Extended pipeline with smart features:
```
Input -> extract (+ optional image extraction) -> compose frontmatter
      -> [if --clean] clean content via LLM
      -> [if --images] describe images via Gemini vision
      -> [if --summary] generate summary via LLM
      -> assemble (frontmatter + [summary] + content + [image descriptions])
      -> write
```

### Module Dependency Graph

```
cli.py
  -> pipeline.convert_file(clean=, summary=, images=)
       -> extraction.extract_file(extract_images=)
       -> frontmatter.compose_frontmatter()
       -> smart.clean.clean_content()       [if --clean]
       -> smart.images.describe_images()    [if --images]
       -> smart.summary.summarize_content() [if --summary]
       -> assemble + write

smart/llm.py (shared)
  <- smart/clean.py
  <- smart/summary.py
  <- smart/images.py
```

### Error Flow

```
LLM call fails
  -> tenacity retries (up to 5 attempts for 429/503)
  -> retries exhausted: LLMError raised
  -> calling smart module catches LLMError
  -> logs WARNING with context
  -> returns original content (unenhanced)
  -> pipeline continues
```

---

## File-by-File Breakdown

### 1. `src/to_markdown/core/constants.py` (extend)

Add the following constant categories:

```python
# --- LLM ---
GEMINI_DEFAULT_MODEL = "gemini-2.5-flash"
GEMINI_API_KEY_ENV = "GEMINI_API_KEY"
GEMINI_MODEL_ENV = "GEMINI_MODEL"

# --- LLM Retry ---
LLM_RETRY_MAX_ATTEMPTS = 5
LLM_RETRY_MIN_WAIT_SECONDS = 1
LLM_RETRY_MAX_WAIT_SECONDS = 60

# --- LLM Token Limits ---
MAX_CLEAN_TOKENS = 100_000        # ~400K chars at 4 chars/token
MAX_SUMMARY_TOKENS = 1_024        # max output tokens for summary
CHARS_PER_TOKEN_ESTIMATE = 4

# --- LLM Temperature ---
CLEAN_TEMPERATURE = 0.1
SUMMARY_TEMPERATURE = 0.3
IMAGE_DESCRIPTION_TEMPERATURE = 0.2

# --- LLM Prompts ---
CLEAN_PROMPT = """..."""           # Multi-line prompt for artifact repair
SUMMARY_PROMPT = """..."""         # Multi-line prompt for summarization
IMAGE_DESCRIPTION_PROMPT = """..."""  # Multi-line prompt for image description

# --- Smart Feature Output ---
SUMMARY_SECTION_HEADING = "## Summary"
IMAGE_SECTION_HEADING = "## Image Descriptions"
```

Estimated size: ~120 lines total (13 existing + ~107 new). Well under 300 limit.

### 2. `src/to_markdown/smart/__init__.py` (new)

Package init. Exports public functions for use by pipeline.

### 3. `src/to_markdown/smart/llm.py` (new, ~80 lines)

Gemini client wrapper:
- `LLMError(Exception)`: Base exception for LLM failures
- `get_client() -> genai.Client`: Create/cache client from env var
- `generate(contents, *, model, max_output_tokens, temperature) -> str`: Wrapper with
  tenacity retry. Returns response text. Raises `LLMError` on exhausted retries.

Key implementation details:
- `_is_retryable(exc)`: Returns True for ServerError or ClientError with code 429
- tenacity `@retry` decorator with `wait_exponential` and `stop_after_attempt`
- Cache client instance at module level (lazy initialization)

### 4. `src/to_markdown/smart/clean.py` (new, ~90 lines)

Content cleanup:
- `clean_content(content: str, format_type: str) -> str`: Main function called by pipeline.
  Handles chunking, LLM calls, and reassembly. Catches `LLMError` and returns original
  content with warning.
- `_chunk_content(content: str, max_chars: int) -> list[str]`: Split at paragraph boundaries
  (double newline). Each chunk under max_chars.
- `_build_clean_prompt(chunk: str, format_type: str) -> str`: Format the CLEAN_PROMPT
  template with document format context.

### 5. `src/to_markdown/smart/summary.py` (new, ~50 lines)

Document summarization:
- `summarize_content(content: str, format_type: str) -> str | None`: Generate summary text.
  Returns the summary string or None on failure. Catches `LLMError` and returns None with
  warning.
- `format_summary_section(summary: str) -> str`: Wraps summary text in the
  `## Summary` section with proper markdown formatting.

### 6. `src/to_markdown/smart/images.py` (new, ~80 lines)

Image description:
- `describe_images(images: list[dict]) -> str | None`: Process extracted images through
  Gemini vision. Returns formatted markdown section or None if no images/failure.
- `_describe_single_image(image: dict) -> str | None`: Send one image to Gemini, return
  description text. Catches `LLMError` per image (partial success).
- `_format_image_section(descriptions: list[dict]) -> str`: Assemble
  `## Image Descriptions` section with subsections per image.
- `_image_mime_type(format_str: str) -> str`: Convert Kreuzberg format string to MIME type
  (e.g. "png" -> "image/png").

### 7. `src/to_markdown/core/extraction.py` (modify, ~80 lines)

Add optional image extraction:
- Add `extract_images` parameter to `extract_file()` function
- When `extract_images=True`, create `ExtractionConfig` with
  `images=ImageExtractionConfig()`
- Add `images` field to `ExtractionResult` dataclass: `images: list[dict] = field(...)`
- Default remains `extract_images=False` (no behavior change for existing callers)

### 8. `src/to_markdown/core/pipeline.py` (modify, ~140 lines)

Extend `convert_file()`:
- Add `clean`, `summary`, `images` boolean parameters (all default False)
- Pass `extract_images=images` to `extract_file()`
- After frontmatter composition, apply smart features in order:
  1. If `clean`: call `smart.clean.clean_content(content, format_type)`
  2. If `images` and extracted images exist: call `smart.images.describe_images(images)`
  3. If `summary`: call `smart.summary.summarize_content(content, format_type)`
- Assemble final markdown: frontmatter + [summary section] + content + [image section]

### 9. `src/to_markdown/cli.py` (modify, ~150 lines)

Add smart feature flags:
- `--clean / -c`: `Annotated[bool, typer.Option("--clean", "-c", ...)]`
- `--summary / -s`: `Annotated[bool, typer.Option("--summary", "-s", ...)]`
- `--images / -i`: `Annotated[bool, typer.Option("--images", "-i", ...)]`
- API key validation: if any smart flag is True, check `os.environ.get(GEMINI_API_KEY_ENV)`.
  If missing, print error and exit.
- Call `load_dotenv()` at start of `main()` (conditional import to handle missing
  python-dotenv gracefully)
- Pass flags to `convert_file()`

### 10. `pyproject.toml` (modify)

Add `python-dotenv` to `[llm]` extras:
```toml
llm = [
  "google-genai>=1.59.0",
  "tenacity>=8.0",
  "python-dotenv>=1.0",
]
```

### 11. Test Files

#### `tests/test_smart/__init__.py` (new)
Empty package init.

#### `tests/test_smart/test_llm.py` (new, ~80 lines)
- Test client creation with and without API key
- Test retry behavior with mocked failures
- Test fail-fast on non-retryable errors (401, 400)
- Test generate() returns response text

#### `tests/test_smart/test_clean.py` (new, ~100 lines)
- Test clean_content with mocked LLM response
- Test chunking for large documents
- Test graceful degradation on LLM failure
- Test that frontmatter is not sent to LLM
- Test format_type context is included in prompt

#### `tests/test_smart/test_summary.py` (new, ~70 lines)
- Test summarize_content with mocked LLM response
- Test summary section formatting
- Test graceful degradation on LLM failure
- Test summary of empty content (skipped)

#### `tests/test_smart/test_images.py` (new, ~90 lines)
- Test describe_images with mocked LLM response
- Test image section formatting
- Test partial success (some images fail)
- Test no images case (returns None)
- Test mime type derivation from format string

#### `tests/test_cli.py` (extend)
- Test --clean flag passes through to pipeline
- Test --summary flag passes through to pipeline
- Test --images flag passes through to pipeline
- Test missing API key error message
- Test smart flags work without API key when no smart flag is used

#### `tests/test_pipeline.py` (extend)
- Test pipeline with smart flags (mocked smart modules)
- Test processing order: clean -> images -> summary
- Test flag combinations

#### `tests/conftest.py` (extend)
- Add `mock_gemini_client` fixture
- Add `mock_generate` fixture that returns configurable responses
- Add `sample_extracted_images` fixture

---

## Risk Assessment

| Risk | Severity | Probability | Mitigation |
|------|----------|-------------|------------|
| --clean prompt modifies content | High | Medium | Prompt explicitly forbids changes; manual testing required |
| Token estimation inaccuracy | Low | Medium | Conservative limit; graceful handling if API rejects |
| Kreuzberg image extraction fails | Medium | Low | Graceful degradation; skip images with warning |
| constants.py approaches 300 lines | Low | Medium | Keep prompts concise; monitor file size |
| python-dotenv import fails without [llm] | Medium | High | Conditional import with fallback |
| Rate limits on free tier (10 RPM) | Medium | Medium | Tenacity retry handles 429; warning on exhaustion |

---

## Implementation Order

The dependency order for implementation:

1. **constants.py** - All constants must exist before any module references them
2. **smart/llm.py** - Client wrapper must exist before feature modules
3. **smart/clean.py** - Can be built once llm.py is ready
4. **smart/summary.py** - Can be built once llm.py is ready (parallel with clean)
5. **smart/images.py** - Can be built once llm.py is ready (parallel with clean/summary)
6. **extraction.py** - Add image extraction support (needed for images.py integration)
7. **pipeline.py** - Integrate all smart modules into the pipeline
8. **cli.py** - Add flags and API key validation
9. **pyproject.toml** - Add python-dotenv dependency
10. **Tests** - Can be written alongside modules, but integration tests need pipeline changes
11. **Docs** - Update .env.example, --help text, memory docs
