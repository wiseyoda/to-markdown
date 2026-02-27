"""LLM-powered image description via Gemini vision."""

import asyncio
import logging

from google.genai import types

from to_markdown.core.constants import (
    IMAGE_DESCRIPTION_PROMPT,
    IMAGE_DESCRIPTION_TEMPERATURE,
    IMAGE_SECTION_HEADING,
    PARALLEL_LLM_MAX_CONCURRENCY,
)
from to_markdown.smart.llm import LLMError, generate, generate_async

logger = logging.getLogger(__name__)

_MIME_TYPE_MAP = {
    "png": "image/png",
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
    "gif": "image/gif",
    "bmp": "image/bmp",
    "tiff": "image/tiff",
    "tif": "image/tiff",
    "webp": "image/webp",
    # PDF image compression filter names from Kreuzberg
    "dctdecode": "image/jpeg",
    "flatedecode": "image/png",
    "ccittfaxdecode": "image/tiff",
    "jbig2decode": "image/png",
    "jpxdecode": "image/jpeg",
}


def describe_images(images: list[dict]) -> str | None:
    """Describe extracted images via Gemini vision.

    Args:
        images: List of extracted image dicts from Kreuzberg, each with
            keys: data (bytes), format (str), page_number (int), width, height.

    Returns:
        Formatted markdown section with image descriptions, or None if no images
        or all descriptions fail.
    """
    if not images:
        logger.info("No images to describe")
        return None

    descriptions: list[dict] = []
    for i, image in enumerate(images):
        desc = _describe_single_image(image)
        if desc:
            descriptions.append(
                {
                    "index": i + 1,
                    "page": image.get("page_number"),
                    "description": desc,
                }
            )
        else:
            page = image.get("page_number")
            logger.warning("Failed to describe image %d on page %s", i + 1, page)

    if not descriptions:
        logger.warning("All image descriptions failed")
        return None

    return _format_image_section(descriptions)


def _describe_single_image(image: dict) -> str | None:
    """Send a single image to Gemini vision for description.

    Returns:
        Description text, or None on failure.
    """
    mime_type = _image_mime_type(image.get("format", "png"))
    image_part = types.Part.from_bytes(data=image["data"], mime_type=mime_type)

    try:
        return generate(
            [IMAGE_DESCRIPTION_PROMPT, image_part],
            temperature=IMAGE_DESCRIPTION_TEMPERATURE,
        )
    except LLMError as exc:
        logger.debug("Image description failed: %s", exc)
        return None


def _format_image_section(descriptions: list[dict]) -> str:
    """Assemble the image descriptions markdown section."""
    lines = [IMAGE_SECTION_HEADING, ""]
    for desc in descriptions:
        page_info = f" (page {desc['page']})" if desc["page"] else ""
        lines.append(f"### Image {desc['index']}{page_info}")
        lines.append("")
        lines.append(desc["description"])
        lines.append("")
    return "\n".join(lines)


def _image_mime_type(format_str: str) -> str:
    """Convert image format string to MIME type."""
    return _MIME_TYPE_MAP.get(format_str.lower(), f"image/{format_str.lower()}")


async def _describe_single_image_async(
    image: dict,
    semaphore: asyncio.Semaphore,
) -> str | None:
    """Send a single image to Gemini vision async for description."""
    async with semaphore:
        mime_type = _image_mime_type(image.get("format", "png"))
        image_part = types.Part.from_bytes(data=image["data"], mime_type=mime_type)

        try:
            return await generate_async(
                [IMAGE_DESCRIPTION_PROMPT, image_part],
                temperature=IMAGE_DESCRIPTION_TEMPERATURE,
            )
        except LLMError as exc:
            logger.debug("Image description failed: %s", exc)
            return None


async def describe_images_async(images: list[dict]) -> str | None:
    """Describe extracted images via Gemini vision with concurrent API calls.

    Args:
        images: List of extracted image dicts from Kreuzberg.

    Returns:
        Formatted markdown section with image descriptions, or None if no images
        or all descriptions fail.
    """
    if not images:
        logger.info("No images to describe")
        return None

    semaphore = asyncio.Semaphore(PARALLEL_LLM_MAX_CONCURRENCY)
    tasks = [_describe_single_image_async(img, semaphore) for img in images]
    results = await asyncio.gather(*tasks)

    descriptions: list[dict] = []
    for i, desc in enumerate(results):
        if desc:
            descriptions.append(
                {
                    "index": i + 1,
                    "page": images[i].get("page_number"),
                    "description": desc,
                }
            )
        else:
            page = images[i].get("page_number")
            logger.warning("Failed to describe image %d on page %s", i + 1, page)

    if not descriptions:
        logger.warning("All image descriptions failed")
        return None

    return _format_image_section(descriptions)
