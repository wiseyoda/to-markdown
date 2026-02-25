"""HTML format snapshot and quality tests."""

from pathlib import Path

from tests.conftest import normalize_markdown
from to_markdown.core.extraction import extract_file
from to_markdown.core.pipeline import convert_file


class TestHtmlSnapshots:
    """Snapshot tests capturing full pipeline output for HTML files."""

    def test_simple(self, html_simple: Path, snapshot, tmp_path: Path):
        output = tmp_path / "simple.md"
        convert_file(html_simple, output_path=output)
        content = normalize_markdown(output.read_text(encoding="utf-8"))
        assert content == snapshot

    def test_with_table(self, html_with_table: Path, snapshot, tmp_path: Path):
        output = tmp_path / "table.md"
        convert_file(html_with_table, output_path=output)
        content = normalize_markdown(output.read_text(encoding="utf-8"))
        assert content == snapshot


class TestHtmlQuality:
    """Content quality assertions for HTML extraction."""

    def test_content_not_empty(self, html_simple: Path):
        result = extract_file(html_simple)
        assert len(result.content.strip()) > 0

    def test_heading_preserved(self, html_simple: Path):
        result = extract_file(html_simple)
        assert "Welcome" in result.content

    def test_table_content_present(self, html_with_table: Path):
        result = extract_file(html_with_table)
        assert "Quarter" in result.content
        assert "Revenue" in result.content

    def test_link_text_present(self, html_with_table: Path):
        result = extract_file(html_with_table)
        assert "Example Site" in result.content or "example.com" in result.content

    def test_heading_structure(self, html_with_table: Path):
        result = extract_file(html_with_table)
        assert "Data Report" in result.content
        assert "Summary" in result.content


class TestHtmlFrontmatter:
    """Frontmatter composition verification for HTML files."""

    def test_has_format_field(self, html_simple: Path, tmp_path: Path):
        output = tmp_path / "fm_test.md"
        convert_file(html_simple, output_path=output)
        content = output.read_text(encoding="utf-8")
        assert "format:" in content

    def test_has_title_when_present(self, html_simple: Path):
        result = extract_file(html_simple)
        assert result.metadata.get("title") == "Simple Page"

    def test_has_extracted_at(self, html_simple: Path, tmp_path: Path):
        output = tmp_path / "fm_test.md"
        convert_file(html_simple, output_path=output)
        content = output.read_text(encoding="utf-8")
        assert "extracted_at:" in content
