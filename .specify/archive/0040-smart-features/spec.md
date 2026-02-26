# Feature Specification: Smart Features

**Phase**: `0040-smart-features`
**Created**: 2026-02-25
**Status**: Draft
**Input**: Phase spec `.specify/phases/0040-smart-features.md`

---

## User Scenarios & Testing

### User Story 1 - Clean Extraction Artifacts (Priority: P1)

A user converts a PDF with multi-column layout and gets concatenated words (`inBangkok`),
decorative spacing (`L E A D E R S H I P`), and wall-of-text paragraphs. They run
`to-markdown file.pdf --clean` and get properly formatted, readable markdown with all
artifacts fixed and zero content loss.

**Why this priority**: This is the highest-value smart feature. Raw Kreuzberg output for
complex PDFs has real formatting artifacts that make the markdown hard to read for both
humans and LLMs. Fixing these artifacts is the core motivation for the entire phase.

**Independent Test**: Convert a PDF with known extraction artifacts using `--clean` and
verify the output has proper word spacing, no decorative letter gaps, and structured data
properly formatted as lists/tables.

**Acceptance Scenarios**:

1. **Given** a GEMINI_API_KEY is set and a PDF with concatenated words, **When** user runs
   `to-markdown file.pdf --clean`, **Then** output has proper word boundaries (e.g.
   `inBangkok` -> `in Bangkok`)
2. **Given** a GEMINI_API_KEY is set and a PDF with decorative spacing, **When** user runs
   `to-markdown file.pdf --clean`, **Then** decorative spacing is collapsed (e.g.
   `L E A D E R S H I P` -> `LEADERSHIP`)
3. **Given** a GEMINI_API_KEY is set and a PDF with wall-of-text data, **When** user runs
   `to-markdown file.pdf --clean`, **Then** labeled data is restructured into markdown
   lists or tables
4. **Given** a GEMINI_API_KEY is set and --clean is used, **When** the LLM processes the
   content, **Then** no original content is added, removed, or rephrased -- only formatting
   is fixed
5. **Given** a document exceeding MAX_CLEAN_TOKENS, **When** user runs with `--clean`,
   **Then** content is chunked at paragraph boundaries, processed in pieces, and reassembled
6. **Given** GEMINI_API_KEY is set but the Gemini API returns 503, **When** user runs with
   `--clean`, **Then** retries with exponential backoff up to 5 attempts, then falls back
   to uncleaned content with a warning

---

### User Story 2 - Generate Document Summary (Priority: P2)

A user wants a quick overview of a document for their LLM context. They run
`to-markdown file.pdf --summary` and get a concise summary section inserted after the
frontmatter, before the main content.

**Why this priority**: Summaries are valuable for LLM pipelines that need to quickly assess
document relevance. Simpler to implement than --clean (single LLM call, no chunking).

**Independent Test**: Convert a document using `--summary` and verify the output contains
a `## Summary` section after frontmatter with a coherent summary.

**Acceptance Scenarios**:

1. **Given** a GEMINI_API_KEY is set, **When** user runs `to-markdown file.pdf --summary`,
   **Then** output contains a `## Summary` section after the frontmatter `---` and before
   the main document content
2. **Given** a GEMINI_API_KEY is set and both flags used, **When** user runs
   `to-markdown file.pdf --clean --summary`, **Then** clean is applied first, then summary
   is generated from the cleaned content
3. **Given** the Gemini API fails for summary, **When** user runs with `--summary`, **Then**
   output is produced without the summary section and a warning is logged

---

### User Story 3 - Describe Document Images (Priority: P3)

A user has a document with charts, diagrams, or photos. They run
`to-markdown file.pdf --images` and get detailed, factual descriptions of each image
appended as an `## Image Descriptions` section.

**Why this priority**: Image descriptions complete the "all information represented as text"
goal from the constitution. More complex to implement (Kreuzberg image extraction + Gemini
vision) and may not work for all document types.

**Independent Test**: Convert a PDF containing images using `--images` and verify the output
contains an `## Image Descriptions` section with descriptions for each extracted image.

**Acceptance Scenarios**:

1. **Given** a GEMINI_API_KEY is set and a document with images, **When** user runs
   `to-markdown file.pdf --images`, **Then** output contains `## Image Descriptions`
   section with a subsection per image
2. **Given** a document with no images, **When** user runs with `--images`, **Then** no
   image descriptions section is added (no error)
3. **Given** Kreuzberg extracts images but Gemini fails for one, **When** user runs with
   `--images`, **Then** successfully described images are included and a warning is logged
   for the failed one

---

### User Story 4 - Combined Smart Features (Priority: P2)

A user wants maximum enhancement and runs `to-markdown file.pdf --clean --summary --images`.
All three features are applied in the correct order and the output is well-structured.

**Why this priority**: Users will naturally combine flags. Correct interaction between
features is essential.

**Independent Test**: Convert a document with all three flags and verify clean was applied
to content, summary reflects cleaned content, and image descriptions are present.

**Acceptance Scenarios**:

1. **Given** all three flags, **When** user runs the command, **Then** processing order is:
   clean -> images -> summary
2. **Given** all three flags and clean fails, **When** user runs the command, **Then** summary
   and images still run on the original (uncleaned) content with a warning about clean failure

---

### User Story 5 - Missing API Key Error (Priority: P1)

A user runs `to-markdown file.pdf --clean` without setting GEMINI_API_KEY. They get a clear,
actionable error message explaining what to do.

**Why this priority**: First-time users will hit this. Error message quality is critical for
adoption.

**Independent Test**: Run with a smart flag and no API key, verify the exit code and error
message content.

**Acceptance Scenarios**:

1. **Given** no GEMINI_API_KEY in environment, **When** user runs with any smart flag,
   **Then** CLI exits with EXIT_ERROR and prints a message including "GEMINI_API_KEY"
   and instructions to set it
2. **Given** no GEMINI_API_KEY but no smart flags used, **When** user runs
   `to-markdown file.pdf`, **Then** conversion succeeds normally (no LLM needed)

---

### Edge Cases

- What happens when --clean produces output longer than the original? Accept it (restructuring
  can add whitespace/formatting).
- What happens when GEMINI_API_KEY is set but invalid? First LLM call fails with ClientError
  (401), retries are skipped (fail-fast on auth errors), warning logged, output without
  enhancement.
- What happens when --images is used on a text-only document (e.g. .txt)? No images extracted
  by Kreuzberg, no image descriptions added, no error.
- What happens when the Gemini API returns empty text? Treat as failure, log warning, use
  original content.
- What happens when document content is empty after extraction? Skip LLM calls entirely (nothing
  to clean/summarize), log info message.

---

## Requirements

### Functional Requirements

#### Gemini Client (smart/llm.py)

- **FR-001**: System MUST provide a `get_client()` function that creates a `genai.Client`
  using `GEMINI_API_KEY` from environment variables
- **FR-002**: System MUST provide a `generate()` function that wraps
  `client.models.generate_content()` with tenacity retry logic
- **FR-003**: System MUST retry on HTTP 429 (rate limit) and 503 (server error) with
  exponential backoff (min=1s, max=60s, max 5 attempts)
- **FR-004**: System MUST fail fast (no retry) on HTTP 400, 401, 403
- **FR-005**: System MUST read model name from `GEMINI_MODEL` env var, defaulting to
  `gemini-2.5-flash`
- **FR-006**: System MUST define an `LLMError` exception class for smart feature failures

#### --clean Flag (smart/clean.py)

- **FR-007**: System MUST accept a `--clean` CLI flag that triggers LLM-based artifact repair
- **FR-008**: System MUST fix word concatenation artifacts (e.g. `inBangkok` -> `in Bangkok`)
- **FR-009**: System MUST fix decorative letter spacing (e.g. `L E A D E R S H I P` ->
  `LEADERSHIP`)
- **FR-010**: System MUST fix wall-of-text paragraphs containing labeled data by restructuring
  into markdown lists or tables
- **FR-011**: System MUST fix collapsed line breaks (e.g.
  `Debby CarreauYPO Global Chairman` -> two separate lines)
- **FR-012**: The LLM MUST NOT add, remove, or rephrase any content -- only fix
  formatting/structure
- **FR-013**: System MUST chunk content at paragraph boundaries when document exceeds
  MAX_CLEAN_TOKENS
- **FR-014**: System MUST process each chunk independently and reassemble the full document
- **FR-015**: System MUST preserve frontmatter as-is (never send frontmatter to LLM)
- **FR-016**: System MUST replace raw extraction content with cleaned content in the output

#### --summary Flag (smart/summary.py)

- **FR-017**: System MUST accept a `--summary` CLI flag that triggers LLM summarization
- **FR-018**: System MUST insert a `## Summary` section after frontmatter, before main content
- **FR-019**: System MUST summarize the cleaned content if `--clean` is also passed
- **FR-020**: Summary MUST capture key facts an LLM would need to answer questions about
  the document
- **FR-021**: System MUST respect MAX_SUMMARY_TOKENS for the summary output length

#### --images Flag (smart/images.py)

- **FR-022**: System MUST accept an `--images` CLI flag that triggers image description
- **FR-023**: System MUST use Kreuzberg's `ImageExtractionConfig` to extract images from
  the document
- **FR-024**: System MUST send each extracted image to Gemini vision for description
- **FR-025**: System MUST append an `## Image Descriptions` section at the end of the content
- **FR-026**: Each image description MUST include image index and page number as a subsection
  heading
- **FR-027**: Image descriptions MUST be detailed, factual, and useful for accessibility

#### CLI Integration

- **FR-028**: System MUST validate GEMINI_API_KEY presence before pipeline execution when
  any smart flag is passed
- **FR-029**: System MUST exit with EXIT_ERROR and a clear message if API key is missing
- **FR-030**: System MUST call `load_dotenv()` early in CLI execution to load .env files
- **FR-031**: System MUST enforce processing order: clean -> images -> summary regardless
  of flag order
- **FR-032**: Smart flags MUST work independently or in any combination

#### Prompt Engineering

- **FR-033**: All prompt templates MUST be stored in `core/constants.py` as named constants
- **FR-034**: --clean prompt MUST emphasize artifact repair (not rewriting) and include
  format-specific context
- **FR-035**: --summary prompt MUST specify desired format and that it should capture key
  facts for LLM consumption
- **FR-036**: --images prompt MUST request detailed, factual descriptions for accessibility
  and LLM consumption

#### Graceful Degradation

- **FR-037**: If an LLM call fails after retries, system MUST log a warning and continue
  with unenhanced content
- **FR-038**: Each smart feature MUST degrade independently (failure of one does not block
  others)
- **FR-039**: Core conversion (no smart flags) MUST never be affected by LLM module
  availability

#### Tests

- **FR-040**: All LLM responses MUST be mocked in tests for deterministic behavior
- **FR-041**: Tests MUST verify graceful degradation when LLM is unavailable
- **FR-042**: Tests MUST verify API key validation and error messages
- **FR-043**: Tests MUST verify flag combinations (--clean + --summary, all three together)
- **FR-044**: Tests MUST verify chunking behavior for large documents
- **FR-045**: Tests MUST verify that existing tests continue to pass (no regressions)

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: `to-markdown file.pdf --clean` produces output with zero word concatenation
  artifacts when tested on a real PDF with known artifacts
- **SC-002**: `to-markdown file.pdf --summary` produces output with a coherent `## Summary`
  section that accurately reflects the document content
- **SC-003**: `to-markdown file.pdf --images` produces output with an
  `## Image Descriptions` section containing factual descriptions for each extracted image
- **SC-004**: All three flags combined produce a well-structured output with correct
  processing order
- **SC-005**: Missing API key produces a clear error message mentioning `GEMINI_API_KEY`
- **SC-006**: All 102+ existing tests pass with zero regressions
- **SC-007**: `ruff check` and `ruff format --check` pass with zero errors
- **SC-008**: Smart feature tests achieve coverage of all functional requirements
- **SC-009**: No source file exceeds 300 lines (excluding tests)
