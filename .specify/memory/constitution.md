# to-markdown Constitution

> **Agents**: Reference this document for architectural principles and non-negotiable project requirements.
> This is the authoritative source for project governance and development philosophy.

## Product Vision

A CLI file converter that transforms binary documents (PDF, DOCX, PPTX, XLSX, images) into
well-structured Markdown files optimized for LLM consumption. The output should be so complete
that an LLM never needs to look at the source file again.

**Target Audience**: AI/LLM pipelines and developers who feed documents to language models

**Primary Experience**: `to-markdown file.pdf` produces a single, self-contained .md file with
all information from the source document represented as text

## Core Principles

### I. Completeness Over Brevity

Every piece of information in the source document must be represented in the output Markdown.
Text, structure, metadata, tables, and visual content descriptions - nothing should be lost.

- ALL text content must be extracted and properly formatted
- Document structure (headings, lists, tables) must be faithfully preserved
- Metadata goes in YAML frontmatter; structured data in fenced code blocks
- Images and charts must be describable via optional --images flag

**Rationale**: The entire point of this tool is that an LLM can work with the .md file instead
of the source document. If information is lost, the tool has failed its purpose (D-9, D-11).

### II. Magic Defaults, Flags for Edge Cases

The tool should produce excellent output with zero flags. Smart auto-detection handles format
quirks, OCR needs, and table extraction by default. Flags exist only for non-default
enhancements.

- Core conversion requires zero flags and zero configuration
- Tables are extracted as structured data by default
- OCR is auto-detected when needed (scanned PDFs, images)
- Enhancement flags (--summary, --images, --toc, --chunk) are strictly opt-in
- The LLM features require an API key but core conversion works fully offline

**Rationale**: "Work like magic without a ton of flags." A great first-run experience is
non-negotiable for a tool that targets developer workflows (D-16, D-6).

### III. Kreuzberg Wrapper Architecture

Document extraction is delegated to Kreuzberg (Rust-based, 76+ formats). The to-markdown
project wraps Kreuzberg with an LLM-optimized output layer.

- Kreuzberg handles all format parsing, OCR, and table extraction
- to-markdown adds: YAML frontmatter (from Kreuzberg metadata), LLM features (--summary,
  --images), CLI UX (Typer, --force, --verbose), and golden file quality testing
- Kreuzberg is isolated behind an adapter interface (`core/extraction.py`) for API stability
- Pipeline: Kreuzberg extract -> compose frontmatter -> apply LLM features -> output .md

**Rationale**: Kreuzberg provides production-quality extraction for 76+ formats with a Rust
core (35+ files/sec, 91% F1 on PDFs). Building per-format parsers from scratch would replicate
existing work. Our value is in the LLM-optimized wrapper layer (D-10, D-17, D-31).

### IV. Simplicity and Maintainability

Solo developer with AI assistance. Every architectural decision must favor simplicity and
low maintenance overhead. Pragmatic trade-offs over theoretical purity.

- Prefer standard libraries over novel approaches
- Each format converter is independently testable
- No premature abstractions - three similar lines beat a premature helper
- Dependencies are chosen per-format with documented rationale (research phase per format)

**Rationale**: The tool must remain maintainable by a single developer. Complexity is the
enemy of longevity (D-7, D-6).

### V. Quality Through Testing

Conversion quality is verified through golden file tests, format coverage, and edge cases.
Output quality is the product - it must be measured and maintained.

- Golden file tests compare output against known-good .md reference files
- Every supported format has coverage tests (converts without errors)
- Edge cases tested: corrupted files, huge files, empty files, scanned PDFs
- Test fixtures curated per format with representative real-world documents

**Rationale**: For a file converter, the output IS the product. If tests don't verify output
quality, there's no quality guarantee (D-25).

### VI. Zero Tolerance for Sloppiness

Code discipline is non-negotiable. Every file touched is left better than it was found.

- **No magic numbers** - every numeric literal gets a named constant, and ALL constants
  live in `core/constants.py` (single source of truth - never define constants elsewhere)
- **No duplication** - if two functions do the same thing, refactor immediately. When in
  doubt, refactor.
- **Fix what you see** - if you encounter a bug, bad pattern, or code smell while working
  on something else, fix it right then. No "this isn't related to my changes" or "this is
  good enough." If you're in the file, you own it.
- **No file over 300 lines** - source files (excluding tests) must stay under 300 lines.
  If a file grows past this, split it. This is a hard limit, not a guideline.
- **Docs stay current** - memory documents, README, and `--help` output must always reflect
  the current state of the code. No drift. Update docs in the same commit as code changes.

**Rationale**: Small disciplines compound. A codebase that tolerates "just this once" exceptions
quickly becomes unmaintainable. Fixing as you go is cheaper than fixing later.

### VII. Phases Are Done When They're Actually Done

A phase is not complete until a human can use the feature end-to-end and verify it works
on real-world inputs. Automated tests are necessary but not sufficient.

- Every completed phase includes **real-world smoke tests** - not just `pytest`, but
  actually running the tool on real documents and verifying the output
- Every completed phase includes **clear human testing instructions** - step-by-step
  commands the human can copy-paste to verify the feature works, with expected outcomes
- "Tests pass" is the minimum bar, not the finish line
- Smoke test results are documented before a phase is marked complete

**Rationale**: Automated tests verify what we thought to test. Real-world usage catches
everything else. The human must be able to verify independently (D-25).

## Technology Stack

**Core Technologies**: Python, uv, Typer, pytest, ruff

**LLM Integration**: Google Gemini 2.5 Flash (GA) for smart features

**Deviation Process**: Any deviation from approved technologies MUST be documented in the
feature's `plan.md` with clear justification.

> See [`tech-stack.md`](./tech-stack.md) for complete list of approved technologies.

## Development Workflow

### Code Review Requirements

- All changes to `main` branch require pull request review
- PRs MUST include description of changes and testing performed
- Reviewer verifies constitution compliance before approval
- Squash merge for clean history

### Quality Gates

Before merge, all PRs MUST pass:

1. Build with no errors (`ruff check`)
2. Linter with no errors (`ruff check`)
3. All automated tests passing (`pytest`)
4. Code formatting check (`ruff format --check`)
5. No secrets detected in code (.env files in .gitignore)

### Commit Standards

- Conventional Commits format: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`
- Commit messages describe "why" not just "what"
- Each commit represents a logical unit of change

## Governance

### Authority

This Constitution supersedes all other development practices and guidelines.
When conflicts arise, Constitution principles take precedence.

### Amendment Process

1. Propose amendment via pull request to this file
2. Document rationale for change in PR description
3. Changes require project lead approval
4. Version increment follows semantic versioning:
   - MAJOR: Principle removed or fundamentally redefined
   - MINOR: New principle added or existing principle expanded
   - PATCH: Clarifications, typo fixes, non-semantic refinements
5. All dependent artifacts updated as part of amendment PR

### Compliance Review

- Every PR review includes Constitution compliance check
- Complexity violations MUST be documented in `plan.md` with justification

### Runtime Guidance

For day-to-day development guidance, code style details, and project-specific conventions,
refer to the generated `CLAUDE.md` file at project root and feature-specific `plan.md` files.

**Version**: 1.2.1 | **Ratified**: 2026-02-25 | **Last Amended**: 2026-02-27
