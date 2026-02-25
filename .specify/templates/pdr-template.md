---
version: '1.0'
description: 'Product Design Requirements template - captures WHAT we want, not HOW to build it'
---

# PDR: [FEATURE NAME]

<!--
  IMPORTANT: This document captures PRODUCT requirements, not TECHNICAL requirements.
  Focus on WHAT the feature should do and WHY it matters.
  Do NOT include: architecture, code structure, implementation details, or technology choices.

  Think like a product manager, not an engineer.
-->

**PDR ID**: `pdr-[short-slug]`
**Created**: [DATE]
**Author**: [NAME or "Agent"]
**Status**: Draft | Ready | Approved | Implemented
**Priority**: P1 | P2 | P3

---

## Problem Statement

<!--
  What problem are we solving? Why does this matter now?
  Be specific about the pain point. Use concrete examples.
-->

**The Problem**: [Describe the current pain point or gap]

**Who is affected**: [User personas or roles impacted]

**Current workaround**: [How do users cope today, if at all?]

**Why now**: [What makes this timely or urgent?]

---

## Desired Outcome

<!--
  What does success look like from the user's perspective?
  Describe the end state, not the journey to get there.
-->

**After this feature ships, users will be able to**:
- [Outcome 1 - what they can DO that they couldn't before]
- [Outcome 2]
- [Outcome 3]

**The experience should feel**: [adjectives - e.g., "seamless", "instant", "trustworthy"]

---

## User Stories

<!--
  Write from the user's perspective. Focus on goals and value, not mechanics.
  Each story should be independently valuable.
-->

### Story 1: [Brief Title]
**As a** [type of user],
**I want to** [goal or desire],
**So that** [benefit or value I receive].

**Value**: [Why this matters to the user]

---

### Story 2: [Brief Title]
**As a** [type of user],
**I want to** [goal or desire],
**So that** [benefit or value I receive].

**Value**: [Why this matters to the user]

---

### Story 3: [Brief Title]
**As a** [type of user],
**I want to** [goal or desire],
**So that** [benefit or value I receive].

**Value**: [Why this matters to the user]

---

## Success Criteria

<!--
  How will we KNOW this feature is successful?
  These should be measurable, observable, and testable.
  Avoid technical metrics - focus on user outcomes.
-->

| Criterion | Target | How We'll Measure |
|-----------|--------|-------------------|
| [User behavior/outcome] | [Specific target] | [Observable indicator] |
| [User satisfaction metric] | [Specific target] | [Observable indicator] |
| [Business outcome] | [Specific target] | [Observable indicator] |

---

## Constraints

<!--
  What are the boundaries we must work within?
  These are NOT implementation constraints - they are product/business constraints.
-->

- **Must**: [Non-negotiable requirement - e.g., "Must work offline"]
- **Must**: [Another hard requirement]
- **Should**: [Important but not blocking - e.g., "Should complete in under 3 seconds"]
- **Must Not**: [Explicit prohibition - e.g., "Must not require account creation"]

---

## Non-Goals

<!--
  What are we explicitly NOT trying to solve?
  This prevents scope creep and sets clear boundaries.
-->

- **Not solving**: [Related problem we're deferring]
- **Not solving**: [Adjacent feature we're intentionally excluding]
- **Out of scope**: [Thing users might expect but we won't include]

---

## Dependencies

<!--
  What external factors affect this feature?
  These are product/business dependencies, not technical ones.
-->

| Dependency | Type | Impact | Status |
|------------|------|--------|--------|
| [External system/process] | Blocking / Informational | [How it affects us] | Known / Unknown |
| [Other feature/PDR] | Blocking / Informational | [How it affects us] | Known / Unknown |

---

## Open Questions

<!--
  What do we still need to figure out?
  Mark questions as they get resolved.
-->

- [ ] [Unresolved question about user needs or product direction]
- [ ] [Another open question]
- [x] [Resolved question] → **Answer**: [The resolution]

---

## Acceptance Criteria

<!--
  When is this feature DONE from a product perspective?
  These are the conditions that must be true before we ship.
-->

1. [ ] [Observable user-facing behavior that must work]
2. [ ] [Another observable behavior]
3. [ ] [Edge case that must be handled]
4. [ ] [User verification checkpoint - e.g., "User can complete [task] without assistance"]

---

## Related PDRs

<!--
  Link to other PDRs that this feature relates to.
  This helps when bundling PDRs into phases.
-->

- `pdr-[slug]`: [Relationship - e.g., "depends on", "enables", "conflicts with"]

---

## Notes

<!--
  Any additional context, research links, user quotes, or background.
-->

- [Additional context]
- [User feedback or quotes that inspired this PDR]
