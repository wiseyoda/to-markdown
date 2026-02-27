---
version: '1.0'
description: 'Pre-specification discovery for production readiness and documentation'
---

# Discovery: Production Readiness & Documentation

**Phase**: `0130-production-readiness-docs`
**Created**: 2026-02-27
**Status**: Complete

## Phase Context

**Source**: ROADMAP Phase 0130
**Goal**: Clean up documentation, finalize governance, and prepare for v1.0.0 release.

---

## Codebase Examination

### Current State Assessment

| Category | Status | Details |
|----------|--------|---------|
| TODO/FIXME comments | Clean | 0 found in src/ or tests/ |
| Line count compliance | OK | tasks.py 283, cli.py 279 (both under 300) |
| Unused imports/dead code | Clean | No issues found |
| Public docstrings | 100% | All public functions documented |
| Constants centralized | Yes | All in core/constants.py (181 lines) |
| Lint/format | Clean | 0 ruff violations, all 53 files formatted |
| Test suite | 505 passing | 14 syrupy snapshots, 70s runtime |

### Files Relevant to This Phase

| Location | Description | Relevance |
|----------|-------------|-----------|
| `README.md` | Current README | Needs overhaul for public audience |
| `pyproject.toml` | Project metadata, v0.1.0 | Version bump to 1.0.0 |
| `.specify/memory/constitution.md` | Governance | Stale "Gemini 3.0 Flash" reference on line 126 |
| `.specify/memory/testing-strategy.md` | Test docs | Version 1.1.0, predates Phase 0125 (505 tests) |
| `.specify/memory/glossary.md` | Terms | Missing 4 terms: Sanitization, Async Pipeline, Background Task, MCP |

### Missing Production Artifacts

| Artifact | Status | Notes |
|----------|--------|-------|
| `.github/workflows/` | Missing | No CI/CD configured |
| `CHANGELOG.md` | Missing | No release notes |
| `LICENSE` | Missing | MIT declared in pyproject.toml but no file |
| Git tags | None | No version tags exist |
| README badges | None | No shields/badges |
| Coverage config | Missing | pytest-cov installed but not configured |

### Existing Patterns & Conventions

- **Conventional Commits**: All commits use `feat:`, `fix:`, `docs:`, `chore:` prefixes
- **Squash merge**: PR-based workflow with squash merges to main
- **Optional extras**: `[llm]` and `[mcp]` extras pattern in pyproject.toml
- **Constitution compliance**: Every phase verifies against constitution principles
- **Memory doc versioning**: SemVer with ratified/amended dates

### Entry Points

| Entry Point | Location | Invocation |
|-------------|----------|------------|
| CLI | `cli.py:app` | `uv run to-markdown <file>` |
| MCP server | `mcp/server.py:run_server` | `python -m to_markdown.mcp` |
| MCP script | `to-markdown-mcp` | Via pyproject.toml scripts |
| Worker | `core/worker.py:run_worker` | Hidden `--_worker` flag |

### Constraints Discovered

- **Python 3.14+**: GitHub Actions must use Python 3.14 (bleeding edge, may need `actions/setup-python` with specific config)
- **No PyPI yet**: Distribution is local `uv run` and MCP server only
- **tests.py sleep calls**: 2 `time.sleep(0.01)` in test_tasks.py for ordering - minimal flake risk
- **39 deprecation warnings**: From google-genai package internals, not our code

---

## Requirements Sources

### From Phase Document

1. README overhaul - polished, public-facing
2. Documentation cleanup - audit all memory docs
3. Code cleanup - TODOs, docstrings, lint, dead code, constants, 300-line limit
4. Test suite hardening - flaky tests, coverage, edge cases
5. CI/CD setup - GitHub Actions
6. Release preparation - v1.0.0, CHANGELOG, GitHub release
7. Governance finalization - constitution, decisions, memory reconciliation

### From Memory Documents

- **Constitution**: Principle VI (Zero Tolerance for Sloppiness) - docs must stay current
- **Constitution**: Principle VII (Phases Done When Actually Done) - human testing instructions
- **Tech Stack**: Distribution section mentions PyPI as "Future"
- **Coding Standards**: 300-line limit, constants in constants.py

---

## Scope Clarification

### Question 1: CI Python Matrix

**Context**: Project requires Python 3.14+. GitHub Actions needs version matrix configuration.

**Question**: What Python versions should the CI test matrix include?

**Options Presented**:
- A (Recommended): 3.14 only
- B: 3.14 + 3.15-dev
- C: 3.13 + 3.14

**User Answer**: 3.14 only

---

### Question 2: PyPI Publishing

**Context**: Phase doc mentions optional PyPI workflow.

**Question**: Should we include a PyPI publish workflow?

**Options Presented**:
- A (Recommended): Skip PyPI for now
- B: Manual-trigger workflow
- C: Auto-publish on tag

**User Answer**: Skip PyPI for now

---

### Question 3: Coverage Threshold

**Context**: pytest-cov installed but no threshold configured.

**Question**: What minimum coverage threshold for CI?

**Options Presented**:
- A (Recommended): 80%
- B: 90%
- C: No threshold, report only

**User Answer**: 80%

---

### Confirmed Understanding

**What the user wants to achieve**:
Prepare to-markdown for production/public release with polished docs, CI, and v1.0.0 tag.

**How it relates to existing code**:
Primarily documentation, configuration, and governance - minimal source code changes. Code audit
shows the codebase is already clean.

**Key constraints and requirements**:
- CI with Python 3.14 only (no PyPI publishing)
- 80% coverage threshold
- README rewritten for public audience
- All memory docs audited and updated
- CHANGELOG, LICENSE, and badges added
- v1.0.0 tagged

**Technical approach**:
- GitHub Actions for CI (lint + test + format check on PR)
- Coverage reporting via pytest-cov
- Conventional CHANGELOG from git history
- MIT LICENSE file from template

---

## Recommendations for SPECIFY

### Should Include in Spec

- README.md complete rewrite with badges, examples, architecture overview
- GitHub Actions CI workflow (lint, test, format, coverage)
- CHANGELOG.md from phase history
- LICENSE file (MIT)
- Memory doc updates (constitution, testing-strategy, glossary)
- Version 1.0.0 in pyproject.toml
- Coverage configuration in pyproject.toml
- Git tag v1.0.0

### Should Exclude from Spec (Non-Goals)

- PyPI publishing workflow (deferred per user)
- Additional Python version matrix (3.14 only per user)
- CONTRIBUTING.md (not requested, can be added later)
- SECURITY.md (not requested)
- Source code refactoring (codebase is already clean)
- New features or functionality

### Potential Risks

- Python 3.14 may not be fully available in GitHub Actions runners yet
- Coverage may be below 80% initially (need to measure first)
- CHANGELOG generation from git history may require manual curation
