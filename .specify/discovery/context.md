# Project Context

> Populated during the discovery interview.

## Identity

- **Name**: to-markdown
- **Type**: CLI tool (file converter)
- **Description**: Universal file-to-Markdown converter optimized for LLM consumption. Converts binary documents into well-structured Markdown files so complete that an LLM never needs the source file again.
- **Audience**: AI/LLM pipelines (preprocessing documents for language models)
- **Stage**: Greenfield (starting from scratch)

## Problem Statement

LLMs currently waste time re-extracting info from binary files each session. They install
libraries, run ad-hoc conversion tools, and rarely save the output. to-markdown provides a
one-shot conversion that produces an MD file so complete the LLM never needs to look at the
source file again.

## Core Formats

PDF, DOCX, PPTX, XLSX, Images (OCR) - extensible to more formats via plugin architecture.

## Key Design Principles

- "Work like magic without a ton of flags" - smart defaults, flags for edge cases
- Completeness: ALL information from source represented in output
- YAML frontmatter for metadata, fenced code blocks for structured data
- Single output file (no sidecars)

## Tech Stack

- Python 3.12+, uv, Typer, ruff, pytest
- Google Gemini 3.0 Flash for smart features (--summary, --images)
- Plugin registry + pipeline architecture (parse -> normalize -> render)

## Existing Assets

- None. Truly starting from zero.

## Constraints

- Must be fast, easy to use, and easy to maintain
- Core conversion works offline (no LLM required)
- Smart features require GEMINI_API_KEY via .env
- Local development only (no distribution yet)

## Team

- Solo developer with AI assistance

## Criticality

- Internal tool: reliability matters but not mission-critical

---
*Last Updated: 2026-02-25*
