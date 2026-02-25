"""PDF format snapshot and quality tests."""

from pathlib import Path

from tests.conftest import normalize_markdown
from to_markdown.core.extraction import extract_file
from to_markdown.core.pipeline import convert_file


class TestPdfSnapshots:
    """Snapshot tests capturing full pipeline output for PDF files."""

    def test_simple(self, pdf_simple: Path, snapshot, tmp_path: Path):
        output = tmp_path / "simple.md"
        convert_file(pdf_simple, output_path=output)
        content = normalize_markdown(output.read_text(encoding="utf-8"))
        assert content == snapshot

    def test_with_headings(self, pdf_with_headings: Path, snapshot, tmp_path: Path):
        output = tmp_path / "headings.md"
        convert_file(pdf_with_headings, output_path=output)
        content = normalize_markdown(output.read_text(encoding="utf-8"))
        assert content == snapshot

    def test_with_table(self, pdf_with_table: Path, snapshot, tmp_path: Path):
        output = tmp_path / "table.md"
        convert_file(pdf_with_table, output_path=output)
        content = normalize_markdown(output.read_text(encoding="utf-8"))
        assert content == snapshot


class TestPdfQuality:
    """Content quality assertions for PDF extraction."""

    def test_content_not_empty(self, pdf_simple: Path):
        result = extract_file(pdf_simple)
        assert len(result.content.strip()) > 0

    def test_simple_contains_expected_text(self, pdf_simple: Path):
        result = extract_file(pdf_simple)
        assert "Hello World" in result.content

    def test_multi_page_contains_body_text(self, pdf_with_headings: Path):
        result = extract_file(pdf_with_headings)
        # Note: Kreuzberg may not extract heading text from fpdf2-generated PDFs
        # due to font-size-based rendering. Body paragraphs are reliably extracted.
        assert "first chapter" in result.content
        assert "second chapter" in result.content


class TestPdfFrontmatter:
    """Frontmatter composition verification for PDF files."""

    def test_has_format_field(self, pdf_simple: Path, tmp_path: Path):
        output = tmp_path / "fm_test.md"
        convert_file(pdf_simple, output_path=output)
        content = output.read_text(encoding="utf-8")
        assert "format:" in content

    def test_has_extracted_at(self, pdf_simple: Path, tmp_path: Path):
        output = tmp_path / "fm_test.md"
        convert_file(pdf_simple, output_path=output)
        content = output.read_text(encoding="utf-8")
        assert "extracted_at:" in content

    def test_has_pages_when_available(self, pdf_simple: Path):
        result = extract_file(pdf_simple)
        assert result.metadata.get("page_count") is not None
