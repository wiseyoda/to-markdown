# Phase 0125: Smart Pipeline — Plan

## Architecture Changes

### Pipeline Flow (Before)

```
Input -> extract -> frontmatter -> [clean] -> [images] -> [summary] -> assemble
                                   (serial)   (serial)    (serial)
```

### Pipeline Flow (After)

```
Input -> extract -> sanitize -> frontmatter -> [clean + images] -> [summary] -> assemble
                    (always)                   (parallel async)    (depends on clean)
```

### Key Design Decisions

1. **Sanitize before frontmatter** — clean content before metadata composition
2. **Clean + images concurrent** — clean operates on text, images on binary data
3. **Summary after clean** — needs the cleaned content as input
4. **asyncio.run() at boundary** — keep all external APIs synchronous
5. **Semaphore for rate limiting** — max 5 concurrent Gemini calls

## Implementation Plan

### Section 1: Content Sanitization (core/sanitize.py)

**New file**: `src/to_markdown/core/sanitize.py` (~60 lines)

```python
# Public API:
def sanitize_content(content: str) -> SanitizeResult:
    """Strip non-visible characters from extracted content."""
    # Returns dataclass with cleaned content + stats (chars_removed, was_modified)
```

**Constants** (in `constants.py`):
- `SANITIZE_ZERO_WIDTH_CHARS`: frozenset of zero-width Unicode codepoints
- `SANITIZE_CONTROL_CHARS`: frozenset of control character codepoints
- `SANITIZE_DIRECTIONAL_CHARS`: frozenset of RTL/LTR override codepoints

**Integration point**: Called in `_build_content()` after `extract_file()`, before
frontmatter composition. Result's `was_modified` flag drives `sanitized: true` in
frontmatter.

### Section 2: Clean by Default

**Changes to `cli.py`**:
- Add `--no-clean` flag (Typer option, default False)
- Compute effective clean: `effective_clean = (not no_clean) and _has_llm_available()`
  unless `--no-clean` is passed
- `--clean` flag remains but doesn't change behavior (clean is already the default)
- Update `_validate_api_key()` to only validate when summary or images requested
  (clean auto-disables when key is missing, so no validation needed)

**Changes to `core/pipeline.py`**:
- `_build_content()` gains `sanitize: bool = True` parameter
- Sanitize step inserted before frontmatter
- `sanitized` flag passed to `compose_frontmatter()`

**Changes to `core/frontmatter.py`**:
- Accept optional `sanitized: bool = False` parameter
- Add `sanitized: true` to YAML when True

**Changes to `mcp/tools.py`**:
- `handle_convert_file()` defaults `clean=True`
- `handle_convert_batch()` defaults `clean=True`
- Add `sanitize` parameter (default True)
- Auto-skip clean if LLM not available (same logic as CLI)

### Section 3: Async LLM Infrastructure (smart/llm.py)

**New function**: `generate_async()` — mirrors `generate()` but uses
`client.aio.models.generate_content()`.

**Internal**: `_generate_with_retry_async()` — async version with tenacity retry.

**Note**: tenacity's `@retry` decorator works on async functions out of the box.

### Section 4: Parallel Image Descriptions (smart/images.py)

**New function**: `describe_images_async()` — replaces the sequential loop with
`asyncio.gather()`.

```python
async def describe_images_async(images: list[dict]) -> str | None:
    semaphore = asyncio.Semaphore(PARALLEL_LLM_MAX_CONCURRENCY)
    tasks = [_describe_single_image_async(img, semaphore) for img in images]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # Process results, skip failures
```

**Keep sync `describe_images()` as thin wrapper** for backwards compatibility:
```python
def describe_images(images: list[dict]) -> str | None:
    return asyncio.run(describe_images_async(images))
```

Wait — this would nest `asyncio.run()` if called from an already-async context.
Better approach: make the pipeline async and only call `asyncio.run()` once at the
top level. The sync `describe_images()` stays for direct testing but the pipeline
calls the async version.

### Section 5: Parallel Clean Chunks (smart/clean.py)

**New function**: `clean_content_async()` — chunks content, then dispatches all chunks
concurrently via `asyncio.gather()`.

```python
async def clean_content_async(content: str, format_type: str) -> str:
    chunks = _chunk_content(content, MAX_CLEAN_TOKENS * CHARS_PER_TOKEN_ESTIMATE)
    if len(chunks) == 1:
        # Single chunk, no parallelism needed
        return await _clean_single_chunk_async(chunks[0], format_type)
    semaphore = asyncio.Semaphore(PARALLEL_LLM_MAX_CONCURRENCY)
    tasks = [_clean_single_chunk_async(c, format_type, semaphore) for c in chunks]
    results = await asyncio.gather(*tasks)
    return "\n\n".join(results)
```

### Section 6: Async Pipeline Orchestration (core/pipeline.py)

**New internal function**: `_build_content_async()`

```python
async def _build_content_async(input_path, *, sanitize, clean, summary, images):
    result = extract_file(input_path, extract_images=images)  # sync (CPU-bound)

    content = result.content
    if sanitize:
        sanitize_result = sanitize_content(content)
        content = sanitize_result.content

    frontmatter = compose_frontmatter(result.metadata, input_path, sanitized=...)

    # Parallel: clean + images
    tasks = []
    if clean:
        tasks.append(clean_content_async(content, format_type))
    if images and result.images:
        tasks.append(describe_images_async(result.images))

    results = await asyncio.gather(*tasks)
    # Unpack results based on which tasks were submitted

    if summary:
        summary_text = await summarize_content_async(content, format_type)

    # Assemble
```

**`_build_content()` becomes**:
```python
def _build_content(...):
    return asyncio.run(_build_content_async(...))
```

### Section 7: CLI and Flag Updates

**New flags in `cli.py`**:
- `--no-clean`: `bool = False` — disable auto-clean
- `--no-sanitize`: `bool = False` — disable sanitization

**Logic change**: Remove `clean` from `_validate_api_key()` check. Clean auto-disables
when LLM is unavailable. Only validate for `summary` and `images`.

**Help text updates**: All flags updated to reflect new defaults.

### Section 8: Batch, Background, MCP Pass-Through

All call sites that pass `clean`, `summary`, `images` to `convert_file()` or
`convert_to_string()` need to also pass `sanitize` parameter.

- `core/batch.py`: Add `sanitize` parameter to `convert_batch()`
- `core/display.py`: Pass through `no_sanitize` from CLI
- `core/background.py`: Pass through new flags
- `mcp/tools.py`: Default `clean=True`, add `sanitize` param
- `mcp/server.py`: Updated tool definitions
- `mcp/background_tools.py`: Pass through new flags

## File Change Summary

| File | Lines Changed (est.) | Type |
|------|---------------------|------|
| `core/sanitize.py` | ~80 | New |
| `core/constants.py` | ~25 | Modify |
| `core/pipeline.py` | ~80 | Modify (major) |
| `core/frontmatter.py` | ~5 | Modify |
| `smart/llm.py` | ~40 | Modify |
| `smart/images.py` | ~40 | Modify |
| `smart/clean.py` | ~30 | Modify |
| `smart/summary.py` | ~20 | Modify |
| `cli.py` | ~30 | Modify |
| `mcp/tools.py` | ~15 | Modify |
| `mcp/server.py` | ~10 | Modify |
| `mcp/background_tools.py` | ~10 | Modify |
| `core/batch.py` | ~5 | Modify |
| `core/display.py` | ~5 | Modify |
| `core/background.py` | ~10 | Modify |
| `tests/test_sanitize.py` | ~120 | New |
| `tests/test_smart/test_llm.py` | ~40 | Modify |
| `tests/test_smart/test_images.py` | ~40 | Modify |
| `tests/test_smart/test_clean.py` | ~30 | Modify |
| `tests/test_pipeline.py` | ~40 | Modify |
| `tests/test_cli.py` | ~30 | Modify |
| `tests/test_mcp_tools.py` | ~20 | Modify |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Nested asyncio.run() | Medium | High | Single asyncio.run() at pipeline boundary only |
| Rate limiting with 5 concurrent | Low | Medium | Semaphore + existing tenacity retry |
| Sanitize strips visible chars | Low | High | Only strip Unicode Cf category + explicit list |
| Existing tests break | Medium | Medium | Run full suite after each section |
| 300-line limit exceeded | Medium | Low | pipeline.py is 168 lines, ~80 added = ~248. Safe. |

## Dependencies

- No new external dependencies (asyncio is stdlib, google-genai already has async)
- tenacity already supports async functions
- No pyproject.toml changes needed
