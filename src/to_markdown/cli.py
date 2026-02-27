"""Typer CLI entry point for to-markdown."""

import logging
import os
from pathlib import Path
from typing import Annotated

import typer

from to_markdown import __version__
from to_markdown.core.cli_helpers import (
    configure_logging,
    get_store,
    load_dotenv,
    validate_api_key,
)
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


def _is_llm_available() -> bool:
    """Check if LLM features can be used (SDK installed + API key set)."""
    try:
        import google.genai  # noqa: F401
    except ImportError:
        return False
    return bool(os.environ.get(GEMINI_API_KEY_ENV))


@app.command()
def main(
    input_path: Annotated[
        str | None,
        typer.Argument(help="File, directory, or glob pattern to convert to Markdown."),
    ] = None,
    setup: Annotated[
        bool,
        typer.Option("--setup", help="Run interactive configuration wizard."),
    ] = False,
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
            help=(
                "Fix extraction artifacts via LLM (enabled by default when GEMINI_API_KEY is set)."
            ),
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
    no_clean: Annotated[
        bool,
        typer.Option(
            "--no-clean",
            help="Disable automatic content cleaning (clean is on by default with API key).",
        ),
    ] = False,
    no_sanitize: Annotated[
        bool,
        typer.Option(
            "--no-sanitize",
            help="Disable prompt injection sanitization.",
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
    background: Annotated[
        bool,
        typer.Option("--background", "--bg", help="Run conversion in background."),
    ] = False,
    status: Annotated[
        str | None,
        typer.Option("--status", help="Show task status (task ID or 'all')."),
    ] = None,
    cancel: Annotated[
        str | None,
        typer.Option("--cancel", help="Cancel a running background task."),
    ] = None,
    _worker: Annotated[
        str | None,
        typer.Option("--_worker", help="Internal worker flag.", hidden=True),
    ] = None,
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
    configure_logging(verbose, quiet)
    load_dotenv()

    # Compute effective clean: enabled by default when LLM available
    effective_clean = clean or (not no_clean and _is_llm_available())
    if no_clean:
        effective_clean = False

    # Setup wizard (early return, no input_path required)
    if setup:
        from to_markdown.core.setup import run_setup, run_setup_quiet

        if quiet:
            run_setup_quiet()
        else:
            run_setup()
        raise typer.Exit(EXIT_SUCCESS)

    # input_path is required for all other modes
    if input_path is None:
        logger.error("Missing required argument: INPUT_PATH")
        raise typer.Exit(EXIT_ERROR)

    # Mutual exclusivity check
    bg_flags = sum(bool(x) for x in [background, status, cancel])
    if bg_flags > 1:
        logger.error("--background, --status, and --cancel are mutually exclusive")
        raise typer.Exit(EXIT_ERROR)

    # Background processing flags (lazy import, early returns)
    if _worker is not None or status is not None or cancel is not None or background:
        from to_markdown.core.background import (
            handle_background,
            handle_cancel,
            handle_status,
            handle_worker,
        )

        store = get_store()

        if _worker is not None:
            handle_worker(_worker, store)
            return

        if status is not None:
            handle_status(status, store)
            return

        if cancel is not None:
            handle_cancel(cancel, store)
            return

        validate_api_key(summary, images)
        handle_background(
            input_path,
            output,
            force=force,
            clean=effective_clean,
            summary=summary,
            images_flag=images,
            no_sanitize=no_sanitize,
            store=store,
        )
        return

    # Standard conversion mode
    validate_api_key(summary, images)

    resolved = Path(input_path)

    # Batch mode: directory or glob pattern
    if resolved.is_dir() or is_glob_pattern(input_path):
        run_batch(
            input_path,
            output,
            recursive=not no_recursive,
            force=force,
            clean=effective_clean,
            summary=summary,
            images=images,
            sanitize=not no_sanitize,
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
            clean=effective_clean,
            summary=summary,
            images=images,
            sanitize=not no_sanitize,
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
