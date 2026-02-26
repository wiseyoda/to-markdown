# Implementation Plan: Batch Processing

**Branch**: `0050-batch-processing` | **Date**: 2026-02-26 | **Spec**: `specs/0050-batch-processing/spec.md`

## Summary

Add batch processing to to-markdown: directory input, glob patterns, rich progress bar, and
continue-on-error handling. Wraps the existing single-file `convert_file()` pipeline in a
batch loop with file discovery, progress reporting, and result aggregation.

## Technical Context

**Language/Version**: Python 3.14+
**Primary Dependencies**: Typer 0.24+, Kreuzberg 4.3.8+, rich (new - progress bars)
**Testing**: pytest 9.0+, syrupy 5.0+
**Target Platform**: macOS / Linux CLI
**Performance Goals**: Process files at Kreuzberg speed (~35 files/sec for simple formats)
**Constraints**: No parallel processing (sequential only), no memory accumulation across files

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Completeness Over Brevity | PASS | All batch features specified, no gaps |
| II. Magic Defaults | PASS | Recursive by default, continue-on-error by default |
| III. Kreuzberg Wrapper | PASS | Batch wraps convert_file() which wraps Kreuzberg |
| IV. Simplicity | PASS | One new module (batch.py), minimal CLI changes |
| V. Quality Through Testing | PASS | Golden file tests, edge cases, error scenarios |
| VI. Zero Tolerance | PASS | Constants in constants.py, no magic numbers |
| VII. Phases Done Right | PASS | Human testing instructions required |

## Project Structure

### Documentation (this feature)

```text
specs/0050-batch-processing/
├── discovery.md          # Codebase examination
├── spec.md               # Feature specification
├── plan.md               # This file
└── tasks.md              # Task breakdown
```

### Source Code Changes

```text
src/to_markdown/
├── cli.py                  # MODIFY: accept dir/glob, new flags, batch dispatch
├── core/
│   ├── batch.py            # NEW: file discovery + batch conversion loop
│   ├── constants.py        # MODIFY: add batch constants
│   ├── pipeline.py         # UNCHANGED
│   ├── extraction.py       # UNCHANGED
│   └── frontmatter.py      # UNCHANGED
└── smart/                  # UNCHANGED

tests/
├── test_cli.py             # MODIFY: add batch CLI tests
├── test_batch.py           # NEW: batch module tests
└── conftest.py             # MODIFY: add batch fixtures
```

## Architecture

### Input Detection Flow

```
CLI receives input string
  │
  ├── Is it an existing file? ──────────────> Single-file conversion (existing path)
  │
  ├── Is it an existing directory? ─────────> Batch: discover_files() -> convert_batch()
  │
  ├── Contains glob chars (* ? [)? ─────────> Batch: resolve_glob() -> convert_batch()
  │
  └── Otherwise ────────────────────────────> Error: file/directory not found
```

### Batch Processing Flow

```
discover_files(source, recursive) -> list[Path]
  │
  ├── Walk directory (rglob/glob) or resolve glob pattern
  ├── Skip hidden files/dirs (starting with .)
  ├── Skip extensionless files
  └── Sort by path for deterministic order

convert_batch(files, output_dir, flags) -> BatchResult
  │
  ├── For each file (with rich Progress bar):
  │     ├── Try convert_file()
  │     ├── Success -> add to succeeded list
  │     ├── UnsupportedFormatError -> add to skipped list
  │     ├── OutputExistsError (no --force) -> add to skipped list
  │     ├── Other error -> add to failed list
  │     └── If --fail-fast and error -> break
  │
  └── Return BatchResult(succeeded, failed, skipped)
```

### New Module: `core/batch.py`

```python
@dataclass(frozen=True)
class BatchResult:
    succeeded: list[Path]
    failed: list[tuple[Path, str]]   # (path, error message)
    skipped: list[tuple[Path, str]]  # (path, reason)

    @property
    def total(self) -> int: ...
    @property
    def exit_code(self) -> int: ...

def discover_files(source: Path, *, recursive: bool = True) -> list[Path]: ...

def convert_batch(
    files: list[Path],
    output_dir: Path | None = None,
    *,
    force: bool = False,
    clean: bool = False,
    summary: bool = False,
    images: bool = False,
    fail_fast: bool = False,
    quiet: bool = False,
) -> BatchResult: ...
```

### CLI Changes

Current:
```
to-markdown <file> [OPTIONS]
```

New:
```
to-markdown <input> [OPTIONS]
```

Where `<input>` can be a file path, directory path, or quoted glob pattern.

New flags:
- `--no-recursive` - Disable recursive directory scanning
- `--fail-fast` - Stop on first error

Argument type changes from `Path` to `str` to support glob patterns, with validation
in the command function.

### Output Path Resolution for Batch

When `-o <dir>` is used with batch:
```
Input:  docs/reports/quarterly.pdf
Output: <output_dir>/reports/quarterly.md  (relative structure preserved)
```

When no `-o` (default):
```
Input:  docs/reports/quarterly.pdf
Output: docs/reports/quarterly.md  (next to source file)
```

### Exit Code Strategy

| Scenario | Exit Code | Constant |
|----------|-----------|----------|
| All files succeed (skips OK) | 0 | EXIT_SUCCESS |
| Some succeed, some fail | 4 | EXIT_PARTIAL |
| All fail | 1 | EXIT_ERROR |
| No files found | 1 | EXIT_ERROR |
| Single file (existing) | 0/1/2/3 | Unchanged |

### Dependencies

**New core dependency**: `rich>=13.0` for progress bars.

Rich provides `rich.progress.Progress` with built-in support for:
- File count and percentage
- Current task description (file name)
- ETA and elapsed time
- Respects terminal width

Rich is added as a core dependency (not optional) because batch progress is a core feature.

## Decisions

- **D-55**: Use `rich` library for progress bars
- **D-56**: Detect input type (file/dir/glob) from CLI argument rather than separate subcommands
- **D-57**: No maintained extension list; let Kreuzberg decide per-file via UnsupportedFormatError
- **D-58**: EXIT_PARTIAL (4) for mixed-result batch runs
- **D-59**: Skip hidden files/dirs and extensionless files during directory scanning
- **D-60**: Argument type changes from `Path` to `str` to support glob patterns
- **D-61**: `rich` is a core dependency (not optional) because batch progress is core functionality
- **D-62**: Output directory mirroring preserves relative path structure from input root
