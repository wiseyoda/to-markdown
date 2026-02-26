"""Typer CLI entry point for to-markdown."""

import logging
import os
from pathlib import Path
from typing import Annotated

import typer

from to_markdown import __version__
from to_markdown.core.constants import (
    APP_NAME,
    EXIT_ALREADY_EXISTS,
    EXIT_ERROR,
    EXIT_SUCCESS,
    EXIT_UNSUPPORTED,
    GEMINI_API_KEY_ENV,
)
from to_markdown.core.display import is_glob_pattern, run_batch
from to_markdown.core.extraction import ExtractionError, UnsupportedFormatError
from to_markdown.core.pipeline import OutputExistsError, convert_file

logger = logging.getLogger(APP_NAME)

app = typer.Typer(
    name=APP_NAME,
    help="Convert files to Markdown optimized for LLM consumption.",
    add_completion=False,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{APP_NAME} {__version__}")
        raise typer.Exit(EXIT_SUCCESS)


def _configure_logging(verbose: int, quiet: bool) -> None:
    """Configure logging level based on CLI flags."""
    if quiet:
        level = logging.ERROR
    elif verbose >= 2:
        level = logging.DEBUG
    elif verbose == 1:
        level = logging.INFO
    else:
        level = logging.WARNING

    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
        force=True,
    )


def _load_dotenv() -> None:
    """Load .env file if python-dotenv is available."""
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass


def _validate_api_key(clean: bool, summary: bool, images: bool) -> None:
    """Validate GEMINI_API_KEY is set when smart features are requested."""
    if not (clean or summary or images):
        return

    if not os.environ.get(GEMINI_API_KEY_ENV):
        logger.error(
            "%s is not set. Smart features (--clean, --summary, --images) require a "
            "Gemini API key.\n\n"
            "Set it with:\n"
            "  export GEMINI_API_KEY=your-api-key\n\n"
            "Or add it to a .env file in your project directory.",
            GEMINI_API_KEY_ENV,
        )
        raise typer.Exit(EXIT_ERROR)


@app.command()
def main(
    input_path: Annotated[
        str,
        typer.Argument(help="File, directory, or glob pattern to convert to Markdown."),
    ],
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output path (file or directory)."),
    ] = None,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Overwrite existing output file."),
    ] = False,
    clean: Annotated[
        bool,
        typer.Option(
            "--clean",
            "-c",
            help="Fix extraction artifacts via LLM (requires GEMINI_API_KEY).",
        ),
    ] = False,
    summary: Annotated[
        bool,
        typer.Option(
            "--summary",
            "-s",
            help="Generate document summary via LLM (requires GEMINI_API_KEY).",
        ),
    ] = False,
    images: Annotated[
        bool,
        typer.Option(
            "--images",
            "-i",
            help="Describe images via LLM vision (requires GEMINI_API_KEY).",
        ),
    ] = False,
    no_recursive: Annotated[
        bool,
        typer.Option("--no-recursive", help="Disable recursive directory scanning."),
    ] = False,
    fail_fast: Annotated[
        bool,
        typer.Option("--fail-fast", help="Stop batch conversion on first error."),
    ] = False,
    verbose: Annotated[
        int,
        typer.Option("--verbose", "-v", count=True, help="Increase verbosity (-v or -vv)."),
    ] = 0,
    quiet: Annotated[
        bool,
        typer.Option("--quiet", "-q", help="Suppress all non-error output."),
    ] = False,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            help="Show version and exit.",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    """Convert files to Markdown with YAML frontmatter.

    Accepts a single file, a directory (converts all supported files), or a glob
    pattern (e.g., "docs/*.pdf"). Directories are scanned recursively by default.
    """
    _configure_logging(verbose, quiet)
    _load_dotenv()
    _validate_api_key(clean, summary, images)

    resolved = Path(input_path)

    # Batch mode: directory or glob pattern
    if resolved.is_dir() or is_glob_pattern(input_path):
        run_batch(
            input_path,
            output,
            recursive=not no_recursive,
            force=force,
            clean=clean,
            summary=summary,
            images=images,
            fail_fast=fail_fast,
            quiet=quiet,
            verbose=verbose,
        )
        return  # run_batch raises typer.Exit

    # Single file mode (existing behavior)
    try:
        result_path = convert_file(
            resolved,
            output_path=output,
            force=force,
            clean=clean,
            summary=summary,
            images=images,
        )
    except FileNotFoundError as exc:
        logger.error("%s", exc)
        raise typer.Exit(EXIT_ERROR) from exc
    except UnsupportedFormatError as exc:
        logger.error("%s", exc)
        raise typer.Exit(EXIT_UNSUPPORTED) from exc
    except OutputExistsError as exc:
        logger.error("%s", exc)
        raise typer.Exit(EXIT_ALREADY_EXISTS) from exc
    except ExtractionError as exc:
        logger.error("%s", exc)
        raise typer.Exit(EXIT_ERROR) from exc
    except Exception as exc:
        logger.error("Unexpected error: %s", exc)
        raise typer.Exit(EXIT_ERROR) from exc

    if not quiet:
        typer.echo(f"Converted {input_path} \u2192 {result_path}")

    raise typer.Exit(EXIT_SUCCESS)


if __name__ == "__main__":
    app()
