# Feature Specification: Batch Processing

**Feature Branch**: `0050-batch-processing`
**Created**: 2026-02-26
**Status**: Draft

---

## User Scenarios & Testing

### User Story 1 - Directory Conversion (Priority: P1)

A developer has a folder of mixed documents (PDFs, DOCX files, spreadsheets) and wants to
convert them all to Markdown in one command.

**Why this priority**: This is the core use case for batch processing. Without directory
support, users must run the tool once per file.

**Independent Test**: Run `to-markdown docs/` on a directory with 5+ mixed-format files and
verify all supported files are converted.

**Acceptance Scenarios**:

1. **Given** a directory with 3 PDF and 2 DOCX files, **When** the user runs
   `to-markdown docs/`, **Then** 5 .md files are created next to their source files.
2. **Given** a directory with subdirectories, **When** the user runs `to-markdown docs/`,
   **Then** all files in all subdirectories are converted (recursive by default).
3. **Given** a directory with subdirectories, **When** the user runs
   `to-markdown docs/ --no-recursive`, **Then** only top-level files are converted.
4. **Given** a directory with some unsupported files (.py, .js), **When** the user runs
   `to-markdown docs/`, **Then** unsupported files are silently skipped and supported
   files are converted.
5. **Given** a directory, **When** the user runs `to-markdown docs/ -o output/`, **Then**
   .md files are placed in `output/` mirroring the input directory structure.
6. **Given** an empty directory, **When** the user runs `to-markdown empty_dir/`, **Then**
   the tool reports "No supported files found" and exits with EXIT_ERROR.

---

### User Story 2 - Glob Pattern Conversion (Priority: P2)

A developer wants to convert only specific files matching a pattern, like all PDFs in a
directory.

**Why this priority**: Extends directory support with filtering. Valuable but less common
than converting everything.

**Independent Test**: Run `to-markdown "docs/*.pdf"` and verify only PDF files are converted.

**Acceptance Scenarios**:

1. **Given** a directory with PDFs and DOCX files, **When** the user runs
   `to-markdown "docs/*.pdf"`, **Then** only PDF files are converted.
2. **Given** a glob that matches no files, **When** the user runs
   `to-markdown "docs/*.xyz"`, **Then** the tool reports "No files matched" and exits
   with EXIT_ERROR.
3. **Given** a glob pattern with multiple matches, **When** the user runs
   `to-markdown "reports/*.docx"`, **Then** all matching files are converted with
   progress reporting.

---

### User Story 3 - Progress Reporting (Priority: P1)

During batch conversion, the user sees a progress bar showing how many files have been
processed and which file is currently being converted.

**Why this priority**: Essential UX for batch operations - users need feedback on long-running
conversions.

**Independent Test**: Run `to-markdown docs/` on a directory with 5+ files and verify the
progress bar appears with file count and percentage.

**Acceptance Scenarios**:

1. **Given** a directory with 10 files, **When** the user runs `to-markdown docs/`,
   **Then** a progress bar shows "Converting: 3/10 (30%) current_file.pdf".
2. **Given** batch mode with `--quiet`, **When** the user runs `to-markdown docs/ -q`,
   **Then** no progress bar or success messages appear (only errors).
3. **Given** batch mode with `--verbose`, **When** the user runs `to-markdown docs/ -v`,
   **Then** progress bar shows plus per-file logging details.
4. **Given** batch conversion completes, **When** all files are processed, **Then** a
   summary line shows "Converted 8 files (2 skipped, 1 failed)".

---

### User Story 4 - Error Handling (Priority: P1)

When one file in a batch fails to convert, the tool continues processing remaining files
and reports errors at the end.

**Why this priority**: Without continue-on-error, one bad file stops the entire batch.

**Independent Test**: Include a corrupted file in a batch directory and verify other files
still convert successfully.

**Acceptance Scenarios**:

1. **Given** a directory with 5 files where 1 is corrupted, **When** the user runs
   `to-markdown docs/`, **Then** 4 files convert successfully, 1 is reported as failed,
   and exit code is EXIT_PARTIAL.
2. **Given** a directory with a corrupted file, **When** the user runs
   `to-markdown docs/ --fail-fast`, **Then** conversion stops at the first error with
   EXIT_ERROR.
3. **Given** a directory where all files convert successfully, **When** the user runs
   `to-markdown docs/`, **Then** exit code is EXIT_SUCCESS.
4. **Given** a directory where all files fail, **When** the user runs `to-markdown docs/`,
   **Then** exit code is EXIT_ERROR.
5. **Given** a batch with existing output files, **When** the user runs
   `to-markdown docs/`, **Then** files with existing output are skipped (counted as
   skipped) unless `--force` is passed.

---

### Edge Cases

- Empty directory: report "No supported files found", exit EXIT_ERROR
- Directory with only hidden files: same as empty
- Glob matching zero files: report "No files matched pattern", exit EXIT_ERROR
- Glob with directory path that doesn't exist: report file not found, exit EXIT_ERROR
- Very large directory (1000+ files): must not consume excessive memory
- Nested directory with mixed supported/unsupported: skip unsupported silently
- Single file still works exactly as before (no regression)
- Batch with --force: overwrites all existing output files
- Batch with --clean/--summary/--images: applies smart features to each file
- Input is a symlink to a directory: follow it and process

---

## Requirements

### Functional Requirements

- **FR-001**: System MUST accept a directory path as input and convert all supported files
  within it to Markdown.
- **FR-002**: Directory conversion MUST be recursive by default, with `--no-recursive` flag
  to limit to top-level only.
- **FR-003**: System MUST accept quoted glob patterns (e.g., `"docs/*.pdf"`) and convert
  all matching files.
- **FR-004**: System MUST display a rich progress bar during batch conversion showing file
  count, current file name, and percentage complete.
- **FR-005**: Progress bar MUST be suppressed when `--quiet` flag is used.
- **FR-006**: System MUST continue processing on individual file errors (log warning, skip
  file) by default.
- **FR-007**: System MUST support `--fail-fast` flag to stop on first error.
- **FR-008**: System MUST print a summary after batch conversion: X succeeded, Y failed,
  Z skipped.
- **FR-009**: System MUST return EXIT_PARTIAL (4) when some files succeed and some fail.
- **FR-010**: System MUST return EXIT_SUCCESS (0) when all files succeed (skips are OK).
- **FR-011**: System MUST return EXIT_ERROR (1) when all files fail or no files are found.
- **FR-012**: When `-o` is a directory in batch mode, output MUST mirror the input directory
  structure within the output directory.
- **FR-013**: When no `-o` is given in batch mode, .md files MUST be placed next to their
  source files (same as single-file behavior).
- **FR-014**: System MUST skip hidden files (starting with `.`) and directories during
  scanning.
- **FR-015**: System MUST skip files with no extension during directory scanning.
- **FR-016**: Files that Kreuzberg reports as unsupported format MUST be counted as
  "skipped", not "failed".
- **FR-017**: Existing single-file behavior MUST be completely preserved (no regression).
- **FR-018**: Smart features (--clean, --summary, --images) MUST work with batch mode,
  applied per-file.
- **FR-019**: `--force` in batch mode MUST overwrite all existing output files.
- **FR-020**: Files with existing .md output MUST be counted as "skipped" (not "failed")
  unless `--force` is passed.

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: `to-markdown docs/` converts all supported files in a directory with progress
  feedback and a completion summary.
- **SC-002**: `to-markdown "*.pdf"` converts only matching files.
- **SC-003**: One corrupted file in a batch does not prevent other files from converting.
- **SC-004**: All 170+ existing tests continue to pass (no regression).
- **SC-005**: `ruff check` and `ruff format --check` pass.
- **SC-006**: New batch tests cover directory scanning, glob matching, progress output,
  error handling, and summary reporting.
