# Phase 0125: Smart Pipeline — Discovery

## Codebase Examination

### Current Pipeline Architecture

The conversion pipeline flows through `_build_content()` in `core/pipeline.py`:

```
Input -> Kreuzberg extract -> compose frontmatter -> [clean] -> [images] -> [summary] -> assemble
```

Key observations:
- Clean, images, and summary are **serial**: each waits for the previous to finish
- Clean operates on **text content**, images on **binary data** — they're independent
- Image descriptions loop **sequentially** in `smart/images.py:describe_images()`
- Clean chunks also process **sequentially** in `smart/clean.py:clean_content()`
- Summary depends on cleaned content (must wait for clean)

### LLM Call Sites

| Module | Function | Calls per invocation | Input |
|--------|----------|---------------------|-------|
| `smart/clean.py` | `clean_content()` | 1 per chunk (N chunks for large docs) | Text |
| `smart/images.py` | `describe_images()` | 1 per image (N images) | Binary + prompt |
| `smart/summary.py` | `summarize_content()` | 1 always | Text |

### google-genai Async API

Confirmed `client.aio.models` provides `AsyncModels` class. The async variant:
```python
response = await client.aio.models.generate_content(model=model, contents=contents, config=config)
```
Uses the same Client instance — no separate async client needed.

### Current Flag Defaults

| Flag | Default | Behavior |
|------|---------|----------|
| `--clean` | `False` | Opt-in, requires `GEMINI_API_KEY` |
| `--summary` | `False` | Opt-in, requires `GEMINI_API_KEY` |
| `--images` | `False` | Opt-in, requires `GEMINI_API_KEY` |

### Content Safety

Currently no filtering between extraction and LLM features. Raw Kreuzberg output goes
directly to frontmatter composition and LLM prompts.

### Files That Need Changes

| File | Changes |
|------|---------|
| `core/pipeline.py` | Sanitize step, async orchestration, clean default |
| `core/constants.py` | New constants (sanitize patterns, concurrency, flags) |
| `core/frontmatter.py` | `sanitized` field |
| `core/sanitize.py` | **New** — prompt injection filtering |
| `smart/llm.py` | `generate_async()` function |
| `smart/images.py` | Parallel image descriptions |
| `smart/clean.py` | Parallel chunk cleaning |
| `cli.py` | `--no-clean`, `--no-sanitize` flags, auto-clean logic |
| `mcp/tools.py` | Default `clean=True` for MCP, sanitize parameter |
| `mcp/server.py` | Updated tool parameter defaults |
| `core/batch.py` | Pass through new defaults |
| `core/display.py` | Pass through new flags |
| `core/background.py` | Pass through new flags |

### Test Files That Need Changes/Creation

| File | Purpose |
|------|---------|
| `tests/test_sanitize.py` | **New** — sanitize module tests |
| `tests/test_smart/test_llm.py` | Add async generate tests |
| `tests/test_smart/test_images.py` | Parallel execution tests |
| `tests/test_smart/test_clean.py` | Parallel chunk tests |
| `tests/test_pipeline.py` | Sanitize integration, clean default, async pipeline |
| `tests/test_cli.py` | New flags (`--no-clean`, `--no-sanitize`) |
| `tests/test_mcp_tools.py` | Updated defaults |

## Decisions

### D-76: Clean by default when API key is present
- **Phase**: 0125 - Smart Pipeline
- **Status**: Decided
- **Confidence**: High
- **Context**: The whole point of to-markdown is LLM-optimized output. Clean fixes
  extraction artifacts (word concatenation, spacing, collapsed breaks). Users shouldn't
  need to remember a flag for the core value proposition.
- **Decision**: Auto-enable `--clean` when `GEMINI_API_KEY` is set and the LLM SDK is
  installed. Add `--no-clean` to explicitly disable. `--clean` flag remains but becomes
  a no-op (already the default). When no API key is set, clean is silently skipped
  (core extraction still works offline).
- **Alternatives**: Keep clean opt-in, make all LLM features default
- **Consequences**: Better default output quality. `--summary` and `--images` remain
  opt-in because they add new content (clean only fixes existing content). Users who
  want fast offline conversion use `--no-clean`.

### D-77: Sanitize by default, --no-sanitize to opt out
- **Phase**: 0125 - Smart Pipeline
- **Status**: Decided
- **Confidence**: High
- **Context**: PDF hidden text injection is a known attack vector for LLM-targeted
  pipelines. Our output is explicitly "optimized for LLM consumption."
- **Decision**: Apply content sanitization after Kreuzberg extraction, before any LLM
  features. Strip: zero-width Unicode chars, RTL/LTR overrides, null/control bytes,
  invisible Unicode categories. Log warnings at INFO level. Add `sanitized: true` to
  YAML frontmatter when content was modified. `--no-sanitize` to disable.
- **Alternatives**: Opt-in only, block conversion on detection
- **Consequences**: Safer default for LLM consumption. Minimal false positives since we
  only strip clearly non-visible characters. `--no-sanitize` available for forensic use.

### D-78: Parallel LLM via asyncio.gather with semaphore
- **Phase**: 0125 - Smart Pipeline
- **Status**: Decided
- **Confidence**: High
- **Context**: 20-image PDF makes 20 serial API calls. Each is 500ms-2s. Total wait:
  10-40 seconds. This is pure I/O wait, perfectly parallelizable.
- **Decision**: Add `generate_async()` in `smart/llm.py` using `client.aio.models`.
  Use `asyncio.gather()` + `asyncio.Semaphore(PARALLEL_LLM_MAX_CONCURRENCY)` to limit
  concurrent calls. Parallelize: image descriptions, clean chunks. Pipeline runs clean
  and images concurrently (independent data). Summary waits for clean. Use
  `asyncio.run()` at pipeline boundary; keep CLI/MCP interfaces synchronous.
- **Alternatives**: ThreadPoolExecutor, multiprocessing, sequential (current)
- **Consequences**: ~4x speedup on image-heavy docs (with concurrency=5 and 20 images).
  asyncio is stdlib (no new deps). google-genai has native async support.

### D-79: Sanitize scope — character-level only, not content-level
- **Phase**: 0125 - Smart Pipeline
- **Status**: Decided
- **Confidence**: High
- **Context**: OpenDataLoader PDF filters "suspicious instruction patterns" (e.g.,
  "ignore previous instructions"). This is fragile and creates false positives on
  legitimate content about prompt engineering, AI safety, etc.
- **Decision**: Sanitize at the character level only: zero-width chars, control chars,
  RTL/LTR overrides, null bytes. Do NOT filter based on text content/patterns. Content
  filtering is too subjective and would break legitimate documents.
- **Alternatives**: Content pattern matching, ML-based detection
- **Consequences**: No false positives on legitimate content. Catches the most common
  injection vectors (invisible chars). Users who want content-level filtering can
  post-process the output.

### D-80: Pipeline becomes async internally
- **Phase**: 0125 - Smart Pipeline
- **Status**: Decided
- **Confidence**: Medium-High
- **Context**: To parallelize clean + images, the pipeline needs async orchestration.
  But the CLI and MCP interfaces should remain synchronous for simplicity.
- **Decision**: Add `_build_content_async()` as the new core function. `_build_content()`
  becomes a thin wrapper: `asyncio.run(_build_content_async(...))`. This keeps all
  external interfaces synchronous while enabling internal parallelism.
- **Alternatives**: Keep sync pipeline and only parallelize within each feature,
  use threads instead of asyncio
- **Consequences**: Clean + images can run concurrently. No external API changes.
  asyncio.run() has minimal overhead for sync callers. Tests can use pytest-asyncio
  or simply call the sync wrappers.
