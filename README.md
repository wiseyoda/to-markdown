# to-markdown

CLI file-to-Markdown converter optimized for LLM consumption. Wraps
[Kreuzberg](https://github.com/Goldziher/kreuzberg) (76+ formats) with YAML
frontmatter and a polished CLI.

## Install

```bash
uv sync
```

## Usage

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
| 1 | Error (file not found, extraction failed) |
| 2 | Unsupported file format |
| 3 | Output file already exists (use `--force`) |

## Development

```bash
uv sync --all-extras
uv run pytest
uv run ruff check
uv run ruff format --check
```
