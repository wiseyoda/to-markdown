# Discovery Decisions

> Decisions captured during the discovery interview.
> Format: D-N where N is sequential.

---

#### D-1: Project Type
- **Phase**: 0 - Discovery
- **Status**: Decided
- **Confidence**: High
- **Context**: Establishing what to-markdown is
- **Decision**: File converter that converts files from various formats (HTML, PDF, DOCX, etc.) into Markdown
- **Alternatives**: Web scraper, content pipeline
- **Consequences**: Enables focused file-in/markdown-out architecture, Constrains scope to file conversion
- **Memory Doc Impact**: constitution.md

#### D-2: Software Type
- **Phase**: 0 - Discovery
- **Status**: Decided
- **Confidence**: High
- **Context**: How users interact with the tool
- **Decision**: CLI tool, run from the terminal
- **Alternatives**: Library/SDK, Web API, CLI + Library hybrid
- **Consequences**: Enables simple invocation, piping, and scripting; Constrains to terminal UX
- **Memory Doc Impact**: constitution.md, tech-stack.md

#### D-3: Primary Audience
- **Phase**: 0 - Discovery
- **Status**: Decided
- **Confidence**: High
- **Context**: Who will use this tool
- **Decision**: AI/LLM pipelines - used as a preprocessing step for feeding content to language models
- **Alternatives**: Developers, content creators, general users
- **Consequences**: Enables optimization for machine-readable output; Requires clean, structured Markdown output
- **Memory Doc Impact**: constitution.md

#### D-4: Project Stage
- **Phase**: 0 - Discovery
- **Status**: Decided
- **Confidence**: High
- **Context**: Starting point for development
- **Decision**: Greenfield - starting from scratch with no existing code
- **Alternatives**: Prototype, brownfield, rewrite
- **Consequences**: Enables clean architecture decisions; Requires all infrastructure to be built
- **Memory Doc Impact**: tech-stack.md

#### D-5: Existing Assets
- **Phase**: 0 - Discovery
- **Status**: Decided
- **Confidence**: High
- **Context**: What we're building from
- **Decision**: Nothing exists yet - truly starting from zero
- **Alternatives**: N/A
- **Consequences**: Requires building everything from scratch
- **Memory Doc Impact**: N/A

#### D-6: Key Constraints
- **Phase**: 0 - Discovery
- **Status**: Decided
- **Confidence**: High
- **Context**: Non-negotiable qualities
- **Decision**: Must be fast, easy to use, and easy to maintain. No hard language constraint.
- **Alternatives**: N/A
- **Consequences**: Constrains tech choices to languages/frameworks that are performant and maintainable
- **Memory Doc Impact**: constitution.md, tech-stack.md

#### D-7: Team Composition
- **Phase**: 0 - Discovery
- **Status**: Decided
- **Confidence**: High
- **Context**: Who will develop and maintain this
- **Decision**: Solo developer with AI assistance
- **Alternatives**: N/A
- **Consequences**: Requires simple architecture, good docs, low maintenance overhead
- **Memory Doc Impact**: constitution.md

#### D-8: Criticality Level
- **Phase**: 0 - Discovery
- **Status**: Decided
- **Confidence**: High
- **Context**: How critical is reliability
- **Decision**: Internal tool - used by developer/team, reliability matters but not mission-critical
- **Alternatives**: Hobby, production, mission-critical
- **Consequences**: Enables pragmatic trade-offs; Requires reasonable error handling but not exhaustive
- **Memory Doc Impact**: constitution.md

#### D-9: Core Problem Statement
- **Phase**: 1 - Problem & Vision
- **Status**: Decided
- **Confidence**: High
- **Context**: Why this tool needs to exist
- **Decision**: LLMs currently waste time re-extracting info from binary files each session - installing libraries, running ad-hoc conversion tools, and rarely saving output. to-markdown provides a one-shot conversion that produces an MD file so complete the LLM never needs to look at the source file again.
- **Alternatives**: Using existing tools (pandoc, markitdown, html2text) - all have issues with speed, output quality, or format coverage
- **Consequences**: Enables LLM-optimized output as the primary design goal; Requires "completeness" as a core quality metric
- **Memory Doc Impact**: constitution.md

#### D-10: Input Format Support
- **Phase**: 1 - Problem & Vision
- **Status**: Decided
- **Confidence**: High
- **Context**: Which file formats to support
- **Decision**: Core formats: PDF, DOCX, PPTX, Images (OCR), XLSX. Architecture must be extensible to support virtually any format in the future ("universal translator to markdown").
- **Alternatives**: Starting with just HTML+PDF
- **Consequences**: Requires plugin/extensible converter architecture; Enables future format additions without core changes
- **Memory Doc Impact**: tech-stack.md, constitution.md

#### D-11: Output Quality Requirements
- **Phase**: 1 - Problem & Vision
- **Status**: Decided
- **Confidence**: High
- **Context**: What the output Markdown should contain
- **Decision**: All of: structure preservation (headings, lists, tables), clean text extraction, and metadata retention. The guiding principle is that ALL information in the source file must be represented as text in the MD file. Structured data uses fenced code blocks within the MD.
- **Alternatives**: Text-only extraction, separate metadata files
- **Consequences**: Enables single-file consumption by LLMs; Requires robust extraction for each format
- **Memory Doc Impact**: constitution.md, coding-standards.md

#### D-12: Metadata Strategy
- **Phase**: 1 - Problem & Vision
- **Status**: Decided
- **Confidence**: High
- **Context**: How to represent document metadata
- **Decision**: YAML frontmatter for document metadata (title, author, dates, page count, etc.). Structured data found within documents represented as fenced code blocks inside the MD. No sidecar files - everything in one file.
- **Alternatives**: JSON sidecar files, no metadata
- **Consequences**: Enables single-file LLM consumption; Constrains to frontmatter-compatible metadata
- **Memory Doc Impact**: coding-standards.md

#### D-13: Smart Enhancement Flags
- **Phase**: 1 - Problem & Vision
- **Status**: Decided
- **Confidence**: High
- **Context**: Optional LLM-powered enhancements
- **Decision**: Support optional flags like --summary (adds LLM-generated summary at top) and --images (describes images/charts using a cheap LLM like Haiku). Core conversion works without any LLM. Smart features are opt-in.
- **Alternatives**: Always-on LLM features, no LLM features
- **Consequences**: Enables enhanced output when LLM API is available; Requires API key management for smart features; Core tool works offline
- **Memory Doc Impact**: constitution.md, tech-stack.md

#### D-14: CLI Interface Design
- **Phase**: 3 - Core Features
- **Status**: Decided
- **Confidence**: High
- **Context**: How users invoke the tool
- **Decision**: Simple invocation: `to-markdown file.pdf` creates file.md next to input. Optional `-o path` for custom output location (file or directory). No batch/directory/glob support initially.
- **Alternatives**: Directory support, glob patterns, stdin piping
- **Consequences**: Enables dead-simple UX; Batch processing deferred to later phase
- **Memory Doc Impact**: coding-standards.md

#### D-15: Output Default Location
- **Phase**: 3 - Core Features
- **Status**: Decided
- **Confidence**: High
- **Context**: Where converted files go
- **Decision**: Same directory as input file, same filename with .md extension. Overridable with `-o` flag pointing to a file or directory.
- **Alternatives**: CWD, dedicated output directory
- **Consequences**: Enables zero-config usage; Predictable output location
- **Memory Doc Impact**: coding-standards.md

#### D-16: Smart Defaults Philosophy
- **Phase**: 3 - Core Features
- **Status**: Decided
- **Confidence**: High
- **Context**: How much should "just work" vs require flags
- **Decision**: "Work like magic without a ton of flags." Extract tables as structured data by default. Auto-detect OCR needs. Flags only for non-default enhancements (--summary, --images, --toc, --chunk). The tool should produce excellent output with zero flags.
- **Alternatives**: Minimal defaults with many flags, opinionated single-mode
- **Consequences**: Enables great first-run experience; Requires smart auto-detection logic
- **Memory Doc Impact**: constitution.md, coding-standards.md

#### D-17: Converter Architecture
- **Phase**: 4 - Technical Architecture
- **Status**: Decided
- **Confidence**: High
- **Context**: How format handlers are organized internally
- **Decision**: Hybrid: plugin registry for format discovery (each format registers itself) + pipeline stages for processing (parse -> normalize -> render). Each plugin implements the parse stage; shared normalization and Markdown rendering handles the rest.
- **Alternatives**: Pure plugin, pure pipeline, simple strategy pattern
- **Consequences**: Enables easy addition of new formats; Requires well-defined intermediate representation between parse and render
- **Memory Doc Impact**: coding-standards.md, tech-stack.md

#### D-18: Implementation Language
- **Phase**: 4 - Technical Architecture
- **Status**: Decided
- **Confidence**: High
- **Context**: Which language to build in
- **Decision**: Python. Best library ecosystem for document processing (PDF, DOCX, PPTX, OCR). Good fit for the problem domain.
- **Alternatives**: TypeScript/Node, Go, Rust
- **Consequences**: Enables access to best document parsing libraries; Requires Python runtime
- **Memory Doc Impact**: tech-stack.md

#### D-19: Python Tooling Stack
- **Phase**: 4 - Technical Architecture
- **Status**: Decided
- **Confidence**: High
- **Context**: Python project tooling
- **Decision**: uv (package manager), pytest (testing), ruff (formatting/linting), Typer (CLI framework). Choose what's best for the project.
- **Alternatives**: pip, unittest, black, click, argparse
- **Consequences**: Enables modern, fast Python development workflow
- **Memory Doc Impact**: tech-stack.md

#### D-20: Library Research Approach
- **Phase**: 4 - Technical Architecture
- **Status**: Decided
- **Confidence**: High
- **Context**: How to select document parsing libraries
- **Decision**: Each format converter gets its own roadmap phase that includes research and pros/cons analysis before selecting the parsing library.
- **Alternatives**: Picking libraries upfront, using a single omnibus library
- **Consequences**: Enables informed decisions per format; Requires research phases in roadmap
- **Memory Doc Impact**: tech-stack.md

#### D-21: Distribution Strategy
- **Phase**: 4 - Technical Architecture
- **Status**: Decided
- **Confidence**: High
- **Context**: How users install the tool
- **Decision**: Local development only for now. No PyPI/Homebrew distribution yet.
- **Alternatives**: PyPI, Homebrew tap, pipx
- **Consequences**: Enables focus on functionality over packaging; Distribution deferred
- **Memory Doc Impact**: tech-stack.md

#### D-22: LLM Provider for Smart Features
- **Phase**: 4 - Technical Architecture
- **Status**: Decided
- **Confidence**: High
- **Context**: Which LLM to use for --summary, --images, etc.
- **Decision**: Google Gemini 3.0 Flash (Preview) as the primary LLM for smart features. Cheap, fast, and user has available API quota.
- **Alternatives**: Anthropic Haiku, OpenAI GPT-4o-mini, multi-provider abstraction
- **Consequences**: Requires google-genai SDK; API key via .env; Single provider simplifies implementation
- **Memory Doc Impact**: tech-stack.md

#### D-23: Credential Management
- **Phase**: 6 - Security
- **Status**: Decided
- **Confidence**: High
- **Context**: How API keys are stored
- **Decision**: Simple .env file for API keys (GEMINI_API_KEY). Local-only usage doesn't need more complexity. Doppler integration possible in future.
- **Alternatives**: macOS Keychain, config file, Doppler
- **Consequences**: Enables simple setup; .env must be in .gitignore
- **Memory Doc Impact**: tech-stack.md

#### D-24: Performance Profile
- **Phase**: 7 - Performance
- **Status**: Decided
- **Confidence**: High
- **Context**: Expected usage patterns
- **Decision**: Primary use case is single file at a time. Batch processing (multiple files/directories) is a later phase after single-file conversion works for all formats.
- **Alternatives**: Batch-first, concurrent processing from day one
- **Consequences**: Enables simpler initial architecture; Batch/parallel processing deferred
- **Memory Doc Impact**: constitution.md

#### D-25: Testing Strategy
- **Phase**: 8 - Testing
- **Status**: Decided
- **Confidence**: High
- **Context**: How to verify conversion quality
- **Decision**: Golden file tests (compare output against known-good .md references) + format coverage tests (each format converts without errors) + edge case tests (corrupted files, huge files, empty files, scanned PDFs).
- **Alternatives**: Output-only testing, format coverage only
- **Consequences**: Requires curating test fixture files for each format; Enables confidence in output quality
- **Memory Doc Impact**: testing-strategy.md

#### D-26: Long-term Vision
- **Phase**: 10 - Future
- **Status**: Decided
- **Confidence**: High
- **Context**: Where the project is headed
- **Decision**: Stay as a CLI tool. No plans for API service, MCP server, or library packaging. May publish to PyPI eventually.
- **Alternatives**: CLI + MCP server, CLI + API, full platform
- **Consequences**: Enables focused CLI development; No need for HTTP/server architecture
- **Memory Doc Impact**: constitution.md

#### D-27: Overwrite Protection
- **Phase**: Post-discovery amendment
- **Status**: Decided
- **Confidence**: High
- **Context**: What happens when output .md already exists
- **Decision**: Error by default if output file exists. Require explicit `--force` flag to overwrite. Prevents accidental data loss.
- **Alternatives**: Silent overwrite, prompt user
- **Consequences**: Requires --force flag implementation; Prevents data loss
- **Memory Doc Impact**: coding-standards.md, constitution.md

#### D-28: HTML Format Support
- **Phase**: Post-discovery amendment
- **Status**: Decided
- **Confidence**: High
- **Context**: Missing the simplest and most common format
- **Decision**: Add HTML as the first real converter (Phase 0025) after core pipeline. Simplest format, validates the full plugin architecture end-to-end before tackling binary formats.
- **Alternatives**: Jump straight to PDF
- **Consequences**: Enables early pipeline validation; Adds one phase to roadmap
- **Memory Doc Impact**: tech-stack.md, coding-standards.md

#### D-29: Standard CLI Flags
- **Phase**: Post-discovery amendment
- **Status**: Decided
- **Confidence**: High
- **Context**: CLI hygiene and usability
- **Decision**: All builds include: --version, --verbose/-v (stackable to -vv for debug), --quiet/-q, --force/-f. These are non-negotiable baseline flags.
- **Alternatives**: Minimal flags, add later
- **Consequences**: Built into Phase 0020 from day one
- **Memory Doc Impact**: coding-standards.md

#### D-30: Logging Strategy
- **Phase**: Post-discovery amendment
- **Status**: Decided
- **Confidence**: High
- **Context**: How the tool communicates progress and warnings
- **Decision**: Python logging module with levels mapped to CLI verbosity: --quiet=ERROR, default=WARNING, --verbose=INFO, -vv=DEBUG. Warnings surface useful info like "3 images skipped."
- **Alternatives**: Print statements, no logging
- **Consequences**: Requires logging setup in Phase 0020; Enables useful feedback without noise
- **Memory Doc Impact**: coding-standards.md

#### D-31: Python Version Update
- **Phase**: 0010 - Research & Tooling
- **Status**: Decided
- **Confidence**: High
- **Context**: Python 3.14.3 is latest stable (Feb 2026). All core tools support 3.14.
- **Decision**: Update minimum Python version from 3.12+ to 3.14+. Gets t-strings, deferred annotations, stable free-threading.
- **Alternatives**: 3.12+ (conservative), 3.13+ (moderate)
- **Consequences**: Narrower compatibility but access to latest features; All tools confirmed compatible
- **Memory Doc Impact**: tech-stack.md, coding-standards.md

#### D-32: Snapshot Testing Tool
- **Phase**: 0010 - Research & Tooling
- **Status**: Decided
- **Confidence**: High
- **Context**: Need golden file testing for converter output quality
- **Decision**: syrupy 5.1.0+ for snapshot/golden file testing. Zero deps, MIT, .ambr files. Supports SingleFileSnapshotExtension for raw Markdown comparison.
- **Alternatives**: pytest-snapshot (less active), custom comparison (more code), pytest-golden (YAML-based)
- **Consequences**: Adds syrupy as dev dependency; Enables output quality verification
- **Memory Doc Impact**: tech-stack.md, testing-strategy.md

#### D-33: Coverage Reporting
- **Phase**: 0010 - Research & Tooling
- **Status**: Decided
- **Confidence**: High
- **Context**: Need coverage reporting for test suite
- **Decision**: pytest-cov 7.0.0+ for coverage reporting. Standard, well-maintained.
- **Alternatives**: coverage.py directly
- **Consequences**: Adds pytest-cov as dev dependency
- **Memory Doc Impact**: tech-stack.md

#### D-34: Kreuzberg as Extraction Backend (ARCHITECTURAL PIVOT)
- **Phase**: 0010 - Research & Tooling
- **Status**: Decided
- **Confidence**: High
- **Context**: Research discovered Kreuzberg (Rust core, 76+ formats, 91% F1 on PDFs) and MarkItDown (Microsoft, 87.5k stars). Both handle all target formats. Building per-format parsers from scratch would replicate existing production-quality work.
- **Decision**: Adopt Kreuzberg 4.3.8+ as the extraction backend. Build to-markdown as a thin CLI wrapper (~500-800 lines) that adds YAML frontmatter, LLM features, golden file testing, and CLI UX on top of Kreuzberg's extraction.
- **Alternatives**: MarkItDown (50-60% coverage, poor PDF tables, no OCR), per-format libraries (full control but 6+ phases of parser development), abandon project entirely
- **Consequences**: Eliminates 6 per-format converter phases; Reduces codebase to wrapper layer; Depends on Kreuzberg API stability (mitigated by adapter interface); ROADMAP restructured from 10 phases to 5 phases
- **Memory Doc Impact**: constitution.md (Principle III), coding-standards.md (project structure), tech-stack.md, ROADMAP.md, all phase files

#### D-35: LLM Default Model
- **Phase**: 0010 - Research & Tooling
- **Status**: Decided
- **Confidence**: High
- **Context**: Gemini 2.5 Flash is GA with free tier ($0.30/1M input). Gemini 3.0 Flash is still preview, no free tier ($0.50/1M input).
- **Decision**: Default to Gemini 2.5 Flash (model ID: gemini-2.5-flash). Users can override via GEMINI_MODEL env var to use 3.0 Flash or future models.
- **Alternatives**: Gemini 3.0 Flash default (better benchmarks but preview/costlier)
- **Consequences**: Stable model ID, free tier access for testing, lower cost; google-genai SDK confirmed as only SDK needed
- **Memory Doc Impact**: tech-stack.md, coding-standards.md (constants)

#### D-36: LLM Dependencies as Optional Extras
- **Phase**: 0010 - Research & Tooling
- **Status**: Decided
- **Confidence**: High
- **Context**: Core conversion must work offline. LLM features are opt-in.
- **Decision**: google-genai and tenacity packaged as optional extras [llm]. Core install does not include LLM dependencies.
- **Alternatives**: Include all deps by default
- **Consequences**: Smaller default install; Users must install extras for --summary/--images
- **Memory Doc Impact**: tech-stack.md

#### D-37: ROADMAP Restructuring
- **Phase**: 0010 - Research & Tooling
- **Status**: Decided
- **Confidence**: High
- **Context**: Kreuzberg adoption eliminates need for 6 per-format converter phases.
- **Decision**: Restructure ROADMAP from 10 phases to 5: Research & Tooling (0010), Core CLI & Pipeline (0020), Format Quality & Testing (0030), Smart Features (0040), Batch Processing (0050).
- **Alternatives**: Keep original phases but simplify each
- **Consequences**: Dramatically reduced project scope and timeline; Old phase files archived
- **Memory Doc Impact**: ROADMAP.md, all phase files
