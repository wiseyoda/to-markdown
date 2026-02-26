# Discovery: Smart Features

**Phase**: `0040-smart-features`
**Created**: 2026-02-25
**Status**: Complete

## Phase Context

**Source**: ROADMAP Phase 0040
**Goal**: Add LLM-powered `--clean`, `--summary`, and `--images` flags using Gemini 2.5 Flash
via the google-genai SDK. These are opt-in enhancements that require a GEMINI_API_KEY.

---

## Codebase Examination

### Related Implementations

| Location | Description | Relevance |
|----------|-------------|-----------|
| `src/to_markdown/cli.py` | Typer CLI entry point (106 lines) | Must add --clean, --summary, --images flags |
| `src/to_markdown/core/pipeline.py` | Conversion pipeline (80 lines) | Must inject smart feature steps between frontmatter and write |
| `src/to_markdown/core/extraction.py` | Kreuzberg adapter (65 lines) | Must enable ImageExtractionConfig for --images |
| `src/to_markdown/core/frontmatter.py` | YAML frontmatter composition (55 lines) | Untouched; frontmatter preserved as-is by --clean |
| `src/to_markdown/core/constants.py` | All project constants (13 lines) | Must add LLM constants (model, tokens, retry, prompts) |
| `pyproject.toml` | Dependencies | `[llm]` extras already defined: google-genai, tenacity |
| `tests/conftest.py` | Shared test fixtures | Must add LLM mock fixtures |

### Existing Patterns & Conventions

- **Kreuzberg adapter pattern**: All extraction goes through `core/extraction.py` which wraps
  Kreuzberg's API in project-specific types (`ExtractionResult`). Smart features should follow
  a similar adapter pattern for the Gemini client.
- **Pipeline orchestration**: `core/pipeline.py` owns the flow: extract -> frontmatter ->
  assemble -> write. Smart features must plug into this pipeline between frontmatter and write.
- **Error hierarchy**: Custom exceptions inherit from a base class (`ExtractionError`). The
  smart module should follow the same pattern with an `LLMError` base.
- **Constants-only pattern**: Every literal value lives in `core/constants.py`. Prompt templates,
  token limits, retry parameters, and model names must go there.
- **CLI flag pattern**: Typer `Annotated` type hints with `typer.Option(...)`. Flags are
  validated in the CLI layer, conversion logic in the pipeline layer.
- **Logging pattern**: Python `logging` module, levels mapped to `--verbose`/`--quiet`.

### Integration Points

- **CLI -> Pipeline**: `cli.py:main()` calls `pipeline.convert_file()`. Must extend the function
  signature to accept smart feature flags (`clean`, `summary`, `images`).
- **Pipeline -> Smart modules**: Pipeline calls individual smart modules in order:
  clean -> images -> summary. Each module receives content/images and returns transformed content.
- **Smart modules -> Gemini**: All modules call through a shared Gemini client wrapper
  (`smart/llm.py`) that handles authentication, retry, and error mapping.
- **Extraction -> Images**: For `--images`, the extraction adapter must be enhanced to optionally
  enable Kreuzberg's `ImageExtractionConfig` and return extracted images.
- **Environment -> API key**: `python-dotenv` loads `.env` file; `GEMINI_API_KEY` and
  `GEMINI_MODEL` read from `os.environ`.

### Constraints Discovered

- **Kreuzberg ExtractedImage**: Returns a `TypedDict` with `data` (bytes), `format` (str,
  e.g. "png", "jpeg"), `image_index` (int), `page_number` (int), `width`/`height` (int).
  No mime_type field -- must derive from `format` (e.g. `f"image/{format}"`).
- **google-genai error hierarchy**: `APIError` (base) with `code` (int), `status` (str),
  `message` (str). Subclasses: `ClientError` (4xx), `ServerError` (5xx). Retry on
  `ServerError` (503) and `ClientError` where `code == 429`.
- **google-genai GenerateContentConfig**: Uses `camelCase` field names (`maxOutputTokens`,
  `systemInstruction`, `temperature`), not snake_case.
- **python-dotenv not in deps**: Must add `python-dotenv` to the `[llm]` optional extras
  in pyproject.toml.
- **300-line limit**: `constants.py` is currently 13 lines. Adding prompts could push it
  near the limit. Prompts should be stored as multi-line string constants, kept concise.
- **No smart/ directory yet**: Must create `src/to_markdown/smart/` with `__init__.py`,
  `llm.py`, `clean.py`, `summary.py`, `images.py`.

---

## Research Findings

### google-genai SDK (v1.59.0+)

Confirmed usage patterns from installed SDK:

```python
from google import genai
from google.genai import types

# Text generation
client = genai.Client(api_key="...")
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=["prompt", document_text],
    config=types.GenerateContentConfig(
        maxOutputTokens=8192,
        temperature=0.1,
    ),
)
result_text = response.text

# Image understanding (vision)
image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[image_part, "Describe this image in detail."],
)
```

Error classes: `google.genai.errors.APIError` (base), `.ClientError` (4xx), `.ServerError`
(5xx). The `APIError.code` field holds the HTTP status code.

### tenacity (v8.0+)

Confirmed available decorators:

```python
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

@retry(
    retry=retry_if_exception_type((ServerError, RateLimitError)),
    wait=wait_exponential(multiplier=1, min=1, max=60),
    stop=stop_after_attempt(5),
)
def call_gemini(...):
    ...
```

`wait_exponential` with jitter is preferred for rate-limited APIs.

### python-dotenv

Simple usage: `load_dotenv()` reads `.env` file, does not override existing env vars.
Must be called early in the CLI entry point (not in library code).

### Kreuzberg ImageExtractionConfig

Configured via `ExtractionConfig(images=ImageExtractionConfig())`. Returns
`ExtractionResult.images` as `list[ExtractedImage] | None`. Each `ExtractedImage` is a
`TypedDict` with `data` (bytes), `format` (str), `page_number` (int), `width`/`height` (int).

---

## Decisions

#### D-44: python-dotenv as LLM Dependency
- **Phase**: 0040 - Smart Features
- **Status**: Decided
- **Confidence**: High
- **Context**: Need to load GEMINI_API_KEY from .env files for convenience
- **Decision**: Add python-dotenv to the `[llm]` optional extras in pyproject.toml. Call
  `load_dotenv()` in the CLI entry point before checking for the API key.
- **Alternatives**: Manual env var export only (less convenient), keyring (overkill)
- **Consequences**: One additional dependency in the LLM extras; .env files already in .gitignore
- **Memory Doc Impact**: tech-stack.md

#### D-45: Gemini Client as Singleton Module
- **Phase**: 0040 - Smart Features
- **Status**: Decided
- **Confidence**: High
- **Context**: Multiple smart features (clean, summary, images) all need a Gemini client
- **Decision**: `smart/llm.py` provides `get_client()` function that creates and caches a
  `genai.Client` instance. Also provides a `generate()` wrapper that adds retry logic via
  tenacity. All smart modules call `generate()` instead of the SDK directly.
- **Alternatives**: Each module creates its own client (duplication), dependency injection
  container (overkill)
- **Consequences**: Single point for client configuration, retry policy, and error handling
- **Memory Doc Impact**: coding-standards.md (project structure)

#### D-46: Retry Policy for LLM Calls
- **Phase**: 0040 - Smart Features
- **Status**: Decided
- **Confidence**: High
- **Context**: Gemini API can return 429 (rate limit) or 503 (service unavailable)
- **Decision**: Use tenacity with exponential backoff: min=1s, max=60s, max 5 attempts.
  Retry on `ServerError` and `ClientError` where code == 429. Fail fast on all other errors
  (400 bad request, 401 invalid key, 403 forbidden).
- **Alternatives**: Simple sleep-and-retry loop (less robust), no retry (poor UX)
- **Consequences**: Adds ~10 lines of retry configuration; handles transient failures gracefully
- **Memory Doc Impact**: None

#### D-47: Smart Feature Processing Order
- **Phase**: 0040 - Smart Features
- **Status**: Decided
- **Confidence**: High
- **Context**: When multiple flags are combined, order matters
- **Decision**: Processing order: clean -> images -> summary. Clean first so summary and images
  work with better-formatted content. Images before summary so image descriptions can be included
  in the summary context.
- **Alternatives**: summary -> clean -> images (summary of raw text is lower quality)
- **Consequences**: Pipeline must enforce this order regardless of flag order on CLI
- **Memory Doc Impact**: None

#### D-48: Graceful Degradation Strategy
- **Phase**: 0040 - Smart Features
- **Status**: Decided
- **Confidence**: High
- **Context**: LLM failures must not prevent core conversion from succeeding
- **Decision**: If any LLM call fails after retry exhaustion, log a WARNING and continue
  with the unenhanced content. The output .md is still produced -- just without the failed
  enhancement. This applies to each smart feature independently (e.g. clean can fail while
  summary succeeds).
- **Alternatives**: Error and stop (violates core-works-offline principle), silent failure
  (hides problems)
- **Consequences**: Users always get output; warnings tell them what was skipped
- **Memory Doc Impact**: None

#### D-49: API Key Validation Strategy
- **Phase**: 0040 - Smart Features
- **Status**: Decided
- **Confidence**: High
- **Context**: Users need clear feedback when they use --clean/--summary/--images without
  setting up a GEMINI_API_KEY
- **Decision**: Validate API key presence in the CLI layer BEFORE calling the pipeline. If
  any smart flag is passed without GEMINI_API_KEY set, print a clear error message and exit
  with EXIT_ERROR. Do not attempt partial conversion.
- **Alternatives**: Attempt conversion and degrade (confusing UX), validate in pipeline
  (wrong layer)
- **Consequences**: Fast, clear failure with actionable message
- **Memory Doc Impact**: None

#### D-50: Prompt Templates as Constants
- **Phase**: 0040 - Smart Features
- **Status**: Decided
- **Confidence**: High
- **Context**: Phase spec requires prompts stored as constants, not inline strings
- **Decision**: Store all prompt templates in `core/constants.py` as multi-line string
  constants. Use Python format strings for variable substitution (e.g. `{format_type}`
  placeholder for document format context). Three prompts: CLEAN_PROMPT, SUMMARY_PROMPT,
  IMAGE_DESCRIPTION_PROMPT.
- **Alternatives**: Separate prompts.py file (violates single constants file rule),
  Jinja2 templates (overkill)
- **Consequences**: Prompts centralized and version-controlled; constants.py grows but stays
  well under 300 lines
- **Memory Doc Impact**: None

#### D-51: Chunking Strategy for --clean
- **Phase**: 0040 - Smart Features
- **Status**: Decided
- **Confidence**: High
- **Context**: Documents exceeding Gemini's context window need chunking for --clean
- **Decision**: Use MAX_CLEAN_TOKENS constant (default: 100,000 tokens, approximated as
  ~4 chars per token = 400,000 chars). If content exceeds this, split at paragraph boundaries
  (double newline). Process each chunk independently and reassemble. Frontmatter is never
  sent to the LLM.
- **Alternatives**: Send entire document and let API truncate (loses content), word-level
  splitting (breaks context)
- **Consequences**: Large documents are processed correctly; paragraph-boundary splitting
  preserves context within chunks
- **Memory Doc Impact**: None

#### D-52: Summary Insertion Point
- **Phase**: 0040 - Smart Features
- **Status**: Decided
- **Confidence**: High
- **Context**: Phase spec says "insert summary section after frontmatter, before main content"
- **Decision**: Insert summary as a Markdown section with `## Summary` heading immediately
  after the frontmatter `---` delimiter and before the document content. Separated by blank
  lines above and below.
- **Alternatives**: Inline in frontmatter (breaks YAML), at end of document (less visible)
- **Consequences**: Clean separation of generated summary from extracted content
- **Memory Doc Impact**: None

#### D-53: Image Description Insertion Strategy
- **Phase**: 0040 - Smart Features
- **Status**: Decided
- **Confidence**: High
- **Context**: Need to decide how image descriptions appear in the output
- **Decision**: Append an `## Image Descriptions` section at the end of the document content.
  Each image gets a subsection: `### Image N (Page P)` with the Gemini-generated description.
  This keeps descriptions separate from the main content flow.
- **Alternatives**: Inline alt text (hard to place without knowing original image positions),
  frontmatter field (too long for YAML)
- **Consequences**: Clean output structure; image descriptions are discoverable but not mixed
  into the text flow
- **Memory Doc Impact**: glossary.md (new term: "image description section")

#### D-54: Temperature Setting for Smart Features
- **Phase**: 0040 - Smart Features
- **Status**: Decided
- **Confidence**: High
- **Context**: Different smart features need different creativity levels
- **Decision**: --clean uses temperature=0.1 (near-deterministic, must not invent content).
  --summary uses temperature=0.3 (slightly creative for readable prose). --images uses
  temperature=0.2 (factual descriptions with some fluency). All stored as constants.
- **Alternatives**: Same temperature for all (suboptimal), user-configurable (too many flags)
- **Consequences**: Each feature gets an appropriate creativity level
- **Memory Doc Impact**: None

---

## Scope Clarification

### Confirmed Understanding

**What the user wants to achieve**:
Add three LLM-powered flags (--clean, --summary, --images) that enhance the base Kreuzberg
extraction output using Gemini 2.5 Flash. These are opt-in, require GEMINI_API_KEY, and
degrade gracefully on failure.

**How it relates to existing code**:
Smart features plug into the existing pipeline between frontmatter composition and file write.
The pipeline function gains three new boolean parameters. A new `smart/` package contains the
LLM client and feature modules.

**Key constraints and requirements**:
- Core conversion must never be blocked by LLM failures
- --clean must fix formatting only, never add/remove/rephrase content
- All constants in `core/constants.py`
- No file over 300 lines
- Tests use mocked LLM responses
- python-dotenv for .env loading

**Technical approach**:
Shared Gemini client in `smart/llm.py`, feature modules in `smart/clean.py`,
`smart/summary.py`, `smart/images.py`. Tenacity retry on transient errors.
Paragraph-based chunking for large documents.

---

## Recommendations for Spec

### Should Include in Spec

- Gemini client wrapper with retry and error handling
- --clean flag with all artifact types listed in phase spec
- --summary flag with insertion point
- --images flag with Kreuzberg image extraction + Gemini vision
- CLI integration with API key validation
- Prompt templates as constants
- Test suite with mocked LLM responses
- Graceful degradation for each feature independently

### Should Exclude from Spec (Non-Goals)

- Streaming LLM responses (unnecessary for batch file conversion)
- Custom prompt overrides via CLI flags (future feature)
- Caching LLM responses across runs (future feature)
- Async LLM calls (sync is fine for single-file processing)
- Multi-provider LLM support (Gemini only per D-22)

### Potential Risks

- **Prompt quality**: --clean prompt must be carefully crafted to prevent content changes.
  Mitigation: Include explicit constraints in prompt, test with real artifacts.
- **Token estimation**: Character-based approximation (~4 chars/token) may be inaccurate.
  Mitigation: Use conservative limit, errors are handled gracefully.
- **Kreuzberg image extraction reliability**: ImageExtractionConfig may not work for all
  formats. Mitigation: Graceful degradation if no images returned.
- **constants.py growth**: Adding prompts + LLM constants could add 100+ lines.
  Mitigation: Keep prompts concise; file is well under 300-line limit.
