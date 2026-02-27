"""Helper functions extracted from cli.py to stay under the 300-line limit."""

import logging
import os

import typer

from to_markdown.core.constants import APP_NAME, EXIT_ERROR, GEMINI_API_KEY_ENV

logger = logging.getLogger(APP_NAME)


def configure_logging(verbose: int, quiet: bool) -> None:
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


def load_dotenv() -> None:
    """Load .env file if python-dotenv is available."""
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass


def validate_api_key(summary: bool, images: bool) -> None:
    """Validate GEMINI_API_KEY is set when smart features are requested.

    Only validates for --summary and --images. Clean auto-disables when LLM
    is unavailable, so it does not need validation.
    """
    if not (summary or images):
        return

    if not os.environ.get(GEMINI_API_KEY_ENV):
        logger.error(
            "%s is not set. Smart features (--summary, --images) require a "
            "Gemini API key.\n\n"
            "Set it with:\n"
            "  export GEMINI_API_KEY=your-api-key\n\n"
            "Or add it to a .env file in your project directory.",
            GEMINI_API_KEY_ENV,
        )
        raise typer.Exit(EXIT_ERROR)


def get_store():
    """Get the default TaskStore (lazy import)."""
    from to_markdown.core.background import get_store

    return get_store()
