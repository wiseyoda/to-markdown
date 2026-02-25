"""Kreuzberg adapter: thin wrapper isolating the project from Kreuzberg API changes."""

from dataclasses import dataclass, field
from pathlib import Path

from kreuzberg import ExtractionConfig, extract_file_sync
from kreuzberg.exceptions import KreuzbergError, ValidationError


class ExtractionError(Exception):
    """Raised when document extraction fails."""


class UnsupportedFormatError(ExtractionError):
    """Raised when the file format is not supported by Kreuzberg."""


@dataclass(frozen=True)
class ExtractionResult:
    """Structured result from Kreuzberg extraction."""

    content: str
    metadata: dict = field(default_factory=dict)
    tables: list = field(default_factory=list)


_DEFAULT_CONFIG = ExtractionConfig(
    output_format="markdown",
    enable_quality_processing=True,
)


def extract_file(file_path: Path) -> ExtractionResult:
    """Extract content and metadata from a file via Kreuzberg.

    Args:
        file_path: Path to the file to extract.

    Returns:
        ExtractionResult with content, metadata, and tables.

    Raises:
        FileNotFoundError: If the file does not exist.
        UnsupportedFormatError: If Kreuzberg cannot handle the file format.
        ExtractionError: If extraction fails for other reasons.
    """
    path = Path(file_path)
    if not path.exists():
        msg = f"File not found: {path}"
        raise FileNotFoundError(msg)

    try:
        result = extract_file_sync(str(path), config=_DEFAULT_CONFIG)
    except ValidationError as exc:
        msg = f"Unsupported format: {path.suffix or 'unknown'}"
        raise UnsupportedFormatError(msg) from exc
    except KreuzbergError as exc:
        msg = f"Extraction failed for {path.name}: {exc}"
        raise ExtractionError(msg) from exc

    return ExtractionResult(
        content=result.content,
        metadata=result.metadata if isinstance(result.metadata, dict) else {},
        tables=result.tables if isinstance(result.tables, list) else [],
    )
