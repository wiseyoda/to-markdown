---
phase: 0020
name: core-cli-pipeline
status: not_started
created: 2026-02-25
updated: 2026-02-25
---

# Phase 0020: Core CLI & Pipeline

**Goal**: Build the complete to-markdown CLI that wraps Kreuzberg for document extraction,
composes YAML frontmatter from metadata, and outputs a single .md file. This is the MVP -
after this phase, `to-markdown file.pdf` produces a working .md file.

**Scope**:

### 1. Project Setup
- Initialize pyproject.toml with uv, Python 3.14+, all dependencies
- Configure ruff (0.15+, 2026 style guide), pytest (9.1+), syrupy
- Create project structure per coding-standards.md
- Set up .env.example, .gitignore

### 2. Kreuzberg Adapter
- `core/extraction.py`: Thin adapter around Kreuzberg's `extract_file_sync`
- Default to `output_format="markdown"` with `enable_quality_processing=True`
- Return structured result (content, metadata, tables)
- Error handling for unsupported formats, corrupted files, missing files

### 3. Frontmatter Composition
- `core/frontmatter.py`: Compose YAML frontmatter from Kreuzberg metadata
- Fields: title, author, creation date, page count, format, extraction date
- Clean, structured YAML between `---` delimiters

### 4. Pipeline
- `core/pipeline.py`: Kreuzberg extract -> frontmatter -> assemble -> output
- Handles file path resolution (input -> output .md path)
- Overwrite protection (error unless --force)

### 5. CLI
- `cli.py`: Typer-based CLI entry point
- `to-markdown <file>` - convert a file
- Flags: --version, --verbose/-v, --quiet/-q, --force/-f, -o <path>
- Proper exit codes (0 success, 1 error, 2 unsupported, 3 already exists)
- Logging setup per coding-standards.md

### 6. Tests
- test_extraction.py: Kreuzberg adapter works for basic text file
- test_frontmatter.py: YAML frontmatter composition
- test_pipeline.py: End-to-end pipeline
- test_cli.py: CLI argument parsing, exit codes, output file creation

**Deliverables**:
- [ ] pyproject.toml with all dependencies configured
- [ ] Working CLI: `uv run to-markdown <file>` produces .md with frontmatter
- [ ] Kreuzberg adapter with error handling
- [ ] Frontmatter composition from metadata
- [ ] All baseline tests passing
- [ ] `ruff check` + `ruff format --check` passing

**Verification Gate**: `to-markdown test.txt` produces valid .md with frontmatter;
`ruff check` + `pytest` pass.

**Estimated Complexity**: Medium (wrapper code, not parser development)
