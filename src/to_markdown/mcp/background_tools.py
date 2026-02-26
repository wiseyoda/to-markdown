"""MCP background task tool handlers (start, status, list, cancel)."""

import contextlib
import json
import logging
import os
import signal
from pathlib import Path

from to_markdown.core.constants import GEMINI_API_KEY_ENV

logger = logging.getLogger(__name__)


def _get_task_store():
    """Get the default TaskStore (lazy import)."""
    from to_markdown.core.tasks import get_default_store

    return get_default_store()


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


def handle_start_conversion(
    file_path: str,
    *,
    clean: bool = False,
    summary: bool = False,
    images: bool = False,
) -> str:
    """Start a background conversion and return task ID immediately."""
    path = Path(file_path)
    if not path.exists():
        msg = f"File or directory not found: {file_path}"
        raise ValueError(msg)

    if clean or summary or images:
        _validate_llm_flags(clean=clean, summary=summary, images=images)

    store = _get_task_store()
    is_batch = path.is_dir()

    command_args = json.dumps({
        "input_path": file_path,
        "output_path": None,
        "force": True,
        "clean": clean,
        "summary": summary,
        "images": images,
        "is_batch": is_batch,
    })

    task = store.create(file_path, command_args=command_args)

    from to_markdown.core.worker import spawn_worker

    spawn_worker(task.id, store)

    lines = [
        f"**Task ID**: {task.id}",
        f"**Status**: {task.status.value}",
        f"**Input**: {file_path}",
        "**Message**: Background conversion started. Use get_task_status to check progress.",
    ]
    return "\n".join(lines)


def handle_get_task_status(task_id: str) -> str:
    """Get status of a background task by ID."""
    store = _get_task_store()
    store.check_orphans()

    task = store.get(task_id)
    if task is None:
        msg = f"Task not found: {task_id}"
        raise ValueError(msg)

    lines = [
        f"**Task ID**: {task.id}",
        f"**Status**: {task.status.value}",
        f"**Input**: {task.input_path}",
    ]
    if task.output_path:
        lines.append(f"**Output**: {task.output_path}")
    if task.duration is not None:
        lines.append(f"**Duration**: {task.duration:.1f}s")
    if task.error:
        lines.append(f"**Error**: {task.error}")

    return "\n".join(lines)


def handle_list_tasks() -> str:
    """List all recent background tasks."""
    store = _get_task_store()
    store.check_orphans()

    tasks = store.list()
    if not tasks:
        return "No background tasks found."

    lines = [f"**Total tasks**: {len(tasks)}", ""]
    for task in tasks:
        input_name = Path(task.input_path).name
        duration = f"{task.duration:.1f}s" if task.duration is not None else "-"
        lines.append(f"- **{task.id}** | {task.status.value} | {input_name} | {duration}")

    return "\n".join(lines)


def handle_cancel_task(task_id: str) -> str:
    """Cancel a running background task."""
    store = _get_task_store()
    task = store.get(task_id)

    if task is None:
        msg = f"Task not found: {task_id}"
        raise ValueError(msg)

    if task.is_done:
        return f"Task {task.id} already {task.status.value}"

    if task.pid is not None:
        with contextlib.suppress(OSError, ProcessLookupError):
            os.kill(task.pid, signal.SIGTERM)

    from to_markdown.core.tasks import TaskStatus, _now_iso

    store.update(
        task.id,
        status=TaskStatus.CANCELLED.value,
        completed_at=_now_iso(),
    )
    return f"Cancelled task {task.id}"
