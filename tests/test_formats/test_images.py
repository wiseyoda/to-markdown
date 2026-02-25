"""Image format snapshot and quality tests."""

import shutil
from pathlib import Path

import pytest

from tests.conftest import normalize_markdown
from to_markdown.core.extraction import extract_file
from to_markdown.core.pipeline import convert_file


class TestImageSnapshots:
    """Snapshot tests capturing full pipeline output for image files."""

    def test_png_simple(self, image_png_simple: Path, snapshot, tmp_path: Path):
        output = tmp_path / "text.md"
        convert_file(image_png_simple, output_path=output)
        content = normalize_markdown(output.read_text(encoding="utf-8"))
        assert content == snapshot

    def test_jpg_simple(self, image_jpg_simple: Path, snapshot, tmp_path: Path):
        output = tmp_path / "colored.md"
        convert_file(image_jpg_simple, output_path=output)
        content = normalize_markdown(output.read_text(encoding="utf-8"))
        assert content == snapshot


class TestImageQuality:
    """Content quality assertions for image extraction."""

    def test_content_not_empty(self, image_png_simple: Path):
        result = extract_file(image_png_simple)
        assert len(result.content.strip()) > 0

    def test_png_metadata_extracted(self, image_png_simple: Path):
        result = extract_file(image_png_simple)
        assert result.metadata.get("width") is not None
        assert result.metadata.get("height") is not None

    def test_jpg_metadata_extracted(self, image_jpg_simple: Path):
        result = extract_file(image_jpg_simple)
        assert result.metadata.get("width") is not None
        assert result.metadata.get("height") is not None


class TestImageFrontmatter:
    """Frontmatter composition verification for image files."""

    def test_has_format_field(self, image_png_simple: Path, tmp_path: Path):
        output = tmp_path / "fm_test.md"
        convert_file(image_png_simple, output_path=output)
        content = output.read_text(encoding="utf-8")
        assert "format:" in content

    def test_has_extracted_at(self, image_png_simple: Path, tmp_path: Path):
        output = tmp_path / "fm_test.md"
        convert_file(image_png_simple, output_path=output)
        content = output.read_text(encoding="utf-8")
        assert "extracted_at:" in content


@pytest.mark.ocr
@pytest.mark.skipif(
    shutil.which("tesseract") is None,
    reason="Tesseract not installed",
)
class TestImageOcr:
    """OCR text extraction tests (require Tesseract)."""

    def test_png_ocr_extracts_text(self, image_png_simple: Path):
        """Verify OCR can extract 'Test Image' text from the PNG fixture."""
        from kreuzberg import ExtractionConfig, OcrConfig, extract_file_sync

        result = extract_file_sync(
            str(image_png_simple),
            config=ExtractionConfig(
                force_ocr=True,
                ocr=OcrConfig(backend="tesseract", language="eng"),
            ),
        )
        assert "Test" in result.content or "Image" in result.content
