# Phase 0125: Smart Pipeline — Specification

## Overview

Harden the to-markdown pipeline for security, quality, and performance. Three features:
clean by default, prompt injection sanitization, and parallel LLM calls.

## Requirements

### R1: Clean by Default

**R1.1**: When `GEMINI_API_KEY` is set and the `google-genai` SDK is installed, content
cleaning runs automatically without any flag.

**R1.2**: `--no-clean` flag disables automatic cleaning.

**R1.3**: `--clean` / `-c` flag remains accepted but is a no-op when clean is already
the default. No warning or error for using it.

**R1.4**: When no API key is set, clean is silently skipped. Core extraction works
offline with no errors or warnings about missing clean.

**R1.5**: `--summary` and `--images` remain opt-in only (they add new content; clean
only fixes existing content).

**R1.6**: MCP `convert_file` and `convert_batch` tools default to `clean=True` when
API key is available.

**R1.7**: Batch processing respects clean-by-default behavior.

**R1.8**: Background processing (`--bg`) respects clean-by-default behavior.

### R2: Prompt Injection Sanitization

**R2.1**: New `core/sanitize.py` module that strips non-visible characters from
extracted content.

**R2.2**: Characters removed: zero-width Unicode (U+200B, U+200C, U+200D, U+FEFF),
RTL/LTR directional overrides (U+202A-U+202E, U+2066-U+2069), null bytes (U+0000),
control characters (U+0001-U+0008, U+000E-U+001F, U+007F), and Unicode category Cf
(format characters) excluding standard whitespace.

**R2.3**: Sanitization runs after Kreuzberg extraction, before clean/LLM features.
Position in pipeline: `extract -> sanitize -> frontmatter -> clean -> images -> summary`.

**R2.4**: When content is modified by sanitization, add `sanitized: true` to YAML
frontmatter.

**R2.5**: Log at INFO level when characters are stripped, including count of removed
characters. Example: `"Sanitized: removed 42 non-visible characters"`.

**R2.6**: `--no-sanitize` flag disables sanitization entirely.

**R2.7**: Sanitization is on by default (no flag needed to enable). No API key required.

**R2.8**: Sanitization must not modify visible content. Only non-visible/control
characters are removed.

### R3: Parallel LLM Calls

**R3.1**: New `generate_async()` function in `smart/llm.py` using
`client.aio.models.generate_content()`.

**R3.2**: Same retry logic as sync `generate()` (tenacity, exponential backoff).

**R3.3**: Image descriptions dispatched concurrently via `asyncio.gather()` with
`asyncio.Semaphore(PARALLEL_LLM_MAX_CONCURRENCY)`.

**R3.4**: Clean chunks dispatched concurrently via same mechanism.

**R3.5**: In `_build_content()`, clean and images run concurrently (independent data
streams). Summary waits for clean to complete.

**R3.6**: Pipeline entry points (`convert_file`, `convert_to_string`) remain
synchronous. Async orchestration is internal only via `asyncio.run()`.

**R3.7**: `PARALLEL_LLM_MAX_CONCURRENCY` constant defaults to 5. Prevents rate
limiting from too many concurrent Gemini calls.

**R3.8**: Error handling: individual image/chunk failures don't crash the batch.
Failed items are logged and skipped, same as current behavior.

## Non-Requirements

- Content-level prompt injection detection (pattern matching like "ignore previous
  instructions") — too many false positives (D-79)
- Cross-document parallelism in batch mode — batch already has progress handling
- Making CLI async — keep Typer CLI synchronous
- New dependencies — asyncio is stdlib, google-genai has native async
- Parallelizing summary — single call, always depends on cleaned content

## Acceptance Criteria

1. `to-markdown file.pdf` with API key set produces cleaned output (no `--clean` needed)
2. `to-markdown file.pdf --no-clean` skips cleaning even with API key
3. `to-markdown file.pdf` without API key works offline (clean silently skipped)
4. Content with zero-width chars has them stripped, frontmatter shows `sanitized: true`
5. `to-markdown file.pdf --no-sanitize` preserves all original characters
6. 20-image PDF completes in ~4-5 API call durations, not 20 serial durations
7. All existing tests pass (no regressions)
8. `--help` text reflects new behavior
