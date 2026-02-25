"""XLSX format snapshot and quality tests."""

from pathlib import Path

from tests.conftest import normalize_markdown
from to_markdown.core.extraction import extract_file
from to_markdown.core.pipeline import convert_file


class TestXlsxSnapshots:
    """Snapshot tests capturing full pipeline output for XLSX files."""

    def test_simple(self, xlsx_simple: Path, snapshot, tmp_path: Path):
        output = tmp_path / "simple.md"
        convert_file(xlsx_simple, output_path=output)
        content = normalize_markdown(output.read_text(encoding="utf-8"))
        assert content == snapshot

    def test_multi_sheet(self, xlsx_multi_sheet: Path, snapshot, tmp_path: Path):
        output = tmp_path / "multi.md"
        convert_file(xlsx_multi_sheet, output_path=output)
        content = normalize_markdown(output.read_text(encoding="utf-8"))
        assert content == snapshot


class TestXlsxQuality:
    """Content quality assertions for XLSX extraction."""

    def test_content_not_empty(self, xlsx_simple: Path):
        result = extract_file(xlsx_simple)
        assert len(result.content.strip()) > 0

    def test_tabular_data_present(self, xlsx_simple: Path):
        result = extract_file(xlsx_simple)
        assert "Product" in result.content
        assert "Widget" in result.content

    def test_all_sheets_represented(self, xlsx_multi_sheet: Path):
        result = extract_file(xlsx_multi_sheet)
        assert "Sales" in result.content
        assert "Expenses" in result.content

    def test_multi_sheet_data_complete(self, xlsx_multi_sheet: Path):
        result = extract_file(xlsx_multi_sheet)
        assert "Revenue" in result.content
        assert "Rent" in result.content


class TestXlsxFrontmatter:
    """Frontmatter composition verification for XLSX files."""

    def test_has_format_field(self, xlsx_simple: Path, tmp_path: Path):
        output = tmp_path / "fm_test.md"
        convert_file(xlsx_simple, output_path=output)
        content = output.read_text(encoding="utf-8")
        assert "format:" in content

    def test_has_extracted_at(self, xlsx_simple: Path, tmp_path: Path):
        output = tmp_path / "fm_test.md"
        convert_file(xlsx_simple, output_path=output)
        content = output.read_text(encoding="utf-8")
        assert "extracted_at:" in content
