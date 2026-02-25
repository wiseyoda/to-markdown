"""PPTX format snapshot and quality tests."""

from pathlib import Path

from tests.conftest import normalize_markdown
from to_markdown.core.extraction import extract_file
from to_markdown.core.pipeline import convert_file


class TestPptxSnapshots:
    """Snapshot tests capturing full pipeline output for PPTX files."""

    def test_simple(self, pptx_simple: Path, snapshot, tmp_path: Path):
        output = tmp_path / "simple.md"
        convert_file(pptx_simple, output_path=output)
        content = normalize_markdown(output.read_text(encoding="utf-8"))
        assert content == snapshot

    def test_multi_slide(self, pptx_multi_slide: Path, snapshot, tmp_path: Path):
        output = tmp_path / "multi.md"
        convert_file(pptx_multi_slide, output_path=output)
        content = normalize_markdown(output.read_text(encoding="utf-8"))
        assert content == snapshot


class TestPptxQuality:
    """Content quality assertions for PPTX extraction."""

    def test_content_not_empty(self, pptx_simple: Path):
        result = extract_file(pptx_simple)
        assert len(result.content.strip()) > 0

    def test_slide_content_extracted(self, pptx_multi_slide: Path):
        result = extract_file(pptx_multi_slide)
        assert "Project Overview" in result.content
        assert "Key Metrics" in result.content
        assert "Next Steps" in result.content

    def test_speaker_notes_present(self, pptx_multi_slide: Path):
        result = extract_file(pptx_multi_slide)
        assert "growth trend" in result.content


class TestPptxFrontmatter:
    """Frontmatter composition verification for PPTX files."""

    def test_has_format_field(self, pptx_simple: Path, tmp_path: Path):
        output = tmp_path / "fm_test.md"
        convert_file(pptx_simple, output_path=output)
        content = output.read_text(encoding="utf-8")
        assert "format:" in content

    def test_has_extracted_at(self, pptx_simple: Path, tmp_path: Path):
        output = tmp_path / "fm_test.md"
        convert_file(pptx_simple, output_path=output)
        content = output.read_text(encoding="utf-8")
        assert "extracted_at:" in content
