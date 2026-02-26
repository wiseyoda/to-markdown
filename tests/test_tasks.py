"""Tests for background task management (core/tasks.py)."""

import os
import sqlite3
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from to_markdown.core.constants import (
    TASK_DB_FILENAME,
    TASK_ID_LENGTH,
    TASK_LIST_MAX_RESULTS,
    TASK_LOG_DIR,
    TASK_RETENTION_HOURS,
    TASK_STATUS_CANCELLED,
    TASK_STATUS_COMPLETED,
    TASK_STATUS_FAILED,
    TASK_STATUS_PENDING,
    TASK_STATUS_RUNNING,
)

# ---- Fixtures ----


@pytest.fixture()
def store_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for TaskStore."""
    d = tmp_path / ".to-markdown"
    d.mkdir()
    return d


@pytest.fixture()
def store(store_dir: Path):
    """Create a TaskStore with a temporary database."""
    from to_markdown.core.tasks import TaskStore

    return TaskStore(db_path=store_dir / TASK_DB_FILENAME)


# ---- T003: Task Dataclass and TaskStatus Enum ----


class TestTaskStatus:
    """Tests for TaskStatus enum."""

    def test_all_status_values_exist(self):
        from to_markdown.core.tasks import TaskStatus

        assert TaskStatus.PENDING.value == TASK_STATUS_PENDING
        assert TaskStatus.RUNNING.value == TASK_STATUS_RUNNING
        assert TaskStatus.COMPLETED.value == TASK_STATUS_COMPLETED
        assert TaskStatus.FAILED.value == TASK_STATUS_FAILED
        assert TaskStatus.CANCELLED.value == TASK_STATUS_CANCELLED

    def test_status_count(self):
        from to_markdown.core.tasks import TaskStatus

        assert len(TaskStatus) == 5


class TestTaskDataclass:
    """Tests for Task dataclass."""

    def test_task_creation_with_required_fields(self):
        from to_markdown.core.tasks import Task, TaskStatus

        task = Task(
            id="a1b2c3d4",
            status=TaskStatus.PENDING,
            input_path="/path/to/file.pdf",
            created_at="2026-02-26T10:00:00",
        )
        assert task.id == "a1b2c3d4"
        assert task.status == TaskStatus.PENDING
        assert task.input_path == "/path/to/file.pdf"
        assert task.created_at == "2026-02-26T10:00:00"

    def test_task_optional_fields_default_none(self):
        from to_markdown.core.tasks import Task, TaskStatus

        task = Task(
            id="a1b2c3d4",
            status=TaskStatus.PENDING,
            input_path="/path/to/file.pdf",
            created_at="2026-02-26T10:00:00",
        )
        assert task.output_path is None
        assert task.command_args is None
        assert task.started_at is None
        assert task.completed_at is None
        assert task.error is None
        assert task.pid is None

    def test_task_duration_none_when_not_started(self):
        from to_markdown.core.tasks import Task, TaskStatus

        task = Task(
            id="a1b2c3d4",
            status=TaskStatus.PENDING,
            input_path="/path/to/file.pdf",
            created_at="2026-02-26T10:00:00",
        )
        assert task.duration is None

    def test_task_duration_calculated_when_completed(self):
        from to_markdown.core.tasks import Task, TaskStatus

        task = Task(
            id="a1b2c3d4",
            status=TaskStatus.COMPLETED,
            input_path="/path/to/file.pdf",
            created_at="2026-02-26T10:00:00",
            started_at="2026-02-26T10:00:01",
            completed_at="2026-02-26T10:00:46",
        )
        assert task.duration is not None
        assert task.duration == pytest.approx(45.0, abs=1.0)

    def test_task_is_done_for_terminal_states(self):
        from to_markdown.core.tasks import Task, TaskStatus

        for status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
            task = Task(
                id="a1b2c3d4",
                status=status,
                input_path="/path/to/file.pdf",
                created_at="2026-02-26T10:00:00",
            )
            assert task.is_done is True

    def test_task_is_done_false_for_active_states(self):
        from to_markdown.core.tasks import Task, TaskStatus

        for status in (TaskStatus.PENDING, TaskStatus.RUNNING):
            task = Task(
                id="a1b2c3d4",
                status=status,
                input_path="/path/to/file.pdf",
                created_at="2026-02-26T10:00:00",
            )
            assert task.is_done is False


# ---- T004: TaskStore SQLite Operations ----


class TestTaskStoreInit:
    """Tests for TaskStore initialization."""

    def test_creates_database_file(self, store_dir: Path):
        from to_markdown.core.tasks import TaskStore

        db_path = store_dir / TASK_DB_FILENAME
        TaskStore(db_path=db_path)
        assert db_path.exists()

    def test_creates_tasks_table(self, store):
        conn = sqlite3.connect(store.db_path)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
        assert cursor.fetchone() is not None
        conn.close()

    def test_wal_mode_enabled(self, store):
        conn = sqlite3.connect(store.db_path)
        cursor = conn.execute("PRAGMA journal_mode")
        mode = cursor.fetchone()[0]
        conn.close()
        assert mode == "wal"

    def test_auto_creates_parent_directories(self, tmp_path: Path):
        from to_markdown.core.tasks import TaskStore

        deep_path = tmp_path / "a" / "b" / "c" / TASK_DB_FILENAME
        store = TaskStore(db_path=deep_path)
        assert deep_path.exists()
        assert store.db_path == deep_path

    def test_creates_log_directory(self, tmp_path: Path):
        from to_markdown.core.tasks import TaskStore

        store_dir = tmp_path / ".to-markdown"
        db_path = store_dir / TASK_DB_FILENAME
        TaskStore(db_path=db_path)
        log_dir = store_dir / TASK_LOG_DIR
        assert log_dir.exists()


class TestTaskStoreCreate:
    """Tests for TaskStore.create()."""

    def test_create_returns_task_with_id(self, store):
        task = store.create("/path/to/file.pdf")
        assert len(task.id) == TASK_ID_LENGTH
        assert all(c in "0123456789abcdef" for c in task.id)

    def test_create_sets_pending_status(self, store):
        from to_markdown.core.tasks import TaskStatus

        task = store.create("/path/to/file.pdf")
        assert task.status == TaskStatus.PENDING

    def test_create_sets_created_at(self, store):
        task = store.create("/path/to/file.pdf")
        assert task.created_at is not None

    def test_create_stores_command_args(self, store):
        args = '{"clean": true, "summary": false}'
        task = store.create("/path/to/file.pdf", command_args=args)
        assert task.command_args == args

    def test_create_unique_ids(self, store):
        ids = {store.create("/path/to/file.pdf").id for _ in range(20)}
        assert len(ids) == 20


class TestTaskStoreGet:
    """Tests for TaskStore.get()."""

    def test_get_existing_task(self, store):
        created = store.create("/path/to/file.pdf")
        fetched = store.get(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.input_path == "/path/to/file.pdf"

    def test_get_nonexistent_returns_none(self, store):
        assert store.get("nonexistent") is None


class TestTaskStoreUpdate:
    """Tests for TaskStore.update()."""

    def test_update_status(self, store):
        from to_markdown.core.tasks import TaskStatus

        task = store.create("/path/to/file.pdf")
        store.update(task.id, status=TaskStatus.RUNNING.value)
        fetched = store.get(task.id)
        assert fetched.status == TaskStatus.RUNNING

    def test_update_multiple_fields(self, store):
        from to_markdown.core.tasks import TaskStatus

        task = store.create("/path/to/file.pdf")
        store.update(
            task.id,
            status=TaskStatus.COMPLETED.value,
            output_path="/path/to/file.md",
            completed_at="2026-02-26T10:01:00",
        )
        fetched = store.get(task.id)
        assert fetched.status == TaskStatus.COMPLETED
        assert fetched.output_path == "/path/to/file.md"
        assert fetched.completed_at == "2026-02-26T10:01:00"

    def test_update_pid(self, store):
        task = store.create("/path/to/file.pdf")
        store.update(task.id, pid=12345)
        fetched = store.get(task.id)
        assert fetched.pid == 12345


class TestTaskStoreList:
    """Tests for TaskStore.list()."""

    def test_list_returns_all_tasks(self, store):
        store.create("/path/to/a.pdf")
        store.create("/path/to/b.pdf")
        store.create("/path/to/c.pdf")
        tasks = store.list()
        assert len(tasks) == 3

    def test_list_ordered_by_created_at_desc(self, store):
        store.create("/path/to/a.pdf")
        time.sleep(0.01)
        store.create("/path/to/b.pdf")
        time.sleep(0.01)
        store.create("/path/to/c.pdf")
        tasks = store.list()
        assert tasks[0].input_path == "/path/to/c.pdf"
        assert tasks[2].input_path == "/path/to/a.pdf"

    def test_list_respects_limit(self, store):
        for i in range(5):
            store.create(f"/path/to/{i}.pdf")
        tasks = store.list(limit=3)
        assert len(tasks) == 3

    def test_list_default_limit(self, store):
        for i in range(5):
            store.create(f"/path/to/{i}.pdf")
        tasks = store.list()
        assert len(tasks) <= TASK_LIST_MAX_RESULTS

    def test_list_empty_store(self, store):
        assert store.list() == []


class TestTaskStoreDelete:
    """Tests for TaskStore.delete()."""

    def test_delete_removes_task(self, store):
        task = store.create("/path/to/file.pdf")
        store.delete(task.id)
        assert store.get(task.id) is None

    def test_delete_removes_log_file(self, store, store_dir: Path):
        task = store.create("/path/to/file.pdf")
        log_dir = store_dir / TASK_LOG_DIR
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"{task.id}.log"
        log_file.write_text("some log output")

        store.delete(task.id)
        assert not log_file.exists()


# ---- T010: Cleanup and Orphan Detection ----


class TestTaskStoreCleanup:
    """Tests for TaskStore.cleanup()."""

    def test_cleanup_removes_old_completed_tasks(self, store):
        from to_markdown.core.tasks import TaskStatus

        task = store.create("/path/to/file.pdf")
        # Manually set created_at to 25 hours ago
        old_time = "2026-02-25T08:00:00"
        store.update(
            task.id,
            status=TaskStatus.COMPLETED.value,
            created_at=old_time,
            completed_at=old_time,
        )
        removed = store.cleanup(max_age_hours=TASK_RETENTION_HOURS)
        assert removed >= 1
        assert store.get(task.id) is None

    def test_cleanup_preserves_recent_tasks(self, store):
        from to_markdown.core.tasks import TaskStatus

        task = store.create("/path/to/file.pdf")
        store.update(task.id, status=TaskStatus.COMPLETED.value)
        removed = store.cleanup(max_age_hours=TASK_RETENTION_HOURS)
        assert removed == 0
        assert store.get(task.id) is not None

    def test_cleanup_preserves_running_tasks(self, store):
        from to_markdown.core.tasks import TaskStatus

        task = store.create("/path/to/file.pdf")
        old_time = "2026-02-25T08:00:00"
        store.update(
            task.id,
            status=TaskStatus.RUNNING.value,
            created_at=old_time,
        )
        store.cleanup(max_age_hours=TASK_RETENTION_HOURS)
        assert store.get(task.id) is not None

    def test_cleanup_removes_log_files(self, store, store_dir: Path):
        from to_markdown.core.tasks import TaskStatus

        task = store.create("/path/to/file.pdf")
        log_dir = store_dir / TASK_LOG_DIR
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"{task.id}.log"
        log_file.write_text("old log")

        old_time = "2026-02-25T08:00:00"
        store.update(
            task.id,
            status=TaskStatus.COMPLETED.value,
            created_at=old_time,
            completed_at=old_time,
        )
        store.cleanup(max_age_hours=TASK_RETENTION_HOURS)
        assert not log_file.exists()


class TestTaskStoreCheckOrphans:
    """Tests for TaskStore.check_orphans()."""

    def test_marks_stale_pid_as_failed(self, store):
        from to_markdown.core.tasks import TaskStatus

        task = store.create("/path/to/file.pdf")
        store.update(
            task.id,
            status=TaskStatus.RUNNING.value,
            pid=999999,  # Non-existent PID
        )
        orphaned = store.check_orphans()
        assert orphaned >= 1
        fetched = store.get(task.id)
        assert fetched.status == TaskStatus.FAILED
        assert "orphan" in fetched.error.lower()

    def test_preserves_task_with_valid_pid(self, store):
        from to_markdown.core.tasks import TaskStatus

        task = store.create("/path/to/file.pdf")
        # Use current process PID (known to be alive)
        store.update(
            task.id,
            status=TaskStatus.RUNNING.value,
            pid=os.getpid(),
        )
        store.check_orphans()
        fetched = store.get(task.id)
        assert fetched.status == TaskStatus.RUNNING

    def test_ignores_non_running_tasks(self, store):
        from to_markdown.core.tasks import TaskStatus

        task = store.create("/path/to/file.pdf")
        store.update(task.id, status=TaskStatus.COMPLETED.value, pid=999999)
        orphaned = store.check_orphans()
        assert orphaned == 0

    def test_handles_no_pid_gracefully(self, store):
        from to_markdown.core.tasks import TaskStatus

        task = store.create("/path/to/file.pdf")
        store.update(task.id, status=TaskStatus.RUNNING.value)
        # pid is None - should be treated as orphan
        orphaned = store.check_orphans()
        assert orphaned >= 1


class TestGetDefaultStore:
    """Tests for get_default_store()."""

    def test_returns_task_store_instance(self, tmp_path: Path):
        from to_markdown.core.tasks import TaskStore, get_default_store

        with patch.dict(os.environ, {"TO_MARKDOWN_DATA_DIR": str(tmp_path)}):
            # Reset singleton for test
            import to_markdown.core.tasks

            to_markdown.core.tasks._default_store = None
            store = get_default_store()
            assert isinstance(store, TaskStore)
            # Clean up
            to_markdown.core.tasks._default_store = None
