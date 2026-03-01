"""Conversion pipeline: extract -> sanitize -> frontmatter -> smart -> assemble -> write."""

import logging
from pathlib import Path

from to_markdown.core.constants import DEFAULT_OUTPUT_EXTENSION
from to_markdown.core.content_builder import build_content, build_content_async

logger = logging.getLogger(__name__)


class OutputExistsError(Exception):
    """Raised when the output file already exists and --force was not passed."""


def convert_file(
    input_path: Path,
    output_path: Path | None = None,
    *,
    force: bool = False,
    clean: bool = False,
    summary: bool = False,
    images: bool = False,
    sanitize: bool = True,
) -> Path:
    """Convert a file to Markdown with YAML frontmatter.

    Args:
        input_path: Path to the source file.
        output_path: Custom output path (file or directory). Defaults to input dir.
        force: If True, overwrite existing output file.
        clean: If True, clean extraction artifacts via LLM.
        summary: If True, generate a summary section via LLM.
        images: If True, describe images via LLM vision.
        sanitize: If True, strip non-visible characters to prevent prompt injection.

    Returns:
        Path to the created .md file.

    Raises:
        FileNotFoundError: If the input file does not exist.
        OutputExistsError: If the output file exists and force is False.
        UnsupportedFormatError: If the file format is not supported.
        ExtractionError: If extraction fails.
    """
    input_path = Path(input_path).resolve()
    if not input_path.exists():
        msg = f"File not found: {input_path}"
        raise FileNotFoundError(msg)

    resolved_output = _resolve_output_path(input_path, output_path)

    if resolved_output.exists() and not force:
        msg = f"Output file already exists: {resolved_output} (use --force to overwrite)"
        raise OutputExistsError(msg)

    markdown = build_content(
        input_path,
        clean=clean,
        summary=summary,
        images=images,
        sanitize=sanitize,
    )

    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    resolved_output.write_text(markdown, encoding="utf-8")
    logger.info("Wrote: %s", resolved_output)

    return resolved_output


def convert_to_string(
    input_path: Path,
    *,
    clean: bool = False,
    summary: bool = False,
    images: bool = False,
    sanitize: bool = True,
) -> str:
    """Convert a file to Markdown and return the content as a string.

    Same pipeline as convert_file() but returns the markdown content directly
    instead of writing to disk. Used by the MCP server.

    Args:
        input_path: Path to the source file.
        clean: If True, clean extraction artifacts via LLM.
        summary: If True, generate a summary section via LLM.
        images: If True, describe images via LLM vision.
        sanitize: If True, strip non-visible characters to prevent prompt injection.

    Returns:
        Assembled markdown string with frontmatter and content.

    Raises:
        FileNotFoundError: If the input file does not exist.
        UnsupportedFormatError: If the file format is not supported.
        ExtractionError: If extraction fails.
    """
    input_path = Path(input_path).resolve()
    if not input_path.exists():
        msg = f"File not found: {input_path}"
        raise FileNotFoundError(msg)

    return build_content(
        input_path,
        clean=clean,
        summary=summary,
        images=images,
        sanitize=sanitize,
    )


async def convert_file_async(
    input_path: Path,
    output_path: Path | None = None,
    *,
    force: bool = False,
    clean: bool = False,
    summary: bool = False,
    images: bool = False,
    sanitize: bool = True,
) -> Path:
    """Async version of convert_file() for use inside a running event loop (e.g. MCP).

    Same behavior as convert_file() but awaits build_content_async() directly,
    avoiding the asyncio.run() call that would crash inside FastMCP's event loop.
    """
    input_path = Path(input_path).resolve()
    if not input_path.exists():
        msg = f"File not found: {input_path}"
        raise FileNotFoundError(msg)

    resolved_output = _resolve_output_path(input_path, output_path)

    if resolved_output.exists() and not force:
        msg = f"Output file already exists: {resolved_output} (use --force to overwrite)"
        raise OutputExistsError(msg)

    markdown = await build_content_async(
        input_path,
        clean=clean,
        summary=summary,
        images=images,
        sanitize=sanitize,
    )

    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    resolved_output.write_text(markdown, encoding="utf-8")
    logger.info("Wrote: %s", resolved_output)

    return resolved_output


async def convert_to_string_async(
    input_path: Path,
    *,
    clean: bool = False,
    summary: bool = False,
    images: bool = False,
    sanitize: bool = True,
) -> str:
    """Async version of convert_to_string() for use inside a running event loop (e.g. MCP).

    Same behavior as convert_to_string() but awaits build_content_async() directly,
    avoiding the asyncio.run() call that would crash inside FastMCP's event loop.
    """
    input_path = Path(input_path).resolve()
    if not input_path.exists():
        msg = f"File not found: {input_path}"
        raise FileNotFoundError(msg)

    return await build_content_async(
        input_path,
        clean=clean,
        summary=summary,
        images=images,
        sanitize=sanitize,
    )


def _resolve_output_path(input_path: Path, output_path: Path | None) -> Path:
    """Resolve the output file path.

    Rules:
        - No -o flag: same directory as input, with .md extension
        - -o is a directory: place file in that directory with .md extension
        - -o is a file path: use it as-is
    """
    if output_path is None:
        return input_path.with_suffix(DEFAULT_OUTPUT_EXTENSION)

    output_path = Path(output_path)
    if output_path.is_dir():
        return output_path / (input_path.stem + DEFAULT_OUTPUT_EXTENSION)

    return output_path
