# Human Testing Instructions: Smart Features (Phase 0040)

## Prerequisites

1. Set up a Gemini API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

2. Install with LLM extras:
   ```bash
   uv pip install -e ".[llm,dev]"
   ```

3. Verify installation:
   ```bash
   uv run to-markdown --help
   # Should show --clean, --summary, --images flags
   ```

## Test 1: Missing API Key Error

```bash
# Unset the key temporarily
unset GEMINI_API_KEY
uv run to-markdown tests/fixtures/pdf/simple.pdf --clean
```

**Expected**: Error message mentioning `GEMINI_API_KEY` with setup instructions. Exit code 1.

```bash
# Verify no error without smart flags
uv run to-markdown tests/fixtures/pdf/simple.pdf -f
```

**Expected**: Successful conversion (exit code 0).

## Test 2: --clean Flag on a Real PDF

```bash
export GEMINI_API_KEY=your-key
uv run to-markdown some-real-document.pdf --clean -f
```

**Expected**:
- Output .md file is created
- Word concatenation artifacts are fixed (e.g. `inBangkok` → `in Bangkok`)
- Decorative spacing collapsed (e.g. `L E A D E R S H I P` → `LEADERSHIP`)
- No content added, removed, or rephrased

## Test 3: --summary Flag

```bash
uv run to-markdown some-document.pdf --summary -f
```

**Expected**:
- Output contains a `## Summary` section after the frontmatter `---`
- Summary is 3-5 sentences capturing key facts
- Summary appears before the main document content

## Test 4: --images Flag

```bash
uv run to-markdown document-with-images.pdf --images -f
```

**Expected**:
- Output contains an `## Image Descriptions` section at the end
- Each image has a `### Image N (page P)` subsection
- Descriptions are factual and detailed

## Test 5: Combined Flags

```bash
uv run to-markdown document.pdf --clean --summary --images -f
```

**Expected**:
- All three enhancements present in output
- Summary reflects cleaned content (not raw extraction)
- Processing order: clean → images → summary

## Test 6: Graceful Degradation

```bash
# Set an invalid API key
GEMINI_API_KEY=invalid-key uv run to-markdown tests/fixtures/pdf/simple.pdf --clean -f -v
```

**Expected**:
- Output file is still created (conversion succeeds)
- Warning logged about LLM failure
- Content is the raw extraction (uncleaned)

## Test 7: Automated Tests

```bash
uv run pytest -v
uv run ruff check
uv run ruff format --check
```

**Expected**:
- 168 tests pass, 0 failures
- ruff check: All checks passed
- ruff format: All files already formatted
