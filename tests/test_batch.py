"""Tests for batch processing module."""

from pathlib import Path
from unittest.mock import patch

from to_markdown.core.batch import BatchResult, convert_batch, discover_files, resolve_glob
from to_markdown.core.constants import EXIT_ERROR, EXIT_PARTIAL, EXIT_SUCCESS


class TestDiscoverFiles:
    """Tests for discover_files() - directory scanning."""

    def test_finds_files_in_directory(self, batch_dir: Path) -> None:
        files = discover_files(batch_dir)
        assert len(files) >= 3  # report.txt, notes.txt, readme.html + sub/deep.txt

    def test_recursive_by_default(self, batch_dir: Path) -> None:
        files = discover_files(batch_dir)
        names = {f.name for f in files}
        assert "deep.txt" in names

    def test_non_recursive(self, batch_dir: Path) -> None:
        files = discover_files(batch_dir, recursive=False)
        names = {f.name for f in files}
        assert "deep.txt" not in names

    def test_skips_hidden_files(self, hidden_files_dir: Path) -> None:
        files = discover_files(hidden_files_dir)
        names = {f.name for f in files}
        assert ".hidden_file.txt" not in names
        assert ".DS_Store" not in names

    def test_skips_extensionless_files(self, hidden_files_dir: Path) -> None:
        files = discover_files(hidden_files_dir)
        names = {f.name for f in files}
        assert "Makefile" not in names

    def test_includes_visible_files(self, hidden_files_dir: Path) -> None:
        files = discover_files(hidden_files_dir)
        names = {f.name for f in files}
        assert "visible.txt" in names

    def test_empty_directory(self, empty_dir: Path) -> None:
        files = discover_files(empty_dir)
        assert files == []

    def test_returns_sorted_paths(self, batch_dir: Path) -> None:
        files = discover_files(batch_dir)
        assert files == sorted(files)

    def test_skips_hidden_directories(self, tmp_path: Path) -> None:
        d = tmp_path / "project"
        d.mkdir()
        (d / ".git").mkdir()
        (d / ".git" / "config").write_text("git config\n")
        (d / "doc.txt").write_text("content\n")
        files = discover_files(d)
        names = {f.name for f in files}
        assert "config" not in names
        assert "doc.txt" in names


class TestResolveGlob:
    """Tests for resolve_glob() - glob pattern resolution."""

    def test_matches_by_extension(self, batch_dir: Path) -> None:
        pattern = str(batch_dir / "*.txt")
        files = resolve_glob(pattern)
        assert all(f.suffix == ".txt" for f in files)
        assert len(files) >= 2

    def test_matches_html(self, batch_dir: Path) -> None:
        pattern = str(batch_dir / "*.html")
        files = resolve_glob(pattern)
        assert len(files) == 1
        assert files[0].name == "readme.html"

    def test_no_matches_returns_empty(self, batch_dir: Path) -> None:
        pattern = str(batch_dir / "*.xyz")
        files = resolve_glob(pattern)
        assert files == []

    def test_returns_sorted(self, batch_dir: Path) -> None:
        pattern = str(batch_dir / "*.txt")
        files = resolve_glob(pattern)
        assert files == sorted(files)


class TestBatchResult:
    """Tests for BatchResult dataclass."""

    def test_total_count(self) -> None:
        result = BatchResult(
            succeeded=[Path("a.md")],
            failed=[(Path("b.pdf"), "error")],
            skipped=[(Path("c.py"), "unsupported")],
        )
        assert result.total == 3

    def test_exit_code_all_success(self) -> None:
        result = BatchResult(
            succeeded=[Path("a.md")],
            failed=[],
            skipped=[(Path("c.py"), "unsupported")],
        )
        assert result.exit_code == EXIT_SUCCESS

    def test_exit_code_partial(self) -> None:
        result = BatchResult(
            succeeded=[Path("a.md")],
            failed=[(Path("b.pdf"), "error")],
            skipped=[],
        )
        assert result.exit_code == EXIT_PARTIAL

    def test_exit_code_all_failed(self) -> None:
        result = BatchResult(
            succeeded=[],
            failed=[(Path("b.pdf"), "error")],
            skipped=[],
        )
        assert result.exit_code == EXIT_ERROR

    def test_exit_code_none_processed(self) -> None:
        result = BatchResult(succeeded=[], failed=[], skipped=[])
        assert result.exit_code == EXIT_ERROR

    def test_exit_code_only_skipped(self) -> None:
        result = BatchResult(
            succeeded=[],
            failed=[],
            skipped=[(Path("c.py"), "unsupported")],
        )
        assert result.exit_code == EXIT_ERROR


class TestConvertBatch:
    """Tests for convert_batch() - batch conversion loop."""

    @patch("to_markdown.core.batch.convert_file")
    def test_successful_batch(self, mock_convert, batch_dir: Path) -> None:
        files = [batch_dir / "report.txt", batch_dir / "notes.txt"]
        mock_convert.side_effect = [
            files[0].with_suffix(".md"),
            files[1].with_suffix(".md"),
        ]
        result = convert_batch(files, quiet=True)
        assert len(result.succeeded) == 2
        assert len(result.failed) == 0
        assert result.exit_code == EXIT_SUCCESS

    @patch("to_markdown.core.batch.convert_file")
    def test_mixed_results(self, mock_convert, batch_dir: Path) -> None:
        from to_markdown.core.extraction import UnsupportedFormatError

        files = [batch_dir / "report.txt", batch_dir / "notes.txt"]
        mock_convert.side_effect = [
            files[0].with_suffix(".md"),
            UnsupportedFormatError("unsupported"),
        ]
        result = convert_batch(files, quiet=True)
        assert len(result.succeeded) == 1
        assert len(result.skipped) == 1
        assert result.exit_code == EXIT_SUCCESS  # skips don't count as failures

    @patch("to_markdown.core.batch.convert_file")
    def test_actual_failure(self, mock_convert, batch_dir: Path) -> None:
        from to_markdown.core.extraction import ExtractionError

        files = [batch_dir / "report.txt", batch_dir / "notes.txt"]
        mock_convert.side_effect = [
            files[0].with_suffix(".md"),
            ExtractionError("extraction failed"),
        ]
        result = convert_batch(files, quiet=True)
        assert len(result.succeeded) == 1
        assert len(result.failed) == 1
        assert result.exit_code == EXIT_PARTIAL

    @patch("to_markdown.core.batch.convert_file")
    def test_all_failures(self, mock_convert, batch_dir: Path) -> None:
        from to_markdown.core.extraction import ExtractionError

        files = [batch_dir / "report.txt", batch_dir / "notes.txt"]
        mock_convert.side_effect = ExtractionError("fail")
        result = convert_batch(files, quiet=True)
        assert len(result.succeeded) == 0
        assert len(result.failed) == 2
        assert result.exit_code == EXIT_ERROR

    @patch("to_markdown.core.batch.convert_file")
    def test_fail_fast(self, mock_convert, batch_dir: Path) -> None:
        from to_markdown.core.extraction import ExtractionError

        files = [batch_dir / "report.txt", batch_dir / "notes.txt"]
        mock_convert.side_effect = ExtractionError("fail")
        result = convert_batch(files, fail_fast=True, quiet=True)
        assert len(result.failed) == 1
        assert mock_convert.call_count == 1

    @patch("to_markdown.core.batch.convert_file")
    def test_output_exists_skipped(self, mock_convert, batch_dir: Path) -> None:
        from to_markdown.core.pipeline import OutputExistsError

        files = [batch_dir / "report.txt"]
        mock_convert.side_effect = OutputExistsError("exists")
        result = convert_batch(files, quiet=True)
        assert len(result.skipped) == 1
        assert "exists" in result.skipped[0][1].lower()

    @patch("to_markdown.core.batch.convert_file")
    def test_output_directory_passed_through(self, mock_convert, batch_dir: Path) -> None:
        files = [batch_dir / "report.txt"]
        out_dir = batch_dir / "output"
        mock_convert.return_value = out_dir / "report.md"
        convert_batch(files, output_dir=out_dir, quiet=True, batch_root=batch_dir)
        call_kwargs = mock_convert.call_args[1]
        assert call_kwargs["output_path"] is not None

    @patch("to_markdown.core.batch.convert_file")
    def test_force_passed_through(self, mock_convert, batch_dir: Path) -> None:
        files = [batch_dir / "report.txt"]
        mock_convert.return_value = files[0].with_suffix(".md")
        convert_batch(files, force=True, quiet=True)
        call_kwargs = mock_convert.call_args[1]
        assert call_kwargs["force"] is True

    @patch("to_markdown.core.batch.convert_file")
    def test_smart_flags_passed_through(self, mock_convert, batch_dir: Path) -> None:
        files = [batch_dir / "report.txt"]
        mock_convert.return_value = files[0].with_suffix(".md")
        convert_batch(files, clean=True, summary=True, images=True, quiet=True)
        call_kwargs = mock_convert.call_args[1]
        assert call_kwargs["clean"] is True
        assert call_kwargs["summary"] is True
        assert call_kwargs["images"] is True

    @patch("to_markdown.core.batch.convert_file")
    def test_output_dir_mirroring(self, mock_convert, batch_dir: Path) -> None:
        """When -o dir is used, output mirrors input structure."""
        sub_file = batch_dir / "sub" / "deep.txt"
        out_dir = batch_dir / "output"
        mock_convert.return_value = out_dir / "sub" / "deep.md"
        convert_batch([sub_file], output_dir=out_dir, quiet=True, batch_root=batch_dir)
        call_kwargs = mock_convert.call_args[1]
        output_path = call_kwargs["output_path"]
        # Output should preserve the relative path: sub/deep.md
        assert "sub" in str(output_path)


class TestEdgeCases:
    """Tests for batch edge cases."""

    @patch("to_markdown.core.batch.convert_file")
    def test_corrupted_file_continues(self, mock_convert, batch_dir: Path) -> None:
        """A corrupted file doesn't stop batch processing."""
        from to_markdown.core.extraction import ExtractionError

        files = [batch_dir / "report.txt", batch_dir / "notes.txt"]
        mock_convert.side_effect = [
            ExtractionError("corrupted"),
            files[1].with_suffix(".md"),
        ]
        result = convert_batch(files, quiet=True)
        assert len(result.succeeded) == 1
        assert len(result.failed) == 1

    @patch("to_markdown.core.batch.convert_file")
    def test_all_unsupported_files(self, mock_convert, batch_dir: Path) -> None:
        """All files unsupported results in EXIT_ERROR."""
        from to_markdown.core.extraction import UnsupportedFormatError

        files = [batch_dir / "report.txt", batch_dir / "notes.txt"]
        mock_convert.side_effect = UnsupportedFormatError("unsupported")
        result = convert_batch(files, quiet=True)
        assert len(result.skipped) == 2
        assert len(result.succeeded) == 0
        assert result.exit_code == EXIT_ERROR

    @patch("to_markdown.core.batch.convert_file")
    def test_existing_outputs_skipped(self, mock_convert, batch_dir: Path) -> None:
        """Files with existing output are skipped."""
        from to_markdown.core.pipeline import OutputExistsError

        files = [batch_dir / "report.txt", batch_dir / "notes.txt"]
        mock_convert.side_effect = [
            OutputExistsError("report.md exists"),
            files[1].with_suffix(".md"),
        ]
        result = convert_batch(files, quiet=True)
        assert len(result.skipped) == 1
        assert len(result.succeeded) == 1

    @patch("to_markdown.core.batch.convert_file")
    def test_force_overwrites_existing(self, mock_convert, batch_dir: Path) -> None:
        """With --force, existing outputs are overwritten."""
        files = [batch_dir / "report.txt"]
        mock_convert.return_value = files[0].with_suffix(".md")
        result = convert_batch(files, force=True, quiet=True)
        assert len(result.succeeded) == 1
        assert mock_convert.call_args[1]["force"] is True

    def test_symlink_directory(self, batch_dir: Path, tmp_path: Path) -> None:
        """Symlinks to directories are followed."""
        link = tmp_path / "link_to_docs"
        link.symlink_to(batch_dir)
        files = discover_files(link)
        assert len(files) >= 3


class TestProgressReporting:
    """Tests for progress bar behavior."""

    @patch("to_markdown.core.batch.convert_file")
    def test_quiet_mode_no_progress(self, mock_convert, batch_dir: Path) -> None:
        """In quiet mode, _NoProgress is used (no output)."""
        from to_markdown.core.batch import _make_progress, _NoProgress

        progress = _make_progress(quiet=True, total=5)
        assert isinstance(progress, _NoProgress)

    @patch("to_markdown.core.batch.convert_file")
    def test_normal_mode_rich_progress(self, mock_convert, batch_dir: Path) -> None:
        """In normal mode, _RichProgress is used."""
        from to_markdown.core.batch import _make_progress, _RichProgress

        progress = _make_progress(quiet=False, total=5)
        assert isinstance(progress, _RichProgress)

    @patch("to_markdown.core.batch.convert_file")
    def test_batch_completes_with_progress(self, mock_convert, batch_dir: Path) -> None:
        """Batch conversion works with progress bar enabled (non-quiet)."""
        files = [batch_dir / "report.txt", batch_dir / "notes.txt"]
        mock_convert.side_effect = [
            files[0].with_suffix(".md"),
            files[1].with_suffix(".md"),
        ]
        # Run with quiet=False to exercise the rich progress path
        result = convert_batch(files, quiet=False)
        assert len(result.succeeded) == 2
