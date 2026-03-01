"""Tests for the conversion pipeline (core/pipeline.py)."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from to_markdown.core.content_builder import build_content_async
from to_markdown.core.pipeline import (
    OutputExistsError,
    convert_file,
    convert_to_string,
)


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
    """Tests for smart feature integration in the pipeline (async internally)."""

    def test_clean_flag_calls_clean_content_async(self, sample_text_file: Path):
        mock_clean = AsyncMock(return_value="cleaned")
        with patch("to_markdown.smart.clean.clean_content_async", mock_clean):
            result = convert_file(sample_text_file, clean=True)
            mock_clean.assert_called_once()
            content = result.read_text()
            assert "cleaned" in content

    def test_clean_flag_false_skips_clean(self, sample_text_file: Path):
        mock_clean = AsyncMock()
        with patch("to_markdown.smart.clean.clean_content_async", mock_clean):
            convert_file(sample_text_file, clean=False)
            mock_clean.assert_not_called()

    def test_summary_flag_calls_summarize_async(self, sample_text_file: Path):
        mock_summarize = AsyncMock(return_value="A summary.")
        with (
            patch("to_markdown.smart.summary.summarize_content_async", mock_summarize),
            patch(
                "to_markdown.smart.summary.format_summary_section",
                return_value="## Summary\n\nA summary.\n",
            ),
        ):
            result = convert_file(sample_text_file, summary=True)
            content = result.read_text()
            assert "## Summary" in content

    def test_summary_none_skips_section(self, sample_text_file: Path):
        mock_summarize = AsyncMock(return_value=None)
        with patch("to_markdown.smart.summary.summarize_content_async", mock_summarize):
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

        mock_describe = AsyncMock(return_value="## Image Descriptions\n\n### Image 1\n\nA photo.\n")
        with (
            patch("to_markdown.core.content_builder.extract_file", return_value=mock_result),
            patch("to_markdown.smart.images.describe_images_async", mock_describe),
        ):
            result = convert_file(sample_text_file, images=True)
            mock_describe.assert_called_once_with(mock_images)
            content = result.read_text()
            assert "## Image Descriptions" in content

    def test_clean_and_images_run_in_parallel(self, sample_text_file: Path):
        """Clean and images are gathered via asyncio.gather for parallel execution."""
        mock_images = [{"data": b"img", "format": "png", "page_number": 1}]
        mock_result = MagicMock()
        mock_result.content = "text"
        mock_result.metadata = {"format_type": "pdf"}
        mock_result.tables = []
        mock_result.images = mock_images

        mock_clean = AsyncMock(return_value="cleaned content")
        mock_describe = AsyncMock(return_value="## Image Descriptions\n\nimage desc\n")

        with (
            patch("to_markdown.core.content_builder.extract_file", return_value=mock_result),
            patch("to_markdown.smart.clean.clean_content_async", mock_clean),
            patch("to_markdown.smart.images.describe_images_async", mock_describe),
        ):
            result = convert_file(sample_text_file, clean=True, images=True)
            mock_clean.assert_called_once()
            mock_describe.assert_called_once_with(mock_images)
            content = result.read_text()
            assert "cleaned content" in content
            assert "## Image Descriptions" in content

    def test_summary_runs_after_clean(self, sample_text_file: Path):
        """Summary depends on cleaned content, so it runs after clean finishes."""
        call_order = []

        async def mock_clean(content, fmt):
            call_order.append("clean")
            return "cleaned content"

        async def mock_summarize(content, fmt):
            call_order.append("summary")
            # Summary should receive cleaned content
            assert content == "cleaned content"
            return "A summary."

        mock_result = MagicMock()
        mock_result.content = "text"
        mock_result.metadata = {"format_type": "pdf"}
        mock_result.tables = []
        mock_result.images = []

        with (
            patch("to_markdown.core.content_builder.extract_file", return_value=mock_result),
            patch("to_markdown.smart.clean.clean_content_async", side_effect=mock_clean),
            patch(
                "to_markdown.smart.summary.summarize_content_async",
                side_effect=mock_summarize,
            ),
            patch(
                "to_markdown.smart.summary.format_summary_section",
                return_value="## Summary\n\nA summary.\n",
            ),
        ):
            convert_file(sample_text_file, clean=True, summary=True)
            assert call_order == ["clean", "summary"]

    def test_clean_failure_doesnt_block_summary(self, sample_text_file: Path):
        mock_clean = AsyncMock(side_effect=lambda c, f: c)
        mock_summarize = AsyncMock(return_value="Summary works.")
        with (
            patch("to_markdown.smart.clean.clean_content_async", mock_clean),
            patch("to_markdown.smart.summary.summarize_content_async", mock_summarize),
            patch(
                "to_markdown.smart.summary.format_summary_section",
                return_value="## Summary\n\nSummary works.\n",
            ),
        ):
            result = convert_file(sample_text_file, clean=True, summary=True)
            content = result.read_text()
            assert "## Summary" in content


class TestSanitize:
    """Tests for sanitize parameter in the pipeline."""

    def test_sanitize_enabled_by_default(self, sample_text_file: Path):
        """Sanitize runs by default (sanitize=True)."""
        sanitize_mod = __import__(
            "to_markdown.core.sanitize",
            fromlist=["sanitize_content"],
        )
        with patch(
            "to_markdown.core.sanitize.sanitize_content",
            wraps=sanitize_mod.sanitize_content,
        ) as mock:
            convert_file(sample_text_file)
            mock.assert_called_once()

    def test_sanitize_disabled_skips_sanitization(self, sample_text_file: Path):
        """When sanitize=False, sanitize_content is not called."""
        with patch("to_markdown.core.sanitize.sanitize_content") as mock:
            convert_file(sample_text_file, sanitize=False)
            mock.assert_not_called()

    def test_sanitize_removes_invisible_chars(self, sample_text_file: Path):
        """Sanitization strips zero-width characters from content."""
        content_with_zwsp = "Hello\u200bworld"
        mock_result = MagicMock()
        mock_result.content = content_with_zwsp
        mock_result.metadata = {"format_type": "txt"}
        mock_result.tables = []
        mock_result.images = []

        with patch("to_markdown.core.content_builder.extract_file", return_value=mock_result):
            result = convert_file(sample_text_file)
            output = result.read_text()
            assert "\u200b" not in output
            assert "Helloworld" in output

    def test_sanitize_adds_frontmatter_flag_when_modified(self, sample_text_file: Path):
        """When content is sanitized, frontmatter includes sanitized: true."""
        content_with_zwsp = "Hello\u200bworld"
        mock_result = MagicMock()
        mock_result.content = content_with_zwsp
        mock_result.metadata = {"format_type": "txt"}
        mock_result.tables = []
        mock_result.images = []

        with patch("to_markdown.core.content_builder.extract_file", return_value=mock_result):
            result = convert_file(sample_text_file)
            output = result.read_text()
            assert "sanitized: true" in output

    def test_sanitize_no_frontmatter_flag_when_clean(self, sample_text_file: Path):
        """When content has no invisible chars, frontmatter omits sanitized flag."""
        result = convert_file(sample_text_file)
        output = result.read_text()
        assert "sanitized:" not in output

    def test_sanitize_runs_before_clean(self, sample_text_file: Path):
        """Sanitization happens before LLM clean step."""
        call_order = []

        from to_markdown.core.sanitize import SanitizeResult

        def mock_sanitize(content):
            call_order.append("sanitize")
            return SanitizeResult(content=content, chars_removed=0, was_modified=False)

        async def mock_clean(content, fmt):
            call_order.append("clean")
            return content

        with (
            patch("to_markdown.core.sanitize.sanitize_content", side_effect=mock_sanitize),
            patch("to_markdown.smart.clean.clean_content_async", side_effect=mock_clean),
        ):
            convert_file(sample_text_file, clean=True, sanitize=True)
            assert call_order == ["sanitize", "clean"]

    def test_sanitize_convert_to_string(self, sample_text_file: Path):
        """Sanitize parameter works with convert_to_string too."""
        content_with_zwsp = "Hello\u200bworld"
        mock_result = MagicMock()
        mock_result.content = content_with_zwsp
        mock_result.metadata = {"format_type": "txt"}
        mock_result.tables = []
        mock_result.images = []

        with patch("to_markdown.core.content_builder.extract_file", return_value=mock_result):
            result = convert_to_string(sample_text_file, sanitize=True)
            assert "\u200b" not in result
            assert "sanitized: true" in result

    def test_sanitize_false_convert_to_string(self, sample_text_file: Path):
        """sanitize=False works with convert_to_string."""
        with patch("to_markdown.core.sanitize.sanitize_content") as mock:
            convert_to_string(sample_text_file, sanitize=False)
            mock.assert_not_called()


class TestConvertToString:
    """Tests for convert_to_string() - returns content instead of writing to disk."""

    def test_returns_string_with_frontmatter(self, sample_text_file: Path):
        result = convert_to_string(sample_text_file)
        assert isinstance(result, str)
        assert result.startswith("---\n")
        assert "extracted_at:" in result

    def test_returns_source_content(self, sample_text_file: Path):
        result = convert_to_string(sample_text_file)
        assert "Hello" in result
        assert "test document" in result

    def test_does_not_write_file(self, sample_text_file: Path):
        convert_to_string(sample_text_file)
        output = sample_text_file.with_suffix(".md")
        assert not output.exists()

    def test_missing_input_raises_error(self, tmp_path: Path):
        missing = tmp_path / "nonexistent.txt"
        with pytest.raises(FileNotFoundError):
            convert_to_string(missing)

    def test_clean_flag(self, sample_text_file: Path):
        mock_clean = AsyncMock(return_value="cleaned")
        with patch("to_markdown.smart.clean.clean_content_async", mock_clean):
            result = convert_to_string(sample_text_file, clean=True)
            mock_clean.assert_called_once()
            assert "cleaned" in result

    def test_summary_flag(self, sample_text_file: Path):
        mock_summarize = AsyncMock(return_value="A summary.")
        with (
            patch("to_markdown.smart.summary.summarize_content_async", mock_summarize),
            patch(
                "to_markdown.smart.summary.format_summary_section",
                return_value="## Summary\n\nA summary.\n",
            ),
        ):
            result = convert_to_string(sample_text_file, summary=True)
            assert "## Summary" in result

    def test_consistent_with_convert_file(self, sample_text_file: Path):
        """convert_to_string and convert_file should produce the same content."""
        string_result = convert_to_string(sample_text_file)
        file_path = convert_file(sample_text_file)
        file_result = file_path.read_text()
        assert string_result == file_result


class TestBuildContentAsync:
    """Tests for the async core function build_content_async."""

    def test_build_content_async_is_coroutine(self, sample_text_file: Path):
        """build_content_async returns a coroutine."""
        coro = build_content_async(sample_text_file)
        assert asyncio.iscoroutine(coro)
        # Clean up the coroutine to avoid RuntimeWarning
        coro.close()

    def test_build_content_async_produces_markdown(self, sample_text_file: Path):
        """build_content_async produces valid markdown with frontmatter."""
        result = asyncio.run(build_content_async(sample_text_file))
        assert result.startswith("---\n")
        assert "extracted_at:" in result
        assert "Hello" in result

    def test_build_content_async_with_clean(self, sample_text_file: Path):
        """build_content_async calls clean_content_async when clean=True."""
        mock_clean = AsyncMock(return_value="async cleaned")
        with patch("to_markdown.smart.clean.clean_content_async", mock_clean):
            result = asyncio.run(build_content_async(sample_text_file, clean=True))
            mock_clean.assert_called_once()
            assert "async cleaned" in result

    def test_build_content_async_with_summary(self, sample_text_file: Path):
        """build_content_async calls summarize_content_async when summary=True."""
        mock_summarize = AsyncMock(return_value="Async summary.")
        with (
            patch("to_markdown.smart.summary.summarize_content_async", mock_summarize),
            patch(
                "to_markdown.smart.summary.format_summary_section",
                return_value="## Summary\n\nAsync summary.\n",
            ),
        ):
            result = asyncio.run(build_content_async(sample_text_file, summary=True))
            mock_summarize.assert_called_once()
            assert "## Summary" in result

    def test_build_content_async_parallel_gather(self, sample_text_file: Path):
        """Clean and images are submitted to asyncio.gather for parallel execution."""
        mock_images = [{"data": b"img", "format": "png", "page_number": 1}]
        mock_result = MagicMock()
        mock_result.content = "text"
        mock_result.metadata = {"format_type": "pdf"}
        mock_result.tables = []
        mock_result.images = mock_images

        mock_clean = AsyncMock(return_value="cleaned")
        mock_describe = AsyncMock(return_value="## Image Descriptions\n\nimage\n")

        with (
            patch("to_markdown.core.content_builder.extract_file", return_value=mock_result),
            patch("to_markdown.smart.clean.clean_content_async", mock_clean),
            patch("to_markdown.smart.images.describe_images_async", mock_describe),
            patch(
                "to_markdown.core.content_builder.asyncio.gather",
                wraps=asyncio.gather,
            ) as mock_gather,
        ):
            result = asyncio.run(build_content_async(sample_text_file, clean=True, images=True))
            mock_gather.assert_called_once()
            assert "cleaned" in result
            assert "## Image Descriptions" in result


class TestAsyncPipeline:
    """Tests for async pipeline orchestration (T018)."""

    def test_pipeline_no_llm_features(self, tmp_path: Path):
        """Pipeline works without any LLM features (no async overhead)."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Simple content")

        with patch("to_markdown.core.content_builder.extract_file") as mock_extract:
            mock_result = MagicMock()
            mock_result.content = "Extracted content"
            mock_result.metadata = {"format_type": "txt"}
            mock_result.images = []
            mock_extract.return_value = mock_result

            result = convert_to_string(test_file)
            assert "Extracted content" in result

    def test_clean_and_images_run_concurrently(self, tmp_path: Path):
        """When both clean and images enabled, they run via asyncio.gather."""
        test_file = tmp_path / "test.pdf"
        test_file.write_text("content")

        call_order = []

        async def mock_clean(*args, **kwargs):
            call_order.append("clean_start")
            return "Cleaned content"

        async def mock_images(*args, **kwargs):
            call_order.append("images_start")
            return "## Image Descriptions\n\n### Image 1\n\nA photo\n"

        with (
            patch("to_markdown.core.content_builder.extract_file") as mock_extract,
            patch("to_markdown.core.sanitize.sanitize_content") as mock_sanitize,
            patch("to_markdown.smart.clean.clean_content_async", side_effect=mock_clean),
            patch(
                "to_markdown.smart.images.describe_images_async",
                side_effect=mock_images,
            ),
        ):
            mock_result = MagicMock()
            mock_result.content = "Raw content"
            mock_result.metadata = {"format_type": "pdf"}
            mock_result.images = [{"data": b"img", "format": "png", "page_number": 1}]
            mock_extract.return_value = mock_result
            mock_sanitize.return_value = MagicMock(
                content="Raw content",
                was_modified=False,
            )

            result = convert_to_string(test_file, clean=True, images=True)
            assert "Cleaned content" in result
            assert "Image Descriptions" in result

    def test_summary_uses_cleaned_content(self, tmp_path: Path):
        """Summary runs after clean and uses cleaned content."""
        test_file = tmp_path / "test.pdf"
        test_file.write_text("content")

        captured_summary_input = []

        async def mock_summarize(content, format_type):
            captured_summary_input.append(content)
            return "A summary"

        with (
            patch("to_markdown.core.content_builder.extract_file") as mock_extract,
            patch("to_markdown.core.sanitize.sanitize_content") as mock_sanitize,
            patch(
                "to_markdown.smart.clean.clean_content_async",
                new_callable=AsyncMock,
                return_value="CLEANED",
            ),
            patch(
                "to_markdown.smart.summary.summarize_content_async",
                side_effect=mock_summarize,
            ),
            patch(
                "to_markdown.smart.summary.format_summary_section",
                return_value="## Summary\n\nA summary\n",
            ),
        ):
            mock_result = MagicMock()
            mock_result.content = "Raw dirty content"
            mock_result.metadata = {"format_type": "pdf"}
            mock_result.images = []
            mock_extract.return_value = mock_result
            mock_sanitize.return_value = MagicMock(
                content="Raw dirty content",
                was_modified=False,
            )

            result = convert_to_string(test_file, clean=True, summary=True)
            # Summary should receive the cleaned content, not the raw content
            assert captured_summary_input[0] == "CLEANED"
            assert "Summary" in result

    def test_sanitize_false_skips_sanitization(self, tmp_path: Path):
        """sanitize=False skips the sanitization step entirely."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        with patch("to_markdown.core.content_builder.extract_file") as mock_extract:
            mock_result = MagicMock()
            mock_result.content = "Content with \u200b zero-width"
            mock_result.metadata = {"format_type": "txt"}
            mock_result.images = []
            mock_extract.return_value = mock_result

            result = convert_to_string(test_file, sanitize=False)
            # Zero-width char should still be in the output
            assert "\u200b" in result

    def test_sanitized_frontmatter_field(self, tmp_path: Path):
        """Frontmatter includes sanitized: true when content was sanitized."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        with patch("to_markdown.core.content_builder.extract_file") as mock_extract:
            mock_result = MagicMock()
            mock_result.content = "Hello\u200bWorld"
            mock_result.metadata = {"format_type": "txt"}
            mock_result.images = []
            mock_extract.return_value = mock_result

            result = convert_to_string(test_file, sanitize=True)
            assert "sanitized: true" in result
            # Zero-width char should not be in content after frontmatter
            assert "\u200b" not in result.split("---", 2)[-1]

    def test_all_features_together(self, tmp_path: Path):
        """Sanitize + clean + images + summary: all features work together."""
        test_file = tmp_path / "test.pdf"
        test_file.write_text("content")

        with (
            patch("to_markdown.core.content_builder.extract_file") as mock_extract,
            patch(
                "to_markdown.smart.clean.clean_content_async",
                new_callable=AsyncMock,
                return_value="Cleaned text",
            ),
            patch(
                "to_markdown.smart.images.describe_images_async",
                new_callable=AsyncMock,
                return_value="## Image Descriptions\n\n### Image 1\n\nA chart\n",
            ),
            patch(
                "to_markdown.smart.summary.summarize_content_async",
                new_callable=AsyncMock,
                return_value="Doc summary",
            ),
            patch(
                "to_markdown.smart.summary.format_summary_section",
                return_value="## Summary\n\nDoc summary\n",
            ),
        ):
            mock_result = MagicMock()
            mock_result.content = "Raw \u200bcontent"
            mock_result.metadata = {"format_type": "pdf"}
            mock_result.images = [{"data": b"img", "format": "png", "page_number": 1}]
            mock_extract.return_value = mock_result

            result = convert_to_string(
                test_file,
                clean=True,
                images=True,
                summary=True,
                sanitize=True,
            )
            assert "sanitized: true" in result
            assert "Cleaned text" in result
            assert "Image Descriptions" in result
            assert "## Summary" in result
            # Zero-width char should be removed
            assert "\u200b" not in result

    def test_clean_false_skips_clean(self, tmp_path: Path):
        """clean=False skips the LLM clean step entirely."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        with (
            patch("to_markdown.core.content_builder.extract_file") as mock_extract,
            patch("to_markdown.smart.clean.clean_content_async") as mock_clean,
        ):
            mock_result = MagicMock()
            mock_result.content = "Original content"
            mock_result.metadata = {"format_type": "txt"}
            mock_result.images = []
            mock_extract.return_value = mock_result

            result = convert_to_string(test_file, clean=False)
            mock_clean.assert_not_called()
            assert "Original content" in result
