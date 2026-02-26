"""FastMCP server exposing to-markdown file conversion tools."""

import logging
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from pydantic import Field

from to_markdown.core.constants import MCP_SERVER_INSTRUCTIONS, MCP_SERVER_NAME
from to_markdown.mcp.tools import (
    handle_cancel_task,
    handle_convert_batch,
    handle_convert_file,
    handle_get_status,
    handle_get_task_status,
    handle_list_formats,
    handle_list_tasks,
    handle_start_conversion,
)

logger = logging.getLogger(__name__)

mcp = FastMCP(MCP_SERVER_NAME, instructions=MCP_SERVER_INSTRUCTIONS)


@mcp.tool()
def convert_file(
    file_path: Annotated[str, Field(description="Absolute path to the file to convert")],
    clean: Annotated[
        bool, Field(description="Fix extraction artifacts via LLM (requires GEMINI_API_KEY)")
    ] = False,
    summary: Annotated[
        bool, Field(description="Generate document summary via LLM (requires GEMINI_API_KEY)")
    ] = False,
    images: Annotated[
        bool, Field(description="Describe images via LLM vision (requires GEMINI_API_KEY)")
    ] = False,
) -> str:
    """Convert a single file to LLM-optimized Markdown with YAML frontmatter.

    Extracts text from documents (PDF, DOCX, XLSX, PPTX, HTML, images, and more)
    and produces clean Markdown with metadata frontmatter. Returns the markdown
    content directly.
    """
    try:
        return handle_convert_file(file_path, clean=clean, summary=summary, images=images)
    except ValueError as exc:
        raise ToolError(str(exc)) from exc
    except Exception as exc:
        logger.exception("convert_file failed")
        raise ToolError(f"Conversion failed: {exc}") from exc


@mcp.tool()
def convert_batch(
    directory_path: Annotated[str, Field(description="Absolute path to the directory to convert")],
    recursive: Annotated[bool, Field(description="Scan subdirectories recursively")] = True,
    clean: Annotated[
        bool, Field(description="Fix extraction artifacts via LLM (requires GEMINI_API_KEY)")
    ] = False,
    summary: Annotated[
        bool, Field(description="Generate document summary via LLM (requires GEMINI_API_KEY)")
    ] = False,
    images: Annotated[
        bool, Field(description="Describe images via LLM vision (requires GEMINI_API_KEY)")
    ] = False,
) -> str:
    """Convert all supported files in a directory to Markdown.

    Recursively discovers and converts files, skipping hidden files and unsupported
    formats. Returns a structured summary with per-file results.
    """
    try:
        return handle_convert_batch(
            directory_path,
            recursive=recursive,
            clean=clean,
            summary=summary,
            images=images,
        )
    except ValueError as exc:
        raise ToolError(str(exc)) from exc
    except Exception as exc:
        logger.exception("convert_batch failed")
        raise ToolError(f"Batch conversion failed: {exc}") from exc


@mcp.tool()
def list_formats() -> str:
    """List all file formats supported by to-markdown.

    Returns a categorized list of supported formats including documents,
    spreadsheets, presentations, images, and more.
    """
    return handle_list_formats()


@mcp.tool()
def get_status() -> str:
    """Get to-markdown version and feature availability.

    Returns version info, Python version, and whether LLM-powered smart features
    (clean, summary, images) are available.
    """
    return handle_get_status()


@mcp.tool()
def start_conversion(
    file_path: Annotated[
        str, Field(description="Absolute path to the file or directory to convert")
    ],
    clean: Annotated[
        bool, Field(description="Fix extraction artifacts via LLM (requires GEMINI_API_KEY)")
    ] = False,
    summary: Annotated[
        bool, Field(description="Generate document summary via LLM (requires GEMINI_API_KEY)")
    ] = False,
    images: Annotated[
        bool, Field(description="Describe images via LLM vision (requires GEMINI_API_KEY)")
    ] = False,
) -> str:
    """Start a background file conversion and return a task ID immediately.

    Use this for large files or batch conversions that may take a while.
    Poll with get_task_status to check progress.
    """
    try:
        return handle_start_conversion(
            file_path, clean=clean, summary=summary, images=images,
        )
    except ValueError as exc:
        raise ToolError(str(exc)) from exc
    except Exception as exc:
        logger.exception("start_conversion failed")
        raise ToolError(f"Failed to start conversion: {exc}") from exc


@mcp.tool()
def get_task_status(
    task_id: Annotated[str, Field(description="Task ID returned by start_conversion")],
) -> str:
    """Get the status of a background conversion task.

    Returns task status, input/output paths, duration, and any errors.
    """
    try:
        return handle_get_task_status(task_id)
    except ValueError as exc:
        raise ToolError(str(exc)) from exc
    except Exception as exc:
        logger.exception("get_task_status failed")
        raise ToolError(f"Failed to get task status: {exc}") from exc


@mcp.tool()
def list_tasks() -> str:
    """List all recent background conversion tasks.

    Returns a summary of all tasks from the last 24 hours, including
    their status, input paths, and durations.
    """
    try:
        return handle_list_tasks()
    except Exception as exc:
        logger.exception("list_tasks failed")
        raise ToolError(f"Failed to list tasks: {exc}") from exc


@mcp.tool()
def cancel_task(
    task_id: Annotated[str, Field(description="Task ID to cancel")],
) -> str:
    """Cancel a running background conversion task.

    Sends SIGTERM to the worker process and marks the task as cancelled.
    """
    try:
        return handle_cancel_task(task_id)
    except ValueError as exc:
        raise ToolError(str(exc)) from exc
    except Exception as exc:
        logger.exception("cancel_task failed")
        raise ToolError(f"Failed to cancel task: {exc}") from exc


def run_server() -> None:
    """Start the MCP server on stdio transport."""
    mcp.run(transport="stdio")
