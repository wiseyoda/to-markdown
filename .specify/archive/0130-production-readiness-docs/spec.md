---
version: '1.1'
description: 'Feature specification for production readiness and documentation'
---

# Feature Specification: Production Readiness & Documentation

**Feature Branch**: `0130-production-readiness-docs`
**Created**: 2026-02-27
**Status**: Draft

## User Scenarios & Testing

### User Story 1 - README-Driven First Impression (Priority: P1)

A developer discovers to-markdown on GitHub. They read the README and within 2 minutes
understand what the tool does, how to install it, and how to use it. Badges show the
project is actively maintained and tests pass.

**Why this priority**: The README is the public face of the project. A poor README kills
adoption regardless of code quality.

**Independent Test**: Visit the GitHub repo page and verify the README is clear, complete,
and visually polished with badges.

**Acceptance Scenarios**:

1. **Given** a developer visits the repo, **When** they read the README, **Then** they
   understand the tool's purpose in the first 2 sentences, see install instructions, and
   find at least 3 usage examples
2. **Given** a developer reads the README, **When** they look for badges, **Then** they
   see Python version, license, and CI status badges at the top
3. **Given** a developer wants to contribute, **When** they read the README, **Then** they
   find a Development section with testing commands (`pytest`, `ruff check`, `ruff format`)

---

### User Story 2 - CI Catches Regressions (Priority: P1)

A contributor opens a PR with a change that breaks tests or introduces lint violations.
GitHub Actions CI runs automatically and flags the issue before merge.

**Why this priority**: CI is essential for maintaining code quality as the project grows.
Without it, regressions slip into main.

**Independent Test**: Push a branch with a failing test and verify CI catches it.

**Acceptance Scenarios**:

1. **Given** a PR is opened, **When** CI runs, **Then** lint check (`ruff check`),
   format check (`ruff format --check`), and tests (`pytest`) all execute
2. **Given** tests fail on a PR, **When** the author views the PR, **Then** they see
   which check failed and can read the error output
3. **Given** coverage drops below 80%, **When** CI runs, **Then** the coverage check fails

---

### User Story 3 - Release Documentation (Priority: P2)

A user upgrading to v1.0.0 wants to know what changed across all development phases.
They read the CHANGELOG and understand the full feature set.

**Why this priority**: Release documentation provides confidence that the project is
mature and well-maintained.

**Independent Test**: Read CHANGELOG.md and verify it covers all 10 phases (0010-0050,
0100-0130).

**Acceptance Scenarios**:

1. **Given** a user reads CHANGELOG.md, **When** they look for v1.0.0, **Then** they find
   a summary of all features with 2-3 bullets per phase
2. **Given** a user checks the license, **When** they look for LICENSE, **Then** they find
   the full MIT license text with 2026 copyright

---

### User Story 4 - Governance Accuracy (Priority: P2)

A developer (or AI agent) reads the memory documents to understand project conventions.
All documents are accurate and reflect the current state of the codebase.

**Why this priority**: Stale governance docs cause incorrect decisions in future development.

**Independent Test**: Read each memory doc and verify claims match the codebase.

**Acceptance Scenarios**:

1. **Given** an agent reads constitution.md, **When** it checks the LLM reference,
   **Then** it finds "Gemini 2.5 Flash (GA)" (not stale "3.0 Flash")
2. **Given** an agent reads testing-strategy.md, **When** it checks the test count,
   **Then** it finds the current count (505+) and Phase 0125 additions documented
3. **Given** an agent reads glossary.md, **When** it looks for "Sanitization",
   **Then** it finds a definition

---

### User Story 5 - Clean v1.0.0 Release (Priority: P3)

The project owner tags v1.0.0 and the version in pyproject.toml matches the git tag.
The project metadata is complete and accurate.

**Why this priority**: Version consistency is important but depends on all other work
being complete first.

**Independent Test**: Check `pyproject.toml` version matches git tag.

**Acceptance Scenarios**:

1. **Given** the release is prepared, **When** checking pyproject.toml, **Then** version
   is "1.0.0"
2. **Given** v1.0.0 is tagged, **When** checking git tags, **Then** `v1.0.0` exists

---

### Edge Cases

- What happens if Python 3.14 is not available on GitHub Actions runners?
  - Use `actions/setup-python@v5` with `allow-prereleases: true`
- What if current coverage is below 80%?
  - Measure first, add tests if needed to reach threshold
- What if CHANGELOG generation misses important details?
  - Manual curation based on ROADMAP phase descriptions and MEMORY.md

## Requirements

### Functional Requirements

- **FR-001**: README.md MUST be rewritten as a polished, public-facing document containing:
  (a) project title and 2-sentence purpose description, (b) badges (Python version, license,
  CI status), (c) feature highlights ("What it does"), (d) quick start with install and
  first conversion, (e) usage examples (single file, batch, smart features, background,
  sanitization), (f) AI Agent Integration (MCP) section, (g) exit codes table, (h) Development
  section (test, lint, format commands), (i) License section. README MUST be readable by
  non-technical users for the overview section (NFR-002). Phase-specific testing instructions
  (current "How to Test Phase 0100" section) MUST be removed.
- **FR-002**: README.md MUST include badges for Python version, license, and CI status
  using shields.io or GitHub's built-in badge URLs
- **FR-003**: GitHub Actions CI workflow MUST run `ruff check`, `ruff format --check`,
  and `pytest --cov=to_markdown --cov-fail-under=80` on every PR to main and on push
  to main
- **FR-004**: CI MUST test against Python 3.14 only, using `actions/setup-python@v5`
  with `allow-prereleases: true` for availability
- **FR-005**: CI MUST enforce 80% minimum test coverage via pytest-cov
- **FR-006**: Coverage configuration MUST be added to pyproject.toml with
  `[tool.coverage.run]` (source = `["src/to_markdown"]`) and `[tool.coverage.report]`
  (`fail_under = 80`, `omit = ["*/tests/*"]`)
- **FR-007**: CHANGELOG.md MUST be created in Keep a Changelog format summarizing all
  10 phases (0010, 0020, 0030, 0040, 0050, 0100, 0110, 0120, 0125, 0130) with 2-3
  bullet points per phase describing key features
- **FR-008**: LICENSE file MUST be created with full MIT license text and 2026 copyright
- **FR-009**: constitution.md MUST be updated to fix stale "Gemini 3.0 Flash (Preview)"
  reference to "Gemini 2.5 Flash (GA)" and version bumped to v1.2.1
- **FR-010**: testing-strategy.md MUST be updated to version 1.2.0 with current test
  count (505+), Phase 0125 additions (async pattern testing, sanitization tests,
  parallel LLM test strategies), and updated date
- **FR-011**: glossary.md MUST be updated to version 2.1.0 with new terms:
  Sanitization (filtering non-visible Unicode for prompt injection prevention),
  Background Task (detached subprocess conversion via --background),
  MCP (Model Context Protocol for AI agent integration),
  Clean (LLM-powered extraction artifact repair, auto-enabled with API key)
- **FR-012**: pyproject.toml version MUST be set to "1.0.0"
- **FR-013**: Git tag `v1.0.0` MUST be created after all changes are merged to main
  (handled during `/flow.merge`, not during implementation)
- **FR-014**: All source files MUST pass `ruff check` with 0 errors and
  `ruff format --check` with all files formatted (code cleanup verification)

### Non-Functional Requirements

- **NFR-001**: CI workflow MUST complete in under 5 minutes for typical PR
- **NFR-002**: README overview section MUST be readable by non-technical users
  (incorporated into FR-001)
- **NFR-003**: All memory documents MUST have accurate version numbers and dates

## Success Criteria

### Measurable Outcomes

| SC | Metric | Verified By |
|----|--------|-------------|
| SC-001 | `uv run ruff check` produces 0 errors | T001, T019 |
| SC-002 | `uv run ruff format --check` shows all files formatted | T001, T019 |
| SC-003 | `uv run pytest` passes all tests (505+) | T018 |
| SC-004 | `uv run pytest --cov=to_markdown --cov-fail-under=80` passes | T003, T020 |
| SC-005 | GitHub Actions CI workflow runs successfully on a test PR | T005 |
| SC-006 | README.md has 3+ badges, install section, usage examples, architecture | T007, T008 |
| SC-007 | CHANGELOG.md covers all 10 phases | T013, T015 |
| SC-008 | LICENSE file exists with MIT text | T014 |
| SC-009 | All memory docs have current version numbers and dates | T012 |
| SC-010 | pyproject.toml shows version "1.0.0" | T016 |
