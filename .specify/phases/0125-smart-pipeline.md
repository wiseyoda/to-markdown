---
phase: 0125
name: smart-pipeline
status: not_started
created: 2026-02-27
updated: 2026-02-27
---

# Phase 0125: Smart Pipeline Improvements

**Goal**: Harden the LLM pipeline for security, quality, and performance. Make `--clean`
the default behavior when a Gemini API key is available, add prompt injection filtering for
LLM-bound output, and parallelize API calls to eliminate the serial bottleneck on
image-heavy documents.

---

## 1. Clean by Default

Currently `--clean` is opt-in. Since the whole point of to-markdown is LLM-optimized
output, clean should be the default behavior when `GEMINI_API_KEY` is set.

**Changes**:

- Auto-enable clean when API key is present (no flag needed)
- Add `--no-clean` flag to explicitly disable cleaning
- `--clean` flag becomes a no-op (already the default) but remains for backwards compat
- When no API key is set, skip clean silently (core extraction still works offline)
- Update MCP `convert_file` and `convert_to_string` tools to default `clean=True`
- Update batch processing to respect the new default
- Update `--help` text to reflect the new behavior

**Key design question**: Should `--summary` and `--images` also auto-enable when the API
key is present? Recommend: **no** -- clean is non-destructive (fixes artifacts), while
summary and images add new content. Keep those opt-in.

## 2. Prompt Injection Filtering

PDFs and other documents can contain hidden text layers, invisible elements, and off-page
content designed to inject malicious prompts into LLM contexts. Since our output is
explicitly "optimized for LLM consumption," this is a direct attack surface.

**Changes**:

- Add `src/to_markdown/core/sanitize.py` module
- Filter known prompt injection vectors from extracted content:
  - Invisible/hidden text (zero-size fonts, white-on-white, off-page positioned text)
  - Suspicious instruction patterns (e.g., "ignore previous instructions", "system prompt")
  - Null bytes, control characters, and Unicode abuse (RTL overrides, zero-width chars)
- Apply sanitization in `_build_content()` after extraction, before clean/LLM features
- Add `--no-sanitize` flag to disable filtering (for debugging/forensic use)
- Sanitize by default (no flag needed to enable)
- Log warnings when content is stripped (at INFO level) so users know filtering occurred
- Add `sanitized: true` field to YAML frontmatter when filtering was applied
- Add constants to `constants.py`: patterns, character lists, thresholds

**What NOT to do**:

- Don't try to catch every possible injection -- focus on the well-known PDF-specific
  vectors (hidden text layers, invisible fonts, off-page content)
- Don't modify visible content -- only strip content that is clearly hidden/malicious
- Don't block conversion on detection -- strip and warn, always produce output

## 3. Parallel LLM Calls

Image-heavy documents are slow because each image description is a serial API call.
A 20-image PDF makes 20 sequential round-trips to Gemini. With network latency of
~500ms-2s per call, that's 10-40 seconds of pure wait time.

**Changes**:

- Add `asyncio`-based concurrent API calls in `smart/images.py`
  - Use `asyncio.gather()` with a semaphore to limit concurrency
  - Add `PARALLEL_LLM_MAX_CONCURRENCY` constant (default: 5) to avoid rate limiting
- Add async variant of `generate()` in `smart/llm.py` (`generate_async()`)
  - google-genai SDK supports `await client.aio.models.generate_content()`
  - Retry logic via tenacity works with async (`@retry` on async functions)
- Parallelize image descriptions: all images dispatched concurrently (up to semaphore limit)
- Parallelize clean chunks: when content is chunked, clean chunks concurrently
- Summary remains serial (single call, depends on cleaned content)
- Pipeline orchestration in `_build_content()`:
  - Clean and images can run in parallel (clean operates on text, images on binary data)
  - Summary must wait for clean to finish (it summarizes cleaned content)
  - Use `asyncio.run()` at the pipeline entry point; keep CLI/MCP interfaces synchronous
- Add `PARALLEL_LLM_MAX_CONCURRENCY` and `PARALLEL_LLM_SEMAPHORE_TIMEOUT` to constants.py
- Progress logging: "Describing images (5 concurrent)..." instead of per-image logs

**Performance target**: A 20-image document should complete in roughly the time of
4-5 serial calls (with concurrency=5), not 20 serial calls. ~4x speedup on image-heavy
docs.

**What NOT to do**:

- Don't add aiohttp or other async HTTP libraries -- google-genai has built-in async
- Don't make the CLI async -- use `asyncio.run()` at the boundary
- Don't parallelize across documents in batch mode here (batch already has its own
  progress handling; cross-document parallelism is a separate concern)

---

## Deliverables

- [ ] `--clean` enabled by default when API key is present
- [ ] `--no-clean` flag to opt out
- [ ] `src/to_markdown/core/sanitize.py` with prompt injection filtering
- [ ] `--no-sanitize` flag for debugging
- [ ] `sanitized: true` frontmatter field when filtering is applied
- [ ] `generate_async()` in `smart/llm.py`
- [ ] Parallel image descriptions via `asyncio.gather()` + semaphore
- [ ] Parallel clean chunks
- [ ] Clean + images run concurrently in pipeline
- [ ] All existing tests pass (no regressions)
- [ ] New tests for sanitization (hidden text, control chars, Unicode abuse)
- [ ] New tests for parallel execution (mock concurrent calls)
- [ ] New tests for clean-by-default behavior
- [ ] Updated `--help` text, README, and memory docs
- [ ] Constants in `constants.py` (no magic numbers)

## Verification Gate

**USER GATE**: Run `to-markdown` on a real PDF with images -- confirm clean runs by
default, sanitization warnings appear in verbose mode, and image descriptions complete
noticeably faster than before. Run `to-markdown --no-clean --no-sanitize` to confirm
opt-out works. All tests pass.

## Estimated Complexity

Medium-High (async plumbing + security filtering + default behavior change across
CLI/MCP/batch)
