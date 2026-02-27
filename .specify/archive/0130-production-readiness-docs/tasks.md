# Tasks: Production Readiness & Documentation

## Phase Goals Coverage

| # | Phase Goal | Spec Requirement(s) | Task(s) | Status |
|---|------------|---------------------|---------|--------|
| 1 | README overhaul for public-facing documentation | FR-001, FR-002, NFR-002 | T007-T008 | COVERED |
| 2 | Documentation cleanup and memory document audit | FR-009, FR-010, FR-011, NFR-003 | T009-T012 | COVERED |
| 3 | Code cleanup - TODOs, docstrings, lint, dead code, constants, 300-line limit | FR-014, SC-001, SC-002 | T001 | COVERED |
| 4 | Test suite hardening - fix flaky tests, coverage, edge cases | FR-005, FR-006, SC-004 | T002-T003 | COVERED |
| 5 | CI/CD setup with GitHub Actions | FR-003, FR-004, NFR-001 | T004-T006 | COVERED |
| 6 | Release preparation - v1.0.0, CHANGELOG, GitHub release | FR-007, FR-008, FR-012, FR-013 | T013-T016 | COVERED |
| 7 | Governance finalization - constitution, decisions, memory reconciliation | FR-009, FR-010, FR-011, NFR-003 | T009-T012 | COVERED |

Coverage: 7/7 goals COVERED

**Note**: Goals 2 and 7 overlap (governance docs are both documentation and governance).
Tasks T009-T012 serve both goals. This is intentional - a single set of tasks addresses
both concerns.

---

## Progress Dashboard

> Last updated: 2026-02-27 | Run `specflow tasks sync` to refresh

| Phase | Status | Progress |
|-------|--------|----------|
| Setup | PENDING | 0/3 |
| US1: README & Badges | PENDING | 0/2 |
| US2: CI/CD | PENDING | 0/3 |
| US3: Release Docs | PENDING | 0/3 |
| US4: Governance | PENDING | 0/4 |
| Release | PENDING | 0/2 |
| Verification | PENDING | 0/4 |

**Overall**: 0/21 (0%) | **Current**: None

---

**Input**: Design documents from `specs/0130-production-readiness-docs/`
**Prerequisites**: plan.md (required), spec.md (required)

## Phase 1: Setup (Foundation)

**Purpose**: Verify code cleanliness and measure coverage baseline

- [x] T001 [P] Run lint and format check — run `uv run ruff check` and `uv run ruff format --check`; fix ALL errors and formatting violations; result MUST be 0 errors and 0 format changes (FR-014)
- [x] T002 [P] Add coverage configuration to pyproject.toml — add `[tool.coverage.run]` with `source = ["src/to_markdown"]` and `[tool.coverage.report]` with `fail_under = 80` and `omit = ["*/tests/*"]` (FR-006)
- [x] T003 Measure baseline coverage — run `uv run pytest --cov=to_markdown --cov-fail-under=80`; if below 80%, identify gaps and add tests until threshold is met (FR-005, SC-004). Depends on T002.

**Checkpoint**: Baseline measured, lint clean, ready for CI and docs work

---

## Phase 2: US1 - README & Badges (Priority: P1)

**Goal**: Polished, public-facing README with badges

**Independent Test**: Visit repo page, verify README is clear and complete

- [x] T007 [US1] Rewrite README.md — structure: (a) title + 2-sentence purpose + badges, (b) "What it does" feature highlights, (c) quick start (install + first conversion), (d) usage examples (single file, batch, smart features, background, sanitization), (e) AI Agent Integration (MCP) condensed, (f) exit codes table, (g) Development section (test/lint/format commands), (h) License section. REMOVE the "How to Test (Phase 0100: MCP Server)" section (lines 225-256 of current README). Must be readable by non-technical users in the overview. (FR-001, NFR-002)
- [x] T008 [P] [US1] Add badges to README.md — Python version badge (`python-3.14+-blue`), MIT license badge, and CI status badge pointing to `.github/workflows/ci.yml`. Use shields.io or GitHub badge URLs. (FR-002)

---

## Phase 3: US2 - CI/CD (Priority: P1)

**Goal**: GitHub Actions CI that catches regressions on every PR

**Independent Test**: Push a branch and verify CI runs successfully

- [x] T004 [US2] Create `.github/workflows/ci.yml` — single job on ubuntu-latest; steps: checkout, `astral-sh/setup-uv@v5`, `actions/setup-python@v5` with `python-version: '3.14'` and `allow-prereleases: true`, `uv sync --all-extras`, `uv run ruff check`, `uv run ruff format --check`, `uv run pytest --cov=to_markdown --cov-fail-under=80`. Trigger on PR to main and push to main. (FR-003, FR-004, FR-005)
- [x] T005 [P] [US2] Validate CI workflow YAML — verify syntax is valid, action versions exist, step ordering correct. (SC-005)
- [x] T006 [US2] Update README CI badge URL — point badge to actual workflow path `wiseyoda/to-markdown/actions/workflows/ci.yml`. Depends on T004.

---

## Phase 4: US3 - Release Documentation (Priority: P2)

**Goal**: CHANGELOG and LICENSE ready for v1.0.0

**Independent Test**: Read CHANGELOG.md, verify all 10 phases covered

- [x] T013 [P] [US3] Create CHANGELOG.md — Keep a Changelog format with v1.0.0 section; include all 10 phases in order (0010, 0020, 0030, 0040, 0050, 0100, 0110, 0120, 0125, 0130) with 2-3 bullet points each summarizing key features. Reference ROADMAP.md and MEMORY.md for phase summaries. (FR-007, SC-007)
- [x] T014 [P] [US3] Create LICENSE file — full MIT license text with `Copyright (c) 2026` and project owner. Standard MIT template from opensource.org. (FR-008, SC-008)
- [x] T015 [US3] Verify release files — confirm CHANGELOG covers all 10 phases with substantive descriptions; confirm LICENSE has standard MIT text. Depends on T013, T014.

---

## Phase 5: US4 - Governance Updates (Priority: P2)

**Goal**: All memory documents accurate and current

**Independent Test**: Read each doc and verify claims match codebase

- [x] T009 [P] [US4] Update constitution.md — fix line 126 "Google Gemini 3.0 Flash (Preview)" to "Google Gemini 2.5 Flash (GA)"; bump version from 1.2.0 to 1.2.1; update "Last Amended" date to 2026-02-27. (FR-009)
- [x] T010 [P] [US4] Update testing-strategy.md — update test count to 505+; add Phase 0125 notes (async pattern testing with pytest-asyncio, sanitization test coverage, parallel LLM test strategies); bump version from 1.1.0 to 1.2.0; update date. Reference MEMORY.md "Phase 0125 Implementation Notes". (FR-010)
- [x] T011 [P] [US4] Update glossary.md — add 4 terms: "Sanitization" (filtering non-visible Unicode chars for prompt injection prevention), "Background Task" (detached subprocess conversion via --background flag), "MCP" (Model Context Protocol for AI agent integration), "Clean" (LLM-powered extraction artifact repair, auto-enabled with API key); bump version from 2.0.0 to 2.1.0; update date. (FR-011)
- [x] T012 [US4] Verify all memory docs — cross-check all versions, dates, and claims against codebase; verify constitution, coding-standards, testing-strategy, tech-stack, and glossary are all current. Depends on T009, T010, T011. (NFR-003, SC-009)

---

## Phase 6: Release

**Purpose**: Version bump (git tag is created during `/flow.merge`, not here)

- [x] T016 Set version to "1.0.0" in pyproject.toml — update `version` field. (FR-012, SC-010)
- [x] T017 Update `src/to_markdown/__init__.py` — if `__version__` is defined there, update to "1.0.0"

---

## Phase 7: Verification

- [x] T018 [V] Run test suite — `uv run pytest` all tests pass (SC-003)
- [x] T019 [V] Run linter and formatter — `uv run ruff check` 0 errors, `uv run ruff format --check` all formatted (SC-001, SC-002)
- [x] T020 [V] Run coverage check — `uv run pytest --cov=to_markdown --cov-fail-under=80` passes (SC-004)
- [x] T021 [V] Verify all new files committed — CHANGELOG.md, LICENSE, `.github/workflows/ci.yml`, updated README.md, updated memory docs

---

## Dependencies & Execution Order

### Task Dependencies

| Task | Depends On | Reason |
|------|-----------|--------|
| T003 | T002 | Coverage config must exist before measuring |
| T006 | T004 | Badge URL requires workflow to exist |
| T008 | T004 | CI badge requires workflow to exist |
| T012 | T009, T010, T011 | Verify after all docs updated |
| T015 | T013, T014 | Verify after release files created |
| T016-T017 | T001-T015 | Version bump is last before verification |
| T018-T021 | T016-T017 | Final verification after all changes |

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (README)**: Can start after Phase 1
- **Phase 3 (CI/CD)**: Can start after Phase 1; T006 depends on T004
- **Phase 4 (Release Docs)**: Can start after Phase 1 (parallel with Phases 2-3)
- **Phase 5 (Governance)**: Can start after Phase 1 (parallel with Phases 2-4)
- **Phase 6 (Release)**: Depends on Phases 2-5 complete
- **Phase 7 (Verification)**: Depends on Phase 6

### Parallel Opportunities

- T001, T002 can run in parallel (lint vs coverage config)
- T007 and T004 can run in parallel (README vs CI workflow)
- T009, T010, T011 can all run in parallel (different memory docs)
- T013, T014 can run in parallel (CHANGELOG vs LICENSE)
