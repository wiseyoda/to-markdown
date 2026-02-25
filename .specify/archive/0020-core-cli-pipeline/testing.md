# Human Testing Instructions: Phase 0020 - Core CLI & Pipeline

## Prerequisites

```bash
cd ~/dev/to-markdown
uv sync
```

## Test 1: Basic Text File Conversion

```bash
echo "Hello, world! This is a test." > /tmp/test-input.txt
uv run to-markdown /tmp/test-input.txt
cat /tmp/test-input.md
```

**Expected**: `/tmp/test-input.md` is created with:
- YAML frontmatter between `---` delimiters (format, extracted_at fields)
- The text "Hello, world!" in the body

## Test 2: Version Flag

```bash
uv run to-markdown --version
```

**Expected**: Prints `to-markdown 0.1.0` and exits.

## Test 3: Overwrite Protection

```bash
# First run creates the file
uv run to-markdown /tmp/test-input.txt --force
# Second run without --force should fail
uv run to-markdown /tmp/test-input.txt
echo "Exit code: $?"
```

**Expected**: Second run prints an error about existing file and exits with code 3.

## Test 4: Force Overwrite

```bash
uv run to-markdown /tmp/test-input.txt --force
echo "Exit code: $?"
```

**Expected**: Exits 0, file is overwritten.

## Test 5: Custom Output Path

```bash
mkdir -p /tmp/md-output
uv run to-markdown /tmp/test-input.txt -o /tmp/md-output/
cat /tmp/md-output/test-input.md
```

**Expected**: Output written to `/tmp/md-output/test-input.md`.

## Test 6: Missing File

```bash
uv run to-markdown /tmp/nonexistent-file.txt
echo "Exit code: $?"
```

**Expected**: Error message, exit code 1.

## Test 7: Verbose Mode

```bash
uv run to-markdown /tmp/test-input.txt -v --force
```

**Expected**: Shows INFO-level messages (extracting, composing frontmatter, wrote).

## Test 8: Quiet Mode

```bash
uv run to-markdown /tmp/test-input.txt -q --force
```

**Expected**: No output at all (silent success).

## Test 9: Try a Real Document (if available)

```bash
# Try any PDF, DOCX, or other document you have
uv run to-markdown ~/Documents/some-document.pdf
cat ~/Documents/some-document.md
```

**Expected**: Frontmatter with metadata (title, pages, format, etc.) + extracted content.

## Cleanup

```bash
rm -f /tmp/test-input.txt /tmp/test-input.md
rm -rf /tmp/md-output
```

## Automated Tests

```bash
uv run pytest -v          # 44 tests should pass
uv run ruff check         # No lint errors
uv run ruff format --check # No format issues
```
