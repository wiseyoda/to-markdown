# Lessons Learned - Phase 0020: Core CLI & Pipeline

## Decisions

- Chose to delegate format detection entirely to Kreuzberg rather than maintaining our own
  extension list. Kreuzberg raises `ValidationError` for unsupported formats, `ParsingError`
  for extraction failures. This keeps the adapter thin.
- Used `dict` for metadata (not a custom dataclass) since Kreuzberg already returns a dict.
  No conversion needed.
- PyYAML `sort_keys=False` preserves field order in frontmatter, making output more readable.

## Gotchas

- pytest 9.1 is not yet available on PyPI (only 9.0.2). Tech stack research docs cited a
  future version. Adjusted to `>=9.0`.
- Kreuzberg returns `OSError` (not `FileNotFoundError`) for missing files. Our adapter does
  its own existence check first with a clearer message.
- `ruff` 0.15.2 enforces `datetime.UTC` over `timezone.utc` (UP017 rule) - good to know for
  all future datetime code.
- `hatchling` requires README.md to exist if declared in pyproject.toml. Created early.

## Patterns

- Typer's `count=True` option works well for stackable verbose flags (`-v`, `-vv`).
- `typer.testing.CliRunner` provides excellent CLI test coverage without subprocess overhead.
- Kreuzberg `extract_file_sync` is fast (~0.04s for text files). No performance concerns
  for single-file processing.
