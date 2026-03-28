"""Tests for the Kreuzberg adapter (core/extraction.py)."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from to_markdown.core.extraction import (
    ExtractionError,
    ExtractionResult,
    UnsupportedFormatError,
    _extraction_quality,
    _is_sparse_pdf_extraction,
    extract_file,
)


class TestExtractionResult:
    """Tests for the ExtractionResult dataclass."""

    def test_fields_have_correct_types(self):
        result = ExtractionResult(content="hello", metadata={"key": "val"}, tables=[])
        assert isinstance(result.content, str)
        assert isinstance(result.metadata, dict)
        assert isinstance(result.tables, list)

    def test_defaults_for_metadata_and_tables(self):
        result = ExtractionResult(content="hello")
        assert result.metadata == {}
        assert result.tables == []

    def test_is_frozen(self):
        result = ExtractionResult(content="hello")
        with pytest.raises(AttributeError):
            result.content = "changed"


class TestExtractFile:
    """Tests for the extract_file function."""

    def test_extract_text_file(self, sample_text_file: Path):
        result = extract_file(sample_text_file)
        assert isinstance(result, ExtractionResult)
        assert "Hello" in result.content
        assert "test document" in result.content

    def test_metadata_is_dict(self, sample_text_file: Path):
        result = extract_file(sample_text_file)
        assert isinstance(result.metadata, dict)

    def test_metadata_contains_expected_keys(self, sample_text_file: Path):
        result = extract_file(sample_text_file)
        assert "format_type" in result.metadata
        assert "word_count" in result.metadata

    def test_file_not_found(self, tmp_path: Path):
        missing = tmp_path / "nonexistent.txt"
        with pytest.raises(FileNotFoundError, match="File not found"):
            extract_file(missing)

    def test_unsupported_format(self, tmp_path: Path):
        bad_file = tmp_path / "test.xyz"
        bad_file.write_text("random content")
        with pytest.raises(UnsupportedFormatError, match="Unsupported format"):
            extract_file(bad_file)

    def test_tables_is_list(self, sample_text_file: Path):
        result = extract_file(sample_text_file)
        assert isinstance(result.tables, list)


class TestExceptionHierarchy:
    """Tests for custom exception hierarchy."""

    def test_unsupported_format_is_extraction_error(self):
        assert issubclass(UnsupportedFormatError, ExtractionError)

    def test_extraction_error_is_exception(self):
        assert issubclass(ExtractionError, Exception)


class TestExtractionQuality:
    """Tests for the _extraction_quality helper."""

    def test_returns_quality_score_from_metadata(self):
        result = SimpleNamespace(metadata={"quality_score": 0.1}, content="E")
        assert _extraction_quality(result) == 0.1

    def test_defaults_to_1_when_missing(self):
        result = SimpleNamespace(metadata={}, content="some text")
        assert _extraction_quality(result) == 1.0

    def test_defaults_to_1_when_metadata_not_dict(self):
        result = SimpleNamespace(metadata=None, content="some text")
        assert _extraction_quality(result) == 1.0


class TestIsSparseExtractionDetection:
    """Tests for _is_sparse_pdf_extraction."""

    def test_returns_false_for_non_pdf(self):
        result = SimpleNamespace(metadata={"quality_score": 0.1}, content="E")
        assert _is_sparse_pdf_extraction(result, Path("file.docx")) is False

    def test_returns_true_for_low_quality_pdf(self):
        result = SimpleNamespace(metadata={"quality_score": 0.1}, content="E")
        assert _is_sparse_pdf_extraction(result, Path("file.pdf")) is True

    def test_returns_true_for_short_content_pdf(self):
        result = SimpleNamespace(metadata={"quality_score": 1.0}, content="short")
        assert _is_sparse_pdf_extraction(result, Path("file.pdf")) is True

    def test_returns_false_for_good_quality_pdf(self):
        result = SimpleNamespace(metadata={"quality_score": 0.9}, content="x" * 100)
        assert _is_sparse_pdf_extraction(result, Path("file.pdf")) is False

    def test_case_insensitive_suffix(self):
        result = SimpleNamespace(metadata={"quality_score": 0.1}, content="E")
        assert _is_sparse_pdf_extraction(result, Path("FILE.PDF")) is True


class TestOcrFallback:
    """Tests for OCR fallback retry logic in extract_file."""

    def test_ocr_fallback_produces_better_content(self, tmp_path: Path):
        """When standard extraction is sparse, OCR retry should produce better content."""
        pdf_file = tmp_path / "sparse.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 fake content")

        sparse_result = SimpleNamespace(
            content="E",
            metadata={"quality_score": 0.1, "format_type": "pdf"},
            tables=[],
            images=[],
        )
        ocr_result = SimpleNamespace(
            content="Full dashboard content with lots of useful data",
            metadata={"quality_score": 1.0, "format_type": "pdf"},
            tables=[],
            images=[],
        )

        with patch(
            "to_markdown.core.extraction.extract_file_sync",
            side_effect=[sparse_result, ocr_result],
        ):
            result = extract_file(pdf_file)

        assert result.content == "Full dashboard content with lots of useful data"
        assert result.metadata.get("ocr_fallback") is True

    def test_ocr_fallback_not_triggered_for_good_extraction(self, tmp_path: Path):
        """Standard extraction with good quality should not trigger OCR retry."""
        pdf_file = tmp_path / "good.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 fake content")

        good_result = SimpleNamespace(
            content="This is a well-extracted PDF with plenty of content to work with.",
            metadata={"quality_score": 0.9, "format_type": "pdf"},
            tables=[],
            images=[],
        )

        with patch(
            "to_markdown.core.extraction.extract_file_sync",
            return_value=good_result,
        ):
            result = extract_file(pdf_file)

        assert "well-extracted" in result.content
        assert result.metadata.get("ocr_fallback") is None

    def test_ocr_fallback_keeps_original_if_retry_worse(self, tmp_path: Path):
        """If OCR retry produces less content, keep the original."""
        pdf_file = tmp_path / "edge.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 fake content")

        sparse_result = SimpleNamespace(
            content="AB",
            metadata={"quality_score": 0.1, "format_type": "pdf"},
            tables=[],
            images=[],
        )
        worse_result = SimpleNamespace(
            content="A",
            metadata={"quality_score": 0.5, "format_type": "pdf"},
            tables=[],
            images=[],
        )

        with patch(
            "to_markdown.core.extraction.extract_file_sync",
            side_effect=[sparse_result, worse_result],
        ):
            result = extract_file(pdf_file)

        assert result.content == "AB"
        assert result.metadata.get("ocr_fallback") is None
