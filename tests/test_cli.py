"""Tests for the Typer CLI (cli.py)."""

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from to_markdown.cli import app
from to_markdown.core.constants import EXIT_ALREADY_EXISTS, EXIT_ERROR, EXIT_SUCCESS

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
        assert "Convert a file to Markdown" in result.output
        assert "--force" in result.output
        assert "--output" in result.output


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
