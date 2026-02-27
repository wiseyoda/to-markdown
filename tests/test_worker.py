"""Tests for background worker (core/worker.py)."""

import json
import os
import signal
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from to_markdown.core.constants import (
    TASK_DB_FILENAME,
    TASK_LOG_DIR,
    TASK_STATUS_COMPLETED,
)


@pytest.fixture()
def store_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for TaskStore."""
    d = tmp_path / ".to-markdown"
    d.mkdir()
    (d / TASK_LOG_DIR).mkdir()
    return d


@pytest.fixture()
def store(store_dir: Path):
    """Create a TaskStore with a temporary database."""
    from to_markdown.core.tasks import TaskStore

    return TaskStore(db_path=store_dir / TASK_DB_FILENAME)


# ---- T005: spawn_worker() Tests ----


class TestSpawnWorker:
    """Tests for spawn_worker()."""

    @patch("subprocess.Popen")
    def test_spawns_subprocess(self, mock_popen, store, store_dir: Path):
        from to_markdown.core.worker import spawn_worker

        mock_process = MagicMock()
        mock_process.pid = 42
        mock_popen.return_value = mock_process

        task = store.create("/path/to/file.pdf")
        pid = spawn_worker(task.id, store)

        assert pid == 42
        mock_popen.assert_called_once()

    @patch("subprocess.Popen")
    def test_uses_start_new_session(self, mock_popen, store, store_dir: Path):
        from to_markdown.core.worker import spawn_worker

        mock_process = MagicMock()
        mock_process.pid = 42
        mock_popen.return_value = mock_process

        task = store.create("/path/to/file.pdf")
        spawn_worker(task.id, store)

        call_kwargs = mock_popen.call_args[1]
        assert call_kwargs["start_new_session"] is True

    @patch("subprocess.Popen")
    def test_updates_task_pid(self, mock_popen, store, store_dir: Path):
        from to_markdown.core.worker import spawn_worker

        mock_process = MagicMock()
        mock_process.pid = 42
        mock_popen.return_value = mock_process

        task = store.create("/path/to/file.pdf")
        spawn_worker(task.id, store)

        updated = store.get(task.id)
        assert updated.pid == 42

    @patch("subprocess.Popen")
    def test_creates_log_file(self, mock_popen, store, store_dir: Path):
        from to_markdown.core.worker import spawn_worker

        mock_process = MagicMock()
        mock_process.pid = 42
        mock_popen.return_value = mock_process

        task = store.create("/path/to/file.pdf")
        spawn_worker(task.id, store)

        # Log file should be opened (via Popen stdout/stderr)
        call_kwargs = mock_popen.call_args[1]
        assert "stdout" in call_kwargs
        assert "stderr" in call_kwargs

    @patch("subprocess.Popen")
    def test_command_includes_worker_flag(self, mock_popen, store, store_dir: Path):
        from to_markdown.core.worker import spawn_worker

        mock_process = MagicMock()
        mock_process.pid = 42
        mock_popen.return_value = mock_process

        task = store.create("/path/to/file.pdf")
        spawn_worker(task.id, store)

        cmd = mock_popen.call_args[0][0]
        assert "--_worker" in cmd
        assert task.id in cmd


# ---- T011: run_worker() Tests ----


class TestRunWorker:
    """Tests for run_worker()."""

    @patch("to_markdown.core.pipeline.convert_file")
    def test_successful_conversion(self, mock_convert, store, store_dir: Path):
        from to_markdown.core.tasks import TaskStatus
        from to_markdown.core.worker import run_worker

        task = store.create(
            "/path/to/file.pdf",
            command_args=json.dumps(
                {
                    "input_path": "/path/to/file.pdf",
                    "output_path": None,
                    "force": False,
                    "clean": False,
                    "summary": False,
                    "images": False,
                }
            ),
        )
        mock_convert.return_value = Path("/path/to/file.md")

        run_worker(task.id, store)

        fetched = store.get(task.id)
        assert fetched.status == TaskStatus.COMPLETED
        assert fetched.output_path == "/path/to/file.md"
        assert fetched.completed_at is not None
        assert fetched.error is None

    @patch("to_markdown.core.pipeline.convert_file")
    def test_failed_conversion(self, mock_convert, store, store_dir: Path):
        from to_markdown.core.tasks import TaskStatus
        from to_markdown.core.worker import run_worker

        task = store.create(
            "/path/to/file.pdf",
            command_args=json.dumps(
                {
                    "input_path": "/path/to/file.pdf",
                    "output_path": None,
                    "force": False,
                    "clean": False,
                    "summary": False,
                    "images": False,
                }
            ),
        )
        mock_convert.side_effect = RuntimeError("extraction failed")

        run_worker(task.id, store)

        fetched = store.get(task.id)
        assert fetched.status == TaskStatus.FAILED
        assert "extraction failed" in fetched.error
        assert fetched.completed_at is not None

    @patch("to_markdown.core.pipeline.convert_file")
    def test_output_exists_error_marks_failed(self, mock_convert, store, store_dir: Path):
        from to_markdown.core.pipeline import OutputExistsError
        from to_markdown.core.tasks import TaskStatus
        from to_markdown.core.worker import run_worker

        task = store.create(
            "/path/to/file.pdf",
            command_args=json.dumps(
                {
                    "input_path": "/path/to/file.pdf",
                    "output_path": None,
                    "force": False,
                    "clean": False,
                    "summary": False,
                    "images": False,
                }
            ),
        )
        mock_convert.side_effect = OutputExistsError("/path/to/file.md")

        run_worker(task.id, store)

        fetched = store.get(task.id)
        assert fetched.status == TaskStatus.FAILED
        assert fetched.error is not None

    @patch("to_markdown.core.pipeline.convert_file")
    def test_sets_running_status_before_conversion(self, mock_convert, store, store_dir: Path):
        from to_markdown.core.tasks import TaskStatus
        from to_markdown.core.worker import run_worker

        statuses_during_convert = []

        def capture_status(*args, **kwargs):
            fetched = store.get(task.id)
            statuses_during_convert.append(fetched.status)
            return Path("/path/to/file.md")

        mock_convert.side_effect = capture_status

        task = store.create(
            "/path/to/file.pdf",
            command_args=json.dumps(
                {
                    "input_path": "/path/to/file.pdf",
                    "output_path": None,
                    "force": False,
                    "clean": False,
                    "summary": False,
                    "images": False,
                }
            ),
        )

        run_worker(task.id, store)

        assert statuses_during_convert[0] == TaskStatus.RUNNING

    @patch("to_markdown.core.pipeline.convert_file")
    def test_sigterm_sets_cancelled(self, mock_convert, store, store_dir: Path):
        from to_markdown.core.tasks import TaskStatus
        from to_markdown.core.worker import run_worker

        def simulate_sigterm(*args, **kwargs):
            # Simulate SIGTERM by raising the handler directly
            os.kill(os.getpid(), signal.SIGTERM)

        mock_convert.side_effect = simulate_sigterm

        task = store.create(
            "/path/to/file.pdf",
            command_args=json.dumps(
                {
                    "input_path": "/path/to/file.pdf",
                    "output_path": None,
                    "force": False,
                    "clean": False,
                    "summary": False,
                    "images": False,
                }
            ),
        )

        # run_worker registers SIGTERM handler; the SystemExit should be caught
        with pytest.raises(SystemExit):
            run_worker(task.id, store)

        fetched = store.get(task.id)
        assert fetched.status == TaskStatus.CANCELLED


class TestRunWorkerBatch:
    """Tests for run_worker() with batch/directory input."""

    @patch("to_markdown.core.batch.convert_batch")
    @patch("to_markdown.core.batch.discover_files")
    def test_directory_input_calls_convert_batch(
        self, mock_discover, mock_batch, store, store_dir: Path
    ):
        from to_markdown.core.batch import BatchResult
        from to_markdown.core.worker import run_worker

        mock_discover.return_value = [Path("/path/to/docs/a.pdf")]
        mock_batch.return_value = BatchResult(
            succeeded=[Path("/path/to/docs/a.md")],
            failed=[],
            skipped=[],
        )

        task = store.create(
            "/path/to/docs",
            command_args=json.dumps(
                {
                    "input_path": "/path/to/docs",
                    "output_path": None,
                    "force": False,
                    "clean": False,
                    "summary": False,
                    "images": False,
                    "is_batch": True,
                }
            ),
        )

        run_worker(task.id, store)

        mock_batch.assert_called_once()
        fetched = store.get(task.id)
        assert fetched.status.value == TASK_STATUS_COMPLETED


# ---- T021: no_sanitize in background processing ----


class TestRunWorkerSanitize:
    """Tests for sanitize flag passthrough in run_worker()."""

    @patch("to_markdown.core.pipeline.convert_file")
    def test_default_sanitize_true(self, mock_convert, store, store_dir: Path):
        """When sanitize is absent, it defaults to True."""
        from to_markdown.core.worker import run_worker

        task = store.create(
            "/path/to/file.pdf",
            command_args=json.dumps(
                {
                    "input_path": "/path/to/file.pdf",
                    "output_path": None,
                    "force": False,
                    "clean": False,
                    "summary": False,
                    "images": False,
                }
            ),
        )
        mock_convert.return_value = Path("/path/to/file.md")

        run_worker(task.id, store)

        call_kwargs = mock_convert.call_args[1]
        assert call_kwargs["sanitize"] is True

    @patch("to_markdown.core.pipeline.convert_file")
    def test_sanitize_true_explicit(self, mock_convert, store, store_dir: Path):
        """When sanitize is explicitly True, sanitize should be True."""
        from to_markdown.core.worker import run_worker

        task = store.create(
            "/path/to/file.pdf",
            command_args=json.dumps(
                {
                    "input_path": "/path/to/file.pdf",
                    "output_path": None,
                    "force": False,
                    "clean": False,
                    "summary": False,
                    "images": False,
                    "sanitize": True,
                }
            ),
        )
        mock_convert.return_value = Path("/path/to/file.md")

        run_worker(task.id, store)

        call_kwargs = mock_convert.call_args[1]
        assert call_kwargs["sanitize"] is True

    @patch("to_markdown.core.pipeline.convert_file")
    def test_sanitize_false_disables(self, mock_convert, store, store_dir: Path):
        """When sanitize is False, sanitize should be False."""
        from to_markdown.core.worker import run_worker

        task = store.create(
            "/path/to/file.pdf",
            command_args=json.dumps(
                {
                    "input_path": "/path/to/file.pdf",
                    "output_path": None,
                    "force": False,
                    "clean": False,
                    "summary": False,
                    "images": False,
                    "sanitize": False,
                }
            ),
        )
        mock_convert.return_value = Path("/path/to/file.md")

        run_worker(task.id, store)

        call_kwargs = mock_convert.call_args[1]
        assert call_kwargs["sanitize"] is False
