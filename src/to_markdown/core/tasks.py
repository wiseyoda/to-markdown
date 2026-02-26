"""Background task lifecycle management with SQLite store."""

import os
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path

from to_markdown.core.constants import (
    TASK_DB_FILENAME,
    TASK_ID_LENGTH,
    TASK_LIST_MAX_RESULTS,
    TASK_LOG_DIR,
    TASK_STATUS_CANCELLED,
    TASK_STATUS_COMPLETED,
    TASK_STATUS_FAILED,
    TASK_STATUS_PENDING,
    TASK_STATUS_RUNNING,
    TASK_STORE_DIR,
)


class TaskStatus(Enum):
    """Valid states for a background task."""

    PENDING = TASK_STATUS_PENDING
    RUNNING = TASK_STATUS_RUNNING
    COMPLETED = TASK_STATUS_COMPLETED
    FAILED = TASK_STATUS_FAILED
    CANCELLED = TASK_STATUS_CANCELLED


# Terminal states that indicate a task is done
_DONE_STATUSES = frozenset({TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED})

# States eligible for cleanup (not pending or running)
_CLEANABLE_STATUSES = frozenset(
    {
        TaskStatus.COMPLETED,
        TaskStatus.FAILED,
        TaskStatus.CANCELLED,
    }
)


@dataclass
class Task:
    """A background conversion task."""

    id: str
    status: TaskStatus
    input_path: str
    created_at: str
    output_path: str | None = None
    command_args: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    error: str | None = None
    pid: int | None = None

    @property
    def is_done(self) -> bool:
        """Whether this task has reached a terminal state."""
        return self.status in _DONE_STATUSES

    @property
    def duration(self) -> float | None:
        """Duration in seconds, or None if not started/completed."""
        if self.started_at is None or self.completed_at is None:
            return None
        start = datetime.fromisoformat(self.started_at)
        end = datetime.fromisoformat(self.completed_at)
        return (end - start).total_seconds()


def _generate_task_id() -> str:
    """Generate a short hex task ID from UUID4."""
    return uuid.uuid4().hex[:TASK_ID_LENGTH]


def _now_iso() -> str:
    """Current UTC time as ISO 8601 string."""
    return datetime.now(UTC).isoformat()


def _pid_is_alive(pid: int) -> bool:
    """Check if a process with the given PID is running."""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):  # fmt: skip
        return False


_CREATE_TABLE_SQL = """\
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'pending',
    input_path TEXT NOT NULL,
    output_path TEXT,
    command_args TEXT,
    created_at TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    error TEXT,
    pid INTEGER
)"""


class TaskStore:
    """SQLite-backed task persistence."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._ensure_data_dir()
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute(_CREATE_TABLE_SQL)
        self._conn.commit()

    def _ensure_data_dir(self) -> None:
        """Create data directory and log subdirectory."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        (self.db_path.parent / TASK_LOG_DIR).mkdir(exist_ok=True)

    @property
    def log_dir(self) -> Path:
        """Path to the log directory."""
        return self.db_path.parent / TASK_LOG_DIR

    def create(self, input_path: str, command_args: str | None = None) -> Task:
        """Create a new pending task."""
        task = Task(
            id=_generate_task_id(),
            status=TaskStatus.PENDING,
            input_path=input_path,
            command_args=command_args,
            created_at=_now_iso(),
        )
        self._conn.execute(
            "INSERT INTO tasks (id, status, input_path, command_args, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (task.id, task.status.value, task.input_path, task.command_args, task.created_at),
        )
        self._conn.commit()
        return task

    def get(self, task_id: str) -> Task | None:
        """Fetch a task by ID, or None if not found."""
        cursor = self._conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_task(row)

    def list(self, limit: int = TASK_LIST_MAX_RESULTS) -> list[Task]:
        """List recent tasks ordered by creation time (newest first)."""
        cursor = self._conn.execute(
            "SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )
        return [self._row_to_task(row) for row in cursor.fetchall()]

    def update(self, task_id: str, **fields: str | int | None) -> None:
        """Update specific fields on a task."""
        if not fields:
            return
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = [*list(fields.values()), task_id]
        self._conn.execute(
            f"UPDATE tasks SET {set_clause} WHERE id = ?",
            values,
        )
        self._conn.commit()

    def delete(self, task_id: str) -> None:
        """Remove a task and its log file."""
        self._conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self._conn.commit()
        log_file = self.log_dir / f"{task_id}.log"
        if log_file.exists():
            log_file.unlink()

    def cleanup(self, max_age_hours: int) -> int:
        """Remove completed/failed/cancelled tasks older than max_age_hours.

        Returns the number of tasks removed.
        """
        # Find old tasks eligible for cleanup
        cleanable = tuple(s.value for s in _CLEANABLE_STATUSES)
        placeholders = ",".join("?" for _ in cleanable)
        cursor = self._conn.execute(
            f"SELECT id FROM tasks WHERE status IN ({placeholders}) AND created_at < ?",
            (*cleanable, _hours_ago_iso(max_age_hours)),
        )
        old_ids = [row[0] for row in cursor.fetchall()]

        if not old_ids:
            return 0

        # Delete log files
        for task_id in old_ids:
            log_file = self.log_dir / f"{task_id}.log"
            if log_file.exists():
                log_file.unlink()

        # Delete from database
        id_placeholders = ",".join("?" for _ in old_ids)
        self._conn.execute(
            f"DELETE FROM tasks WHERE id IN ({id_placeholders})",
            old_ids,
        )
        self._conn.commit()
        return len(old_ids)

    def check_orphans(self) -> int:
        """Detect running tasks with stale PIDs and mark as failed.

        Returns the number of orphaned tasks found.
        """
        cursor = self._conn.execute(
            "SELECT id, pid FROM tasks WHERE status = ?",
            (TaskStatus.RUNNING.value,),
        )
        orphaned = 0
        now = _now_iso()

        for task_id, pid in cursor.fetchall():
            if pid is None or not _pid_is_alive(pid):
                self.update(
                    task_id,
                    status=TaskStatus.FAILED.value,
                    error="Worker process orphaned (PID no longer running)",
                    completed_at=now,
                )
                orphaned += 1

        return orphaned

    def _row_to_task(self, row: tuple) -> Task:
        """Convert a database row to a Task dataclass."""
        return Task(
            id=row[0],
            status=TaskStatus(row[1]),
            input_path=row[2],
            output_path=row[3],
            command_args=row[4],
            created_at=row[5],
            started_at=row[6],
            completed_at=row[7],
            error=row[8],
            pid=row[9],
        )

    def close(self) -> None:
        """Close the database connection."""
        self._conn.close()


def _hours_ago_iso(hours: int) -> str:
    """Return ISO timestamp for N hours ago."""
    from datetime import timedelta

    return (datetime.now(UTC) - timedelta(hours=hours)).isoformat()


# Module-level singleton
_default_store: TaskStore | None = None


def get_default_store() -> TaskStore:
    """Get or create the default TaskStore singleton."""
    global _default_store
    if _default_store is None:
        data_dir = os.environ.get("TO_MARKDOWN_DATA_DIR")
        if data_dir:
            db_path = Path(data_dir) / TASK_DB_FILENAME
        else:
            db_path = Path(TASK_STORE_DIR).expanduser() / TASK_DB_FILENAME
        _default_store = TaskStore(db_path=db_path)
    return _default_store
