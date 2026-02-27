# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-27

First stable release. to-markdown converts 76+ document formats into LLM-optimized Markdown
with YAML frontmatter, powered by Kreuzberg extraction and optional Gemini LLM features.

### Phase 0010: Research & Tooling

- Selected core stack: Python 3.14+, uv, Typer, ruff, pytest, Kreuzberg as extraction backend
- Established project governance: constitution, coding standards, testing strategy, and glossary
- Completed library research and recorded foundational architectural decisions

### Phase 0020: Core CLI & Pipeline

- Built core conversion pipeline: Kreuzberg extraction adapter, YAML frontmatter composition,
  and Markdown assembly
- Implemented Typer CLI with `--force`, `--verbose`, and `--quiet` flags
- Delivered working `to-markdown file.pdf` end-to-end workflow

### Phase 0030: Format Quality & Testing

- Added golden file testing with syrupy snapshots for output quality verification
- Created programmatic test fixtures for PDF, DOCX, PPTX, XLSX, HTML, and images
- Added OCR test support with Tesseract (graceful skip when unavailable)

### Phase 0040: Smart Features

- Added LLM-powered `--summary` and `--images` flags via Google Gemini
- Implemented retry logic with tenacity for resilient API calls
- Packaged LLM dependencies as optional `[llm]` extras for offline-first core

### Phase 0050: Batch Processing

- Added directory and glob pattern support for multi-file conversion
- Implemented BatchResult tracking with succeeded/failed/skipped lists and partial exit code
- Added rich progress bars for batch feedback (suppressed with `--quiet`)

### Phase 0100: MCP Server

- Added Model Context Protocol server for AI agent integration (Claude Code, Codex CLI, etc.)
- Implemented 4 MCP tools: `convert_file`, `convert_batch`, `list_formats`, `get_status`
- Packaged as optional `[mcp]` extras with stdio transport

### Phase 0110: Background Processing

- Added `--background`/`--bg` flag for async conversions with SQLite task store
- Implemented `--status` and `--cancel` flags for task management
- Added 4 background MCP tools: `start_conversion`, `get_task_status`, `list_tasks`,
  `cancel_task`

### Phase 0120: Easy Install

- Created install scripts for macOS (`install.sh`) and Windows (`install.ps1`) with
  matching uninstall scripts
- Added `--setup` configuration wizard for API key and environment setup
- Implemented shell alias setup for global `to-markdown` command access

### Phase 0125: Smart Pipeline Improvements

- Enabled `--clean` by default when Gemini API key is available (silent degradation otherwise)
- Added content sanitization to strip prompt injection vectors (zero-width, control, and
  directional characters)
- Parallelized LLM pipeline: concurrent image descriptions and async clean/summary processing

### Phase 0130: Production Readiness & Docs

- Overhauled README, added CHANGELOG and LICENSE for release
- Added GitHub Actions CI with coverage enforcement (80% minimum)
- Tagged v1.0.0 for first stable release

[1.0.0]: https://github.com/ppatterson/to-markdown/releases/tag/v1.0.0
