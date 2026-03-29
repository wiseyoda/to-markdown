## Code Quality Review Summary

Reviewed 18 source files across `src/to_markdown/` (core, smart, mcp packages), covering the CLI, pipeline, batch processing, background tasks, LLM integration, MCP server, and all supporting modules. Also reviewed constants.py, extraction.py, frontmatter.py, sanitize.py, and display.py.

Found 2 findings. The most significant is a high-severity bug where `str.format()` is used to embed untrusted document content into LLM prompt strings — any document containing curly brace patterns (JSON, code, templates) will crash the conversion pipeline with an unhandled `KeyError`. This is especially impactful because `--clean` is enabled by default when the API key is set. The second finding is a medium-severity resource leak where failed subprocess spawns leave tasks permanently stuck in "pending" status with no cleanup path.

The codebase is otherwise well-structured: error handling is thorough at the CLI boundary, async/sync boundaries are clean, SQLite usage is safe with parameterized queries, and the TOCTOU race in file writes is correctly mitigated with atomic `open(file, "x")`.
