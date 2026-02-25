# Research: Core Tooling

## Date: 2026-02-25

## Candidates

### Python

- **Latest version**: 3.14.3 (released Feb 3, 2026)
- **Previous stable**: 3.13.12 (released Feb 3, 2026)
- **3.14 key features**: PEP 750 t-strings, PEP 649 deferred annotations, PEP 779 free-threaded
  (no-GIL) now officially supported, PEP 784 compression.zstd
- **3.12 EOL**: Oct 2028 | **3.13 EOL**: Oct 2029 | **3.14 EOL**: Oct 2030
- **Ecosystem**: All tools in our stack support 3.14

### uv (Package Manager)

- **Latest version**: 0.10.6 (released Feb 25, 2026)
- **Last major**: 0.10.0 (Feb 10, 2026) with breaking changes (venv --clear, multi-index errors)
- **Python compatibility**: Manages Python 3.8-3.14 installations
- **License**: MIT / Apache-2.0
- **Status**: Dominant Python package manager. Render.com defaults to uv for deployments.
- **Pros**: Fastest package manager, Python version management, virtual env management
- **Cons**: Pre-1.0, minor breaking changes on minor version bumps

### Typer (CLI Framework)

- **Latest version**: 0.24.0 (released Feb 16, 2026)
- **Maintainer**: Sebastian Ramirez (FastAPI org) - long-term maintenance confirmed
- **Python compatibility**: 3.7+ (supports 3.14)
- **License**: MIT
- **Key features**: Type-safe CLI, auto-help generation, command suggestions on typo
- **Alternative considered**: Cyclopts (v4.4.5) - better Union/Literal types, but smaller
  ecosystem. Not worth switching for a file conversion CLI.

### ruff (Formatter/Linter)

- **Latest version**: 0.15.2 (released Feb 19, 2026)
- **Last major**: 0.15.0 (Feb 3, 2026) with 2026 style guide
- **Publisher**: Astral (same as uv)
- **Python compatibility**: Lints/formats Python 3.7-3.14
- **License**: MIT
- **Key changes**: New 2026 style guide (lambda formatting, exception syntax, blank line
  preservation), block suppression comments, 800+ rules
- **Recommended config**:
  ```toml
  [tool.ruff]
  target-version = "py314"
  line-length = 100

  [tool.ruff.lint]
  select = ["E", "F", "I", "N", "W", "UP", "B", "SIM", "RUF"]

  [tool.ruff.format]
  # defaults follow 2026 style guide
  ```

### pytest (Test Framework)

- **Latest version**: 9.1 (released Feb 15, 2026)
- **Last major**: 9.0.0 (Nov 2025) with native subtests, TOML config, dropped Python 3.9
- **Python compatibility**: 3.10+
- **License**: MIT
- **Key plugins**:
  - **pytest-cov 7.0.0**: Coverage reporting
  - **syrupy 5.1.0**: Snapshot/golden file testing. Zero deps, MIT. `.ambr` files in
    `__snapshots__/`. Run `pytest --snapshot-update` to regenerate. Supports raw file
    comparison via `SingleFileSnapshotExtension` (ideal for Markdown output comparison).
  - **pytest-xdist 3.8.0**: Parallel test execution. Defer until test suite grows to 50+.

## Recommendation

| Tool | Version | Action |
|------|---------|--------|
| Python | 3.14+ | **Update** from 3.12+ |
| uv | 0.10.6+ | Keep |
| Typer | 0.24.0+ | Keep |
| ruff | 0.15.2+ | Keep, use 2026 style guide |
| pytest | 9.1+ | Keep, add pytest-cov and syrupy |

## Human Decision

- **Confirmed**: 2026-02-25
- **Python version**: User chose 3.14+ (bleeding edge)
- **All other tools**: Confirmed as recommended
- **syrupy**: Confirmed for snapshot/golden file testing
- **pytest-xdist**: Deferred until test suite grows

## Sources

- [Python 3.14 release](https://docs.python.org/3/whatsnew/3.14.html)
- [uv on PyPI](https://pypi.org/project/uv/)
- [Typer release notes](https://typer.tiangolo.com/release-notes/)
- [ruff v0.15.0 blog](https://astral.sh/blog/ruff-v0.15.0)
- [pytest changelog](https://docs.pytest.org/en/stable/changelog.html)
- [syrupy on PyPI](https://pypi.org/project/syrupy/)
