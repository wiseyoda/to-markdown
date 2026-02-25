"""Shared test fixtures for to-markdown."""

from pathlib import Path

import pytest


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
