# Tech Stack

> **Agents**: Reference this document for approved technologies and their versions.
> Deviations require documentation in plan.md.

## Core

| Technology | Version | Purpose | Decision |
|-----------|---------|---------|----------|
| Python | 3.14+ | Implementation language | D-18, D-31 |
| uv | 0.10.6+ | Package manager, virtual env, task runner | D-19 |
| Typer | 0.24.0+ | CLI framework (type-safe, auto-help) | D-19 |
| ruff | 0.15.2+ | Linting + formatting (2026 style guide) | D-19 |
| pytest | 9.1+ | Test framework | D-19 |
| pytest-cov | 7.0.0+ | Coverage reporting | D-32 |
| syrupy | 5.1.0+ | Snapshot/golden file testing | D-33 |

## Document Extraction

| Technology | Version | Purpose | Decision |
|-----------|---------|---------|----------|
| Kreuzberg | 4.3.8+ | Extraction backend (76+ formats, Rust core) | D-34 |

Kreuzberg replaces all per-format parsing libraries. It handles PDF, DOCX, PPTX, XLSX,
HTML, images/OCR, and 70+ additional formats via its Rust core.

## LLM Integration

| Technology | Version | Purpose | Decision |
|-----------|---------|---------|----------|
| google-genai | 1.59.0+ | Gemini API SDK for smart features | D-22, D-35 |
| Gemini 2.5 Flash | GA | Default LLM for --summary, --images flags | D-35 |
| tenacity | 8.0+ | Retry with exponential backoff for LLM calls | D-35 |

Default model: `gemini-2.5-flash` (GA, free tier). Override via `GEMINI_MODEL` env var.

## CLI & UX

| Technology | Version | Purpose | Decision |
|-----------|---------|---------|----------|
| rich | 13.0+ | Terminal progress bars for batch processing | D-55, D-61 |

## Infrastructure

| Technology | Purpose | Decision |
|-----------|---------|----------|
| .env files | API key management (GEMINI_API_KEY, GEMINI_MODEL) | D-23 |
| python-dotenv | .env file loading | D-23 |
| Git | Version control | Standard |

## Distribution

| Method | Status | Notes |
|--------|--------|-------|
| Local (uv run) | Current | D-21: local only for now |
| PyPI | Future | May publish eventually (D-26) |
| pipx / uv tool | Future | For global CLI install |

## Constraints

- Core conversion MUST work offline (no LLM required)
- Smart features (--summary, --images) require GEMINI_API_KEY
- LLM dependencies are optional extras (`[llm]`)
- Single-file processing first; batch processing is a later phase (D-24)
- No server/HTTP dependencies - CLI only (D-26)
- Kreuzberg pinned to specific version for API stability

---
*Version: 2.0.0 | Last Updated: 2026-02-25*
