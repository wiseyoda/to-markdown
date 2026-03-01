"""Build markdown content from extracted file data (sync and async)."""

import asyncio
import logging
from pathlib import Path

from to_markdown.core.extraction import extract_file
from to_markdown.core.frontmatter import compose_frontmatter

logger = logging.getLogger(__name__)


def build_content(
    input_path: Path,
    *,
    clean: bool = False,
    summary: bool = False,
    images: bool = False,
    sanitize: bool = True,
) -> str:
    """Build markdown content via async pipeline with sync boundary.

    Delegates to build_content_async() and runs the event loop here.
    This is the ONLY place asyncio.run() is called in the pipeline.
    """
    return asyncio.run(
        build_content_async(
            input_path,
            clean=clean,
            summary=summary,
            images=images,
            sanitize=sanitize,
        )
    )


async def build_content_async(
    input_path: Path,
    *,
    sanitize: bool = True,
    clean: bool = False,
    summary: bool = False,
    images: bool = False,
) -> str:
    """Build markdown content with parallel LLM features.

    Clean and images run concurrently via asyncio.gather() when both are enabled.
    Summary runs after clean (depends on cleaned content).
    """
    logger.info("Extracting: %s", input_path.name)
    result = extract_file(input_path, extract_images=images)

    content = result.content
    format_type = result.metadata.get("format_type", input_path.suffix.lstrip("."))

    # Sanitize (sync, fast -- character-level filtering)
    sanitized = False
    if sanitize:
        from to_markdown.core.sanitize import sanitize_content

        sanitize_result = sanitize_content(content)
        content = sanitize_result.content
        sanitized = sanitize_result.was_modified

    logger.info("Composing frontmatter")
    frontmatter = compose_frontmatter(result.metadata, input_path, sanitized=sanitized)

    # Parallel LLM features: clean + images can run concurrently
    summary_section = ""
    image_section = ""
    cleaned_content = content

    parallel_tasks: list = []
    task_labels: list[str] = []

    if clean:
        logger.info("Cleaning content via LLM")
        from to_markdown.smart.clean import clean_content_async

        parallel_tasks.append(clean_content_async(content, format_type))
        task_labels.append("clean")

    if images and result.images:
        logger.info("Describing %d images via LLM", len(result.images))
        from to_markdown.smart.images import describe_images_async

        parallel_tasks.append(describe_images_async(result.images))
        task_labels.append("images")

    if parallel_tasks:
        results = await asyncio.gather(*parallel_tasks)
        for label, res in zip(task_labels, results, strict=True):
            if label == "clean" and res is not None:
                cleaned_content = res
            elif label == "images" and res:
                image_section = "\n" + res

    # Summary depends on cleaned content (must run after clean)
    if summary:
        logger.info("Generating summary via LLM")
        from to_markdown.smart.summary import format_summary_section, summarize_content_async

        summary_text = await summarize_content_async(cleaned_content, format_type)
        if summary_text:
            summary_section = format_summary_section(summary_text) + "\n"

    # Assemble: frontmatter + [summary] + content + [images]
    markdown = frontmatter + "\n"
    if summary_section:
        markdown += summary_section
    markdown += cleaned_content
    if image_section:
        markdown += image_section

    return markdown
