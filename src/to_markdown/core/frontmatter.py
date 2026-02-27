"""YAML frontmatter composition from Kreuzberg extraction metadata."""

from datetime import UTC, datetime
from pathlib import Path

import yaml


def compose_frontmatter(
    metadata: dict,
    source_path: Path,
    *,
    sanitized: bool = False,
) -> str:
    """Compose YAML frontmatter from extraction metadata.

    Args:
        metadata: Metadata dict from Kreuzberg extraction.
        source_path: Path to the original source file.
        sanitized: Whether the content was cleaned by the LLM sanitizer.

    Returns:
        YAML frontmatter string with leading and trailing ``---`` delimiters.
    """
    data: dict = {}

    _add_if_present(data, "title", metadata.get("title"))
    _add_if_present(data, "author", _normalize_author(metadata.get("authors")))
    _add_if_present(data, "created", _format_date(metadata.get("creation_date")))
    _add_if_present(data, "pages", metadata.get("page_count"))
    _add_if_present(data, "words", metadata.get("word_count"))

    data["format"] = metadata.get("format_type", source_path.suffix.lstrip("."))
    if sanitized:
        data["sanitized"] = True
    data["extracted_at"] = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    yaml_body = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
    return f"---\n{yaml_body}---\n"


def _add_if_present(data: dict, key: str, value: object) -> None:
    """Add a key-value pair to data only if value is truthy."""
    if value:
        data[key] = value


def _normalize_author(authors: object) -> str | None:
    """Normalize authors field to a single string or None."""
    if not authors:
        return None
    if isinstance(authors, list):
        return ", ".join(str(a) for a in authors if a)
    return str(authors)


def _format_date(date_value: object) -> str | None:
    """Format a date value to ISO string, or return None."""
    if not date_value:
        return None
    if isinstance(date_value, datetime):
        return date_value.strftime("%Y-%m-%d")
    return str(date_value)
