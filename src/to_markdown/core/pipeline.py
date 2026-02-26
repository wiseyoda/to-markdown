"""Conversion pipeline: extract -> compose frontmatter -> smart features -> assemble -> write."""

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
) -> Path:
    """Convert a file to Markdown with YAML frontmatter.

    Args:
        input_path: Path to the source file.
        output_path: Custom output path (file or directory). Defaults to input dir.
        force: If True, overwrite existing output file.
        clean: If True, clean extraction artifacts via LLM.
        summary: If True, generate a summary section via LLM.
        images: If True, describe images via LLM vision.

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

    logger.info("Extracting: %s", input_path.name)
    result = extract_file(input_path, extract_images=images)

    logger.info("Composing frontmatter")
    frontmatter = compose_frontmatter(result.metadata, input_path)
    content = result.content
    format_type = result.metadata.get("format_type", input_path.suffix.lstrip("."))

    # Smart features: clean -> images -> summary
    summary_section = ""
    image_section = ""

    if clean:
        logger.info("Cleaning content via LLM")
        from to_markdown.smart.clean import clean_content

        content = clean_content(content, format_type)

    if images and result.images:
        logger.info("Describing %d images via LLM", len(result.images))
        from to_markdown.smart.images import describe_images

        section = describe_images(result.images)
        if section:
            image_section = "\n" + section

    if summary:
        logger.info("Generating summary via LLM")
        from to_markdown.smart.summary import format_summary_section, summarize_content

        summary_text = summarize_content(content, format_type)
        if summary_text:
            summary_section = format_summary_section(summary_text) + "\n"

    # Assemble: frontmatter + [summary] + content + [images]
    markdown = frontmatter + "\n"
    if summary_section:
        markdown += summary_section
    markdown += content
    if image_section:
        markdown += image_section

    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    resolved_output.write_text(markdown, encoding="utf-8")
    logger.info("Wrote: %s", resolved_output)

    return resolved_output


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
