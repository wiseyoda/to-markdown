# Tech Stack

> **Agents**: Reference this document for approved technologies and their versions.
> Deviations require documentation in plan.md.

## Core

| Technology | Version | Purpose | Decision |
|-----------|---------|---------|----------|
| Python | 3.12+ | Implementation language | D-18 |
| uv | latest | Package manager, virtual env, task runner | D-19 |
| Typer | latest | CLI framework (type-safe, auto-help) | D-19 |
| ruff | latest | Linting + formatting | D-19 |
| pytest | latest | Test framework | D-19 |

## LLM Integration

| Technology | Version | Purpose | Decision |
|-----------|---------|---------|----------|
| google-genai | latest | Gemini API SDK for smart features | D-22 |
| Gemini 3.0 Flash | Preview | LLM for --summary, --images flags | D-22 |

## Document Parsing Libraries

> Each format converter selects its library through a dedicated research phase (D-20).
> Libraries are added here as they are selected.

| Format | Library | Version | Decision | Status |
|--------|---------|---------|----------|--------|
| PDF | TBD | - | Research in phase | Pending |
| DOCX | TBD | - | Research in phase | Pending |
| PPTX | TBD | - | Research in phase | Pending |
| XLSX | TBD | - | Research in phase | Pending |
| Images/OCR | TBD | - | Research in phase | Pending |

## Infrastructure

| Technology | Purpose | Decision |
|-----------|---------|----------|
| .env files | API key management (GEMINI_API_KEY) | D-23 |
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
- Single-file processing first; batch processing is a later phase (D-24)
- No server/HTTP dependencies - CLI only (D-26)

---
*Version: 1.0.0 | Last Updated: 2026-02-25*
