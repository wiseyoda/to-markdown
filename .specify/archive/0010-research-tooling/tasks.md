# Tasks: Research & Tooling

## Phase Goals Coverage

| # | Phase Goal | Spec Requirement(s) | Task(s) | Status |
|---|------------|---------------------|---------|--------|
| 1 | Research core tooling | FR-001, FR-007 | T001 | COVERED |
| 2 | Research extraction backend (Kreuzberg) | FR-001, FR-007 | T002 | COVERED |
| 3 | Research LLM integration | FR-001 | T003 | COVERED |
| 4 | Human confirmation on all selections | SC-005 | USER GATE | COVERED |
| 5 | Update tech-stack.md | FR-003 | T008 | COVERED |
| 6 | Update future phase files / ROADMAP | FR-005, FR-006 | T010, T011 | COVERED |
| 7 | Update decisions.md | FR-004 | T009 | COVERED |

Coverage: 7/7 goals (100%)

---

## Progress Dashboard

> Last updated: 2026-02-25 | Run `specflow tasks sync` to refresh

| Phase | Status | Progress |
|-------|--------|----------|
| Research | PENDING | 0/4 |
| Governance Updates | PENDING | 0/7 |
| Verification | PENDING | 0/4 |

**Overall**: 0/15 (0%) | **Current**: None

---

**Input**: Design documents from `specs/0010-research-tooling/`
**Prerequisites**: plan.md (required), spec.md (required)

## Phase 1: Research Documents

**Purpose**: Write research documents capturing all findings and decisions

- [x] T001 [P] [US1] Write core tooling research in .specify/memory/research/core-tooling.md
- [x] T002 [P] [US2] Write Kreuzberg evaluation and adoption rationale in .specify/memory/research/kreuzberg.md
- [x] T003 [P] [US3] Write LLM integration research in .specify/memory/research/llm-integration.md
- [x] T004 [P] [US2] Write cross-cutting comparison (MarkItDown vs Kreuzberg vs per-format) in .specify/memory/research/cross-cutting.md

**Checkpoint**: All research documents created with verified, sourced findings

---

## Phase 2: Governance Updates

**Purpose**: Update all governance documents with confirmed selections and new architecture

- [x] T005 [US5] Update .specify/memory/constitution.md Principle III for wrapper architecture
- [x] T006 [US5] Update .specify/memory/coding-standards.md with Python 3.14 and ruff 0.15 config
- [x] T007 [US5] Update .specify/memory/coding-standards.md project structure for wrapper architecture
- [x] T008 [US5] Update .specify/memory/tech-stack.md with Kreuzberg and all confirmed versions
- [x] T009 [US5] Add decisions D-31 through D-40+ to .specify/discovery/decisions.md
- [x] T010 [US4] Restructure ROADMAP.md with new Kreuzberg wrapper phases
- [x] T011 [US4] Create new phase files for 0020-0050 and archive obsolete 0025-0090 files

**Checkpoint**: All governance documents reflect the Kreuzberg wrapper architecture

---

## Phase 3: Verification

- [x] T012 [V] Verify research documents exist in .specify/memory/research/
- [x] T013 [V] Verify tech-stack.md has zero TBD entries; Kreuzberg listed as extraction backend
- [x] T014 [V] Verify decisions.md contains D-31+ entries for all new selections
- [x] T015 [V] Verify ROADMAP.md and phase files reflect wrapper architecture

---

## Dependencies & Execution Order

### Phase Dependencies

- **Research (Phase 1)**: No dependencies - all 4 tasks can run in parallel
- **Governance Updates (Phase 2)**: Depends on Phase 1 completion
  - T005-T009 can run in parallel (different files)
  - T010 (ROADMAP) should run before T011 (phase files)
- **Verification (Phase 3)**: Depends on Phase 2 completion

### Parallel Opportunities

- All research tasks (T001-T004) can run in parallel (different output files)
- Governance tasks T005-T009 can run in parallel (different files)
- T010 must complete before T011 (phase files depend on ROADMAP structure)
- Verification tasks T012-T015 can run in parallel

## Notes

- [P] tasks = different files, no dependencies
- [V] tasks = verification checks run during /flow.verify
- No [W] wiring tasks needed - this is a research phase with no application code
- All tasks produce documentation, not code
