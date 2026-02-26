"""LLM-powered content cleanup: fix extraction artifacts without altering content."""

import logging

from to_markdown.core.constants import (
    CHARS_PER_TOKEN_ESTIMATE,
    CLEAN_PROMPT,
    CLEAN_TEMPERATURE,
    MAX_CLEAN_TOKENS,
)
from to_markdown.smart.llm import LLMError, generate

logger = logging.getLogger(__name__)


def clean_content(content: str, format_type: str) -> str:
    """Clean extraction artifacts from content via LLM.

    Args:
        content: The extracted document content (without frontmatter).
        format_type: The source document format (e.g. "pdf", "docx").

    Returns:
        Cleaned content, or original content if LLM fails.
    """
    if not content.strip():
        logger.info("Skipping clean: empty content")
        return content

    try:
        chunks = _chunk_content(content, MAX_CLEAN_TOKENS * CHARS_PER_TOKEN_ESTIMATE)
        cleaned_chunks = []
        for chunk in chunks:
            prompt = _build_clean_prompt(chunk, format_type)
            cleaned = generate(prompt, temperature=CLEAN_TEMPERATURE)
            cleaned_chunks.append(cleaned)
        return "\n\n".join(cleaned_chunks)
    except LLMError:
        logger.warning("LLM clean failed, using original content")
        return content


def _chunk_content(content: str, max_chars: int) -> list[str]:
    """Split content at paragraph boundaries (double newline).

    Each chunk will be under max_chars. If a single paragraph exceeds max_chars,
    it becomes its own chunk.
    """
    if len(content) <= max_chars:
        return [content]

    paragraphs = content.split("\n\n")
    chunks: list[str] = []
    current_chunk: list[str] = []
    current_size = 0

    for paragraph in paragraphs:
        paragraph_size = len(paragraph)
        separator_size = 2 if current_chunk else 0

        if current_size + separator_size + paragraph_size > max_chars and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [paragraph]
            current_size = paragraph_size
        else:
            current_chunk.append(paragraph)
            current_size += separator_size + paragraph_size

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks


def _build_clean_prompt(chunk: str, format_type: str) -> str:
    """Format the clean prompt template with document context."""
    return CLEAN_PROMPT.format(format_type=format_type, content=chunk)
