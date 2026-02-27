"""Tests for configuration wizard (core/setup.py)."""

from pathlib import Path
from unittest.mock import patch

import pytest

from to_markdown.core.constants import (
    GEMINI_API_KEY_ENV,
    SETUP_ENV_FILE,
)


@pytest.fixture()
def project_dir(tmp_path: Path) -> Path:
    """Create a temporary project directory."""
    return tmp_path


@pytest.fixture()
def env_file(project_dir: Path) -> Path:
    """Path to the .env file in the project directory."""
    return project_dir / SETUP_ENV_FILE


# ---- T008: Configuration Wizard Core Tests ----


class TestDetectExistingEnv:
    """Tests for detecting existing .env file."""

    def test_detects_existing_env_with_key(self, project_dir: Path, env_file: Path):
        from to_markdown.core.setup import detect_existing_config

        env_file.write_text(f"{GEMINI_API_KEY_ENV}=test-key-123\n")
        result = detect_existing_config(project_dir)
        assert result["has_env"] is True
        assert result["has_api_key"] is True
        assert result["api_key"] == "test-key-123"

    def test_detects_env_without_key(self, project_dir: Path, env_file: Path):
        from to_markdown.core.setup import detect_existing_config

        env_file.write_text("OTHER_VAR=value\n")
        result = detect_existing_config(project_dir)
        assert result["has_env"] is True
        assert result["has_api_key"] is False

    def test_no_env_file(self, project_dir: Path):
        from to_markdown.core.setup import detect_existing_config

        result = detect_existing_config(project_dir)
        assert result["has_env"] is False
        assert result["has_api_key"] is False

    def test_env_with_empty_key(self, project_dir: Path, env_file: Path):
        from to_markdown.core.setup import detect_existing_config

        env_file.write_text(f"{GEMINI_API_KEY_ENV}=\n")
        result = detect_existing_config(project_dir)
        assert result["has_env"] is True
        assert result["has_api_key"] is False


class TestWriteEnvFile:
    """Tests for writing .env file."""

    def test_writes_new_env_file(self, project_dir: Path, env_file: Path):
        from to_markdown.core.setup import write_env_file

        write_env_file(project_dir, "my-api-key-abc")
        assert env_file.exists()
        content = env_file.read_text()
        assert f"{GEMINI_API_KEY_ENV}=my-api-key-abc" in content

    def test_preserves_existing_vars(self, project_dir: Path, env_file: Path):
        from to_markdown.core.setup import write_env_file

        env_file.write_text("OTHER_VAR=keep-this\n")
        write_env_file(project_dir, "new-key-xyz")
        content = env_file.read_text()
        assert "OTHER_VAR=keep-this" in content
        assert f"{GEMINI_API_KEY_ENV}=new-key-xyz" in content

    def test_updates_existing_key(self, project_dir: Path, env_file: Path):
        from to_markdown.core.setup import write_env_file

        env_file.write_text(f"{GEMINI_API_KEY_ENV}=old-key\n")
        write_env_file(project_dir, "new-key")
        content = env_file.read_text()
        assert f"{GEMINI_API_KEY_ENV}=new-key" in content
        assert "old-key" not in content


class TestRunSetup:
    """Tests for the main setup wizard flow."""

    @patch("to_markdown.core.setup.typer.prompt", return_value="")
    @patch("to_markdown.core.setup.typer.confirm", return_value=False)
    def test_skip_api_key(self, mock_confirm, mock_prompt, project_dir: Path, env_file: Path):
        from to_markdown.core.setup import run_setup

        run_setup(project_dir)
        # .env should not be created when user skips
        assert not env_file.exists() or GEMINI_API_KEY_ENV not in env_file.read_text()

    @patch("to_markdown.core.setup.validate_api_key", return_value=True)
    @patch("to_markdown.core.setup.typer.prompt", return_value="test-key-valid")
    @patch("to_markdown.core.setup.typer.confirm", return_value=True)
    def test_accept_valid_key(
        self, mock_confirm, mock_prompt, mock_validate, project_dir: Path, env_file: Path
    ):
        from to_markdown.core.setup import run_setup

        run_setup(project_dir)
        assert env_file.exists()
        assert "test-key-valid" in env_file.read_text()


# ---- T010: API Key Validation Tests ----


class TestValidateApiKey:
    """Tests for API key validation via Gemini test call."""

    @patch("to_markdown.core.setup._check_llm_available", return_value=True)
    @patch("to_markdown.core.setup._make_test_call", return_value="ok")
    def test_valid_key(self, mock_call, mock_check):
        from to_markdown.core.setup import validate_api_key

        assert validate_api_key("valid-key-123") is True

    @patch("to_markdown.core.setup._check_llm_available", return_value=True)
    @patch("to_markdown.core.setup._make_test_call", side_effect=Exception("Invalid API key"))
    def test_invalid_key(self, mock_call, mock_check):
        from to_markdown.core.setup import validate_api_key

        assert validate_api_key("bad-key") is False

    @patch("to_markdown.core.setup._check_llm_available", return_value=False)
    def test_llm_not_available(self, mock_check):
        from to_markdown.core.setup import validate_api_key

        # When google-genai not installed, skip validation and return True
        assert validate_api_key("any-key") is True

    @patch("to_markdown.core.setup._check_llm_available", return_value=True)
    @patch("to_markdown.core.setup._make_test_call", side_effect=Exception("Network error"))
    def test_network_error(self, mock_call, mock_check):
        from to_markdown.core.setup import validate_api_key

        assert validate_api_key("key-123") is False


# ---- T012: CLI --setup Flag Tests ----


class TestSetupFlag:
    """Tests for --setup CLI flag."""

    @patch("to_markdown.core.setup.run_setup")
    def test_setup_flag_triggers_wizard(self, mock_run_setup, tmp_path: Path):
        from typer.testing import CliRunner

        from to_markdown.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["--setup"])
        assert result.exit_code == 0
        mock_run_setup.assert_called_once()

    @patch("to_markdown.core.setup.run_setup_quiet")
    def test_setup_quiet_mode(self, mock_run_quiet, tmp_path: Path):
        from typer.testing import CliRunner

        from to_markdown.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["--setup", "--quiet"])
        assert result.exit_code == 0
        mock_run_quiet.assert_called_once()
