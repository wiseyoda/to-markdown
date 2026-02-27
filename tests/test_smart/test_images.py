"""Tests for the --images module (smart/images.py)."""

import asyncio
from unittest.mock import AsyncMock, patch

from to_markdown.smart.images import (
    _format_image_section,
    _image_mime_type,
    describe_images,
    describe_images_async,
)
from to_markdown.smart.llm import LLMError


class TestDescribeImages:
    """Tests for the describe_images function."""

    def test_returns_formatted_section(self, sample_extracted_images):
        with patch("to_markdown.smart.images.generate", return_value="A chart showing data."):
            result = describe_images(sample_extracted_images)
            assert result is not None
            assert "## Image Descriptions" in result
            assert "A chart showing data." in result

    def test_returns_none_for_empty_list(self):
        result = describe_images([])
        assert result is None

    def test_partial_success(self, sample_extracted_images):
        call_count = 0

        def mock_generate(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise LLMError("fail")
            return "Description of image 2."

        with patch("to_markdown.smart.images.generate", side_effect=mock_generate):
            result = describe_images(sample_extracted_images)
            assert result is not None
            assert "Description of image 2." in result
            assert "Image 2" in result

    def test_all_fail_returns_none(self, sample_extracted_images):
        with patch("to_markdown.smart.images.generate", side_effect=LLMError("fail")):
            result = describe_images(sample_extracted_images)
            assert result is None

    def test_includes_page_numbers(self, sample_extracted_images):
        with patch("to_markdown.smart.images.generate", return_value="Description."):
            result = describe_images(sample_extracted_images)
            assert "(page 1)" in result
            assert "(page 2)" in result

    def test_uses_image_description_temperature(self, sample_extracted_images):
        with patch("to_markdown.smart.images.generate", return_value="ok") as mock_gen:
            describe_images(sample_extracted_images[:1])
            assert mock_gen.call_args.kwargs["temperature"] == 0.2


class TestFormatImageSection:
    """Tests for image section formatting."""

    def test_includes_heading(self):
        descriptions = [{"index": 1, "page": 1, "description": "A photo."}]
        result = _format_image_section(descriptions)
        assert result.startswith("## Image Descriptions\n")

    def test_includes_subsections(self):
        descriptions = [
            {"index": 1, "page": 1, "description": "First image."},
            {"index": 2, "page": 3, "description": "Second image."},
        ]
        result = _format_image_section(descriptions)
        assert "### Image 1 (page 1)" in result
        assert "### Image 2 (page 3)" in result

    def test_no_page_info_when_none(self):
        descriptions = [{"index": 1, "page": None, "description": "An image."}]
        result = _format_image_section(descriptions)
        assert "### Image 1\n" in result
        assert "(page" not in result


class TestImageMimeType:
    """Tests for MIME type derivation."""

    def test_png(self):
        assert _image_mime_type("png") == "image/png"

    def test_jpeg(self):
        assert _image_mime_type("jpeg") == "image/jpeg"

    def test_jpg(self):
        assert _image_mime_type("jpg") == "image/jpeg"

    def test_unknown_format(self):
        assert _image_mime_type("svg") == "image/svg"

    def test_case_insensitive(self):
        assert _image_mime_type("PNG") == "image/png"

    def test_pdf_dctdecode(self):
        assert _image_mime_type("DCTDecode") == "image/jpeg"

    def test_pdf_flatedecode(self):
        assert _image_mime_type("FlateDecode") == "image/png"


class TestDescribeImagesAsync:
    """Tests for describe_images_async()."""

    def _make_image(self, index=1, fmt="png"):
        """Helper to create a test image dict."""
        return {
            "data": b"fake-image-data",
            "format": fmt,
            "page_number": index,
            "width": 100,
            "height": 100,
        }

    def test_multiple_images_concurrent(self):
        """Multiple images dispatched via asyncio.gather."""
        images = [self._make_image(i) for i in range(1, 4)]
        with patch(
            "to_markdown.smart.images.generate_async",
            new_callable=AsyncMock,
        ) as mock:
            mock.return_value = "Description of image"
            result = asyncio.run(describe_images_async(images))
            assert result is not None
            assert "Image 1" in result
            assert "Image 2" in result
            assert "Image 3" in result
            assert mock.await_count == 3

    def test_empty_images_returns_none(self):
        """Empty image list returns None."""
        result = asyncio.run(describe_images_async([]))
        assert result is None

    def test_individual_failure_doesnt_crash(self):
        """One failed image doesn't prevent others from succeeding."""
        images = [self._make_image(i) for i in range(1, 4)]

        async def side_effect(*args, **kwargs):
            # Fail on second call
            if side_effect.call_count == 1:
                side_effect.call_count += 1
                raise LLMError("API error")
            side_effect.call_count += 1
            return "Good description"

        side_effect.call_count = 0

        with patch(
            "to_markdown.smart.images.generate_async",
            new_callable=AsyncMock,
            side_effect=side_effect,
        ):
            result = asyncio.run(describe_images_async(images))
            assert result is not None
            # Should have 2 successful descriptions (1 failed)
            assert "Image 1" in result  # first succeeds
            assert "Image 3" in result  # third succeeds

    def test_all_failures_returns_none(self):
        """All images failing returns None."""
        images = [self._make_image(i) for i in range(1, 3)]
        with patch(
            "to_markdown.smart.images.generate_async",
            new_callable=AsyncMock,
        ) as mock:
            mock.side_effect = LLMError("API error")
            result = asyncio.run(describe_images_async(images))
            assert result is None

    def test_single_image_works(self):
        """Single image still uses async path correctly."""
        images = [self._make_image(1)]
        with patch(
            "to_markdown.smart.images.generate_async",
            new_callable=AsyncMock,
        ) as mock:
            mock.return_value = "Single image desc"
            result = asyncio.run(describe_images_async(images))
            assert result is not None
            assert "Image 1" in result
            assert mock.await_count == 1
