"""Content sanitization: strip non-visible characters to prevent prompt injection."""

import logging
from dataclasses import dataclass

from to_markdown.core.constants import (
    SANITIZE_CONTROL_CHARS,
    SANITIZE_DIRECTIONAL_CHARS,
    SANITIZE_ZERO_WIDTH_CHARS,
)

logger = logging.getLogger(__name__)

_ALL_INVISIBLE_CHARS = (
    SANITIZE_ZERO_WIDTH_CHARS | SANITIZE_CONTROL_CHARS | SANITIZE_DIRECTIONAL_CHARS
)


@dataclass(frozen=True)
class SanitizeResult:
    """Result of content sanitization."""

    content: str
    chars_removed: int
    was_modified: bool


def sanitize_content(content: str) -> SanitizeResult:
    """Strip non-visible characters from extracted content.

    Removes zero-width Unicode characters, control characters, and bidirectional
    overrides that could be used for prompt injection attacks. Normal whitespace
    (spaces, tabs, newlines, carriage returns) is preserved.

    Args:
        content: Raw extracted text content.

    Returns:
        SanitizeResult with cleaned content and removal statistics.
    """
    if not content:
        return SanitizeResult(content=content, chars_removed=0, was_modified=False)

    cleaned_chars: list[str] = []
    removed_count = 0

    for char in content:
        if char in _ALL_INVISIBLE_CHARS:
            removed_count += 1
        else:
            cleaned_chars.append(char)

    if removed_count > 0:
        logger.info("Sanitized: removed %d non-visible characters", removed_count)

    cleaned = "".join(cleaned_chars)
    return SanitizeResult(
        content=cleaned,
        chars_removed=removed_count,
        was_modified=removed_count > 0,
    )
