# Phase 0030 Lessons Learned

## Decisions

- Chose programmatic fixture generation over static binary files. This keeps the repo clean
  and makes fixtures self-documenting, but limits testing to what the generation libraries
  can produce (which may differ from real-world documents).
- Used syrupy's default Amber extension — no custom configuration needed. Snapshot files
  are compact and easy to review.

## Gotchas

- **fpdf2 PDF heading extraction**: Kreuzberg does not reliably extract text rendered with
  different font sizes in fpdf2-generated PDFs. Heading text set via `cell()` may be
  completely dropped. Use `multi_cell()` for all text that needs to be extractable, and
  test for body text rather than heading-specific text.
- **HTML double frontmatter**: Kreuzberg returns its own `---\ntitle: ...\n---` frontmatter
  for HTML files. Our pipeline then adds a second frontmatter block on top. This results in
  double frontmatter in HTML output. Should be addressed in a future phase (detect and merge,
  or strip Kreuzberg's frontmatter).
- **Session-scoped fixtures with --cache-clear**: Changing fixture code requires clearing
  pytest's session fixture cache. Run with `--cache-clear` when modifying fixture factories.
- **except tuple syntax**: `except (ErrorA, UnsupportedFormatError)` requires parentheses.
  `except ErrorA, ErrorB` is a syntax error in Python 3.14 (it was removal of Python 2 syntax).

## Patterns

- **Timestamp normalization**: The `normalize_markdown()` helper in `tests/conftest.py`
  replaces dynamic `extracted_at` timestamps with a fixed value before snapshot comparison.
  This pattern should be reused for any future dynamic fields in output.
- **Format test module structure**: Each format has a test module with three test classes:
  `Test{Format}Snapshots`, `Test{Format}Quality`, `Test{Format}Frontmatter`. Consistent
  pattern makes it easy to add new formats.
- **OCR skip pattern**: `@pytest.mark.skipif(shutil.which("tesseract") is None, ...)` on the
  class level cleanly skips all OCR tests when Tesseract isn't installed.
