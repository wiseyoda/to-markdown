"""Tests for the --clean module (smart/clean.py)."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from to_markdown.core.constants import CHARS_PER_TOKEN_ESTIMATE, MAX_CLEAN_TOKENS
from to_markdown.smart.clean import (
    _build_clean_prompt,
    _chunk_content,
    clean_content,
    clean_content_async,
)
from to_markdown.smart.llm import LLMError


class TestCleanContent:
    """Tests for the clean_content function."""

    def test_returns_cleaned_text(self):
        with patch("to_markdown.smart.clean.generate", return_value="cleaned text"):
            result = clean_content("raw text with inBangkok", "pdf")
            assert result == "cleaned text"

    def test_passes_format_type_in_prompt(self):
        with patch("to_markdown.smart.clean.generate", return_value="ok") as mock_gen:
            clean_content("some text", "pdf")
            prompt_arg = mock_gen.call_args[0][0]
            assert "pdf" in prompt_arg

    def test_skips_empty_content(self):
        with patch("to_markdown.smart.clean.generate") as mock_gen:
            result = clean_content("", "pdf")
            mock_gen.assert_not_called()
            assert result == ""

    def test_skips_whitespace_only_content(self):
        with patch("to_markdown.smart.clean.generate") as mock_gen:
            result = clean_content("   \n\n  ", "pdf")
            mock_gen.assert_not_called()
            assert result == "   \n\n  "

    def test_graceful_degradation_on_llm_failure(self):
        original = "original content with inBangkok"
        with patch("to_markdown.smart.clean.generate", side_effect=LLMError("fail")):
            result = clean_content(original, "pdf")
            assert result == original

    def test_uses_clean_temperature(self):
        with patch("to_markdown.smart.clean.generate", return_value="ok") as mock_gen:
            clean_content("some text", "pdf")
            assert mock_gen.call_args.kwargs["temperature"] == 0.1


class TestChunkContent:
    """Tests for content chunking."""

    def test_small_content_returns_single_chunk(self):
        result = _chunk_content("small text", 1000)
        assert result == ["small text"]

    def test_splits_at_paragraph_boundaries(self):
        content = "paragraph one\n\nparagraph two\n\nparagraph three"
        result = _chunk_content(content, 30)
        assert len(result) >= 2
        for chunk in result:
            assert "\n\n" not in chunk or chunk.count("\n\n") < content.count("\n\n")

    def test_reassembled_chunks_preserve_content(self):
        content = "para one\n\npara two\n\npara three\n\npara four"
        result = _chunk_content(content, 25)
        reassembled = "\n\n".join(result)
        assert reassembled == content

    def test_large_paragraph_becomes_own_chunk(self):
        content = "a" * 100 + "\n\n" + "b" * 10
        result = _chunk_content(content, 50)
        assert len(result) == 2
        assert result[0] == "a" * 100
        assert result[1] == "b" * 10

    def test_multi_chunk_processing(self):
        max_chars = MAX_CLEAN_TOKENS * CHARS_PER_TOKEN_ESTIMATE
        paragraphs = ["x" * 1000 for _ in range(500)]
        content = "\n\n".join(paragraphs)
        result = _chunk_content(content, max_chars)
        assert len(result) >= 2
        reassembled = "\n\n".join(result)
        assert reassembled == content


class TestBuildCleanPrompt:
    """Tests for prompt template formatting."""

    def test_includes_format_type(self):
        result = _build_clean_prompt("text", "pdf")
        assert "pdf" in result

    def test_includes_content(self):
        result = _build_clean_prompt("my document content", "docx")
        assert "my document content" in result

    def test_includes_instructions(self):
        result = _build_clean_prompt("text", "pdf")
        assert "NEVER add new information" in result
        assert "artifact" in result.lower()


class TestCleanContentAsync:
    """Tests for the clean_content_async function."""

    @pytest.mark.asyncio
    async def test_single_chunk_no_parallelism(self):
        mock_gen = AsyncMock(return_value="cleaned text")
        with patch("to_markdown.smart.clean.generate_async", mock_gen):
            result = await clean_content_async("raw text with inBangkok", "pdf")
            assert result == "cleaned text"
            mock_gen.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_multi_chunk_all_processed_concurrently(self):
        max_chars = MAX_CLEAN_TOKENS * CHARS_PER_TOKEN_ESTIMATE
        paragraphs = ["x" * 1000 for _ in range(500)]
        content = "\n\n".join(paragraphs)
        chunks = _chunk_content(content, max_chars)
        assert len(chunks) >= 2

        mock_gen = AsyncMock(return_value="cleaned chunk")
        with patch("to_markdown.smart.clean.generate_async", mock_gen):
            result = await clean_content_async(content, "pdf")
            assert mock_gen.await_count == len(chunks)
            assert result == "\n\n".join(["cleaned chunk"] * len(chunks))

    @pytest.mark.asyncio
    async def test_llm_failure_falls_back_to_original(self):
        original = "original content with inBangkok"
        mock_gen = AsyncMock(side_effect=LLMError("fail"))
        with patch("to_markdown.smart.clean.generate_async", mock_gen):
            result = await clean_content_async(original, "pdf")
            assert result == original

    @pytest.mark.asyncio
    async def test_empty_content_returns_unchanged(self):
        mock_gen = AsyncMock()
        with patch("to_markdown.smart.clean.generate_async", mock_gen):
            result = await clean_content_async("", "pdf")
            mock_gen.assert_not_awaited()
            assert result == ""

    @pytest.mark.asyncio
    async def test_whitespace_only_returns_unchanged(self):
        mock_gen = AsyncMock()
        with patch("to_markdown.smart.clean.generate_async", mock_gen):
            result = await clean_content_async("   \n\n  ", "pdf")
            mock_gen.assert_not_awaited()
            assert result == "   \n\n  "

    @pytest.mark.asyncio
    async def test_logs_warning_on_llm_failure(self, caplog):
        mock_gen = AsyncMock(side_effect=LLMError("fail"))
        with patch("to_markdown.smart.clean.generate_async", mock_gen):
            import logging

            with caplog.at_level(logging.WARNING):
                await clean_content_async("some content", "pdf")
            assert "LLM clean failed" in caplog.text


class TestCleanContentAsyncRun:
    """Tests for clean_content_async() using asyncio.run()."""

    def test_single_chunk_no_parallelism(self):
        """Short content uses single async call (no gather)."""
        with patch(
            "to_markdown.smart.clean.generate_async",
            new_callable=AsyncMock,
        ) as mock:
            mock.return_value = "Cleaned content"
            result = asyncio.run(clean_content_async("Short text", "pdf"))
            assert result == "Cleaned content"
            assert mock.await_count == 1

    def test_multi_chunk_concurrent(self):
        """Large content splits into chunks processed concurrently."""
        chunk1 = "A" * 300_000
        chunk2 = "B" * 300_000
        large_content = chunk1 + "\n\n" + chunk2

        with patch(
            "to_markdown.smart.clean.generate_async",
            new_callable=AsyncMock,
        ) as mock:
            mock.return_value = "Cleaned chunk"
            result = asyncio.run(clean_content_async(large_content, "pdf"))
            assert mock.await_count == 2
            assert result == "Cleaned chunk\n\nCleaned chunk"

    def test_llm_failure_returns_original(self):
        """LLM error falls back to original content."""
        with patch(
            "to_markdown.smart.clean.generate_async",
            new_callable=AsyncMock,
        ) as mock:
            mock.side_effect = LLMError("API error")
            result = asyncio.run(clean_content_async("Original text", "pdf"))
            assert result == "Original text"

    def test_empty_content_returns_unchanged(self):
        """Empty content returns without calling LLM."""
        with patch(
            "to_markdown.smart.clean.generate_async",
            new_callable=AsyncMock,
        ) as mock:
            result = asyncio.run(clean_content_async("", "pdf"))
            assert result == ""
            mock.assert_not_awaited()

    def test_whitespace_only_returns_unchanged(self):
        """Whitespace-only content returns without calling LLM."""
        with patch(
            "to_markdown.smart.clean.generate_async",
            new_callable=AsyncMock,
        ) as mock:
            result = asyncio.run(clean_content_async("   \n  ", "pdf"))
            assert result == "   \n  "
            mock.assert_not_awaited()
