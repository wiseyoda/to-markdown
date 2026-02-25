# Feature Specification: Research & Tooling

**Feature Branch**: `0010-research-tooling`
**Created**: 2026-02-25
**Status**: Draft
**Input**: Phase 0010 definition + discovery research findings

## User Scenarios & Testing

### User Story 1 - Core Tooling Research (Priority: P1)

As a developer, I need confirmed, up-to-date versions and configurations for all core
development tools so that future phases build on a verified foundation.

**Why this priority**: Every subsequent phase depends on these tools being correct.

**Independent Test**: Research documents exist with verified versions; tech-stack.md is updated.

**Acceptance Scenarios**:

1. **Given** the project targets Python 3.14+, **When** I check the research doc,
   **Then** it confirms 3.14 compatibility for all core tools (uv, Typer, ruff, pytest).
2. **Given** ruff 0.15+ has a new 2026 style guide, **When** I check the research doc,
   **Then** it includes recommended ruff configuration for pyproject.toml.
3. **Given** syrupy is recommended for snapshot testing, **When** I check the research doc,
   **Then** it includes usage examples relevant to golden file testing of Markdown output.

---

### User Story 2 - Kreuzberg Evaluation & Adoption (Priority: P1)

As a developer, I need a thorough evaluation of Kreuzberg as the extraction backend so that
the project architecture wraps Kreuzberg instead of building per-format parsers from scratch.

**Why this priority**: This decision eliminates 6 per-format converter phases and fundamentally
simplifies the project. All subsequent phases depend on this architectural direction.

**Independent Test**: Research document exists confirming Kreuzberg's capabilities per format,
with known limitations and quality baselines documented.

**Acceptance Scenarios**:

1. **Given** Kreuzberg handles all 6 target formats, **When** I read the research doc,
   **Then** each format has: quality assessment, known limitations, and output examples.
2. **Given** Kreuzberg is Beta (v4.3.8), **When** I read the research doc,
   **Then** it documents the API stability risk and mitigation strategy (adapter interface).
3. **Given** Kreuzberg outputs metadata as a structured object, **When** I read the research doc,
   **Then** it documents how to compose YAML frontmatter from Kreuzberg's metadata.

---

### User Story 3 - LLM Integration Research (Priority: P2)

As a developer, I need a confirmed LLM integration approach (SDK, model, error handling) so that
the smart features phase (0080) has clear implementation guidance.

**Why this priority**: Smart features are later phases but the SDK choice affects tech-stack now.

**Independent Test**: Research document exists with SDK choice, model recommendation, and code patterns.

**Acceptance Scenarios**:

1. **Given** google-genai is the SDK choice, **When** I read the LLM research doc,
   **Then** it includes working code patterns for text generation and vision/image description.
2. **Given** Gemini 2.5 Flash is the default, **When** I read the research doc,
   **Then** it documents the GEMINI_MODEL env var override pattern for future model upgrades.

---

### User Story 4 - ROADMAP Restructuring (Priority: P1)

As a developer, I need the ROADMAP and phase files restructured to reflect the Kreuzberg wrapper
architecture so that future phases are scoped correctly.

**Why this priority**: The old ROADMAP has 6 per-format converter phases that are no longer
needed. The new ROADMAP should reflect the wrapper architecture.

**Independent Test**: ROADMAP.md reflects the new phase structure with Kreuzberg as the
extraction backend.

**Acceptance Scenarios**:

1. **Given** Kreuzberg replaces per-format libraries, **When** I read the ROADMAP,
   **Then** phases are restructured around: core CLI wrapper, format quality tuning,
   smart features, and batch processing.
2. **Given** old phases 0025-0070 are obsolete, **When** I check phase files,
   **Then** old phase files are archived and new phase files exist for the revised scope.

---

### User Story 5 - Governance Updates (Priority: P1)

As a developer, I need all governance documents updated with concrete selections so that
subsequent phases have authoritative references.

**Why this priority**: Stale governance docs lead to wrong decisions in later phases.

**Independent Test**: tech-stack.md, decisions.md, and phase files all reflect confirmed choices.

**Acceptance Scenarios**:

1. **Given** all library selections are confirmed, **When** I read tech-stack.md,
   **Then** every TBD slot is filled with a specific library name and version.
2. **Given** new decisions were made, **When** I read decisions.md,
   **Then** D-31+ entries exist for each library selection with rationale.
3. **Given** future phases reference specific libraries, **When** I read phase files 0020-0090,
   **Then** each phase mentions its confirmed libraries by name.

---

### Edge Cases

- What happens if a recommended library doesn't support Python 3.14? Document the gap and
  provide a workaround or fallback.
- What if MarkItDown/Kreuzberg produce better output than individual libraries for some format?
  Document the finding and recommend reconsidering the per-format approach for that format.

## Requirements

### Functional Requirements

- **FR-001**: Phase MUST produce research documents in `.specify/memory/research/` for:
  core-tooling, kreuzberg (extraction backend), llm-integration, and a cross-cutting
  comparison of MarkItDown vs Kreuzberg vs per-format libraries.
- **FR-002**: Each research document MUST follow the template format from the phase definition
  (candidates, pros/cons, recommendation, human decision).
- **FR-003**: Phase MUST update `tech-stack.md` replacing all TBD per-format library entries
  with Kreuzberg and adding confirmed versions for all tools.
- **FR-004**: Phase MUST add decisions D-31+ to `decisions.md` for: Python version, Kreuzberg
  adoption, LLM model selection, snapshot testing, and ROADMAP restructuring.
- **FR-005**: Phase MUST restructure ROADMAP.md to reflect the Kreuzberg wrapper architecture,
  replacing per-format converter phases with wrapper-oriented phases.
- **FR-006**: Phase MUST create new phase files for the restructured ROADMAP and archive
  the obsolete per-format phase files.
- **FR-007**: Phase MUST verify Python 3.14 compatibility for Kreuzberg and all core tools.
- **FR-008**: Phase MUST update constitution.md Principle III to reflect that extensibility
  now means configuring Kreuzberg, not writing per-format parser plugins.
- **FR-009**: Phase MUST update coding-standards.md with Python 3.14 config and ruff 0.15
  settings.

### Non-Functional Requirements

- **NFR-001**: All research documents MUST cite sources (PyPI links, GitHub repos, release pages).
- **NFR-002**: Research MUST reflect February 2026 state, not stale May 2025 knowledge.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Research documents exist in `.specify/memory/research/` for core-tooling,
  kreuzberg, llm-integration, and cross-cutting evaluation.
- **SC-002**: tech-stack.md has zero TBD entries remaining; Kreuzberg listed as extraction backend.
- **SC-003**: decisions.md contains D-31+ entries for all new selections including Kreuzberg pivot.
- **SC-004**: ROADMAP.md restructured with new phase files reflecting wrapper architecture.
- **SC-005**: User has confirmed all selections via the USER GATE.
