# to-markdown

CLI file-to-Markdown converter optimized for LLM consumption. Wraps
[Kreuzberg](https://github.com/Goldziher/kreuzberg) (76+ formats) with YAML
frontmatter and a polished CLI.

## Install

```bash
uv sync
```

## Usage

### Single File

```bash
# Convert a file (creates file.md next to the input)
uv run to-markdown document.pdf

# Custom output path
uv run to-markdown document.pdf -o output/

# Overwrite existing output
uv run to-markdown document.pdf --force

# Verbose output
uv run to-markdown document.pdf -v

# Quiet mode (errors only)
uv run to-markdown document.pdf -q
```

### Batch Processing

```bash
# Convert all supported files in a directory (recursive by default)
uv run to-markdown docs/

# Non-recursive (top-level files only)
uv run to-markdown docs/ --no-recursive

# Convert files matching a glob pattern
uv run to-markdown "docs/*.pdf"

# Output to a different directory (mirrors input structure)
uv run to-markdown docs/ -o output/

# Stop on first error
uv run to-markdown docs/ --fail-fast

# Force overwrite all existing output files
uv run to-markdown docs/ --force
```

Batch mode shows a progress bar and prints a summary when done:

```
Converted 8 file(s), 2 skipped, 1 failed
```

### Smart Features

Requires `GEMINI_API_KEY` (install with `uv sync --extra llm`):

```bash
# Fix extraction artifacts via LLM
uv run to-markdown document.pdf --clean

# Generate document summary
uv run to-markdown document.pdf --summary

# Describe images via LLM vision
uv run to-markdown document.pdf --images

# Smart features work with batch mode too
uv run to-markdown docs/ --summary --clean
```

### Output

Creates a `.md` file with YAML frontmatter and extracted content:

```markdown
---
title: Example Document
author: Jane Doe
pages: 12
format: pdf
extracted_at: '2026-02-25T12:00:00Z'
---

Extracted document content in Markdown...
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (file not found, extraction failed, all files failed) |
| 2 | Unsupported file format (single file only) |
| 3 | Output file already exists (use `--force`) |
| 4 | Partial success (batch: some files succeeded, some failed) |

## How to Test (Phase 0050: Batch Processing)

1. Convert a directory of files:
   ```bash
   uv run to-markdown tests/fixtures/
   ```
   Expected: Creates .md files next to each fixture file. Progress bar shows during conversion.

2. Convert with glob pattern:
   ```bash
   uv run to-markdown "tests/fixtures/pdf/*.pdf"
   ```
   Expected: Only PDF files are converted.

3. Test output directory mirroring:
   ```bash
   uv run to-markdown tests/fixtures/ -o /tmp/md-output/
   ```
   Expected: Creates .md files in `/tmp/md-output/` mirroring the fixture directory structure.

4. Test non-recursive mode:
   ```bash
   uv run to-markdown tests/fixtures/ --no-recursive
   ```
   Expected: Only top-level files in `tests/fixtures/` are converted (no subdirectories).

5. Test error handling:
   ```bash
   uv run to-markdown /tmp/empty-dir/
   ```
   Expected: "No supported files found" error message, exit code 1.

6. Test quiet mode:
   ```bash
   uv run to-markdown tests/fixtures/ -q
   ```
   Expected: No progress bar or summary output.

7. Verify exit codes:
   ```bash
   uv run to-markdown tests/fixtures/ --force; echo "Exit: $?"
   ```
   Expected: Exit code 0 for success, 4 for partial failure.

## Development

```bash
uv sync --all-extras
uv run pytest
uv run ruff check
uv run ruff format --check
```
