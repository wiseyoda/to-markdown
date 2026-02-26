"""MCP tool handler implementations (pure business logic, no MCP decorators)."""

import logging
import os
import sys
from pathlib import Path

from to_markdown import __version__
from to_markdown.core.constants import (
    GEMINI_API_KEY_ENV,
    MAX_MCP_OUTPUT_CHARS,
    SUPPORTED_FORMATS_DESCRIPTION,
)

# Re-export background tool handlers for unified import surface
from to_markdown.mcp.background_tools import (  # noqa: F401
    _get_task_store,
    handle_cancel_task,
    handle_get_task_status,
    handle_list_tasks,
    handle_start_conversion,
)

logger = logging.getLogger(__name__)


def handle_convert_file(
    file_path: str,
    *,
    clean: bool = False,
    summary: bool = False,
    images: bool = False,
) -> str:
    """Convert a single file and return structured response with markdown content."""
    path = Path(file_path)
    if not path.exists():
        msg = f"File not found: {file_path}"
        raise ValueError(msg)
    if not path.is_file():
        msg = f"Not a file: {file_path}"
        raise ValueError(msg)

    _validate_llm_flags(clean=clean, summary=summary, images=images)

    from to_markdown.core.pipeline import convert_to_string

    content = convert_to_string(path, clean=clean, summary=summary, images=images)

    # Build structured response envelope
    char_count = len(content)
    lines = [
        f"**Source**: {path.name}",
        f"**Format**: {path.suffix.lstrip('.') or 'unknown'}",
        f"**Characters**: {char_count:,}",
    ]

    features = [f for f in ["clean", "summary", "images"] if locals()[f]]
    if features:
        lines.append(f"**Features**: {', '.join(features)}")

    # Truncate if content exceeds limit
    if char_count > MAX_MCP_OUTPUT_CHARS:
        truncated = content[:MAX_MCP_OUTPUT_CHARS]
        lines.append(
            f"\n**Note**: Output truncated ({char_count:,} chars exceeds "
            f"{MAX_MCP_OUTPUT_CHARS:,} limit). Full content available at: "
            f"{path.with_suffix('.md')}"
        )
        lines.append(f"\n---\n\n{truncated}\n\n[... truncated ...]")
    else:
        lines.append(f"\n---\n\n{content}")

    return "\n".join(lines)


def handle_convert_batch(
    directory_path: str,
    *,
    recursive: bool = True,
    clean: bool = False,
    summary: bool = False,
    images: bool = False,
) -> str:
    """Convert all files in a directory and return structured results."""
    path = Path(directory_path)
    if not path.exists():
        msg = f"Directory not found: {directory_path}"
        raise ValueError(msg)
    if not path.is_dir():
        msg = f"Not a directory: {directory_path}"
        raise ValueError(msg)

    _validate_llm_flags(clean=clean, summary=summary, images=images)

    from to_markdown.core.batch import convert_batch, discover_files

    files = discover_files(path, recursive=recursive)
    if not files:
        msg = f"No supported files found in: {directory_path}"
        raise ValueError(msg)

    result = convert_batch(
        files,
        batch_root=path.resolve(),
        force=True,
        clean=clean,
        summary=summary,
        images=images,
        quiet=True,
    )

    # Build structured response
    lines = [
        f"**Directory**: {directory_path}",
        f"**Recursive**: {recursive}",
        f"**Total files**: {result.total}",
        f"**Succeeded**: {len(result.succeeded)}",
        f"**Failed**: {len(result.failed)}",
        f"**Skipped**: {len(result.skipped)}",
    ]

    if result.succeeded:
        lines.append("\n### Succeeded")
        for p in result.succeeded:
            lines.append(f"- {p.name}")

    if result.failed:
        lines.append("\n### Failed")
        for p, error in result.failed:
            lines.append(f"- {p.name}: {error}")

    if result.skipped:
        lines.append("\n### Skipped")
        for p, reason in result.skipped:
            lines.append(f"- {p.name}: {reason}")

    return "\n".join(lines)


def handle_list_formats() -> str:
    """Return supported file formats description."""
    return SUPPORTED_FORMATS_DESCRIPTION


def handle_get_status() -> str:
    """Return tool version and system status."""
    llm_available = _check_llm_available()
    api_key_set = bool(os.environ.get(GEMINI_API_KEY_ENV))

    lines = [
        f"**Version**: {__version__}",
        f"**Python**: {sys.version.split()[0]}",
        f"**LLM SDK installed**: {llm_available}",
        f"**GEMINI_API_KEY set**: {api_key_set}",
    ]

    if llm_available and api_key_set:
        lines.append("**Smart features**: Available (--clean, --summary, --images)")
    elif llm_available:
        lines.append(
            "**Smart features**: SDK installed but GEMINI_API_KEY not set. "
            f"Set {GEMINI_API_KEY_ENV} environment variable to enable."
        )
    else:
        lines.append("**Smart features**: Not available. Install with: uv sync --extra llm")

    return "\n".join(lines)


def _check_llm_available() -> bool:
    """Check if google-genai SDK is importable."""
    try:
        import google.genai  # noqa: F401

        return True
    except ImportError:
        return False


def _validate_llm_flags(*, clean: bool, summary: bool, images: bool) -> None:
    """Validate LLM flags are usable."""
    if not (clean or summary or images):
        return

    if not _check_llm_available():
        msg = (
            "Smart features (clean, summary, images) require the LLM extras. "
            "Install with: uv sync --extra llm"
        )
        raise ValueError(msg)

    if not os.environ.get(GEMINI_API_KEY_ENV):
        msg = (
            f"Smart features require {GEMINI_API_KEY_ENV} to be set. "
            f"Export it or add it to a .env file."
        )
        raise ValueError(msg)
