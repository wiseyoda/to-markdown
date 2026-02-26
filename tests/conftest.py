"""Shared test fixtures for to-markdown."""

import re
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Pattern matching the dynamic extracted_at timestamp in frontmatter
_TIMESTAMP_PATTERN = re.compile(
    r"extracted_at: '[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z'"
)
# Fixed replacement for snapshot stability
_TIMESTAMP_REPLACEMENT = "extracted_at: '2025-01-01T00:00:00Z'"


def normalize_markdown(content: str) -> str:
    """Replace dynamic extracted_at timestamps with a fixed value for snapshot comparison."""
    return _TIMESTAMP_PATTERN.sub(_TIMESTAMP_REPLACEMENT, content)


@pytest.fixture
def sample_text_file(tmp_path: Path) -> Path:
    """Create a simple text file for testing."""
    file = tmp_path / "sample.txt"
    file.write_text("Hello, this is a test document.\n\nIt has multiple paragraphs.\n")
    return file


@pytest.fixture
def sample_text_content() -> str:
    """The expected content from sample_text_file."""
    return "Hello, this is a test document.\n\nIt has multiple paragraphs.\n"


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    """Create a temporary output directory."""
    out = tmp_path / "output"
    out.mkdir()
    return out


@pytest.fixture
def mock_gemini_client():
    """Mock the Gemini client for LLM tests."""
    mock_client = MagicMock()
    with (
        patch("to_markdown.smart.llm._client", mock_client),
        patch("to_markdown.smart.llm.get_client", return_value=mock_client),
    ):
        yield mock_client


@pytest.fixture
def mock_generate():
    """Mock the generate function with configurable responses."""

    def _make_mock(return_value: str = "Mocked LLM response"):
        return patch("to_markdown.smart.llm.generate", return_value=return_value)

    return _make_mock


@pytest.fixture
def sample_extracted_images() -> list[dict]:
    """Sample extracted images for testing."""
    return [
        {
            "data": b"\x89PNG\r\n\x1a\n" + b"\x00" * 100,
            "format": "png",
            "page_number": 1,
            "width": 200,
            "height": 100,
        },
        {
            "data": b"\xff\xd8\xff\xe0" + b"\x00" * 100,
            "format": "jpeg",
            "page_number": 2,
            "width": 400,
            "height": 300,
        },
    ]
