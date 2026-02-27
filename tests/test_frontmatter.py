"""Tests for YAML frontmatter composition (core/frontmatter.py)."""

from pathlib import Path

import yaml

from to_markdown.core.frontmatter import compose_frontmatter


class TestFullMetadata:
    """Tests with all metadata fields present."""

    def test_all_fields_present(self, tmp_path: Path):
        metadata = {
            "title": "Test Document",
            "authors": ["Alice", "Bob"],
            "creation_date": "2026-01-15",
            "page_count": 42,
            "word_count": 1500,
            "format_type": "pdf",
        }
        result = compose_frontmatter(metadata, tmp_path / "test.pdf")
        parsed = _parse_frontmatter(result)

        assert parsed["title"] == "Test Document"
        assert parsed["author"] == "Alice, Bob"
        assert parsed["created"] == "2026-01-15"
        assert parsed["pages"] == 42
        assert parsed["words"] == 1500
        assert parsed["format"] == "pdf"
        assert "extracted_at" in parsed

    def test_single_author(self, tmp_path: Path):
        metadata = {"authors": "Jane Doe", "format_type": "docx"}
        result = compose_frontmatter(metadata, tmp_path / "test.docx")
        parsed = _parse_frontmatter(result)
        assert parsed["author"] == "Jane Doe"


class TestPartialMetadata:
    """Tests with some metadata fields missing."""

    def test_skips_missing_fields(self, tmp_path: Path):
        metadata = {"format_type": "text", "word_count": 100}
        result = compose_frontmatter(metadata, tmp_path / "test.txt")
        parsed = _parse_frontmatter(result)

        assert "title" not in parsed
        assert "author" not in parsed
        assert "created" not in parsed
        assert "pages" not in parsed
        assert parsed["words"] == 100
        assert parsed["format"] == "text"


class TestEmptyMetadata:
    """Tests with empty or minimal metadata."""

    def test_empty_metadata_has_format_and_extracted_at(self, tmp_path: Path):
        result = compose_frontmatter({}, tmp_path / "test.txt")
        parsed = _parse_frontmatter(result)

        assert parsed["format"] == "txt"
        assert "extracted_at" in parsed
        assert len(parsed) == 2

    def test_format_falls_back_to_extension(self, tmp_path: Path):
        result = compose_frontmatter({}, tmp_path / "document.pdf")
        parsed = _parse_frontmatter(result)
        assert parsed["format"] == "pdf"


class TestSpecialCharacters:
    """Tests with special characters in metadata."""

    def test_title_with_special_chars(self, tmp_path: Path):
        metadata = {"title": "Test: A 'Special' Document & More", "format_type": "text"}
        result = compose_frontmatter(metadata, tmp_path / "test.txt")
        parsed = _parse_frontmatter(result)
        assert parsed["title"] == "Test: A 'Special' Document & More"

    def test_author_with_unicode(self, tmp_path: Path):
        metadata = {"authors": ["Jose Garcia"], "format_type": "text"}
        result = compose_frontmatter(metadata, tmp_path / "test.txt")
        parsed = _parse_frontmatter(result)
        assert "Garcia" in parsed["author"]


class TestSanitizedField:
    """Tests for the sanitized field in frontmatter."""

    def test_frontmatter_sanitized_true(self, tmp_path: Path):
        metadata = {"format_type": "pdf"}
        result = compose_frontmatter(metadata, tmp_path / "test.pdf", sanitized=True)
        parsed = _parse_frontmatter(result)
        assert parsed["sanitized"] is True

    def test_frontmatter_sanitized_false_by_default(self, tmp_path: Path):
        metadata = {"format_type": "pdf"}
        result = compose_frontmatter(metadata, tmp_path / "test.pdf")
        parsed = _parse_frontmatter(result)
        assert "sanitized" not in parsed


class TestDelimiters:
    """Tests for YAML frontmatter delimiter format."""

    def test_starts_with_delimiter(self, tmp_path: Path):
        result = compose_frontmatter({}, tmp_path / "test.txt")
        assert result.startswith("---\n")

    def test_ends_with_delimiter(self, tmp_path: Path):
        result = compose_frontmatter({}, tmp_path / "test.txt")
        assert result.endswith("---\n")

    def test_valid_yaml_between_delimiters(self, tmp_path: Path):
        metadata = {"title": "Test", "format_type": "text"}
        result = compose_frontmatter(metadata, tmp_path / "test.txt")
        # Strip delimiters and parse
        yaml_content = result.strip().removeprefix("---").removesuffix("---").strip()
        parsed = yaml.safe_load(yaml_content)
        assert isinstance(parsed, dict)
        assert parsed["title"] == "Test"


def _parse_frontmatter(frontmatter: str) -> dict:
    """Parse YAML frontmatter string, stripping delimiters."""
    content = frontmatter.strip()
    assert content.startswith("---")
    assert content.endswith("---")
    yaml_body = content.removeprefix("---").removesuffix("---").strip()
    return yaml.safe_load(yaml_body)
