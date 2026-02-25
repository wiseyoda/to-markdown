# Implementation Plan: Core CLI & Pipeline

**Phase**: 0020
**Created**: 2026-02-25
**Status**: Draft
**Input**: spec.md, discovery.md, coding-standards.md, tech-stack.md

## Architecture Overview

```
to-markdown/
  src/
    to_markdown/
      __init__.py          # Package root, __version__
      cli.py               # Typer CLI entry point
      core/
        __init__.py         # Core package
        constants.py        # ALL constants (single source of truth)
        extraction.py       # Kreuzberg adapter
        frontmatter.py      # YAML frontmatter composition
        pipeline.py         # Extract -> frontmatter -> assemble -> write
  tests/
    conftest.py            # Shared fixtures (tmp_path, sample files)
    fixtures/              # Test input files
    test_cli.py            # CLI behavior tests
    test_extraction.py     # Kreuzberg adapter tests
    test_frontmatter.py    # Frontmatter composition tests
    test_pipeline.py       # Pipeline integration tests
```

## Data Flow

```
Input file path
    │
    ▼
┌─────────────┐
│ CLI (cli.py) │  Parse args, configure logging, resolve paths
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ Pipeline          │  Orchestrates the conversion flow
│ (pipeline.py)     │
└──────┬───────────┘
       │
       ├─► extraction.py ──► Kreuzberg extract_file_sync()
       │       │                   │
       │       │              ExtractionResult(content, metadata, tables)
       │       │
       ├─► frontmatter.py ──► compose_frontmatter(metadata) → YAML string
       │
       ├─► Assemble: frontmatter + "\n" + content
       │
       └─► Write output file (with overwrite check)
```

## Key Design Decisions

### D-PL1: Synchronous Kreuzberg API

Use `extract_file_sync` (not async). Single-file processing doesn't benefit from async.
Async will be introduced in Phase 0050 (Batch Processing) if needed.

### D-PL2: Dataclasses for Structured Data

Use `@dataclass` for `ExtractionResult` and `FrontmatterData`. Immutable, typed, simple.

### D-PL3: PyYAML for Frontmatter

Use `yaml.dump()` with `default_flow_style=False` for clean, readable YAML output.
Custom representer to handle `None` values (skip them) and datetime formatting.

### D-PL4: Logging via Python stdlib

`logging` module configured in cli.py based on --verbose/--quiet flags.
No third-party logging library needed.

### D-PL5: Exit Code Strategy

Exit codes defined as constants in `constants.py`. The CLI catches all exceptions and maps
them to appropriate exit codes. No uncaught exceptions reach the user.

## Implementation Phases

### Phase 1: Project Setup (T001-T003)

Foundation files: pyproject.toml, package structure, constants, .env.example, .gitignore updates.

**Files created**: pyproject.toml, src/to_markdown/__init__.py, core/__init__.py,
core/constants.py, .env.example, tests/conftest.py

**Verification**: `uv sync` succeeds, `uv run ruff check` passes on empty package

### Phase 2: Kreuzberg Adapter (T004-T005)

Thin wrapper around Kreuzberg with error handling.

**Files created**: core/extraction.py, tests/test_extraction.py

**Verification**: Tests pass for basic extraction and error cases

### Phase 3: Frontmatter Composition (T006-T007)

YAML frontmatter from metadata.

**Files created**: core/frontmatter.py, tests/test_frontmatter.py

**Verification**: Tests pass for various metadata combinations

### Phase 4: Pipeline (T008-T009)

End-to-end conversion flow.

**Files created**: core/pipeline.py, tests/test_pipeline.py

**Verification**: Can convert a text file to .md with frontmatter

### Phase 5: CLI (T010-T011)

Typer CLI with all flags.

**Files created**: cli.py, tests/test_cli.py

**Verification**: `uv run to-markdown --help` works, all flags functional

### Phase 6: Integration & Polish (T012-T014)

README update, .gitignore, final linting, human testing instructions.

**Verification**: `ruff check` + `ruff format --check` + `pytest` all pass

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Kreuzberg API differs from research docs | Low | Medium | Verify API during T004, adapt early |
| PyYAML output formatting issues | Low | Low | Custom representers, tested thoroughly |
| Typer version incompatibility | Very Low | Low | Pinned in pyproject.toml |
| Test fixtures too large for git | Low | Low | Use small, synthetic test files |

## Testing Strategy

Per testing-strategy.md:

- **Unit tests**: Each module tested in isolation (mock Kreuzberg in extraction tests)
- **Integration tests**: Pipeline tests use real Kreuzberg on small fixtures
- **CLI tests**: Use Typer's `CliRunner` for argument parsing, exit code verification
- **Fixtures**: Small text files created by conftest.py (avoid large binaries in this phase)
- **Golden file tests**: Deferred to Phase 0030 (format quality focus)

## Dependencies on Other Phases

- **Depends on**: Phase 0010 (complete - governance, research, tooling decisions)
- **Depended on by**: All subsequent phases (0030-0050)
