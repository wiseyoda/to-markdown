# Implementation Plan: Research & Tooling

**Branch**: `0010-research-tooling` | **Date**: 2026-02-25 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/0010-research-tooling/spec.md`

## Summary

Research, evaluate, and document all tool selections for the to-markdown project. The major
finding is the adoption of **Kreuzberg** as the extraction backend, pivoting from a per-format
parser approach to a thin CLI wrapper architecture. This phase produces research documents,
restructures the ROADMAP, and updates all governance documents.

No application code is written in this phase.

## Technical Context

**Language/Version**: Python 3.14+
**Primary Dependencies**: N/A (research phase - no code)
**Storage**: N/A
**Testing**: N/A (no code to test)
**Target Platform**: macOS (development), cross-platform (eventual)
**Project Type**: Single CLI project
**Constraints**: Research must reflect February 2026 state

## Constitution Check

_GATE: Passed with amendments needed._

- **Principle I (Completeness)**: Kreuzberg achieves 91% F1 on PDF Markdown output. Meets
  the completeness standard for extraction. LLM features (--summary, --images) add remaining
  completeness for image/chart descriptions.
- **Principle III (Extensible Architecture)**: NEEDS UPDATE. The plugin registry pattern now
  means configuring Kreuzberg's extraction options per format, not writing separate parsers.
  The pipeline becomes: Kreuzberg extract -> compose frontmatter -> apply LLM features -> output.
- **Principle IV (Simplicity)**: Wrapping Kreuzberg is dramatically simpler than writing 6
  format parsers. ~500-800 lines of wrapper code vs. thousands.
- **Principle VI (Zero Tolerance)**: Research documents must be thorough and well-sourced.

## Architectural Pivot: Kreuzberg Wrapper

### Old Architecture (per-format parsers)

```
Input File -> Registry (select converter by extension)
           -> Converter.parse() -> Document IR
           -> Normalizer.normalize() -> Normalized Document
           -> Renderer.render() -> Markdown string
           -> Output (.md file with frontmatter)
```

### New Architecture (Kreuzberg wrapper)

```
Input File -> Kreuzberg.extract(output_format="markdown")
           -> result.content (Markdown) + result.metadata (structured)
           -> Compose YAML frontmatter from metadata
           -> Optionally apply LLM features (--summary, --images)
           -> Assemble final .md (frontmatter + content)
           -> Output (.md file)
```

### Key Differences

- **No per-format parsers needed**: Kreuzberg handles PDF, DOCX, PPTX, XLSX, HTML, images, 76+ formats
- **No intermediate representation**: Kreuzberg produces Markdown directly
- **Frontmatter is our value-add**: Kreuzberg provides metadata; we compose it into YAML
- **LLM features are our value-add**: --summary, --images via Gemini
- **Quality testing is our value-add**: Golden file tests on Kreuzberg's output per format
- **CLI UX is our value-add**: Typer, --force, --verbose, magic defaults

### ROADMAP Restructuring

Old phases (per-format):
```
0010 Research & Tooling
0020 Core Pipeline
0025 HTML Converter
0030 PDF Converter
0040 DOCX Converter
0050 PPTX Converter
0060 XLSX Converter
0070 Image & OCR
0080 Smart Features
0090 Batch Processing
```

New phases (Kreuzberg wrapper):
```
0010 Research & Tooling          <- Current phase (includes ROADMAP restructure)
0020 Core CLI & Pipeline         <- Typer CLI + Kreuzberg integration + frontmatter
0030 Format Quality & Testing    <- Golden file tests per format, quality tuning
0040 Smart Features              <- --summary, --images via Gemini
0050 Batch Processing            <- Directory/glob conversion
```

## Project Structure

### Research Output

```text
.specify/memory/research/
  core-tooling.md       # Python, uv, Typer, ruff, pytest, syrupy
  kreuzberg.md          # Kreuzberg evaluation and adoption rationale
  llm-integration.md    # Gemini SDK and LLM approach
  cross-cutting.md      # MarkItDown vs Kreuzberg vs per-format comparison
```

### Governance Updates

```text
ROADMAP.md                            # Restructured with new phases
.specify/memory/tech-stack.md         # Kreuzberg + confirmed tool versions
.specify/memory/constitution.md       # Principle III updated
.specify/memory/coding-standards.md   # Python 3.14 + ruff 0.15 config
.specify/discovery/decisions.md       # D-31+ entries
.specify/phases/                      # New phase files for 0020-0050
```

## Governance Update Strategy

Updates flow in dependency order:
1. Research documents (source of truth for all decisions)
2. decisions.md (rationale and context for each choice)
3. constitution.md (Principle III amendment for wrapper architecture)
4. tech-stack.md (Kreuzberg + all confirmed tools)
5. coding-standards.md (Python 3.14 + ruff 0.15 config)
6. ROADMAP.md (restructured phases)
7. Phase files (new files for 0020-0050, archive old 0025-0090)
