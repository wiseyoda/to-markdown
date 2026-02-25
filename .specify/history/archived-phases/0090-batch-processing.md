---
phase: 0090
name: batch-processing
status: not_started
created: 2026-02-25
updated: 2026-02-25
---

# Phase 0090: Batch Processing

**Goal**: Add support for converting multiple files at once - directories, glob patterns,
and parallel processing for performance.

**Scope**:
- Support directory input: `to-markdown ./docs/` converts all supported files
- Support glob patterns: `to-markdown "*.pdf"`
- Recursive directory traversal with --recursive flag
- Progress reporting (file count, current file, errors)
- Error handling: continue on failure, report failures at end
- Optional parallel processing for performance
- -o flag with directories: mirror input structure in output directory
- Summary output: N files converted, M failures, time elapsed

**Deliverables**:
- [ ] Directory input support
- [ ] Glob pattern support
- [ ] --recursive flag
- [ ] Progress reporting
- [ ] Graceful error handling (continue on failure)
- [ ] Output directory mirroring with -o
- [ ] Batch summary output
- [ ] Tests for batch scenarios

**Verification Gate**: Batch conversion of a directory with mixed formats completes
successfully with clear progress and error reporting. All tests pass.

**Estimated Complexity**: Medium
