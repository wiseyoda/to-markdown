---
phase: 0020
name: core-pipeline
status: not_started
created: 2026-02-25
updated: 2026-02-25
---

# Phase 0020: Core Pipeline

**Goal**: Set up the Python project scaffolding with uv, create the CLI entry point with Typer,
and build the core pipeline architecture (plugin registry, parse -> normalize -> render stages,
Document IR, and Markdown renderer). No format converters yet - just the framework they plug into.

**Scope**:
- Initialize Python project with uv (pyproject.toml, src layout)
- Set up ruff, pytest, and project configuration
- Create `src/to_markdown/core/constants.py` as the single constants file
- Implement Typer CLI with `to-markdown <file>` and standard flags:
  - `-o <path>` custom output path
  - `--force` / `-f` overwrite existing output
  - `--verbose` / `-v` detailed output (stacks: `-vv` for debug)
  - `--quiet` / `-q` suppress non-error output
  - `--version` print version and exit
- Implement overwrite protection (error if output exists without --force)
- Set up Python `logging` module with verbosity-level mapping
- Build plugin registry (auto-discover converters by extension/MIME type)
- Define Document IR data model (metadata, content blocks, headings, paragraphs, tables, etc.)
- Implement normalizer (IR cleanup and consistency)
- Implement Markdown renderer (IR -> Markdown with YAML frontmatter)
- Create .env.example, update .gitignore
- Write pipeline tests with a stub/dummy converter
- Write README with usage instructions

**Deliverables**:
- [ ] Python project with uv, ruff, pytest configured
- [ ] `src/to_markdown/core/constants.py` with initial constants
- [ ] `to-markdown` CLI entry point (Typer) with all standard flags
- [ ] Overwrite protection (--force to override)
- [ ] Logging setup with verbosity levels
- [ ] Plugin registry with extension/MIME type lookup
- [ ] Document IR data model
- [ ] Markdown renderer with frontmatter support
- [ ] Pipeline integration tests with dummy converter
- [ ] Project README with usage instructions

**Verification Gate**: `to-markdown test.txt` produces a valid .md file with frontmatter using
a stub text converter. `--version`, `--verbose`, `--quiet`, `--force` all work. Overwrite
protection confirmed. Pipeline is tested. `ruff check` and `pytest` pass.

**Estimated Complexity**: Medium
