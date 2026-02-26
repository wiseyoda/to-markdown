"""Tests for the Typer CLI (cli.py)."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from to_markdown.cli import app
from to_markdown.core.constants import (
    EXIT_ALREADY_EXISTS,
    EXIT_BACKGROUND,
    EXIT_ERROR,
    EXIT_PARTIAL,
    EXIT_SUCCESS,
    TASK_DB_FILENAME,
    TASK_LOG_DIR,
)

runner = CliRunner()


class TestVersion:
    """Tests for --version flag."""

    def test_version_prints_and_exits_0(self):
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == EXIT_SUCCESS
        assert "to-markdown" in result.output
        assert "0.1.0" in result.output


class TestHelp:
    """Tests for --help flag."""

    def test_help_prints_usage(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == EXIT_SUCCESS
        assert "Convert files to Markdown" in result.output
        assert "--force" in result.output
        assert "--output" in result.output
        assert "--no-recursive" in result.output
        assert "--fail-fast" in result.output


class TestBasicConversion:
    """Tests for basic file conversion via CLI."""

    def test_converts_text_file(self, sample_text_file: Path):
        result = runner.invoke(app, [str(sample_text_file)])
        assert result.exit_code == EXIT_SUCCESS
        output = sample_text_file.with_suffix(".md")
        assert output.exists()
        assert "Converted" in result.output

    def test_output_contains_frontmatter(self, sample_text_file: Path):
        runner.invoke(app, [str(sample_text_file)])
        output = sample_text_file.with_suffix(".md")
        content = output.read_text()
        assert content.startswith("---\n")


class TestForceFlag:
    """Tests for --force flag."""

    def test_force_overwrites_existing(self, sample_text_file: Path):
        output = sample_text_file.with_suffix(".md")
        output.write_text("old content")

        result = runner.invoke(app, [str(sample_text_file), "--force"])
        assert result.exit_code == EXIT_SUCCESS
        content = output.read_text()
        assert "old content" not in content


class TestOutputFlag:
    """Tests for -o flag."""

    def test_output_to_custom_file(self, sample_text_file: Path, tmp_path: Path):
        custom = tmp_path / "custom.md"
        result = runner.invoke(app, [str(sample_text_file), "-o", str(custom)])
        assert result.exit_code == EXIT_SUCCESS
        assert custom.exists()

    def test_output_to_directory(self, sample_text_file: Path, output_dir: Path):
        result = runner.invoke(app, [str(sample_text_file), "-o", str(output_dir)])
        assert result.exit_code == EXIT_SUCCESS
        expected = output_dir / "sample.md"
        assert expected.exists()


class TestErrorCases:
    """Tests for error handling and exit codes."""

    def test_missing_file_exits_1(self, tmp_path: Path):
        missing = tmp_path / "nonexistent.txt"
        result = runner.invoke(app, [str(missing)])
        assert result.exit_code == EXIT_ERROR

    def test_output_exists_exits_3(self, sample_text_file: Path):
        output = sample_text_file.with_suffix(".md")
        output.write_text("existing")
        result = runner.invoke(app, [str(sample_text_file)])
        assert result.exit_code == EXIT_ALREADY_EXISTS


class TestVerbosity:
    """Tests for --quiet and --verbose flags."""

    def test_quiet_suppresses_success_message(self, sample_text_file: Path):
        result = runner.invoke(app, [str(sample_text_file), "--quiet"])
        assert result.exit_code == EXIT_SUCCESS
        assert "Converted" not in result.output

    def test_verbose_shows_info(self, sample_text_file: Path):
        result = runner.invoke(app, [str(sample_text_file), "-v"])
        assert result.exit_code == EXIT_SUCCESS
        # INFO messages should appear in stderr/logging, success in stdout
        assert "Converted" in result.output


class TestSmartFlags:
    """Tests for --clean, --summary, --images flags."""

    def test_help_shows_smart_flags(self):
        result = runner.invoke(app, ["--help"])
        assert "--clean" in result.output
        assert "--summary" in result.output
        assert "--images" in result.output

    def test_clean_flag_accepted(self, sample_text_file: Path):
        with (
            patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}),
            patch("to_markdown.smart.clean.clean_content", return_value="cleaned"),
        ):
            result = runner.invoke(app, [str(sample_text_file), "--clean"])
            assert result.exit_code == EXIT_SUCCESS

    def test_summary_flag_accepted(self, sample_text_file: Path):
        with (
            patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}),
            patch("to_markdown.smart.summary.summarize_content", return_value=None),
        ):
            result = runner.invoke(app, [str(sample_text_file), "--summary"])
            assert result.exit_code == EXIT_SUCCESS

    def test_images_flag_accepted(self, sample_text_file: Path):
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            result = runner.invoke(app, [str(sample_text_file), "--images"])
            assert result.exit_code == EXIT_SUCCESS

    def test_short_flags_accepted(self, sample_text_file: Path):
        with (
            patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}),
            patch("to_markdown.smart.clean.clean_content", return_value="cleaned"),
        ):
            result = runner.invoke(app, [str(sample_text_file), "-c"])
            assert result.exit_code == EXIT_SUCCESS


class TestApiKeyValidation:
    """Tests for API key validation with smart flags."""

    def test_missing_key_with_clean_exits_error(self, sample_text_file: Path):
        with (
            patch.dict("os.environ", {}, clear=True),
            patch("to_markdown.cli._load_dotenv"),
        ):
            result = runner.invoke(app, [str(sample_text_file), "--clean"])
            assert result.exit_code == EXIT_ERROR

    def test_missing_key_with_summary_exits_error(self, sample_text_file: Path):
        with (
            patch.dict("os.environ", {}, clear=True),
            patch("to_markdown.cli._load_dotenv"),
        ):
            result = runner.invoke(app, [str(sample_text_file), "--summary"])
            assert result.exit_code == EXIT_ERROR

    def test_missing_key_with_images_exits_error(self, sample_text_file: Path):
        with (
            patch.dict("os.environ", {}, clear=True),
            patch("to_markdown.cli._load_dotenv"),
        ):
            result = runner.invoke(app, [str(sample_text_file), "--images"])
            assert result.exit_code == EXIT_ERROR

    def test_error_message_mentions_api_key(self, sample_text_file: Path):
        with (
            patch.dict("os.environ", {}, clear=True),
            patch("to_markdown.cli._load_dotenv"),
        ):
            result = runner.invoke(app, [str(sample_text_file), "--clean"])
            assert "GEMINI_API_KEY" in result.output

    def test_no_error_without_smart_flags(self, sample_text_file: Path):
        with (
            patch.dict("os.environ", {}, clear=True),
            patch("to_markdown.cli._load_dotenv"),
        ):
            result = runner.invoke(app, [str(sample_text_file)])
            assert result.exit_code == EXIT_SUCCESS


class TestBatchDirectory:
    """Tests for batch directory conversion via CLI."""

    def test_directory_converts_files(self, batch_dir: Path):
        result = runner.invoke(app, [str(batch_dir), "--quiet"])
        assert result.exit_code == EXIT_SUCCESS

    def test_directory_with_output_dir(self, batch_dir: Path, tmp_path: Path):
        out_dir = tmp_path / "output"
        out_dir.mkdir()
        result = runner.invoke(app, [str(batch_dir), "-o", str(out_dir), "--quiet"])
        assert result.exit_code == EXIT_SUCCESS

    def test_no_recursive_flag(self, batch_dir: Path):
        result = runner.invoke(app, [str(batch_dir), "--no-recursive", "--quiet"])
        assert result.exit_code == EXIT_SUCCESS

    def test_empty_directory_exits_error(self, empty_dir: Path):
        result = runner.invoke(app, [str(empty_dir)])
        assert result.exit_code == EXIT_ERROR
        assert "No supported files" in result.output

    def test_batch_shows_summary(self, batch_dir: Path):
        result = runner.invoke(app, [str(batch_dir)])
        assert "Converted" in result.output

    def test_nonexistent_directory_exits_error(self, tmp_path: Path):
        missing = tmp_path / "nonexistent"
        result = runner.invoke(app, [str(missing)])
        assert result.exit_code == EXIT_ERROR


class TestBatchGlob:
    """Tests for glob pattern conversion via CLI."""

    def test_glob_converts_matching(self, batch_dir: Path):
        pattern = str(batch_dir / "*.txt")
        result = runner.invoke(app, [pattern, "--quiet"])
        assert result.exit_code == EXIT_SUCCESS

    def test_glob_no_match_exits_error(self, batch_dir: Path):
        pattern = str(batch_dir / "*.xyz")
        result = runner.invoke(app, [pattern])
        assert result.exit_code == EXIT_ERROR
        assert "No files matched" in result.output


class TestBatchFailFast:
    """Tests for --fail-fast flag."""

    @patch("to_markdown.core.batch.convert_file")
    def test_fail_fast_stops_on_error(self, mock_convert, batch_dir: Path):
        from to_markdown.core.extraction import ExtractionError

        mock_convert.side_effect = ExtractionError("fail")
        result = runner.invoke(app, [str(batch_dir), "--fail-fast", "--quiet"])
        assert result.exit_code == EXIT_ERROR
        # Should have tried only 1 file before stopping
        assert mock_convert.call_count == 1


class TestBatchExitCodes:
    """Tests for batch exit codes."""

    @patch("to_markdown.core.batch.convert_file")
    def test_partial_failure_exits_4(self, mock_convert, batch_dir: Path):
        from to_markdown.core.extraction import ExtractionError

        # First call succeeds, rest fail
        mock_convert.side_effect = [
            (batch_dir / "report.md"),
            ExtractionError("fail"),
            ExtractionError("fail"),
            ExtractionError("fail"),
        ]
        result = runner.invoke(app, [str(batch_dir), "--quiet"])
        assert result.exit_code == EXIT_PARTIAL


# ---- Background Processing Tests ----


class TestBackgroundFlag:
    """Tests for --background / --bg flag (T012)."""

    def _make_store(self, tmp_path: Path):
        from to_markdown.core.tasks import TaskStore

        store_dir = tmp_path / ".to-markdown"
        store_dir.mkdir(exist_ok=True)
        (store_dir / TASK_LOG_DIR).mkdir(exist_ok=True)
        return TaskStore(db_path=store_dir / TASK_DB_FILENAME)

    @patch("to_markdown.core.worker.spawn_worker")
    def test_background_prints_task_id(self, mock_spawn, tmp_path: Path):
        mock_spawn.return_value = 42
        store = self._make_store(tmp_path)
        sample = tmp_path / "file.pdf"
        sample.write_text("content")

        with patch("to_markdown.cli._get_store", return_value=store):
            result = runner.invoke(app, [str(sample), "--background"])

        assert result.exit_code == EXIT_BACKGROUND
        # Should print a hex task ID
        output = result.output.strip()
        assert len(output) >= 8

    @patch("to_markdown.core.worker.spawn_worker")
    def test_background_creates_task(self, mock_spawn, tmp_path: Path):
        mock_spawn.return_value = 42
        store = self._make_store(tmp_path)
        sample = tmp_path / "file.pdf"
        sample.write_text("content")

        with patch("to_markdown.cli._get_store", return_value=store):
            result = runner.invoke(app, [str(sample), "--background"])

        tasks = store.list()
        assert len(tasks) == 1
        assert tasks[0].input_path == str(sample)

    @patch("to_markdown.core.worker.spawn_worker")
    def test_background_spawns_worker(self, mock_spawn, tmp_path: Path):
        mock_spawn.return_value = 42
        store = self._make_store(tmp_path)
        sample = tmp_path / "file.pdf"
        sample.write_text("content")

        with patch("to_markdown.cli._get_store", return_value=store):
            runner.invoke(app, [str(sample), "--background"])

        mock_spawn.assert_called_once()

    @patch("to_markdown.core.worker.spawn_worker")
    def test_bg_short_flag_works(self, mock_spawn, tmp_path: Path):
        mock_spawn.return_value = 42
        store = self._make_store(tmp_path)
        sample = tmp_path / "file.pdf"
        sample.write_text("content")

        with patch("to_markdown.cli._get_store", return_value=store):
            result = runner.invoke(app, [str(sample), "--bg"])

        assert result.exit_code == EXIT_BACKGROUND
        mock_spawn.assert_called_once()

    @patch("to_markdown.core.worker.spawn_worker")
    def test_background_runs_cleanup(self, mock_spawn, tmp_path: Path):
        mock_spawn.return_value = 42
        store = self._make_store(tmp_path)
        sample = tmp_path / "file.pdf"
        sample.write_text("content")

        with (
            patch("to_markdown.cli._get_store", return_value=store),
            patch.object(store, "cleanup") as mock_cleanup,
            patch.object(store, "check_orphans") as mock_orphans,
        ):
            runner.invoke(app, [str(sample), "--background"])

        mock_orphans.assert_called_once()
        mock_cleanup.assert_called_once()

    @patch("to_markdown.core.worker.spawn_worker")
    def test_background_preserves_flags_in_command_args(self, mock_spawn, tmp_path: Path):
        mock_spawn.return_value = 42
        store = self._make_store(tmp_path)
        sample = tmp_path / "file.pdf"
        sample.write_text("content")

        with patch("to_markdown.cli._get_store", return_value=store):
            runner.invoke(app, [str(sample), "--background", "--force"])

        tasks = store.list()
        args = json.loads(tasks[0].command_args)
        assert args["force"] is True


class TestWorkerFlag:
    """Tests for --_worker internal flag (T014)."""

    def test_worker_flag_not_in_help(self):
        result = runner.invoke(app, ["--help"])
        assert "--_worker" not in result.output

    @patch("to_markdown.core.worker.run_worker")
    def test_worker_flag_calls_run_worker(self, mock_run, tmp_path: Path):
        store_dir = tmp_path / ".to-markdown"
        store_dir.mkdir(exist_ok=True)
        (store_dir / TASK_LOG_DIR).mkdir(exist_ok=True)

        from to_markdown.core.tasks import TaskStore

        store = TaskStore(db_path=store_dir / TASK_DB_FILENAME)
        task = store.create("/path/to/file.pdf")

        with patch("to_markdown.cli._get_store", return_value=store):
            result = runner.invoke(app, ["dummy", "--_worker", task.id])

        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0] == task.id


class TestStatusFlag:
    """Tests for --status flag (T016)."""

    def _make_store(self, tmp_path: Path):
        from to_markdown.core.tasks import TaskStore

        store_dir = tmp_path / ".to-markdown"
        store_dir.mkdir(exist_ok=True)
        (store_dir / TASK_LOG_DIR).mkdir(exist_ok=True)
        return TaskStore(db_path=store_dir / TASK_DB_FILENAME)

    def test_status_single_shows_details(self, tmp_path: Path):
        from to_markdown.core.tasks import TaskStatus

        store = self._make_store(tmp_path)
        task = store.create("/path/to/file.pdf")
        store.update(
            task.id,
            status=TaskStatus.COMPLETED.value,
            output_path="/path/to/file.md",
            completed_at="2026-02-26T10:01:00",
            started_at="2026-02-26T10:00:00",
        )

        with patch("to_markdown.cli._get_store", return_value=store):
            result = runner.invoke(app, ["dummy", "--status", task.id])

        assert result.exit_code == EXIT_SUCCESS
        assert task.id in result.output
        assert "completed" in result.output.lower()

    def test_status_all_shows_table(self, tmp_path: Path):
        store = self._make_store(tmp_path)
        store.create("/path/to/a.pdf")
        store.create("/path/to/b.pdf")

        with patch("to_markdown.cli._get_store", return_value=store):
            result = runner.invoke(app, ["dummy", "--status", "all"])

        assert result.exit_code == EXIT_SUCCESS
        assert "a.pdf" in result.output
        assert "b.pdf" in result.output

    def test_status_not_found(self, tmp_path: Path):
        store = self._make_store(tmp_path)

        with patch("to_markdown.cli._get_store", return_value=store):
            result = runner.invoke(app, ["dummy", "--status", "nonexistent"])

        assert result.exit_code == EXIT_ERROR
        assert "not found" in result.output.lower()

    def test_status_no_tasks(self, tmp_path: Path):
        store = self._make_store(tmp_path)

        with patch("to_markdown.cli._get_store", return_value=store):
            result = runner.invoke(app, ["dummy", "--status", "all"])

        assert result.exit_code == EXIT_SUCCESS
        assert "no tasks" in result.output.lower()

    def test_status_runs_orphan_check(self, tmp_path: Path):
        store = self._make_store(tmp_path)

        with (
            patch("to_markdown.cli._get_store", return_value=store),
            patch.object(store, "check_orphans") as mock_orphans,
            patch.object(store, "cleanup") as mock_cleanup,
        ):
            runner.invoke(app, ["dummy", "--status", "all"])

        mock_orphans.assert_called_once()
        mock_cleanup.assert_called_once()


class TestCancelFlag:
    """Tests for --cancel flag (T016)."""

    def _make_store(self, tmp_path: Path):
        from to_markdown.core.tasks import TaskStore

        store_dir = tmp_path / ".to-markdown"
        store_dir.mkdir(exist_ok=True)
        (store_dir / TASK_LOG_DIR).mkdir(exist_ok=True)
        return TaskStore(db_path=store_dir / TASK_DB_FILENAME)

    def test_cancel_running_task(self, tmp_path: Path):
        import os

        from to_markdown.core.tasks import TaskStatus

        store = self._make_store(tmp_path)
        task = store.create("/path/to/file.pdf")
        store.update(task.id, status=TaskStatus.RUNNING.value, pid=os.getpid())

        with (
            patch("to_markdown.cli._get_store", return_value=store),
            patch("os.kill") as mock_kill,
        ):
            result = runner.invoke(app, ["dummy", "--cancel", task.id])

        assert result.exit_code == EXIT_SUCCESS
        assert "cancel" in result.output.lower()

    def test_cancel_completed_task(self, tmp_path: Path):
        from to_markdown.core.tasks import TaskStatus

        store = self._make_store(tmp_path)
        task = store.create("/path/to/file.pdf")
        store.update(task.id, status=TaskStatus.COMPLETED.value)

        with patch("to_markdown.cli._get_store", return_value=store):
            result = runner.invoke(app, ["dummy", "--cancel", task.id])

        assert result.exit_code == EXIT_SUCCESS
        assert "already" in result.output.lower()

    def test_cancel_not_found(self, tmp_path: Path):
        store = self._make_store(tmp_path)

        with patch("to_markdown.cli._get_store", return_value=store):
            result = runner.invoke(app, ["dummy", "--cancel", "nonexistent"])

        assert result.exit_code == EXIT_ERROR
        assert "not found" in result.output.lower()

    def test_cancel_runs_orphan_check(self, tmp_path: Path):
        from to_markdown.core.tasks import TaskStatus

        store = self._make_store(tmp_path)
        task = store.create("/path/to/file.pdf")
        store.update(task.id, status=TaskStatus.RUNNING.value, pid=999999)

        with (
            patch("to_markdown.cli._get_store", return_value=store),
            patch.object(store, "check_orphans") as mock_orphans,
            patch.object(store, "cleanup") as mock_cleanup,
            patch("os.kill"),
        ):
            runner.invoke(app, ["dummy", "--cancel", task.id])

        mock_orphans.assert_called_once()
        mock_cleanup.assert_called_once()


class TestMutualExclusivity:
    """Tests for flag mutual exclusivity (T016)."""

    def test_background_and_status_exclusive(self, tmp_path: Path):
        sample = tmp_path / "file.pdf"
        sample.write_text("content")
        result = runner.invoke(app, [str(sample), "--background", "--status", "all"])
        assert result.exit_code == EXIT_ERROR

    def test_background_and_cancel_exclusive(self, tmp_path: Path):
        sample = tmp_path / "file.pdf"
        sample.write_text("content")
        result = runner.invoke(app, [str(sample), "--background", "--cancel", "abc"])
        assert result.exit_code == EXIT_ERROR

    def test_status_and_cancel_exclusive(self, tmp_path: Path):
        sample = tmp_path / "file.pdf"
        sample.write_text("content")
        result = runner.invoke(app, [str(sample), "--status", "all", "--cancel", "abc"])
        assert result.exit_code == EXIT_ERROR
