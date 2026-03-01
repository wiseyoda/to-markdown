"""CLI handlers for background processing flags (--background, --status, --cancel)."""

import contextlib
import json
import logging
import os
import signal
from pathlib import Path

import typer

from to_markdown.core.constants import (
    APP_NAME,
    EXIT_BACKGROUND,
    EXIT_ERROR,
    EXIT_SUCCESS,
    STATUS_COL_ID_WIDTH,
    STATUS_COL_INPUT_WIDTH,
    STATUS_COL_STATUS_WIDTH,
    STATUS_TABLE_SEP_LENGTH,
    TASK_RETENTION_HOURS,
)
from to_markdown.core.display import is_glob_pattern

logger = logging.getLogger(APP_NAME)


def get_store():
    """Get the default TaskStore (lazy import)."""
    from to_markdown.core.tasks import get_default_store

    return get_default_store()


def run_maintenance(store) -> None:
    """Run orphan check and cleanup on the task store."""
    store.check_orphans()
    store.cleanup(max_age_hours=TASK_RETENTION_HOURS)


def handle_status(status_id: str, store) -> None:
    """Handle --status flag."""
    run_maintenance(store)

    if status_id == "all":
        tasks = store.list()
        if not tasks:
            typer.echo("No tasks found.")
            raise typer.Exit(EXIT_SUCCESS)

        typer.echo(
            f"{'ID':<{STATUS_COL_ID_WIDTH}} {'Status':<{STATUS_COL_STATUS_WIDTH}} "
            f"{'Input':<{STATUS_COL_INPUT_WIDTH}} {'Duration'}"
        )
        typer.echo("-" * STATUS_TABLE_SEP_LENGTH)
        for task in tasks:
            input_name = Path(task.input_path).name
            duration = f"{task.duration:.1f}s" if task.duration is not None else "-"
            typer.echo(
                f"{task.id:<{STATUS_COL_ID_WIDTH}} {task.status.value:<{STATUS_COL_STATUS_WIDTH}} "
                f"{input_name:<{STATUS_COL_INPUT_WIDTH}} {duration}"
            )
        raise typer.Exit(EXIT_SUCCESS)

    task = store.get(status_id)
    if task is None:
        typer.echo(f"Task not found: {status_id}")
        raise typer.Exit(EXIT_ERROR)

    typer.echo(f"Task {task.id}")
    typer.echo(f"  Status:  {task.status.value}")
    typer.echo(f"  Input:   {task.input_path}")
    if task.output_path:
        typer.echo(f"  Output:  {task.output_path}")
    if task.started_at:
        typer.echo(f"  Started: {task.started_at}")
    if task.duration is not None:
        typer.echo(f"  Duration: {task.duration:.1f}s")
    if task.error:
        typer.echo(f"  Error:   {task.error}")
    raise typer.Exit(EXIT_SUCCESS)


def handle_cancel(cancel_id: str, store) -> None:
    """Handle --cancel flag."""
    run_maintenance(store)

    task = store.get(cancel_id)
    if task is None:
        typer.echo(f"Task not found: {cancel_id}")
        raise typer.Exit(EXIT_ERROR)

    if task.is_done:
        typer.echo(f"Task {task.id} already {task.status.value}")
        raise typer.Exit(EXIT_SUCCESS)

    if task.pid is not None:
        with contextlib.suppress(OSError, ProcessLookupError):
            os.kill(task.pid, signal.SIGTERM)

    from to_markdown.core.tasks import TaskStatus, _now_iso

    store.update(
        task.id,
        status=TaskStatus.CANCELLED.value,
        completed_at=_now_iso(),
    )
    typer.echo(f"Cancelled task {task.id}")
    raise typer.Exit(EXIT_SUCCESS)


def handle_background(
    input_path: str,
    output: Path | None,
    *,
    force: bool,
    clean: bool,
    summary: bool,
    images_flag: bool,
    no_sanitize: bool = False,
    store,
) -> None:
    """Handle --background flag."""
    run_maintenance(store)

    resolved = Path(input_path)
    is_batch = resolved.is_dir() or is_glob_pattern(input_path)

    command_args = json.dumps(
        {
            "input_path": input_path,
            "output_path": str(output) if output else None,
            "force": force,
            "clean": clean,
            "summary": summary,
            "images": images_flag,
            "sanitize": not no_sanitize,
            "is_batch": is_batch,
        }
    )

    task = store.create(input_path, command_args=command_args)

    from to_markdown.core.worker import spawn_worker

    spawn_worker(task.id, store)
    typer.echo(task.id)
    raise typer.Exit(EXIT_BACKGROUND)


def handle_worker(task_id: str, store) -> None:
    """Handle --_worker flag (internal, hidden)."""
    from to_markdown.core.worker import run_worker

    run_worker(task_id, store)
    raise typer.Exit(EXIT_SUCCESS)
