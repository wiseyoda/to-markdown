"""LLM-powered document summarization via Gemini."""

import logging

from to_markdown.core.constants import (
    MAX_SUMMARY_TOKENS,
    SUMMARY_PROMPT,
    SUMMARY_SECTION_HEADING,
    SUMMARY_TEMPERATURE,
)
from to_markdown.smart.llm import LLMError, generate

logger = logging.getLogger(__name__)


def summarize_content(content: str, format_type: str) -> str | None:
    """Generate a summary of the document content via LLM.

    Args:
        content: The document content to summarize.
        format_type: The source document format (e.g. "pdf", "docx").

    Returns:
        Summary text, or None if LLM fails or content is empty.
    """
    if not content.strip():
        logger.info("Skipping summary: empty content")
        return None

    prompt = SUMMARY_PROMPT.format(content=content)

    try:
        return generate(
            prompt,
            temperature=SUMMARY_TEMPERATURE,
            max_output_tokens=MAX_SUMMARY_TOKENS,
        )
    except LLMError:
        logger.warning("LLM summary failed, skipping summary section")
        return None


def format_summary_section(summary: str) -> str:
    """Wrap summary text in a markdown section.

    Args:
        summary: The summary text to format.

    Returns:
        Formatted markdown section with heading.
    """
    return f"{SUMMARY_SECTION_HEADING}\n\n{summary}\n"
