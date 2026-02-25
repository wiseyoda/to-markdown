"""Shared test fixtures for to-markdown."""

import re
from pathlib import Path

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
