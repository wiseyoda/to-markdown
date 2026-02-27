"""Tests for MCP tool handlers (mcp/tools.py)."""

from pathlib import Path
from unittest.mock import patch

import pytest

from to_markdown.core.constants import (
    MAX_MCP_OUTPUT_CHARS,
    TASK_DB_FILENAME,
    TASK_LOG_DIR,
)
from to_markdown.mcp.tools import (
    _validate_llm_flags,
    handle_convert_batch,
    handle_convert_file,
    handle_get_status,
    handle_list_formats,
)


class TestHandleConvertFile:
    """Tests for handle_convert_file."""

    def test_success_returns_structured_response(self, sample_text_file: Path):
        result = handle_convert_file(str(sample_text_file))
        assert "**Source**: sample.txt" in result
        assert "**Format**: txt" in result
        assert "**Characters**:" in result
        assert "---" in result
        assert "Hello" in result

    def test_file_not_found(self, tmp_path: Path):
        missing = str(tmp_path / "nonexistent.pdf")
        with pytest.raises(ValueError, match="File not found"):
            handle_convert_file(missing)

    def test_not_a_file(self, tmp_path: Path):
        with pytest.raises(ValueError, match="Not a file"):
            handle_convert_file(str(tmp_path))

    def test_output_truncation(self, sample_text_file: Path):
        huge_content = "x" * (MAX_MCP_OUTPUT_CHARS + 1_000)
        with patch(
            "to_markdown.core.pipeline.convert_to_string",
            return_value=huge_content,
        ):
            result = handle_convert_file(str(sample_text_file))
            assert "truncated" in result.lower()
            assert str(MAX_MCP_OUTPUT_CHARS) in result.replace(",", "")

    def test_features_listed_in_response(
        self, sample_text_file: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        with (
            patch("to_markdown.mcp.tools._check_llm_available", return_value=True),
            patch(
                "to_markdown.core.pipeline.convert_to_string",
                return_value="---\ncontent\n",
            ),
        ):
            result = handle_convert_file(str(sample_text_file), clean=True, summary=True)
            assert "**Features**: clean, summary" in result

    def test_clean_default_true(self, sample_text_file: Path):
        """clean=True by default; auto-disables when LLM unavailable."""
        with patch("to_markdown.mcp.tools._check_llm_available", return_value=False):
            # Should NOT raise - clean auto-disables silently
            result = handle_convert_file(str(sample_text_file))
            assert "**Source**: sample.txt" in result

    def test_clean_auto_disables_no_sdk(self, sample_text_file: Path):
        """clean=True silently becomes False when SDK is not installed."""
        with (
            patch("to_markdown.mcp.tools._check_llm_available", return_value=False),
            patch(
                "to_markdown.core.pipeline.convert_to_string",
                return_value="---\ncontent\n",
            ) as mock_convert,
        ):
            handle_convert_file(str(sample_text_file))
            # clean should have been auto-disabled to False
            _args, kwargs = mock_convert.call_args
            assert kwargs["clean"] is False
            assert kwargs["sanitize"] is True

    def test_clean_auto_disables_no_api_key(
        self, sample_text_file: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """clean=True silently becomes False when GEMINI_API_KEY is not set."""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        with (
            patch("to_markdown.mcp.tools._check_llm_available", return_value=True),
            patch(
                "to_markdown.core.pipeline.convert_to_string",
                return_value="---\ncontent\n",
            ) as mock_convert,
        ):
            handle_convert_file(str(sample_text_file))
            # clean should have been auto-disabled
            _args, kwargs = mock_convert.call_args
            assert kwargs["clean"] is False

    def test_clean_stays_enabled_when_llm_available(
        self, sample_text_file: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """clean=True stays True when SDK installed and API key set."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        with (
            patch("to_markdown.mcp.tools._check_llm_available", return_value=True),
            patch(
                "to_markdown.core.pipeline.convert_to_string",
                return_value="---\ncontent\n",
            ) as mock_convert,
        ):
            handle_convert_file(str(sample_text_file))
            _args, kwargs = mock_convert.call_args
            assert kwargs["clean"] is True

    def test_summary_still_raises_without_sdk(self, sample_text_file: Path):
        """summary=True still raises when SDK not installed (only clean auto-disables)."""
        with (
            patch("to_markdown.mcp.tools._check_llm_available", return_value=False),
            pytest.raises(ValueError, match="LLM extras"),
        ):
            handle_convert_file(str(sample_text_file), summary=True)

    def test_images_still_raises_without_api_key(
        self, sample_text_file: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """images=True still raises when API key not set."""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        with (
            patch("to_markdown.mcp.tools._check_llm_available", return_value=True),
            pytest.raises(ValueError, match="GEMINI_API_KEY"),
        ):
            handle_convert_file(str(sample_text_file), images=True)

    def test_sanitize_passed_through(self, sample_text_file: Path, monkeypatch: pytest.MonkeyPatch):
        """sanitize parameter is forwarded to convert_to_string."""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        with (
            patch("to_markdown.mcp.tools._check_llm_available", return_value=False),
            patch(
                "to_markdown.core.pipeline.convert_to_string",
                return_value="---\ncontent\n",
            ) as mock_convert,
        ):
            handle_convert_file(str(sample_text_file), sanitize=False)
            _args, kwargs = mock_convert.call_args
            assert kwargs["sanitize"] is False

    def test_sanitize_defaults_true(self, sample_text_file: Path, monkeypatch: pytest.MonkeyPatch):
        """sanitize defaults to True."""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        with (
            patch("to_markdown.mcp.tools._check_llm_available", return_value=False),
            patch(
                "to_markdown.core.pipeline.convert_to_string",
                return_value="---\ncontent\n",
            ) as mock_convert,
        ):
            handle_convert_file(str(sample_text_file))
            _args, kwargs = mock_convert.call_args
            assert kwargs["sanitize"] is True


class TestHandleConvertBatchNewDefaults:
    """Tests for handle_convert_batch new defaults (T019)."""

    def test_clean_auto_disables_no_sdk(self, batch_dir: Path):
        """clean=True by default silently becomes False when SDK unavailable."""
        with patch("to_markdown.mcp.tools._check_llm_available", return_value=False):
            # Should NOT raise
            result = handle_convert_batch(str(batch_dir))
            assert "**Directory**:" in result

    def test_sanitize_passed_to_batch(self, batch_dir: Path):
        """sanitize parameter is forwarded to convert_batch."""
        with (
            patch("to_markdown.mcp.tools._check_llm_available", return_value=False),
            patch("to_markdown.core.batch.convert_batch") as mock_batch,
            patch("to_markdown.core.batch.discover_files", return_value=[Path("f.txt")]),
        ):
            from to_markdown.core.batch import BatchResult

            mock_batch.return_value = BatchResult(succeeded=[Path("f.md")])
            handle_convert_batch(str(batch_dir), sanitize=False)
            _args, kwargs = mock_batch.call_args
            assert kwargs["sanitize"] is False

    def test_sanitize_defaults_true_in_batch(self, batch_dir: Path):
        """sanitize defaults to True in batch."""
        with (
            patch("to_markdown.mcp.tools._check_llm_available", return_value=False),
            patch("to_markdown.core.batch.convert_batch") as mock_batch,
            patch("to_markdown.core.batch.discover_files", return_value=[Path("f.txt")]),
        ):
            from to_markdown.core.batch import BatchResult

            mock_batch.return_value = BatchResult(succeeded=[Path("f.md")])
            handle_convert_batch(str(batch_dir))
            _args, kwargs = mock_batch.call_args
            assert kwargs["sanitize"] is True

    def test_summary_still_raises_without_sdk(self, batch_dir: Path):
        """summary=True still raises when SDK not installed."""
        with (
            patch("to_markdown.mcp.tools._check_llm_available", return_value=False),
            pytest.raises(ValueError, match="LLM extras"),
        ):
            handle_convert_batch(str(batch_dir), summary=True)


class TestHandleConvertBatch:
    """Tests for handle_convert_batch."""

    def test_success_with_mixed_results(self, batch_dir: Path):
        result = handle_convert_batch(str(batch_dir))
        assert "**Directory**:" in result
        assert "**Total files**:" in result
        assert "**Succeeded**:" in result

    def test_directory_not_found(self, tmp_path: Path):
        missing = str(tmp_path / "nonexistent_dir")
        with pytest.raises(ValueError, match="Directory not found"):
            handle_convert_batch(missing)

    def test_not_a_directory(self, sample_text_file: Path):
        with pytest.raises(ValueError, match="Not a directory"):
            handle_convert_batch(str(sample_text_file))

    def test_empty_directory(self, empty_dir: Path):
        with pytest.raises(ValueError, match="No supported files"):
            handle_convert_batch(str(empty_dir))

    def test_non_recursive(self, batch_dir: Path):
        result = handle_convert_batch(str(batch_dir), recursive=False)
        assert "**Recursive**: False" in result


class TestHandleListFormats:
    """Tests for handle_list_formats."""

    def test_returns_format_description(self):
        result = handle_list_formats()
        assert "PDF" in result
        assert "DOCX" in result
        assert "PNG" in result
        assert "Kreuzberg" in result

    def test_returns_string(self):
        assert isinstance(handle_list_formats(), str)


class TestHandleGetStatus:
    """Tests for handle_get_status."""

    def test_returns_version(self):
        from to_markdown import __version__

        result = handle_get_status()
        assert __version__ in result

    def test_returns_python_version(self):
        result = handle_get_status()
        assert "**Python**:" in result

    def test_llm_available_with_key(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        with patch("to_markdown.mcp.tools._check_llm_available", return_value=True):
            result = handle_get_status()
            assert "Available" in result

    def test_llm_not_installed(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        with patch("to_markdown.mcp.tools._check_llm_available", return_value=False):
            result = handle_get_status()
            assert "Not available" in result

    def test_llm_installed_no_key(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        with patch("to_markdown.mcp.tools._check_llm_available", return_value=True):
            result = handle_get_status()
            assert "GEMINI_API_KEY not set" in result


# ---- Background Tool Handler Tests (T020) ----


class TestHandleStartConversion:
    """Tests for handle_start_conversion."""

    def _make_store(self, tmp_path: Path):
        from to_markdown.core.tasks import TaskStore

        store_dir = tmp_path / ".to-markdown"
        store_dir.mkdir(exist_ok=True)
        (store_dir / TASK_LOG_DIR).mkdir(exist_ok=True)
        return TaskStore(db_path=store_dir / TASK_DB_FILENAME)

    @patch("to_markdown.core.worker.spawn_worker")
    def test_returns_task_id(self, mock_spawn, tmp_path: Path):
        from to_markdown.mcp.tools import handle_start_conversion

        mock_spawn.return_value = 42
        store = self._make_store(tmp_path)
        sample = tmp_path / "file.pdf"
        sample.write_text("content")

        with patch("to_markdown.mcp.background_tools._get_task_store", return_value=store):
            result = handle_start_conversion(str(sample))

        assert "Task ID" in result
        assert "pending" in result.lower()

    @patch("to_markdown.core.worker.spawn_worker")
    def test_creates_task_in_store(self, mock_spawn, tmp_path: Path):
        from to_markdown.mcp.tools import handle_start_conversion

        mock_spawn.return_value = 42
        store = self._make_store(tmp_path)
        sample = tmp_path / "file.pdf"
        sample.write_text("content")

        with patch("to_markdown.mcp.background_tools._get_task_store", return_value=store):
            handle_start_conversion(str(sample))

        tasks = store.list()
        assert len(tasks) == 1

    def test_file_not_found(self, tmp_path: Path):
        from to_markdown.mcp.tools import handle_start_conversion

        store = self._make_store(tmp_path)
        with (
            patch("to_markdown.mcp.background_tools._get_task_store", return_value=store),
            pytest.raises(ValueError, match="not found"),
        ):
            handle_start_conversion(str(tmp_path / "nonexistent.pdf"))

    @patch("to_markdown.core.worker.spawn_worker")
    def test_directory_input(self, mock_spawn, batch_dir: Path, tmp_path: Path):
        from to_markdown.mcp.tools import handle_start_conversion

        mock_spawn.return_value = 42
        store = self._make_store(tmp_path)

        with patch("to_markdown.mcp.background_tools._get_task_store", return_value=store):
            result = handle_start_conversion(str(batch_dir))

        assert "Task ID" in result

    @patch("to_markdown.core.worker.spawn_worker")
    def test_sanitize_in_command_args(self, mock_spawn, tmp_path: Path):
        """sanitize parameter is included in command_args JSON."""
        import json

        from to_markdown.mcp.tools import handle_start_conversion

        mock_spawn.return_value = 42
        store = self._make_store(tmp_path)
        sample = tmp_path / "file.pdf"
        sample.write_text("content")

        with patch("to_markdown.mcp.background_tools._get_task_store", return_value=store):
            handle_start_conversion(str(sample), sanitize=False)

        tasks = store.list()
        assert len(tasks) == 1
        args = json.loads(tasks[0].command_args)
        assert args["sanitize"] is False

    @patch("to_markdown.core.worker.spawn_worker")
    def test_sanitize_defaults_true_in_background(self, mock_spawn, tmp_path: Path):
        """sanitize defaults to True in background command_args."""
        import json

        from to_markdown.mcp.tools import handle_start_conversion

        mock_spawn.return_value = 42
        store = self._make_store(tmp_path)
        sample = tmp_path / "file.pdf"
        sample.write_text("content")

        with patch("to_markdown.mcp.background_tools._get_task_store", return_value=store):
            handle_start_conversion(str(sample))

        tasks = store.list()
        args = json.loads(tasks[0].command_args)
        assert args["sanitize"] is True

    @patch("to_markdown.core.worker.spawn_worker")
    def test_clean_auto_disables_in_background(self, mock_spawn, tmp_path: Path):
        """clean=True auto-disables when LLM unavailable in background start."""
        import json

        from to_markdown.mcp.tools import handle_start_conversion

        mock_spawn.return_value = 42
        store = self._make_store(tmp_path)
        sample = tmp_path / "file.pdf"
        sample.write_text("content")

        with (
            patch("to_markdown.mcp.background_tools._check_llm_available", return_value=False),
            patch("to_markdown.mcp.background_tools._get_task_store", return_value=store),
        ):
            # Should NOT raise even though clean defaults to True
            handle_start_conversion(str(sample))

        tasks = store.list()
        args = json.loads(tasks[0].command_args)
        assert args["clean"] is False


class TestHandleGetTaskStatus:
    """Tests for handle_get_task_status."""

    def _make_store(self, tmp_path: Path):
        from to_markdown.core.tasks import TaskStore

        store_dir = tmp_path / ".to-markdown"
        store_dir.mkdir(exist_ok=True)
        (store_dir / TASK_LOG_DIR).mkdir(exist_ok=True)
        return TaskStore(db_path=store_dir / TASK_DB_FILENAME)

    def test_returns_task_details(self, tmp_path: Path):
        from to_markdown.core.tasks import TaskStatus
        from to_markdown.mcp.tools import handle_get_task_status

        store = self._make_store(tmp_path)
        task = store.create("/path/to/file.pdf")
        store.update(task.id, status=TaskStatus.COMPLETED.value, output_path="/out.md")

        with patch("to_markdown.mcp.background_tools._get_task_store", return_value=store):
            result = handle_get_task_status(task.id)

        assert task.id in result
        assert "completed" in result.lower()

    def test_not_found(self, tmp_path: Path):
        from to_markdown.mcp.tools import handle_get_task_status

        store = self._make_store(tmp_path)
        with (
            patch("to_markdown.mcp.background_tools._get_task_store", return_value=store),
            pytest.raises(ValueError, match="not found"),
        ):
            handle_get_task_status("nonexistent")

    def test_runs_orphan_check(self, tmp_path: Path):
        from to_markdown.mcp.tools import handle_get_task_status

        store = self._make_store(tmp_path)
        task = store.create("/path/to/file.pdf")

        with (
            patch("to_markdown.mcp.background_tools._get_task_store", return_value=store),
            patch.object(store, "check_orphans") as mock_orphans,
        ):
            handle_get_task_status(task.id)

        mock_orphans.assert_called_once()


class TestHandleListTasks:
    """Tests for handle_list_tasks."""

    def _make_store(self, tmp_path: Path):
        from to_markdown.core.tasks import TaskStore

        store_dir = tmp_path / ".to-markdown"
        store_dir.mkdir(exist_ok=True)
        (store_dir / TASK_LOG_DIR).mkdir(exist_ok=True)
        return TaskStore(db_path=store_dir / TASK_DB_FILENAME)

    def test_returns_task_list(self, tmp_path: Path):
        from to_markdown.mcp.tools import handle_list_tasks

        store = self._make_store(tmp_path)
        store.create("/path/to/a.pdf")
        store.create("/path/to/b.pdf")

        with patch("to_markdown.mcp.background_tools._get_task_store", return_value=store):
            result = handle_list_tasks()

        assert "a.pdf" in result
        assert "b.pdf" in result

    def test_empty_returns_no_tasks(self, tmp_path: Path):
        from to_markdown.mcp.tools import handle_list_tasks

        store = self._make_store(tmp_path)

        with patch("to_markdown.mcp.background_tools._get_task_store", return_value=store):
            result = handle_list_tasks()

        assert "no" in result.lower()

    def test_runs_orphan_check(self, tmp_path: Path):
        from to_markdown.mcp.tools import handle_list_tasks

        store = self._make_store(tmp_path)

        with (
            patch("to_markdown.mcp.background_tools._get_task_store", return_value=store),
            patch.object(store, "check_orphans") as mock_orphans,
        ):
            handle_list_tasks()

        mock_orphans.assert_called_once()


class TestHandleCancelTask:
    """Tests for handle_cancel_task."""

    def _make_store(self, tmp_path: Path):
        from to_markdown.core.tasks import TaskStore

        store_dir = tmp_path / ".to-markdown"
        store_dir.mkdir(exist_ok=True)
        (store_dir / TASK_LOG_DIR).mkdir(exist_ok=True)
        return TaskStore(db_path=store_dir / TASK_DB_FILENAME)

    def test_cancels_running_task(self, tmp_path: Path):
        import os

        from to_markdown.core.tasks import TaskStatus
        from to_markdown.mcp.tools import handle_cancel_task

        store = self._make_store(tmp_path)
        task = store.create("/path/to/file.pdf")
        store.update(task.id, status=TaskStatus.RUNNING.value, pid=os.getpid())

        with (
            patch("to_markdown.mcp.background_tools._get_task_store", return_value=store),
            patch("os.kill"),
        ):
            result = handle_cancel_task(task.id)

        assert "cancel" in result.lower()

    def test_already_completed(self, tmp_path: Path):
        from to_markdown.core.tasks import TaskStatus
        from to_markdown.mcp.tools import handle_cancel_task

        store = self._make_store(tmp_path)
        task = store.create("/path/to/file.pdf")
        store.update(task.id, status=TaskStatus.COMPLETED.value)

        with patch("to_markdown.mcp.background_tools._get_task_store", return_value=store):
            result = handle_cancel_task(task.id)

        assert "already" in result.lower()

    def test_not_found(self, tmp_path: Path):
        from to_markdown.mcp.tools import handle_cancel_task

        store = self._make_store(tmp_path)
        with (
            patch("to_markdown.mcp.background_tools._get_task_store", return_value=store),
            pytest.raises(ValueError, match="not found"),
        ):
            handle_cancel_task("nonexistent")


# ---- T019: _validate_llm_flags tests ----


class TestValidateLlmFlags:
    """Tests for _validate_llm_flags (no longer checks clean)."""

    def test_no_flags_returns_none(self):
        """No flags set should return without error."""
        _validate_llm_flags(summary=False, images=False)

    def test_summary_without_sdk_raises(self):
        """summary=True without SDK raises ValueError."""
        with (
            patch("to_markdown.mcp.tools._check_llm_available", return_value=False),
            pytest.raises(ValueError, match="LLM extras"),
        ):
            _validate_llm_flags(summary=True, images=False)

    def test_images_without_api_key_raises(self, monkeypatch: pytest.MonkeyPatch):
        """images=True without API key raises ValueError."""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        with (
            patch("to_markdown.mcp.tools._check_llm_available", return_value=True),
            pytest.raises(ValueError, match="GEMINI_API_KEY"),
        ):
            _validate_llm_flags(summary=False, images=True)

    def test_does_not_accept_clean_parameter(self):
        """_validate_llm_flags no longer accepts clean parameter."""
        with pytest.raises(TypeError):
            _validate_llm_flags(clean=True, summary=False, images=False)
