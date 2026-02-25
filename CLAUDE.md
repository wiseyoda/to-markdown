# to-markdown

CLI file-to-Markdown converter optimized for LLM consumption. Python 3.12+, uv, Typer, ruff, pytest.

## Rules

1. Read `.specify/memory/constitution.md` before any architectural decision
2. Read `.specify/memory/coding-standards.md` before writing any code
3. Read `.specify/memory/testing-strategy.md` before writing any test
4. No magic numbers - all constants live in `src/to_markdown/core/constants.py`
5. No file over 300 lines (excluding tests) - split it
6. No duplication - if two functions do the same thing, refactor now
7. Fix problems you see in any file you touch - no exceptions
8. Output file already exists? Error unless `--force` is passed
9. Update `--help` text, README, and memory docs in the same commit as code changes
10. Phases aren't done until human testing instructions are written and smoke tests pass

## Commands

```bash
uv run to-markdown <file>       # convert a file
uv run pytest                   # run tests
uv run ruff check               # lint
uv run ruff format --check      # format check
```

## Key Files

| What | Where |
|------|-------|
| Constitution (principles) | `.specify/memory/constitution.md` |
| Coding standards | `.specify/memory/coding-standards.md` |
| Testing strategy | `.specify/memory/testing-strategy.md` |
| Tech stack | `.specify/memory/tech-stack.md` |
| Glossary | `.specify/memory/glossary.md` |
| Roadmap | `ROADMAP.md` |
| Phase details | `.specify/phases/*.md` |
| Discovery decisions | `.specify/discovery/decisions.md` |
| Library research | `.specify/memory/research/*.md` |
| Constants (single source) | `src/to_markdown/core/constants.py` |

## Architecture

Plugin registry + pipeline: parse -> normalize -> render. Each format is one converter
module in `src/to_markdown/converters/`. See coding-standards.md for details.

## Commit Style

Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`
