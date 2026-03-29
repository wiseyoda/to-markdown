# Dependencies Review Summary

**Files read**: pyproject.toml, uv.lock, and all 20 Python source files under src/to_markdown/ (cli.py, core/*.py, smart/*.py, mcp/*.py) to trace every import against the declared dependency list.

**What was checked**: All 4 core dependencies, 3 LLM optional deps, 1 MCP optional dep, and 10 dev dependencies were verified for usage, classification (runtime vs dev vs optional), version pinning strategy, license compatibility (all MIT/Apache/BSD), and structural issues (duplicate deps, undeclared imports, missing extras).

**Key observations**: The dependency graph is well-structured — core deps are minimal, LLM and MCP features use optional extras with graceful degradation (try/except ImportError or lazy imports), a uv.lock lockfile pins exact versions, and `requires-python = ">=3.13"` is set. One low-severity hygiene finding: `pydantic` is imported directly in the MCP server module but not declared in the `[mcp]` extras (it arrives transitively via the `mcp` package). Practical risk is minimal since mcp fundamentally depends on pydantic, but explicit declaration is a best practice.
