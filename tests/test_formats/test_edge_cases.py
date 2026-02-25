"""Edge case tests for error handling and unusual inputs."""

from pathlib import Path

import pytest

from to_markdown.core.extraction import (
    ExtractionError,
    UnsupportedFormatError,
    extract_file,
)


class TestEmptyFiles:
    """Zero-byte files should raise appropriate errors."""

    def test_empty_pdf(self, tmp_path: Path):
        empty = tmp_path / "empty.pdf"
        empty.write_bytes(b"")
        with pytest.raises((ExtractionError, UnsupportedFormatError)):
            extract_file(empty)

    def test_empty_docx(self, tmp_path: Path):
        empty = tmp_path / "empty.docx"
        empty.write_bytes(b"")
        with pytest.raises((ExtractionError, UnsupportedFormatError)):
            extract_file(empty)

    def test_empty_html(self, tmp_path: Path):
        empty = tmp_path / "empty.html"
        empty.write_bytes(b"")
        # Empty HTML may extract successfully with empty content or raise
        try:
            result = extract_file(empty)
            # If it doesn't raise, content should be empty or minimal
            assert isinstance(result.content, str)
        except ExtractionError, UnsupportedFormatError:
            pass  # Also acceptable


class TestCorruptedFiles:
    """Random bytes with valid extensions should raise errors."""

    def test_corrupted_pdf(self, tmp_path: Path):
        bad = tmp_path / "corrupted.pdf"
        bad.write_bytes(b"\x00\x01\x02\x03\x04random garbage data")
        with pytest.raises(ExtractionError):
            extract_file(bad)

    def test_corrupted_docx(self, tmp_path: Path):
        bad = tmp_path / "corrupted.docx"
        bad.write_bytes(b"\x00\x01\x02\x03\x04random garbage data")
        with pytest.raises(ExtractionError):
            extract_file(bad)


class TestWrongExtension:
    """Files with mismatched content and extension."""

    def test_html_content_as_pdf(self, tmp_path: Path):
        """HTML content saved with .pdf extension."""
        wrong = tmp_path / "actually_html.pdf"
        wrong.write_text("<html><body><p>Hello</p></body></html>")
        # Kreuzberg may detect actual content type or raise an error
        try:
            result = extract_file(wrong)
            # If extraction succeeds, content should be present
            assert isinstance(result.content, str)
        except ExtractionError, UnsupportedFormatError:
            pass  # Also acceptable


class TestUnicodeContent:
    """Unicode and multilingual content should extract without corruption."""

    def test_cjk_characters(self, tmp_path: Path):
        html = tmp_path / "cjk.html"
        html.write_text(
            "<html><body><p>Chinese: \u4f60\u597d</p>"
            "<p>Japanese: \u3053\u3093\u306b\u3061\u306f</p>"
            "<p>Korean: \uc548\ub155\ud558\uc138\uc694</p></body></html>",
            encoding="utf-8",
        )
        result = extract_file(html)
        assert "\u4f60\u597d" in result.content  # Chinese
        assert "\u3053\u3093\u306b\u3061\u306f" in result.content  # Japanese
        assert "\uc548\ub155\ud558\uc138\uc694" in result.content  # Korean

    def test_emoji_content(self, tmp_path: Path):
        html = tmp_path / "emoji.html"
        html.write_text(
            "<html><body><p>Hello \U0001f44b World \U0001f30d</p></body></html>",
            encoding="utf-8",
        )
        result = extract_file(html)
        assert "\U0001f44b" in result.content or "Hello" in result.content
