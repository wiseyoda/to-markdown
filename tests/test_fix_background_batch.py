"""Integration tests for background batch processing fixes (recursion and globs)."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from to_markdown.cli import app
from to_markdown.core.batch import BatchResult
from to_markdown.core.constants import TASK_DB_FILENAME, TASK_LOG_DIR

runner = CliRunner()


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


class TestBackgroundBatchFixes:
    """Tests for Findings a37de0c9 (recursion) and a9018918 (globs)."""

    @patch("to_markdown.core.worker.spawn_worker")
    def test_background_preserves_no_recursive_flag(self, mock_spawn, store, tmp_path: Path):
        """Verify --no-recursive is preserved in the task payload (Finding a37de0c9)."""
        mock_spawn.return_value = 42
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "file.pdf").write_text("content")

        with patch("to_markdown.cli.get_store", return_value=store):
            runner.invoke(app, [str(docs_dir), "--background", "--no-recursive"])

        tasks = store.list()
        assert len(tasks) == 1
        args = json.loads(tasks[0].command_args)
        assert args["recursive"] is False
        assert args["is_batch"] is True

    @patch("to_markdown.core.worker.spawn_worker")
    def test_background_recursive_default_true(self, mock_spawn, store, tmp_path: Path):
        """Verify recursive defaults to True in the task payload (Finding a37de0c9)."""
        mock_spawn.return_value = 42
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        with patch("to_markdown.cli.get_store", return_value=store):
            runner.invoke(app, [str(docs_dir), "--background"])

        tasks = store.list()
        args = json.loads(tasks[0].command_args)
        assert args["recursive"] is True

    @patch("to_markdown.core.batch.convert_batch")
    @patch("to_markdown.core.batch.discover_files")
    def test_run_worker_uses_recursive_flag(self, mock_discover, mock_batch, store, tmp_path: Path):
        """Verify run_worker passes recursive flag to discover_files (Finding a37de0c9)."""
        from to_markdown.core.worker import run_worker

        mock_discover.return_value = []
        mock_batch.return_value = BatchResult()

        task = store.create(
            str(tmp_path),
            command_args=json.dumps(
                {"input_path": str(tmp_path), "is_batch": True, "recursive": False}
            ),
        )

        run_worker(task.id, store)
        mock_discover.assert_called_once_with(Path(tmp_path), recursive=False)

    @patch("to_markdown.core.batch.convert_batch")
    @patch("to_markdown.core.batch.resolve_glob")
    def test_run_worker_handles_glob_batch(self, mock_resolve, mock_batch, store, tmp_path: Path):
        """Verify run_worker handles glob-based batches (Finding a9018918)."""
        from to_markdown.core.worker import run_worker

        glob_pattern = "docs/*.pdf"
        mock_resolve.return_value = [Path("docs/a.pdf")]
        mock_batch.return_value = BatchResult(succeeded=[Path("docs/a.md")])

        task = store.create(
            glob_pattern,
            command_args=json.dumps(
                {"input_path": glob_pattern, "is_batch": True, "is_glob": True}
            ),
        )

        run_worker(task.id, store)

        mock_resolve.assert_called_once_with(glob_pattern)
        mock_batch.assert_called_once()
        # Verify batch_root is None for globs as per implementation
        assert mock_batch.call_args[1]["batch_root"] is None

    @patch("to_markdown.core.worker.spawn_worker")
    def test_background_detects_glob_batch(self, mock_spawn, store, tmp_path: Path):
        """Verify --background correctly detects and labels glob batches (Finding a9018918)."""
        mock_spawn.return_value = 42
        glob_pattern = "*.pdf"

        with patch("to_markdown.cli.get_store", return_value=store):
            runner.invoke(app, [glob_pattern, "--background"])

        tasks = store.list()
        args = json.loads(tasks[0].command_args)
        assert args["is_batch"] is True
        assert args["is_glob"] is True
