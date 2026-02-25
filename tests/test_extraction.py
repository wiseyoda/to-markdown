"""Tests for the Kreuzberg adapter (core/extraction.py)."""

from pathlib import Path

import pytest

from to_markdown.core.extraction import (
    ExtractionError,
    ExtractionResult,
    UnsupportedFormatError,
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
