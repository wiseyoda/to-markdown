# Discovery: Batch Processing

**Phase**: `0050-batch-processing`
**Created**: 2026-02-26
**Status**: Complete

## Phase Context

**Source**: ROADMAP Phase 0050
**Goal**: Add directory and glob pattern support for converting multiple files at once with
progress reporting, continue-on-error behavior, and a completion summary.

---

## Codebase Examination

### Related Implementations

| Location | Description | Relevance |
|----------|-------------|-----------|
| `src/to_markdown/cli.py:82-168` | Typer CLI entry point, accepts single `Path` argument | Must be extended to accept directory/glob inputs and new flags |
| `src/to_markdown/core/pipeline.py:17-102` | `convert_file()` - single-file conversion pipeline | Reused per-file in batch loop; no changes needed to this function |
| `src/to_markdown/core/pipeline.py:105-120` | `_resolve_output_path()` - output path resolution | Needs adaptation for batch output directory mirroring |
| `src/to_markdown/core/extraction.py:34-89` | `extract_file()` - Kreuzberg adapter | Raises `UnsupportedFormatError` for unknown formats (used for skip logic) |
| `src/to_markdown/core/constants.py` | All project constants | Needs new batch constants (exit codes, progress settings) |

### Existing Patterns & Conventions

- **Lazy imports**: Smart feature modules are lazily imported in pipeline.py to avoid
  requiring google-genai for core use. Batch module should follow same pattern for `rich`.
- **Exception hierarchy**: `ExtractionError` base -> `UnsupportedFormatError` subclass.
  Batch processing will use these to classify failures vs skips.
- **Logging levels**: quiet=ERROR, default=WARNING, verbose=INFO, -vv=DEBUG. Progress
  reporting must respect these levels.
- **Constants in one file**: All numeric literals and configuration values live in
  `core/constants.py`. Batch constants (exit codes, etc.) go there too.
- **Exit codes as constants**: EXIT_SUCCESS, EXIT_ERROR, EXIT_UNSUPPORTED, EXIT_ALREADY_EXISTS.
  Batch adds EXIT_PARTIAL for mixed-result runs.

### Integration Points

- **CLI layer** (`cli.py`): Entry point changes from single-file to multi-mode (file/dir/glob).
  The `main()` function needs to detect input type and dispatch to either single-file or batch.
- **Pipeline** (`pipeline.py`): The existing `convert_file()` function is called per-file by
  the batch loop. No changes to pipeline internals.
- **Constants** (`constants.py`): New exit code, batch-related constants.
- **pyproject.toml**: New `rich` dependency for progress bars.
- **README.md**: New usage section for batch processing.

### Constraints Discovered

- **Typer single-argument**: Current CLI uses `typer.Argument` for a single `Path`. Changing to
  accept multiple inputs requires rethinking the argument type (string for globs vs Path for
  files/dirs).
- **Output path semantics change**: For single files, `-o` can be a file or directory. For batch,
  `-o` must be a directory. Need clear error if `-o` points to a file during batch operations.
- **No Kreuzberg format list**: Kreuzberg doesn't expose a public list of supported extensions.
  For directory scanning, we must try each file and handle `UnsupportedFormatError` as a skip.
- **rich dependency**: Adding `rich` for progress bars adds a new core dependency. Justified
  because batch progress is a core feature, not optional.

---

## Requirements Sources

### From ROADMAP/Phase File

1. `to-markdown path/to/directory/` converts all supported files
2. Recursive by default, `--no-recursive` flag to disable
3. Output structure mirrors input structure
4. `to-markdown "docs/*.pdf"` converts matching files (standard glob patterns)
5. Progress bar: file count, current file, progress percentage
6. Use rich for terminal progress bar
7. Respect `--quiet` flag (suppress progress output)
8. Continue on individual file errors (log warning, skip file)
9. Summary at end: X succeeded, Y failed, Z skipped
10. `--fail-fast` flag to stop on first error

### From Memory Documents

- **Constitution Principle II**: Magic defaults - batch should work with zero extra flags
- **Constitution Principle III**: Kreuzberg wrapper - batch wraps existing pipeline
- **Constitution Principle IV**: Simplicity - minimal new code, reuse convert_file()
- **Constitution Principle VI**: No magic numbers - all batch thresholds in constants.py
- **Tech Stack**: D-24 explicitly deferred batch to a later phase - this is that phase

---

## Scope Clarification

### Confirmed Understanding

**What this phase achieves**:
Convert multiple files via directory paths or glob patterns, with rich progress reporting and
graceful error handling. The batch layer wraps the existing single-file pipeline.

**How it relates to existing code**:
- New `core/batch.py` module orchestrates multi-file conversion
- CLI gains directory/glob detection and new flags
- Existing `convert_file()` is called per-file (unchanged)
- New `rich` dependency for progress bars

**Key constraints and requirements**:
- All existing single-file behavior preserved exactly
- No Kreuzberg changes needed
- Smart features (--clean, --summary, --images) work with batch too
- Output structure mirrors input when using -o directory

**Technical approach**:
- Input detection: file -> single, directory -> batch, glob chars -> glob batch
- File discovery: walk directory / resolve glob, skip hidden files
- Batch loop: iterate with rich progress, catch errors per-file, classify as skip/fail
- Summary: print results table at end

---

## Recommendations for SPECIFY

### Should Include in Spec

- Directory input with recursive/non-recursive scanning
- Glob pattern matching
- Rich progress bar with file count and percentage
- Per-file error handling with continue-on-error
- Fail-fast flag
- Completion summary (succeeded/failed/skipped)
- New exit code for partial failure
- Output directory mirroring for batch

### Should Exclude from Spec (Non-Goals)

- Parallel/concurrent file processing (future optimization)
- Watch mode / auto-reconvert on file changes
- Recursive glob patterns (e.g., `**/*.pdf`) - standard glob is sufficient
- Custom file filtering beyond glob patterns
- Resume/checkpoint for interrupted batch runs

### Potential Risks

- Large directories with thousands of files could be slow (mitigated by Kreuzberg's fast
  rejection of unsupported formats)
- Rich progress bar may not render correctly in all terminals (mitigated by --quiet fallback)

### Decisions Made

- **D-55**: Use `rich` library for progress bars (standard, maintained, good terminal support)
- **D-56**: Input detection by type (file/dir/glob) rather than separate subcommands
- **D-57**: No maintained list of supported extensions; let Kreuzberg decide per-file
- **D-58**: New EXIT_PARTIAL (4) exit code for mixed-result batch runs
- **D-59**: Skip hidden files/dirs and extensionless files during directory scanning
