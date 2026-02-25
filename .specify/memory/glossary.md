# Glossary

> **Agents**: Reference this document for domain-specific terminology.

| Term | Definition |
|------|-----------|
| **Converter** | A format-specific plugin that parses a file type into the Document IR |
| **Document IR** | Intermediate Representation - the shared data model between parse and render stages |
| **Frontmatter** | YAML metadata block at the top of a Markdown file (between `---` delimiters) |
| **Golden file** | A known-good reference .md file used to verify converter output quality |
| **LLM pipeline** | An automated workflow that feeds documents to a language model for processing |
| **Magic defaults** | The principle that the tool should produce excellent output with zero flags |
| **Normalize** | The pipeline stage that standardizes parsed content into a consistent IR format |
| **Parse** | The pipeline stage where a converter extracts content from a source file |
| **Plugin registry** | The central registry where format converters register their supported extensions |
| **Render** | The pipeline stage that converts the normalized IR into Markdown text |
| **Smart features** | Optional LLM-powered enhancements (--summary, --images) that require an API key |
| **Universal translator** | The long-term vision of supporting virtually any file format |

---
*Version: 1.0.0 | Last Updated: 2026-02-25*
