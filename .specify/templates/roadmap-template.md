# [PROJECT_NAME] Development Roadmap

> **Source of Truth**: This document defines all feature phases, their order, and completion status.
> Work proceeds through phases sequentially. Each phase produces a deployable increment.

**Project**: [PROJECT_NAME] - [PROJECT_DESCRIPTION]
**Created**: [CREATED_DATE]
**Schema Version**: 3.0 (ABBC numbering)
**Status**: Active Development

---

## Phase Numbering

Phases use **ABBC** format:

- **A** = Milestone (0-9) - Major version or project stage
- **BB** = Phase (01-99) - Sequential work within milestone
- **C** = Hotfix (0-9) - Insert slot (0 = main phase, 1-9 = hotfixes/inserts)

**Examples**:

- `0010` = Milestone 0, Phase 01, no hotfix
- `0021` = Hotfix 1 inserted after Phase 02
- `1010` = Milestone 1, Phase 01, no hotfix

This allows inserting urgent work without renumbering existing phases.

---

## Phase Overview

| Phase | Name | Status | Verification Gate |
| ----- | ---- | ------ | ----------------- |
| 0010  | [PHASE_NAME] | ⬜ Not Started | [GATE_DESCRIPTION] |
| 0020  | [PHASE_NAME] | ⬜ Not Started | [GATE_DESCRIPTION] |
| 0030  | [PHASE_NAME] | ⬜ Not Started | **USER GATE**: [GATE_DESCRIPTION] |

**Legend**: ⬜ Not Started | 🔄 In Progress | ✅ Complete | **USER GATE** = Requires user verification

---

## Phase Details

Phase details are stored in modular files:

| Location                      | Content                      |
| ----------------------------- | ---------------------------- |
| `.specify/phases/*.md`        | Active/pending phase details |
| `.specify/history/HISTORY.md` | Archived completed phases    |

To view a specific phase:

```bash
specflow phase show 0010
```

To list all phases:

```bash
specflow phase list
specflow phase list --active
specflow phase list --complete
```

---

## Verification Gates Summary

| Gate       | Phase | What User Verifies           |
| ---------- | ----- | ---------------------------- |
| **Gate 1** | 0030  | [USER_VERIFICATION_CRITERIA] |

---

## Phase Sizing Guidelines

Each phase is designed to be:

- **Completable** in a single agentic coding session (~200k tokens)
- **Independently deployable** (no half-finished features)
- **Verifiable** with clear success criteria
- **Building** on previous phases

If a phase is running long:

1. Cut scope to MVP for that phase
2. Document deferred items in `specs/[phase]/checklists/deferred.md`
3. Prioritize verification gate requirements

---

## How to Use This Document

### Starting a Phase

```
/flow.orchestrate
```

Or manually:

```
/flow.design "Phase NNNN - [Phase Name]"
```

### After Completing a Phase

1. Run `/flow.verify` to verify the phase is complete
2. Run `/flow.merge` to close, push, and merge (updates ROADMAP automatically)
3. If USER GATE: get explicit user verification before proceeding

### Adding New Phases

Use SpecFlow commands:

```bash
specflow phase add 0025 "new-phase-name"
specflow phase add 0025 "new-phase-name" --user-gate --gate "Description"
specflow phase open --hotfix "Urgent Fix"
```
