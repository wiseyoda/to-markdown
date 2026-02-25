"""Conversion pipeline: extract -> compose frontmatter -> assemble -> write."""

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
) -> Path:
    """Convert a file to Markdown with YAML frontmatter.

    Args:
        input_path: Path to the source file.
        output_path: Custom output path (file or directory). Defaults to input dir.
        force: If True, overwrite existing output file.

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
    result = extract_file(input_path)

    logger.info("Composing frontmatter")
    frontmatter = compose_frontmatter(result.metadata, input_path)

    markdown = frontmatter + "\n" + result.content

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
