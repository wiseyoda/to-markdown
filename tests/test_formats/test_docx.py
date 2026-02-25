"""DOCX format snapshot and quality tests."""

from pathlib import Path

from tests.conftest import normalize_markdown
from to_markdown.core.extraction import extract_file
from to_markdown.core.pipeline import convert_file


class TestDocxSnapshots:
    """Snapshot tests capturing full pipeline output for DOCX files."""

    def test_simple(self, docx_simple: Path, snapshot, tmp_path: Path):
        output = tmp_path / "simple.md"
        convert_file(docx_simple, output_path=output)
        content = normalize_markdown(output.read_text(encoding="utf-8"))
        assert content == snapshot

    def test_with_formatting(self, docx_with_formatting: Path, snapshot, tmp_path: Path):
        output = tmp_path / "formatted.md"
        convert_file(docx_with_formatting, output_path=output)
        content = normalize_markdown(output.read_text(encoding="utf-8"))
        assert content == snapshot

    def test_with_table(self, docx_with_table: Path, snapshot, tmp_path: Path):
        output = tmp_path / "table.md"
        convert_file(docx_with_table, output_path=output)
        content = normalize_markdown(output.read_text(encoding="utf-8"))
        assert content == snapshot


class TestDocxQuality:
    """Content quality assertions for DOCX extraction."""

    def test_content_not_empty(self, docx_simple: Path):
        result = extract_file(docx_simple)
        assert len(result.content.strip()) > 0

    def test_headings_preserved(self, docx_with_formatting: Path):
        result = extract_file(docx_with_formatting)
        assert "Main Title" in result.content
        assert "Section One" in result.content
        assert "Section Two" in result.content

    def test_formatting_preserved(self, docx_with_formatting: Path):
        result = extract_file(docx_with_formatting)
        assert "bold text" in result.content
        assert "italic text" in result.content

    def test_table_content_present(self, docx_with_table: Path):
        result = extract_file(docx_with_table)
        assert "Alice" in result.content
        assert "Engineering" in result.content


class TestDocxFrontmatter:
    """Frontmatter composition verification for DOCX files."""

    def test_has_format_field(self, docx_simple: Path, tmp_path: Path):
        output = tmp_path / "fm_test.md"
        convert_file(docx_simple, output_path=output)
        content = output.read_text(encoding="utf-8")
        assert "format:" in content

    def test_has_extracted_at(self, docx_simple: Path, tmp_path: Path):
        output = tmp_path / "fm_test.md"
        convert_file(docx_simple, output_path=output)
        content = output.read_text(encoding="utf-8")
        assert "extracted_at:" in content
