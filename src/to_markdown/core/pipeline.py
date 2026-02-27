"""Conversion pipeline: extract -> sanitize -> frontmatter -> smart -> assemble -> write."""

import asyncio
import logging
from pathlib import Path

from to_markdown.core.constants import DEFAULT_OUTPUT_EXTENSION
from to_markdown.core.extraction import extract_file
from to_markdown.core.frontmatter import compose_frontmatter

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

    markdown = _build_content(
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

    return _build_content(
        input_path,
        clean=clean,
        summary=summary,
        images=images,
        sanitize=sanitize,
    )


def _build_content(
    input_path: Path,
    *,
    clean: bool = False,
    summary: bool = False,
    images: bool = False,
    sanitize: bool = True,
) -> str:
    """Build markdown content via async pipeline with sync boundary.

    Delegates to _build_content_async() and runs the event loop here.
    This is the ONLY place asyncio.run() is called in the pipeline.
    """
    return asyncio.run(
        _build_content_async(
            input_path,
            clean=clean,
            summary=summary,
            images=images,
            sanitize=sanitize,
        )
    )


async def _build_content_async(
    input_path: Path,
    *,
    sanitize: bool = True,
    clean: bool = False,
    summary: bool = False,
    images: bool = False,
) -> str:
    """Build markdown content with parallel LLM features.

    Clean and images run concurrently via asyncio.gather() when both are enabled.
    Summary runs after clean (depends on cleaned content).
    """
    logger.info("Extracting: %s", input_path.name)
    result = extract_file(input_path, extract_images=images)

    content = result.content
    format_type = result.metadata.get("format_type", input_path.suffix.lstrip("."))

    # Sanitize (sync, fast -- character-level filtering)
    sanitized = False
    if sanitize:
        from to_markdown.core.sanitize import sanitize_content

        sanitize_result = sanitize_content(content)
        content = sanitize_result.content
        sanitized = sanitize_result.was_modified

    logger.info("Composing frontmatter")
    frontmatter = compose_frontmatter(result.metadata, input_path, sanitized=sanitized)

    # Parallel LLM features: clean + images can run concurrently
    summary_section = ""
    image_section = ""
    cleaned_content = content

    parallel_tasks: list = []
    task_labels: list[str] = []

    if clean:
        logger.info("Cleaning content via LLM")
        from to_markdown.smart.clean import clean_content_async

        parallel_tasks.append(clean_content_async(content, format_type))
        task_labels.append("clean")

    if images and result.images:
        logger.info("Describing %d images via LLM", len(result.images))
        from to_markdown.smart.images import describe_images_async

        parallel_tasks.append(describe_images_async(result.images))
        task_labels.append("images")

    if parallel_tasks:
        results = await asyncio.gather(*parallel_tasks)
        for label, res in zip(task_labels, results, strict=True):
            if label == "clean" and res is not None:
                cleaned_content = res
            elif label == "images" and res:
                image_section = "\n" + res

    # Summary depends on cleaned content (must run after clean)
    if summary:
        logger.info("Generating summary via LLM")
        from to_markdown.smart.summary import format_summary_section, summarize_content_async

        summary_text = await summarize_content_async(cleaned_content, format_type)
        if summary_text:
            summary_section = format_summary_section(summary_text) + "\n"

    # Assemble: frontmatter + [summary] + content + [images]
    markdown = frontmatter + "\n"
    if summary_section:
        markdown += summary_section
    markdown += cleaned_content
    if image_section:
        markdown += image_section

    return markdown


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
