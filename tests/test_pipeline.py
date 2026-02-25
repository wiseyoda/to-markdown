"""Tests for the conversion pipeline (core/pipeline.py)."""

from pathlib import Path

import pytest

from to_markdown.core.pipeline import OutputExistsError, convert_file


class TestBasicConversion:
    """Tests for basic file conversion."""

    def test_creates_output_file(self, sample_text_file: Path):
        result = convert_file(sample_text_file)
        assert result.exists()
        assert result.suffix == ".md"

    def test_output_contains_frontmatter(self, sample_text_file: Path):
        result = convert_file(sample_text_file)
        content = result.read_text()
        assert content.startswith("---\n")
        assert "extracted_at:" in content

    def test_output_contains_source_content(self, sample_text_file: Path):
        result = convert_file(sample_text_file)
        content = result.read_text()
        assert "Hello" in content
        assert "test document" in content

    def test_returns_output_path(self, sample_text_file: Path):
        result = convert_file(sample_text_file)
        expected = sample_text_file.with_suffix(".md")
        assert result == expected


class TestOutputPathResolution:
    """Tests for output path resolution."""

    def test_default_same_directory(self, sample_text_file: Path):
        result = convert_file(sample_text_file)
        assert result.parent == sample_text_file.parent
        assert result.name == "sample.md"

    def test_custom_output_file(self, sample_text_file: Path, tmp_path: Path):
        custom = tmp_path / "custom_output.md"
        result = convert_file(sample_text_file, output_path=custom)
        assert result == custom
        assert custom.exists()

    def test_custom_output_directory(self, sample_text_file: Path, output_dir: Path):
        result = convert_file(sample_text_file, output_path=output_dir)
        expected = output_dir / "sample.md"
        assert result == expected
        assert expected.exists()


class TestOverwriteProtection:
    """Tests for overwrite protection (--force behavior)."""

    def test_error_when_output_exists(self, sample_text_file: Path):
        output = sample_text_file.with_suffix(".md")
        output.write_text("existing content")

        with pytest.raises(OutputExistsError, match="already exists"):
            convert_file(sample_text_file)

    def test_force_overwrites_existing(self, sample_text_file: Path):
        output = sample_text_file.with_suffix(".md")
        output.write_text("old content")

        result = convert_file(sample_text_file, force=True)
        assert result.exists()
        content = result.read_text()
        assert "old content" not in content
        assert "Hello" in content

    def test_no_error_when_output_does_not_exist(self, sample_text_file: Path):
        result = convert_file(sample_text_file)
        assert result.exists()


class TestErrorHandling:
    """Tests for pipeline error handling."""

    def test_missing_input_file(self, tmp_path: Path):
        missing = tmp_path / "nonexistent.txt"
        with pytest.raises(FileNotFoundError):
            convert_file(missing)

    def test_output_directory_created_if_needed(self, sample_text_file: Path, tmp_path: Path):
        nested = tmp_path / "deep" / "nested" / "output.md"
        result = convert_file(sample_text_file, output_path=nested)
        assert result.exists()
        assert result == nested
