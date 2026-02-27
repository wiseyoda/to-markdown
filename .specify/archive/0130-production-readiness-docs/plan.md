---
version: '1.0'
description: 'Implementation plan for production readiness and documentation'
---

# Implementation Plan: Production Readiness & Documentation

**Branch**: `0130-production-readiness-docs` | **Date**: 2026-02-27 | **Spec**: [spec.md](spec.md)

## Summary

Prepare to-markdown for v1.0.0 release by rewriting the README for public consumption,
adding GitHub Actions CI, creating CHANGELOG and LICENSE files, updating stale governance
documents, configuring coverage, and bumping the version.

## Technical Context

**Language/Version**: Python 3.14+
**Primary Dependencies**: No new runtime dependencies. GitHub Actions for CI.
**Storage**: N/A
**Testing**: pytest 9.0+, pytest-cov for coverage reporting
**Target Platform**: macOS/Linux CLI, GitHub Actions (ubuntu-latest)
**Project Type**: Single project
**Constraints**: Python 3.14 availability on GitHub Actions runners

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Completeness Over Brevity | Pass | README will be comprehensive |
| II. Magic Defaults | N/A | No runtime behavior changes |
| III. Kreuzberg Wrapper | N/A | No architecture changes |
| IV. Simplicity | Pass | Standard CI setup, no over-engineering |
| V. Quality Through Testing | Pass | Adding coverage enforcement |
| VI. Zero Tolerance for Sloppiness | Pass | Fixing stale docs, adding CI |
| VII. Phases Done When Actually Done | Pass | USER GATE requires verification |

## Project Structure

### Documentation (this feature)

```text
specs/0130-production-readiness-docs/
├── discovery.md
├── spec.md
├── requirements.md
├── plan.md
└── tasks.md
```

### Source Changes (repository root)

```text
# New files
.github/workflows/ci.yml          # GitHub Actions CI workflow
CHANGELOG.md                       # Version history
LICENSE                             # MIT license text

# Modified files
README.md                          # Complete rewrite
pyproject.toml                     # Version bump, coverage config
.specify/memory/constitution.md    # Fix stale LLM reference
.specify/memory/testing-strategy.md # Update test count, version
.specify/memory/glossary.md        # Add new terms
```

**Structure Decision**: No new source directories. Changes are documentation, configuration,
and governance files only.

## Implementation Approach

### 1. Foundation (Blocking)

Set up coverage configuration and measure baseline before other work. This determines
if additional tests are needed.

- Add `[tool.coverage.run]` and `[tool.coverage.report]` to pyproject.toml
- Run `pytest --cov=to_markdown --cov-fail-under=80` to measure baseline
- If below 80%, identify gaps and add tests

### 2. CI/CD Setup

Create `.github/workflows/ci.yml`:

```yaml
name: CI
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - uses: actions/setup-python@v5
        with:
          python-version: '3.14'
          allow-prereleases: true
      - run: uv sync --all-extras
      - run: uv run ruff check
      - run: uv run ruff format --check
      - run: uv run pytest --cov=to_markdown --cov-fail-under=80
```

Key decisions:
- Use `astral-sh/setup-uv@v5` for uv installation (official action)
- Use `actions/setup-python@v5` with `allow-prereleases: true` for Python 3.14
- Single job combining lint + test (simple, fast)
- Coverage check integrated into test step

### 3. README Rewrite

Complete rewrite of README.md with this structure:
1. Project title + one-line description + badges
2. What it does (feature highlights)
3. Quick start (install + first conversion)
4. Usage (single file, batch, smart features, background, sanitization)
5. AI Agent Integration (MCP) - condensed from current
6. Exit codes (keep current table)
7. Development (testing, linting commands)
8. License

Remove the "How to Test (Phase 0100)" section - it's phase-specific testing that
doesn't belong in a public README.

### 4. Release Files

- **CHANGELOG.md**: Summarize each phase with key features. Use Keep a Changelog format.
- **LICENSE**: Standard MIT license text with copyright year 2026.

### 5. Governance Updates

- **constitution.md**: Line 126 fix, bump to v1.2.1
- **testing-strategy.md**: Update test count, add Phase 0125 notes, bump to v1.2.0
- **glossary.md**: Add 4 new terms, bump to v2.1.0

### 6. Version Bump

- Set `version = "1.0.0"` in pyproject.toml
- Update `__version__` if defined in `__init__.py`

## Integration Architecture

No new modules are created in this phase. All changes are to existing files or new
standalone files (CI workflow, CHANGELOG, LICENSE) that don't require wiring.

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Python 3.14 not on GH Actions | `actions/setup-python@v5` with `allow-prereleases: true` |
| Coverage below 80% | Measure first, add tests if needed |
| CI takes too long | Single job, no matrix; target <5 min |
| Stale README after merge | USER GATE ensures human verification |
