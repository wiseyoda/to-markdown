# Tasks: Smart Features

## Progress Dashboard

> Last updated: 2026-02-25 | Run `specflow tasks sync` to refresh

| Phase | Status | Progress |
|-------|--------|----------|
| Setup | PENDING | 0/3 |
| Gemini Client | PENDING | 0/4 |
| US1: --clean | PENDING | 0/5 |
| US2: --summary | PENDING | 0/3 |
| US3: --images | PENDING | 0/5 |
| Integration | PENDING | 0/5 |
| Polish | PENDING | 0/4 |

**Overall**: 0/29 (0%) | **Current**: None

---

**Input**: Design documents from `.specify/0040-smart-features/`
**Prerequisites**: plan.md, spec.md, discovery.md

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Dependencies and constants foundation

- [ ] T001 Add python-dotenv to `[llm]` optional extras in `pyproject.toml`
- [ ] T002 [P] Add all LLM constants to `src/to_markdown/core/constants.py`:
  model defaults (GEMINI_DEFAULT_MODEL, GEMINI_API_KEY_ENV, GEMINI_MODEL_ENV),
  retry config (LLM_RETRY_MAX_ATTEMPTS, LLM_RETRY_MIN_WAIT_SECONDS,
  LLM_RETRY_MAX_WAIT_SECONDS), token limits (MAX_CLEAN_TOKENS, MAX_SUMMARY_TOKENS,
  CHARS_PER_TOKEN_ESTIMATE), temperatures (CLEAN_TEMPERATURE, SUMMARY_TEMPERATURE,
  IMAGE_DESCRIPTION_TEMPERATURE), section headings (SUMMARY_SECTION_HEADING,
  IMAGE_SECTION_HEADING)
- [ ] T003 Add prompt template constants to `src/to_markdown/core/constants.py`:
  CLEAN_PROMPT (artifact repair with format context placeholder), SUMMARY_PROMPT
  (document summarization for LLM consumption), IMAGE_DESCRIPTION_PROMPT (factual
  image description for accessibility) [depends: T002]

**Checkpoint**: All constants exist and can be imported. `ruff check` passes.

---

## Phase 2: Gemini Client (Shared Infrastructure)

**Purpose**: Shared LLM client that all smart feature modules depend on

- [ ] T004 Create `src/to_markdown/smart/__init__.py` with package docstring
- [ ] T005 Implement Gemini client wrapper in `src/to_markdown/smart/llm.py`:
  `LLMError` exception class, `get_client()` with lazy initialization from
  GEMINI_API_KEY env var, `generate()` wrapper with tenacity retry (exponential
  backoff, retry on 429/503, fail-fast on 400/401/403), returns response text
  [depends: T002]
- [ ] T006 Create `tests/test_smart/__init__.py` and add LLM mock fixtures to
  `tests/conftest.py`: `mock_gemini_client` fixture, `mock_generate` fixture with
  configurable responses
- [ ] T007 Write tests in `tests/test_smart/test_llm.py`: test client creation
  with/without API key, test retry on 429/503, test fail-fast on 401, test
  generate returns text, test LLMError on exhaustion [depends: T005, T006]

**Checkpoint**: `smart/llm.py` importable and fully tested with mocks.

---

## Phase 3: User Story 1 - --clean Flag (Priority: P1)

**Goal**: Fix extraction artifacts (concatenated words, decorative spacing, wall-of-text)
via LLM while preserving all original content.

**Independent Test**: `to-markdown file.pdf --clean` fixes known artifacts without content loss.

- [ ] T008 Implement `src/to_markdown/smart/clean.py`: `clean_content(content, format_type)`
  main function with chunking logic, `_chunk_content(content, max_chars)` splits at paragraph
  boundaries, `_build_clean_prompt(chunk, format_type)` formats CLEAN_PROMPT template,
  catches LLMError and returns original content with warning [depends: T003, T005]
- [ ] T009 Write tests in `tests/test_smart/test_clean.py`: test clean with mocked LLM,
  test chunking splits at paragraph boundaries, test chunk reassembly, test graceful
  degradation on LLM failure, test format_type included in prompt, test empty content
  skipped, test frontmatter not included [depends: T006, T008]
- [ ] T010 Integrate --clean into pipeline: extend `convert_file()` in
  `src/to_markdown/core/pipeline.py` to accept `clean` parameter, call
  `smart.clean.clean_content()` after frontmatter composition when clean=True, pass
  format_type from metadata [depends: T008]
- [ ] T011 Add `--clean / -c` flag to CLI in `src/to_markdown/cli.py`, pass to
  `convert_file()` [depends: T010]
- [ ] T012 Write pipeline and CLI tests for --clean: test in `tests/test_pipeline.py`
  that clean is called when flag=True (mock smart module), test in `tests/test_cli.py`
  that --clean flag is accepted and passed through [depends: T010, T011]

**Checkpoint**: `to-markdown file.txt --clean` works end-to-end with mocked LLM in tests.

---

## Phase 4: User Story 2 - --summary Flag (Priority: P2)

**Goal**: Generate a concise summary section after frontmatter using Gemini.

**Independent Test**: `to-markdown file.pdf --summary` adds `## Summary` section.

- [ ] T013 [P] Implement `src/to_markdown/smart/summary.py`: `summarize_content(content,
  format_type)` generates summary via LLM, `format_summary_section(summary)` wraps in
  markdown section with SUMMARY_SECTION_HEADING, catches LLMError and returns None with
  warning [depends: T003, T005]
- [ ] T014 [P] Write tests in `tests/test_smart/test_summary.py`: test summarize with
  mocked LLM, test section formatting, test graceful degradation, test empty content
  skipped, test summary uses cleaned content when both flags [depends: T006, T013]
- [ ] T015 Integrate --summary into pipeline and CLI: extend `convert_file()` in
  `src/to_markdown/core/pipeline.py` to accept `summary` parameter, call after clean
  (if both), insert summary section between frontmatter and content. Add `--summary / -s`
  flag to `src/to_markdown/cli.py`. Write pipeline and CLI tests for --summary in
  `tests/test_pipeline.py` and `tests/test_cli.py` (bundled because --summary integration
  is simpler than --clean/--images: single pipeline call, no extraction changes).
  [depends: T010, T013]

**Checkpoint**: `to-markdown file.txt --summary` and `--clean --summary` both work.

---

## Phase 5: User Story 3 - --images Flag (Priority: P3)

**Goal**: Extract images from documents and describe them via Gemini vision.

**Independent Test**: `to-markdown file.pdf --images` adds `## Image Descriptions` section.

- [ ] T016 Extend extraction adapter in `src/to_markdown/core/extraction.py`: add
  `extract_images` parameter to `extract_file()`, when True create ExtractionConfig with
  `images=ImageExtractionConfig()`, add `images: list[dict]` field to ExtractionResult
  [depends: none]
- [ ] T017 [P] Implement `src/to_markdown/smart/images.py`: `describe_images(images)`
  processes list of ExtractedImage dicts through Gemini vision, `_describe_single_image(image)`
  sends one image, `_format_image_section(descriptions)` assembles markdown section,
  `_image_mime_type(format_str)` converts format to MIME type, catches LLMError per image
  for partial success [depends: T003, T005]
- [ ] T018 [P] Write tests in `tests/test_smart/test_images.py`: test describe with
  mocked LLM, test image section formatting, test partial success (some fail), test no
  images returns None, test mime type derivation [depends: T006, T017]
- [ ] T019 Integrate --images into pipeline and CLI: extend `convert_file()` in
  `src/to_markdown/core/pipeline.py` to accept `images` parameter, pass
  `extract_images=images` to extraction, call `smart.images.describe_images()` after
  clean/before summary, append image section to content. Add `--images / -i` flag to
  `src/to_markdown/cli.py`. [depends: T015, T016, T017]
- [ ] T020 Write extraction and integration tests: test `extract_file(extract_images=True)`
  in `tests/test_extraction.py`, test pipeline with --images flag in `tests/test_pipeline.py`,
  test CLI --images flag in `tests/test_cli.py` [depends: T016, T019]

**Checkpoint**: `to-markdown file.pdf --images` works with mocked LLM.

---

## Phase 6: Integration (Cross-Feature)

**Purpose**: API key validation, flag combinations, .env loading, combined behavior

- [ ] T021 Add API key validation to CLI: in `src/to_markdown/cli.py`, after `load_dotenv()`,
  check for GEMINI_API_KEY when any smart flag is True. Print clear error with instructions
  and exit with EXIT_ERROR if missing. [depends: T011]
- [ ] T022 Add `load_dotenv()` call to CLI: conditional import of python-dotenv (handle
  ImportError if [llm] not installed), call at start of `main()` before API key check.
  [depends: T001]
- [ ] T023 Write API key validation tests in `tests/test_cli.py`: test missing key error
  message, test exit code, test no error when no smart flags used without key, test key
  loaded from environment [depends: T021, T022]
- [ ] T024 Write flag combination tests: test --clean + --summary processing order in
  `tests/test_pipeline.py`, test all three flags together, test partial failure (clean fails
  but summary/images succeed), test that flags work independently [depends: T015, T019]
- [ ] T025 Update `.env.example` with GEMINI_API_KEY and GEMINI_MODEL entries. Verify
  .env is in .gitignore. [depends: T001]

**Checkpoint**: All smart features work independently and in combination. API key validation
works. All tests pass.

---

## Phase 7: Polish & Documentation

**Purpose**: Final quality pass, docs sync, human testing instructions

- [ ] T026 Update `--help` text: verify Typer docstrings and argument help text for all
  new flags are clear and accurate in `src/to_markdown/cli.py` [depends: T021]
- [ ] T027 Update memory documents: add D-44 through D-54 to
  `.specify/discovery/decisions.md`, update `.specify/memory/glossary.md` with new terms
  (image description section, clean, smart client), update `.specify/memory/tech-stack.md`
  with python-dotenv [depends: T025]
- [ ] T028 Run full quality gate: `uv run ruff check`, `uv run ruff format --check`,
  `uv run pytest` -- verify zero errors, zero failures, no regressions in existing 102 tests
  [depends: T024]
- [ ] T029 Write human testing instructions: create testing checklist with exact commands
  for verifying --clean on a real PDF, --summary on a document, --images on a PDF with
  images, combined flags, and missing API key behavior [depends: T028]

**Checkpoint**: All quality gates pass. Human testing instructions ready.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies -- start immediately
- **Phase 2 (Gemini Client)**: Depends on T002 (constants)
- **Phase 3 (--clean)**: Depends on Phase 2 (client wrapper)
- **Phase 4 (--summary)**: Depends on Phase 2 (client wrapper) and T010 (pipeline extension)
- **Phase 5 (--images)**: Depends on Phase 2 (client wrapper) and T015 (--summary integration, since both modify pipeline.py/cli.py)
- **Phase 6 (Integration)**: Depends on Phases 3, 4, 5
- **Phase 7 (Polish)**: Depends on Phase 6

### Parallel Opportunities

```
Phase 1: T001, T002 parallel; T003 after T002 (both modify constants.py)

Phase 2: T004 + T005 sequential, T006 parallel with T005, T007 after T005+T006

Phase 3-5: After Phase 2 completes:
  - T008 (clean), T013 (summary), T016 (extraction), T017 (images) -- all parallel
  - Tests (T009, T014, T018) parallel with each other after their module
  - Integration (T010, T015, T019) sequential: T010 -> T015 -> T019 (all modify pipeline.py/cli.py)

Phase 6: T021 + T022 parallel, T023-T025 after both
```

### Critical Path

T002 -> T005 -> T008 -> T010 -> T015 -> T019 -> T024 -> T028 -> T029

### Within Each Phase

- Constants before modules (modules import constants)
- Modules before tests (tests import modules)
- Tests before integration (verify modules work before wiring)
- Integration tests after pipeline changes
