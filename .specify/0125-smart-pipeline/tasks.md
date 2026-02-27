# Phase 0125: Smart Pipeline — Tasks

## Section 1: Constants and Sanitization

### T001: Add all new constants [P]
- **Files**: `src/to_markdown/core/constants.py`
- **Description**: Add all new constants for this phase in one task:
  - Sanitization: `SANITIZE_ZERO_WIDTH_CHARS` (frozenset), `SANITIZE_CONTROL_CHARS`
    (frozenset), `SANITIZE_DIRECTIONAL_CHARS` (frozenset)
  - Parallel LLM: `PARALLEL_LLM_MAX_CONCURRENCY = 5`
- **Tests**: None (constants only)
- **Acceptance**: All constants importable, ruff check passes

### T002: Create sanitize module [S]
- **Files**: `src/to_markdown/core/sanitize.py`
- **Description**: New module with `sanitize_content(content: str) -> SanitizeResult`
  dataclass (content, chars_removed, was_modified). Strip zero-width, control, and
  directional chars using sets from constants.py. Log at INFO when chars removed,
  including count: `"Sanitized: removed %d non-visible characters"`.
- **Tests**: `tests/test_sanitize.py`
- **Acceptance**: `sanitize_content("hello\u200bworld")` returns
  `SanitizeResult(content="helloworld", chars_removed=1, was_modified=True)`
- **Depends**: T001

### T003: Write sanitize tests [S]
- **Files**: `tests/test_sanitize.py`
- **Description**: Test cases:
  - Clean content passes through unchanged (was_modified=False)
  - Zero-width chars stripped (U+200B, U+200C, U+200D, U+FEFF)
  - Control chars stripped (U+0000-U+0008, U+000E-U+001F, U+007F)
  - Directional overrides stripped (U+202A-U+202E, U+2066-U+2069)
  - Normal whitespace preserved (spaces, tabs, newlines)
  - Mixed content: visible + invisible chars
  - Empty string input
  - chars_removed count is accurate
  - Unicode letters, CJK, emoji preserved
  - Verify INFO log message emitted when chars removed
- **Acceptance**: All tests pass, covers edge cases
- **Depends**: T001, T002

## Section 2: Clean by Default + Sanitize Integration

### T004: Add sanitized field to frontmatter [P]
- **Files**: `src/to_markdown/core/frontmatter.py`, `tests/test_frontmatter.py`
- **Description**: Add `sanitized: bool = False` parameter to `compose_frontmatter()`.
  When True, add `sanitized: true` to YAML output (before `extracted_at`). Add test
  cases: `compose_frontmatter(metadata, path, sanitized=True)` includes
  `sanitized: true`; `sanitized=False` (default) omits the field.
- **Acceptance**: Frontmatter includes `sanitized: true` only when parameter is True
- **Depends**: None

### T005: Add sanitize parameter to pipeline [S]
- **Files**: `src/to_markdown/core/pipeline.py`
- **Description**: Add `sanitize: bool = True` param to `convert_file()`,
  `convert_to_string()`, and `_build_content()`. Call `sanitize_content()` after
  extraction, before frontmatter. Pass `sanitize_result.was_modified` as `sanitized`
  to `compose_frontmatter()`.
- **Tests**: `tests/test_pipeline.py`
- **Acceptance**: Pipeline sanitizes by default, `sanitize=False` skips it
- **Depends**: T002, T004

### T006: Add --no-clean and --no-sanitize CLI flags [S]
- **Files**: `src/to_markdown/cli.py`
- **Description**: Add `--no-clean` and `--no-sanitize` Typer options (both default
  False). If cli.py approaches 300-line limit, extract `_compute_effective_flags()`
  helper into `core/flags.py`. Update help text for `--clean`: "Enabled by default
  when GEMINI_API_KEY is set." Update help text for new flags.
- **Tests**: `tests/test_cli.py`
- **Acceptance**: `--help` shows new flags
- **Depends**: T005

### T007: Update CLI clean-by-default logic [S]
- **Files**: `src/to_markdown/cli.py`
- **Description**: In `main()`, compute effective clean: if `--no-clean` not passed
  and API key is set and LLM SDK is importable, then `clean=True`. Pass
  `sanitize=not no_sanitize` to `convert_file()` and `run_batch()`. Update
  `_validate_api_key()` to only check for summary/images (clean auto-disables
  when LLM unavailable, no validation needed).
- **Tests**: `tests/test_cli.py`
- **Acceptance**: `to-markdown file.pdf` with API key runs clean. Without API key,
  no error. `--no-clean` skips clean.
- **Depends**: T006

### T008: Write clean-by-default CLI tests [S]
- **Files**: `tests/test_cli.py`
- **Description**: Test cases:
  - With API key set: clean runs by default (mock pipeline, verify clean=True)
  - With `--no-clean`: clean=False even with API key
  - Without API key: clean silently skipped (no error)
  - Without LLM SDK: clean silently skipped (no error)
  - `--clean` flag still accepted (no error, no change)
  - `--no-sanitize` passes sanitize=False to pipeline
  - Summary/images still require explicit flags and API key
- **Acceptance**: All new tests pass
- **Depends**: T007

## Section 3: Async LLM Infrastructure

### T009: Add generate_async to smart/llm.py [P]
- **Files**: `src/to_markdown/smart/llm.py`
- **Description**: Add `generate_async()` and `_generate_with_retry_async()` functions.
  Use `client.aio.models.generate_content()`. Apply same tenacity retry decorator
  (tenacity @retry works on async functions natively). Same parameters and return
  type as sync version. IMPORTANT: async functions must NEVER call `asyncio.run()`
  themselves — they are awaited from the pipeline.
- **Tests**: `tests/test_smart/test_llm.py`
- **Acceptance**: `await generate_async("test")` works with mocked client
- **Depends**: None

### T011: Write async generate tests [S]
- **Files**: `tests/test_smart/test_llm.py`
- **Description**: Test cases:
  - Successful async generation returns text
  - Async retry on 429/503 errors
  - Async raises LLMError on non-retryable failure
  - Empty response raises LLMError
- **Acceptance**: All async tests pass
- **Depends**: T009

## Section 4: Parallel Image Descriptions

### T012: Add describe_images_async [S]
- **Files**: `src/to_markdown/smart/images.py`
- **Description**: Add `describe_images_async()` that dispatches all image descriptions
  concurrently via `asyncio.gather()` with `asyncio.Semaphore(PARALLEL_LLM_MAX_CONCURRENCY)`.
  Add `_describe_single_image_async()` using `generate_async()`. Individual image
  failures are logged (via `logger.warning`) and skipped — never crash the batch.
  Keep sync `describe_images()` for direct/test use.
- **Tests**: `tests/test_smart/test_images.py`
- **Acceptance**: Multiple images described concurrently (mock verifies parallel dispatch)
- **Depends**: T001, T009

### T013: Write parallel image tests [S]
- **Files**: `tests/test_smart/test_images.py`
- **Description**: Test cases:
  - Multiple images processed concurrently (verify gather called)
  - Semaphore limits concurrency to PARALLEL_LLM_MAX_CONCURRENCY
  - Individual failures don't crash batch (still get other descriptions)
  - Failed items logged via logger.warning
  - Empty images list returns None
  - Single image works (no unnecessary parallelism overhead)
- **Acceptance**: All tests pass, verify concurrent execution and error logging
- **Depends**: T012

## Section 5: Parallel Clean Chunks and Async Summary

### T014: Add clean_content_async [S]
- **Files**: `src/to_markdown/smart/clean.py`
- **Description**: Add `clean_content_async()` that chunks content and dispatches
  chunks concurrently via `asyncio.gather()` with semaphore. Single-chunk case
  skips parallelism. Fallback to original content on LLMError (logged via
  `logger.warning`).
- **Tests**: `tests/test_smart/test_clean.py`
- **Acceptance**: Multi-chunk content cleaned concurrently
- **Depends**: T001, T009

### T015: Write parallel clean tests [S]
- **Files**: `tests/test_smart/test_clean.py`
- **Description**: Test cases:
  - Single chunk: no unnecessary parallelism
  - Multi-chunk: all chunks processed concurrently
  - LLM failure: falls back to original content, logs warning
  - Empty content: returns unchanged
- **Acceptance**: All tests pass
- **Depends**: T014

### T016: Add summarize_content_async [P]
- **Files**: `src/to_markdown/smart/summary.py`
- **Description**: Add `summarize_content_async()` using `generate_async()`. Same
  logic as sync version but awaitable. Keep sync version for direct/test use.
- **Tests**: `tests/test_smart/test_summary.py`
- **Acceptance**: Async summarization works with mocked client
- **Depends**: T009

### T016b: Write async summary tests [S]
- **Files**: `tests/test_smart/test_summary.py`
- **Description**: Test cases:
  - Successful async summary returns text
  - LLM failure returns None (graceful fallback)
  - Empty content returns None
  - format_summary_section wraps correctly (existing, verify not broken)
- **Acceptance**: All summary tests pass
- **Depends**: T016

## Section 6: Async Pipeline Orchestration

### T017: Make pipeline async internally [S]
- **Files**: `src/to_markdown/core/pipeline.py`
- **Description**: Add `_build_content_async()` that runs clean + images concurrently
  via `asyncio.gather()`, then summary sequentially (depends on cleaned content).
  `_build_content()` becomes `return asyncio.run(_build_content_async(...))`.
  CRITICAL: `asyncio.run()` is called ONLY in `_build_content()`. All internal async
  functions are awaited, never calling `asyncio.run()` themselves. Keep
  `convert_file()` and `convert_to_string()` synchronous.
- **Tests**: `tests/test_pipeline.py`
- **Acceptance**: Pipeline produces same output as before. Clean + images run
  concurrently when both enabled.
- **Depends**: T005, T012, T014, T016

### T018: Write async pipeline tests [S]
- **Files**: `tests/test_pipeline.py`
- **Description**: Test cases:
  - Sanitize + clean + images + summary: all features work together
  - Clean + images run concurrently (mock timing or call order)
  - Summary waits for clean (verify order)
  - sanitize=False skips sanitization
  - clean=False skips clean
  - No LLM features: pipeline works without async overhead
  - Frontmatter includes `sanitized: true` when content was sanitized
- **Acceptance**: All pipeline tests pass
- **Depends**: T017

## Section 7: MCP, Batch, Background Pass-Through

### T019: Update MCP tools for new defaults [S]
- **Files**: `src/to_markdown/mcp/tools.py`, `src/to_markdown/mcp/server.py`,
  `src/to_markdown/mcp/background_tools.py`
- **Description**: `handle_convert_file()` and `handle_convert_batch()`: add
  `sanitize: bool = True` param. For clean default: if `clean=True` (default) but
  LLM is unavailable (no SDK or no API key), silently skip clean (do not raise error).
  If `clean=False`, skip clean. Remove `clean` from `_validate_llm_flags()` — only
  validate for summary/images. Update `handle_start_conversion()` in
  `background_tools.py` to accept and pass through `sanitize` parameter.
  Update server.py tool definitions with updated parameter descriptions.
- **Tests**: `tests/test_mcp_tools.py`
- **Acceptance**: MCP convert defaults to clean=True with API key, sanitize=True.
  Clean silently skipped when LLM unavailable.
- **Depends**: T017

### T020: Update batch and display for new flags [S]
- **Files**: `src/to_markdown/core/batch.py`, `src/to_markdown/core/display.py`
- **Description**: Add `sanitize: bool = True` parameter to `convert_batch()` and
  `run_batch()`. Pass through to `convert_file()`. CLI passes
  `sanitize=not no_sanitize` via T007.
- **Tests**: Existing batch tests (may need minor updates)
- **Acceptance**: Batch passes sanitize flag through correctly
- **Depends**: T017

### T021: Update background processing for new flags [S]
- **Files**: `src/to_markdown/core/background.py`, `src/to_markdown/core/worker.py`
- **Description**: In `handle_background()`, add `no_sanitize` to `command_args` JSON.
  In `run_worker()` (worker.py), deserialize `no_sanitize` from `command_args` and
  pass `sanitize=not no_sanitize` to `convert_file()`/`convert_batch()`. Also handle
  clean-by-default: if `clean` not explicitly set in args, auto-enable when API key
  is available.
- **Tests**: Existing background tests
- **Acceptance**: Background tasks respect new flags, worker passes sanitize correctly
- **Depends**: T017

### T022: Write MCP and integration tests [S]
- **Files**: `tests/test_mcp_tools.py`
- **Description**: Test cases:
  - convert_file defaults clean=True, sanitize=True
  - convert_file with clean=True but no API key: clean silently skipped
  - convert_file with sanitize=False skips sanitization
  - convert_batch respects new defaults
  - start_conversion passes sanitize parameter through
- **Acceptance**: All MCP tests pass
- **Depends**: T019

## Section 8: Documentation and Cleanup

### T023: Update --help text and README [S]
- **Files**: `src/to_markdown/cli.py`, `README.md`
- **Description**: Update all flag help strings. `--clean` help: "Enabled by default
  when GEMINI_API_KEY is set. This flag is a no-op." Add `--no-clean` and
  `--no-sanitize` to README usage section. Document new default behavior.
- **Acceptance**: `--help` is accurate, README matches current behavior
- **Depends**: T007

### T024: Run full test suite and lint [S]
- **Files**: All
- **Description**: Run `uv run pytest`, `uv run ruff check`, `uv run ruff format --check`.
  Fix any failures. Verify all 362+ existing tests still pass plus new tests.
- **Acceptance**: Zero failures, zero lint errors
- **Depends**: T018, T022

### T025: Update memory documents [S]
- **Files**: `.specify/memory/coding-standards.md`, `.specify/memory/tech-stack.md`,
  `.specify/discovery/decisions.md`
- **Description**: Update coding-standards with new `core/sanitize.py` module.
  Add async patterns note. Update tech-stack if any version changes needed.
  Record decisions D-76 through D-80 in decisions.md.
- **Acceptance**: Memory docs reflect current architecture
- **Depends**: T024

## Task Dependency Graph

```
T001 ──→ T002 ──→ T003
  │        └──→ T005 ──→ T017 ──→ T018
  │                │        │──→ T019 ──→ T022
  │                │        │──→ T020
  │                │        └──→ T021
  │                └──→ T006 ──→ T007 ──→ T008
  │                                 └──→ T023
  ├──→ T012 ──→ T013
  └──→ T014 ──→ T015
T004 (no deps — frontmatter)
T009 ──→ T011
  │──→ T012
  │──→ T014
  └──→ T016 ──→ T016b
T024 ──→ T025
```

## Parallelization Batches

Tasks marked [P] can run in the first batch (no dependencies or independent deps):
- **Batch 1**: T001, T004, T009, T016 (all independent)
- **Batch 2**: T002, T012, T014, T016b (depend on batch 1)
- **Batch 3**: T003, T005, T011, T013, T015 (depend on batch 2)
- **Batch 4**: T006, T017 (depend on batch 3)
- **Batch 5**: T007, T018 (depend on batch 4)
- **Batch 6**: T008, T019, T020, T021, T023 (depend on batch 5)
- **Batch 7**: T022, T024 (depend on batch 6)
- **Batch 8**: T025 (depend on batch 7)

## Task Summary

| ID | Description | Status | Section |
|----|------------|--------|---------|
| T001 | Add all new constants | [ ] | 1 |
| T002 | Create sanitize module | [ ] | 1 |
| T003 | Write sanitize tests | [ ] | 1 |
| T004 | Add sanitized field to frontmatter | [ ] | 2 |
| T005 | Add sanitize parameter to pipeline | [ ] | 2 |
| T006 | Add --no-clean and --no-sanitize CLI flags | [ ] | 2 |
| T007 | Update CLI clean-by-default logic | [ ] | 2 |
| T008 | Write clean-by-default CLI tests | [ ] | 2 |
| T009 | Add generate_async to smart/llm.py | [ ] | 3 |
| T011 | Write async generate tests | [ ] | 3 |
| T012 | Add describe_images_async | [ ] | 4 |
| T013 | Write parallel image tests | [ ] | 4 |
| T014 | Add clean_content_async | [ ] | 5 |
| T015 | Write parallel clean tests | [ ] | 5 |
| T016 | Add summarize_content_async | [ ] | 5 |
| T016b | Write async summary tests | [ ] | 5 |
| T017 | Make pipeline async internally | [ ] | 6 |
| T018 | Write async pipeline tests | [ ] | 6 |
| T019 | Update MCP tools for new defaults | [ ] | 7 |
| T020 | Update batch and display for new flags | [ ] | 7 |
| T021 | Update background processing for new flags | [ ] | 7 |
| T022 | Write MCP and integration tests | [ ] | 7 |
| T023 | Update --help text and README | [ ] | 8 |
| T024 | Run full test suite and lint | [ ] | 8 |
| T025 | Update memory documents | [ ] | 8 |
