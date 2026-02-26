"""Tests for the --summary module (smart/summary.py)."""

from unittest.mock import patch

from to_markdown.smart.llm import LLMError
from to_markdown.smart.summary import format_summary_section, summarize_content


class TestSummarizeContent:
    """Tests for the summarize_content function."""

    def test_returns_summary_text(self):
        with patch("to_markdown.smart.summary.generate", return_value="A concise summary."):
            result = summarize_content("Document content here.", "pdf")
            assert result == "A concise summary."

    def test_skips_empty_content(self):
        with patch("to_markdown.smart.summary.generate") as mock_gen:
            result = summarize_content("", "pdf")
            mock_gen.assert_not_called()
            assert result is None

    def test_skips_whitespace_only_content(self):
        with patch("to_markdown.smart.summary.generate") as mock_gen:
            result = summarize_content("   \n  ", "pdf")
            mock_gen.assert_not_called()
            assert result is None

    def test_graceful_degradation_on_llm_failure(self):
        with patch("to_markdown.smart.summary.generate", side_effect=LLMError("fail")):
            result = summarize_content("Some content", "pdf")
            assert result is None

    def test_uses_summary_temperature(self):
        with patch("to_markdown.smart.summary.generate", return_value="ok") as mock_gen:
            summarize_content("content", "pdf")
            assert mock_gen.call_args.kwargs["temperature"] == 0.3

    def test_uses_max_summary_tokens(self):
        with patch("to_markdown.smart.summary.generate", return_value="ok") as mock_gen:
            summarize_content("content", "pdf")
            assert mock_gen.call_args.kwargs["max_output_tokens"] == 4096

    def test_prompt_includes_content(self):
        with patch("to_markdown.smart.summary.generate", return_value="ok") as mock_gen:
            summarize_content("my document text", "pdf")
            prompt = mock_gen.call_args[0][0]
            assert "my document text" in prompt


class TestFormatSummarySection:
    """Tests for the format_summary_section function."""

    def test_includes_heading(self):
        result = format_summary_section("A summary.")
        assert result.startswith("## Summary\n")

    def test_includes_summary_text(self):
        result = format_summary_section("This is the summary.")
        assert "This is the summary." in result

    def test_has_blank_line_after_heading(self):
        result = format_summary_section("Summary text.")
        lines = result.split("\n")
        assert lines[0] == "## Summary"
        assert lines[1] == ""
        assert lines[2] == "Summary text."
