# Feature Specification: Core CLI & Pipeline

**Feature Branch**: `0020-core-cli-pipeline`
**Created**: 2026-02-25
**Status**: Draft
**Input**: Phase 0020 definition + discovery findings + Kreuzberg research

## User Scenarios & Testing

### User Story 1 - Basic File Conversion (Priority: P1)

As a developer, I want to run `to-markdown file.pdf` and get a well-structured Markdown file
with YAML frontmatter, so that I can feed the output directly to an LLM.

**Why this priority**: This is the core value proposition of the entire tool.

**Independent Test**: Run `uv run to-markdown` on a text file and verify .md output exists with
frontmatter and content.

**Acceptance Scenarios**:

1. **Given** a valid text file `test.txt`, **When** I run `to-markdown test.txt`,
   **Then** `test.md` is created next to the input with YAML frontmatter and extracted content.
2. **Given** a valid PDF file, **When** I run `to-markdown doc.pdf`,
   **Then** `doc.md` is created with frontmatter containing title, page count, and format info.
3. **Given** a file with metadata (author, title), **When** I run `to-markdown file.docx`,
   **Then** the frontmatter includes all available metadata fields.

---

### User Story 2 - Output Path Control (Priority: P1)

As a developer, I want to control where the output file is written using `-o`, so that I can
organize converted files.

**Why this priority**: Essential for scripting and workflow integration.

**Independent Test**: Run `to-markdown file.txt -o /tmp/output.md` and verify file is created
at the specified path.

**Acceptance Scenarios**:

1. **Given** `-o output.md` flag, **When** I run `to-markdown test.txt -o output.md`,
   **Then** the output is written to `output.md` instead of `test.md`.
2. **Given** `-o /tmp/` flag (directory), **When** I run `to-markdown test.txt -o /tmp/`,
   **Then** the output is written to `/tmp/test.md`.
3. **Given** no `-o` flag, **When** I run `to-markdown test.txt`,
   **Then** the output is written to `test.md` next to the input file.

---

### User Story 3 - Overwrite Protection (Priority: P1)

As a developer, I want the tool to refuse to overwrite existing files unless I pass `--force`,
so that I don't accidentally lose data.

**Why this priority**: Data safety is non-negotiable (D-27, Constitution VI).

**Independent Test**: Create an existing output file, run without --force, verify error.

**Acceptance Scenarios**:

1. **Given** `test.md` already exists, **When** I run `to-markdown test.txt`,
   **Then** the tool exits with code 3 and an error message about the existing file.
2. **Given** `test.md` already exists, **When** I run `to-markdown test.txt --force`,
   **Then** `test.md` is overwritten with the new conversion.
3. **Given** `test.md` does not exist, **When** I run `to-markdown test.txt`,
   **Then** `test.md` is created successfully (no --force needed).

---

### User Story 4 - Error Handling (Priority: P1)

As a developer, I want clear error messages and proper exit codes when things go wrong, so that
I can diagnose issues and integrate the tool into scripts.

**Why this priority**: Proper error handling is foundational for a CLI tool.

**Independent Test**: Pass nonexistent file, unsupported format, and verify exit codes.

**Acceptance Scenarios**:

1. **Given** a nonexistent file path, **When** I run `to-markdown missing.txt`,
   **Then** exit code 1 with "File not found" error message.
2. **Given** a file with unsupported format, **When** I run `to-markdown file.xyz`,
   **Then** exit code 2 with "Unsupported format" error message.
3. **Given** a corrupted/unreadable file, **When** I run `to-markdown broken.pdf`,
   **Then** exit code 1 with a descriptive extraction error message.

---

### User Story 5 - CLI Flags & Verbosity (Priority: P2)

As a developer, I want `--version`, `--verbose`, and `--quiet` flags so that I can control the
tool's output level.

**Why this priority**: CLI hygiene (D-29, D-30). Important but not blocking core conversion.

**Independent Test**: Run with --version, --verbose, --quiet and verify output behavior.

**Acceptance Scenarios**:

1. **Given** `--version` flag, **When** I run `to-markdown --version`,
   **Then** it prints the version number and exits 0.
2. **Given** `--verbose` flag, **When** I run `to-markdown test.txt --verbose`,
   **Then** INFO-level messages are shown (format detected, extraction stats).
3. **Given** `--quiet` flag, **When** I run `to-markdown test.txt --quiet`,
   **Then** only ERROR messages are shown (successful conversion is silent).
4. **Given** `-vv` flags, **When** I run `to-markdown test.txt -vv`,
   **Then** DEBUG-level messages are shown (full extraction details).

---

## Functional Requirements

### FR-001: Project Initialization

The project must be initialized with pyproject.toml containing all dependencies, build
configuration, ruff settings, pytest configuration, and a `to-markdown` script entry point.

**Traces to**: Phase Goal "Project setup: pyproject.toml, ruff, pytest, syrupy"

### FR-002: Kreuzberg Adapter

A thin adapter in `core/extraction.py` must wrap Kreuzberg's `extract_file_sync` API, providing:
- Default config: `output_format="markdown"`, `enable_quality_processing=True`
- A structured `ExtractionResult` dataclass with content, metadata, and tables
- Proper error handling for missing files, unsupported formats, and extraction failures

**Traces to**: Phase Goal "Kreuzberg adapter with error handling"

### FR-003: Frontmatter Composition

`core/frontmatter.py` must compose YAML frontmatter from Kreuzberg metadata:
- Fields: title, author, creation_date, page_count, format, word_count, extraction_date
- Only include fields that have values (skip None/empty)
- Output between `---` delimiters
- Use PyYAML for serialization

**Traces to**: Phase Goal "Frontmatter composition"

### FR-004: Pipeline Assembly

`core/pipeline.py` must orchestrate: extract → compose frontmatter → assemble .md → write:
- Resolve output path (same dir as input, `.md` extension, or custom via `-o`)
- Check for existing output file (error unless `--force`)
- Combine frontmatter + content into final Markdown
- Write output file

**Traces to**: Phase Goal "Pipeline: extract -> frontmatter -> assemble -> output"

### FR-005: Typer CLI

`cli.py` must provide a Typer CLI with:
- Positional argument: `file` (input file path)
- Options: `--force/-f`, `--output/-o`, `--verbose/-v` (stackable), `--quiet/-q`, `--version`
- Proper exit codes per coding-standards.md (0, 1, 2, 3)
- Logging setup mapped to verbosity level

**Traces to**: Phase Goals "Typer CLI with flags" and "Proper exit codes"

### FR-006: Baseline Tests

Comprehensive test suite covering:
- `test_extraction.py`: Kreuzberg adapter behavior, error cases
- `test_frontmatter.py`: YAML composition, empty fields, special characters
- `test_pipeline.py`: End-to-end conversion, output path resolution, overwrite protection
- `test_cli.py`: Argument parsing, exit codes, --version, --force, -o

**Traces to**: Phase Goal "Baseline tests for extraction, frontmatter, pipeline, CLI"

## Non-Functional Requirements

### NFR-001: Code Quality

- All code passes `ruff check` and `ruff format --check`
- No file exceeds 300 lines (excluding tests)
- All constants in `core/constants.py`
- Type hints on all public functions

### NFR-002: Python Compatibility

- Requires Python 3.14+ (D-31)
- Uses modern Python features where beneficial

### NFR-003: Offline Operation

- Core conversion works without any network access
- No LLM dependencies in this phase

## Security Considerations

### SC-001: No Credential Storage

This phase has no secrets or API keys. `.env.example` is a template only.

### SC-002: File Path Safety

- Validate input file exists before processing
- Validate output directory exists and is writable
- No path traversal vulnerabilities in `-o` flag handling

## Constraints

- Must use Kreuzberg as extraction backend (D-34)
- Must use Typer for CLI (D-19)
- Must use PyYAML for frontmatter (not hand-rolled YAML)
- All constants in `core/constants.py` (Constitution VI)
- No file over 300 lines (Constitution VI)
