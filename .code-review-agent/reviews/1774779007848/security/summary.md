# Security Review Summary

**Files read**: 22 source files covering the full attack surface — CLI entry point (`cli.py`), MCP server (`server.py`, `tools.py`, `background_tools.py`), pipeline (`pipeline.py`, `content_builder.py`), subprocess management (`worker.py`, `background.py`), SQLite task store (`tasks.py`), content sanitization (`sanitize.py`), LLM integration (`llm.py`, `clean.py`), file extraction (`extraction.py`), batch processing (`batch.py`, `display.py`), setup wizard (`setup.py`, `cli_helpers.py`), frontmatter (`frontmatter.py`), constants (`constants.py`), install scripts (`install.sh`, `install.ps1`), and MCP entry point (`__main__.py`).

**What I checked**: SQL injection (all SQLite queries), command injection (subprocess calls), path traversal (file path handling in CLI and MCP), unsafe deserialization (`yaml`/`pickle`/`eval`), secrets management, format string injection in LLM prompts, signal-based process management, and trust boundaries between CLI/MCP inputs and dangerous sinks (filesystem, SQLite, subprocess, external API).

**Key observations**: The codebase has a strong security posture. All SQL queries use parameterized values. `TaskStore.update()` constructs column names from kwargs keys via f-string, but all 9 call sites use hardcoded keyword arguments with no user-input path to the keys. Subprocess spawning uses list-based `Popen` (no `shell=True`) with hex-only task IDs from `uuid.uuid4()`. File paths are `.resolve()`d before use. Content sanitization strips non-visible Unicode characters before LLM prompt injection. No `eval()`, `exec()`, `pickle`, or unsafe `yaml.load()` found. API keys come from environment variables, not hardcoded.

**Result**: No findings above the 70% confidence threshold. Clean codebase.
