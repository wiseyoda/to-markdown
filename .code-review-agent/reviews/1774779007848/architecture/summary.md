## Architecture Review Summary

Reviewed 20 source files across `src/to_markdown/` (cli.py, core/, mcp/, smart/) plus pyproject.toml. Mapped the full dependency graph between all modules, checked for circular dependencies (none found), evaluated module boundaries between CLI, core, MCP, and smart layers, and assessed coupling and duplication patterns.

Found 2 medium-severity issues: (1) the LLM SDK availability check is independently implemented in 4 files, with `_validate_llm_flags` additionally duplicated within the MCP package despite an existing import path between the two files; (2) task cancellation business logic is duplicated between CLI and MCP layers because `core/background.py` mixes domain operations with typer presentation calls, preventing reuse from the MCP context.

Overall the architecture is clean for a project of this size: clear pipeline flow (extract -> sanitize -> frontmatter -> LLM -> assemble), proper async/sync boundaries with a single `asyncio.run()` entry point, good use of lazy imports for optional dependencies, and well-defined module responsibilities. The duplication findings are real but proportional maintenance costs, not blockers.
