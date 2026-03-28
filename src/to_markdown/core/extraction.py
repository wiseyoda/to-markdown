"""Kreuzberg adapter: thin wrapper isolating the project from Kreuzberg API changes."""

import logging
from dataclasses import dataclass, field
from pathlib import Path

from kreuzberg import ExtractionConfig, ImageExtractionConfig, extract_file_sync
from kreuzberg.exceptions import KreuzbergError, ValidationError

from to_markdown.core.constants import OCR_MIN_CONTENT_LENGTH, OCR_QUALITY_THRESHOLD

logger = logging.getLogger(__name__)


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

    # Auto-retry with OCR if PDF extraction returned sparse content
    if _is_sparse_pdf_extraction(result, path):
        logger.warning(
            "Sparse PDF extraction detected (quality=%.1f, length=%d); retrying with OCR",
            _extraction_quality(result),
            len(result.content.strip()),
        )
        retry_result = _retry_with_ocr(path, extract_images=extract_images)
        if retry_result is not None and len(retry_result.content.strip()) > len(
            result.content.strip()
        ):
            result = retry_result
            metadata = result.metadata if isinstance(result.metadata, dict) else {}
            metadata = {**metadata, "ocr_fallback": True}
            return ExtractionResult(
                content=result.content,
                metadata=metadata,
                tables=result.tables if isinstance(result.tables, list) else [],
                images=_extract_images_list(result, extract_images),
            )

    return ExtractionResult(
        content=result.content,
        metadata=result.metadata if isinstance(result.metadata, dict) else {},
        tables=result.tables if isinstance(result.tables, list) else [],
        images=_extract_images_list(result, extract_images),
    )


def _extraction_quality(result: object) -> float:
    """Get quality score from a Kreuzberg result, defaulting to 1.0."""
    metadata = result.metadata if isinstance(result.metadata, dict) else {}
    return metadata.get("quality_score", 1.0)


def _is_sparse_pdf_extraction(result: object, path: Path) -> bool:
    """Detect when PDF text extraction returned too little content.

    Returns True if the file is a PDF and either the quality score is below
    threshold or the extracted content is shorter than the minimum length.
    """
    if path.suffix.lower() != ".pdf":
        return False
    if _extraction_quality(result) < OCR_QUALITY_THRESHOLD:
        return True
    return len(result.content.strip()) < OCR_MIN_CONTENT_LENGTH


def _retry_with_ocr(path: Path, *, extract_images: bool = False) -> object | None:
    """Retry extraction with force_ocr=True. Returns raw Kreuzberg result or None."""
    retry_config = ExtractionConfig(
        output_format="markdown",
        enable_quality_processing=True,
        force_ocr=True,
        images=ImageExtractionConfig() if extract_images else None,
    )
    try:
        return extract_file_sync(str(path), config=retry_config)
    except KreuzbergError as exc:
        logger.warning("OCR retry failed: %s", exc)
        return None


def _extract_images_list(result: object, extract_images: bool) -> list[dict]:
    """Build normalized image dicts from a Kreuzberg extraction result."""
    if not extract_images or not hasattr(result, "images") or not result.images:
        return []
    return [
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
