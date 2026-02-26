"""Kreuzberg adapter: thin wrapper isolating the project from Kreuzberg API changes."""

from dataclasses import dataclass, field
from pathlib import Path

from kreuzberg import ExtractionConfig, ImageExtractionConfig, extract_file_sync
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
    images: list[dict] = field(default_factory=list)


_DEFAULT_CONFIG = ExtractionConfig(
    output_format="markdown",
    enable_quality_processing=True,
)


def extract_file(file_path: Path, *, extract_images: bool = False) -> ExtractionResult:
    """Extract content and metadata from a file via Kreuzberg.

    Args:
        file_path: Path to the file to extract.
        extract_images: If True, also extract images from the document.

    Returns:
        ExtractionResult with content, metadata, tables, and optionally images.

    Raises:
        FileNotFoundError: If the file does not exist.
        UnsupportedFormatError: If Kreuzberg cannot handle the file format.
        ExtractionError: If extraction fails for other reasons.
    """
    path = Path(file_path)
    if not path.exists():
        msg = f"File not found: {path}"
        raise FileNotFoundError(msg)

    config = ExtractionConfig(
        output_format="markdown",
        enable_quality_processing=True,
        images=ImageExtractionConfig() if extract_images else None,
    )

    try:
        result = extract_file_sync(str(path), config=config)
    except ValidationError as exc:
        msg = f"Unsupported format: {path.suffix or 'unknown'}"
        raise UnsupportedFormatError(msg) from exc
    except KreuzbergError as exc:
        msg = f"Extraction failed for {path.name}: {exc}"
        raise ExtractionError(msg) from exc

    images_list: list[dict] = []
    if extract_images and hasattr(result, "images") and result.images:
        images_list = [
            {
                "data": img.data if hasattr(img, "data") else img.get("data", b""),
                "format": img.format if hasattr(img, "format") else img.get("format", "png"),
                "page_number": (
                    img.page_number if hasattr(img, "page_number") else img.get("page_number")
                ),
                "width": img.width if hasattr(img, "width") else img.get("width"),
                "height": img.height if hasattr(img, "height") else img.get("height"),
            }
            for img in result.images
        ]

    return ExtractionResult(
        content=result.content,
        metadata=result.metadata if isinstance(result.metadata, dict) else {},
        tables=result.tables if isinstance(result.tables, list) else [],
        images=images_list,
    )
