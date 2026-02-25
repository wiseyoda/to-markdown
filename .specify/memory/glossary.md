# Glossary

> **Agents**: Reference this document for domain-specific terminology.

| Term | Definition |
|------|-----------|
| **Adapter** | Thin wrapper around Kreuzberg that isolates the project from API changes (`core/extraction.py`) |
| **Extraction** | The process of pulling content and metadata from a source file via Kreuzberg |
| **ExtractionResult** | Structured dataclass returned by the adapter: content, metadata, tables |
| **Frontmatter** | YAML metadata block at the top of a Markdown file (between `---` delimiters) |
| **Golden file** | A known-good reference .md file used to verify converter output quality |
| **Kreuzberg** | Rust-based extraction backend (76+ formats) that handles all document parsing |
| **LLM pipeline** | An automated workflow that feeds documents to a language model for processing |
| **Magic defaults** | The principle that the tool should produce excellent output with zero flags |
| **Pipeline** | The conversion flow: extract -> compose frontmatter -> assemble -> write output |
| **Smart features** | Optional LLM-powered enhancements (--summary, --images) that require an API key |
| **Universal translator** | The long-term vision of supporting virtually any file format |

---
*Version: 2.0.0 | Last Updated: 2026-02-25*
