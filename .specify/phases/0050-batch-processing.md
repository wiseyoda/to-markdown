---
phase: 0050
name: batch-processing
status: not_started
created: 2026-02-25
updated: 2026-02-25
---

# Phase 0050: Batch Processing

**Goal**: Add directory and glob pattern support for converting multiple files at once with
progress reporting.

**Scope**:

### 1. Directory Conversion
- `to-markdown path/to/directory/` converts all supported files
- Recursive by default, --no-recursive flag to disable
- Output structure mirrors input structure

### 2. Glob Pattern Support
- `to-markdown "docs/*.pdf"` converts matching files
- Standard glob patterns

### 3. Progress Reporting
- Show file count, current file, progress percentage
- Use rich or similar for terminal progress bar
- Respect --quiet flag (suppress progress output)

### 4. Error Handling
- Continue on individual file errors (log warning, skip file)
- Summary at end: X succeeded, Y failed, Z skipped
- --fail-fast flag to stop on first error

### 5. Tests
- Directory with mixed formats
- Glob pattern matching
- Error handling for individual file failures
- Progress reporting output

**Deliverables**:
- [ ] Directory conversion with recursive support
- [ ] Glob pattern support
- [ ] Progress reporting
- [ ] Error handling with continue-on-error
- [ ] All tests passing

**Verification Gate**: Directory conversion with mixed formats; progress reporting; all tests
pass.

**Estimated Complexity**: Medium
