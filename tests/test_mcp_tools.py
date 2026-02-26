"""Tests for MCP tool handlers (mcp/tools.py)."""

from pathlib import Path
from unittest.mock import patch

import pytest

from to_markdown.core.constants import MAX_MCP_OUTPUT_CHARS
from to_markdown.mcp.tools import (
    handle_convert_batch,
    handle_convert_file,
    handle_get_status,
    handle_list_formats,
)


class TestHandleConvertFile:
    """Tests for handle_convert_file."""

    def test_success_returns_structured_response(self, sample_text_file: Path):
        result = handle_convert_file(str(sample_text_file))
        assert "**Source**: sample.txt" in result
        assert "**Format**: txt" in result
        assert "**Characters**:" in result
        assert "---" in result
        assert "Hello" in result

    def test_file_not_found(self, tmp_path: Path):
        missing = str(tmp_path / "nonexistent.pdf")
        with pytest.raises(ValueError, match="File not found"):
            handle_convert_file(missing)

    def test_not_a_file(self, tmp_path: Path):
        with pytest.raises(ValueError, match="Not a file"):
            handle_convert_file(str(tmp_path))

    def test_output_truncation(self, sample_text_file: Path):
        huge_content = "x" * (MAX_MCP_OUTPUT_CHARS + 1_000)
        with patch(
            "to_markdown.core.pipeline.convert_to_string",
            return_value=huge_content,
        ):
            result = handle_convert_file(str(sample_text_file))
            assert "truncated" in result.lower()
            assert str(MAX_MCP_OUTPUT_CHARS) in result.replace(",", "")

    def test_features_listed_in_response(
        self, sample_text_file: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        with (
            patch("to_markdown.mcp.tools._check_llm_available", return_value=True),
            patch(
                "to_markdown.core.pipeline.convert_to_string",
                return_value="---\ncontent\n",
            ),
        ):
            result = handle_convert_file(str(sample_text_file), clean=True, summary=True)
            assert "**Features**: clean, summary" in result

    def test_llm_without_sdk_raises(self, sample_text_file: Path):
        with (
            patch("to_markdown.mcp.tools._check_llm_available", return_value=False),
            pytest.raises(ValueError, match="LLM extras"),
        ):
            handle_convert_file(str(sample_text_file), clean=True)

    def test_llm_without_api_key_raises(
        self, sample_text_file: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        with (
            patch("to_markdown.mcp.tools._check_llm_available", return_value=True),
            pytest.raises(ValueError, match="GEMINI_API_KEY"),
        ):
            handle_convert_file(str(sample_text_file), summary=True)


class TestHandleConvertBatch:
    """Tests for handle_convert_batch."""

    def test_success_with_mixed_results(self, batch_dir: Path):
        result = handle_convert_batch(str(batch_dir))
        assert "**Directory**:" in result
        assert "**Total files**:" in result
        assert "**Succeeded**:" in result

    def test_directory_not_found(self, tmp_path: Path):
        missing = str(tmp_path / "nonexistent_dir")
        with pytest.raises(ValueError, match="Directory not found"):
            handle_convert_batch(missing)

    def test_not_a_directory(self, sample_text_file: Path):
        with pytest.raises(ValueError, match="Not a directory"):
            handle_convert_batch(str(sample_text_file))

    def test_empty_directory(self, empty_dir: Path):
        with pytest.raises(ValueError, match="No supported files"):
            handle_convert_batch(str(empty_dir))

    def test_non_recursive(self, batch_dir: Path):
        result = handle_convert_batch(str(batch_dir), recursive=False)
        assert "**Recursive**: False" in result


class TestHandleListFormats:
    """Tests for handle_list_formats."""

    def test_returns_format_description(self):
        result = handle_list_formats()
        assert "PDF" in result
        assert "DOCX" in result
        assert "PNG" in result
        assert "Kreuzberg" in result

    def test_returns_string(self):
        assert isinstance(handle_list_formats(), str)


class TestHandleGetStatus:
    """Tests for handle_get_status."""

    def test_returns_version(self):
        from to_markdown import __version__

        result = handle_get_status()
        assert __version__ in result

    def test_returns_python_version(self):
        result = handle_get_status()
        assert "**Python**:" in result

    def test_llm_available_with_key(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        with patch("to_markdown.mcp.tools._check_llm_available", return_value=True):
            result = handle_get_status()
            assert "Available" in result

    def test_llm_not_installed(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        with patch("to_markdown.mcp.tools._check_llm_available", return_value=False):
            result = handle_get_status()
            assert "Not available" in result

    def test_llm_installed_no_key(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        with patch("to_markdown.mcp.tools._check_llm_available", return_value=True):
            result = handle_get_status()
            assert "GEMINI_API_KEY not set" in result
