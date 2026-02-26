"""Tests for the conversion pipeline (core/pipeline.py)."""

from pathlib import Path
from unittest.mock import MagicMock, patch

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


class TestSmartFeatures:
    """Tests for smart feature integration in the pipeline."""

    def test_clean_flag_calls_clean_content(self, sample_text_file: Path):
        with patch("to_markdown.smart.clean.clean_content", return_value="cleaned") as mock:
            result = convert_file(sample_text_file, clean=True)
            mock.assert_called_once()
            content = result.read_text()
            assert "cleaned" in content

    def test_clean_flag_false_skips_clean(self, sample_text_file: Path):
        with patch("to_markdown.smart.clean.clean_content") as mock:
            convert_file(sample_text_file, clean=False)
            mock.assert_not_called()

    def test_summary_flag_calls_summarize(self, sample_text_file: Path):
        with (
            patch("to_markdown.smart.summary.summarize_content", return_value="A summary."),
            patch(
                "to_markdown.smart.summary.format_summary_section",
                return_value="## Summary\n\nA summary.\n",
            ),
        ):
            result = convert_file(sample_text_file, summary=True)
            content = result.read_text()
            assert "## Summary" in content

    def test_summary_none_skips_section(self, sample_text_file: Path):
        with patch("to_markdown.smart.summary.summarize_content", return_value=None):
            result = convert_file(sample_text_file, summary=True)
            content = result.read_text()
            assert "## Summary" not in content

    def test_images_flag_with_no_images_skips(self, sample_text_file: Path):
        result = convert_file(sample_text_file, images=True)
        content = result.read_text()
        assert "## Image Descriptions" not in content

    def test_images_flag_with_extracted_images(self, sample_text_file: Path):
        mock_images = [{"data": b"img", "format": "png", "page_number": 1}]
        mock_result = MagicMock()
        mock_result.content = "text content"
        mock_result.metadata = {"format_type": "txt"}
        mock_result.tables = []
        mock_result.images = mock_images

        with (
            patch("to_markdown.core.pipeline.extract_file", return_value=mock_result),
            patch(
                "to_markdown.smart.images.describe_images",
                return_value="## Image Descriptions\n\n### Image 1\n\nA photo.\n",
            ) as mock_desc,
        ):
            result = convert_file(sample_text_file, images=True)
            mock_desc.assert_called_once_with(mock_images)
            content = result.read_text()
            assert "## Image Descriptions" in content

    def test_processing_order_clean_then_images_then_summary(self, sample_text_file: Path):
        call_order = []

        def mock_clean(content, fmt):
            call_order.append("clean")
            return "cleaned content"

        def mock_describe(imgs):
            call_order.append("images")
            return "## Image Descriptions\n\nimage desc\n"

        def mock_summarize(content, fmt):
            call_order.append("summary")
            return "A summary."

        mock_result = MagicMock()
        mock_result.content = "text"
        mock_result.metadata = {"format_type": "pdf"}
        mock_result.tables = []
        mock_result.images = [{"data": b"img", "format": "png", "page_number": 1}]

        with (
            patch("to_markdown.core.pipeline.extract_file", return_value=mock_result),
            patch("to_markdown.smart.clean.clean_content", side_effect=mock_clean),
            patch("to_markdown.smart.images.describe_images", side_effect=mock_describe),
            patch("to_markdown.smart.summary.summarize_content", side_effect=mock_summarize),
            patch(
                "to_markdown.smart.summary.format_summary_section",
                return_value="## Summary\n\nA summary.\n",
            ),
        ):
            convert_file(sample_text_file, clean=True, summary=True, images=True)
            assert call_order == ["clean", "images", "summary"]

    def test_clean_failure_doesnt_block_summary(self, sample_text_file: Path):
        with (
            patch("to_markdown.smart.clean.clean_content", side_effect=lambda c, f: c),
            patch("to_markdown.smart.summary.summarize_content", return_value="Summary works."),
            patch(
                "to_markdown.smart.summary.format_summary_section",
                return_value="## Summary\n\nSummary works.\n",
            ),
        ):
            result = convert_file(sample_text_file, clean=True, summary=True)
            content = result.read_text()
            assert "## Summary" in content
