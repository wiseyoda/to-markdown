"""Background worker: spawn detached subprocesses and execute conversions."""

import json
import logging
import os
import signal
import subprocess
import sys
from pathlib import Path

from to_markdown.core.constants import (
    TASK_STATUS_CANCELLED,
    TASK_STATUS_COMPLETED,
    TASK_STATUS_FAILED,
    TASK_STATUS_RUNNING,
    WORKER_FLAG,
)
from to_markdown.core.tasks import TaskStore, _now_iso

logger = logging.getLogger(__name__)


def spawn_worker(task_id: str, store: TaskStore) -> int:
    """Spawn a detached subprocess to execute a background conversion.

    Args:
        task_id: The task ID to process.
        store: TaskStore instance for PID update.

    Returns:
        PID of the spawned worker process.
    """
    log_file = store.log_dir / f"{task_id}.log"
    log_fd = log_file.open("w")

    cmd = [sys.executable, "-m", "to_markdown.cli", WORKER_FLAG, task_id]

    env = os.environ.copy()
    env["TO_MARKDOWN_DATA_DIR"] = str(store.db_path.parent)

    process = subprocess.Popen(
        cmd,
        start_new_session=True,
        stdout=log_fd,
        stderr=log_fd,
        env=env,
    )

    store.update(task_id, pid=process.pid)

    return process.pid


def run_worker(task_id: str, store: TaskStore) -> None:
    """Execute a conversion task in the worker subprocess.

    This is the entry point called by the hidden --_worker CLI flag.
    It reads the task from the store, runs the conversion, and updates
    the result.

    Args:
        task_id: The task ID to process.
        store: TaskStore instance for status updates.
    """
    task = store.get(task_id)
    if task is None:
        logger.error("Task %s not found", task_id)
        return

    # Register SIGTERM handler for graceful cancellation
    def _handle_sigterm(_signum: int, _frame: object) -> None:
        store.update(
            task_id,
            status=TASK_STATUS_CANCELLED,
            completed_at=_now_iso(),
        )
        raise SystemExit(1)

    signal.signal(signal.SIGTERM, _handle_sigterm)

    # Mark as running
    store.update(
        task_id,
        status=TASK_STATUS_RUNNING,
        started_at=_now_iso(),
    )

    # Parse command args
    args = json.loads(task.command_args) if task.command_args else {}

    try:
        is_batch = args.get("is_batch", False)
        input_path = args.get("input_path", task.input_path)

        if is_batch:
            from to_markdown.core.batch import convert_batch, discover_files

            source = Path(input_path)
            files = discover_files(source)
            result = convert_batch(
                files,
                output_dir=Path(args["output_path"]) if args.get("output_path") else None,
                batch_root=source,
                force=args.get("force", False),
                clean=args.get("clean", False),
                summary=args.get("summary", False),
                images=args.get("images", False),
                sanitize=args.get("sanitize", True),
                quiet=True,
            )
            output_str = f"{len(result.succeeded)} succeeded, {len(result.failed)} failed"
            store.update(
                task_id,
                status=TASK_STATUS_COMPLETED,
                output_path=output_str,
                completed_at=_now_iso(),
            )
        else:
            from to_markdown.core.pipeline import convert_file

            result_path = convert_file(
                Path(input_path),
                output_path=Path(args["output_path"]) if args.get("output_path") else None,
                force=args.get("force", False),
                clean=args.get("clean", False),
                summary=args.get("summary", False),
                images=args.get("images", False),
                sanitize=args.get("sanitize", True),
            )
            store.update(
                task_id,
                status=TASK_STATUS_COMPLETED,
                output_path=str(result_path),
                completed_at=_now_iso(),
            )

    except SystemExit:
        raise
    except Exception as exc:
        store.update(
            task_id,
            status=TASK_STATUS_FAILED,
            error=str(exc),
            completed_at=_now_iso(),
        )
