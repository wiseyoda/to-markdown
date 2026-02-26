"""Batch conversion CLI helpers extracted from cli.py."""

import logging
from pathlib import Path

import typer

from to_markdown.core.batch import BatchResult
from to_markdown.core.constants import APP_NAME, EXIT_ERROR, GLOB_CHARS

logger = logging.getLogger(APP_NAME)


def is_glob_pattern(value: str) -> bool:
    """Check if a string contains glob pattern characters."""
    return any(c in value for c in GLOB_CHARS)


def print_batch_summary(result: BatchResult, verbose: int) -> None:
    """Print batch conversion summary."""
    parts = [f"Converted {len(result.succeeded)} file(s)"]
    if result.skipped:
        parts.append(f"{len(result.skipped)} skipped")
    if result.failed:
        parts.append(f"{len(result.failed)} failed")
    typer.echo(", ".join(parts))

    if verbose >= 1 and result.failed:
        for path, error in result.failed:
            typer.echo(f"  FAILED: {path.name} - {error}", err=True)


def run_batch(
    input_str: str,
    output: Path | None,
    *,
    recursive: bool,
    force: bool,
    clean: bool,
    summary: bool,
    images: bool,
    fail_fast: bool,
    quiet: bool,
    verbose: int,
) -> None:
    """Run batch conversion for directory or glob input."""
    from to_markdown.core.batch import convert_batch, discover_files, resolve_glob

    input_path = Path(input_str)
    is_glob = is_glob_pattern(input_str)

    if is_glob:
        files = resolve_glob(input_str)
        if not files:
            logger.error("No files matched pattern: %s", input_str)
            raise typer.Exit(EXIT_ERROR)
        batch_root = None
    else:
        if not input_path.exists():
            logger.error("Directory not found: %s", input_path)
            raise typer.Exit(EXIT_ERROR)
        files = discover_files(input_path, recursive=recursive)
        if not files:
            logger.error("No supported files found in: %s", input_path)
            raise typer.Exit(EXIT_ERROR)
        batch_root = input_path.resolve()

    # Validate -o is a directory (or doesn't exist) for batch mode
    if output is not None and output.exists() and not output.is_dir():
        logger.error("Output must be a directory for batch mode: %s", output)
        raise typer.Exit(EXIT_ERROR)

    result = convert_batch(
        files,
        output_dir=output,
        batch_root=batch_root,
        force=force,
        clean=clean,
        summary=summary,
        images=images,
        fail_fast=fail_fast,
        quiet=quiet,
    )

    if not quiet:
        print_batch_summary(result, verbose)

    raise typer.Exit(result.exit_code)
