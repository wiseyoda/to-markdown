"""Tests for the Gemini client wrapper (smart/llm.py)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from google.genai import errors as genai_errors

from to_markdown.smart.llm import (
    LLMError,
    generate,
    generate_async,
    get_client,
    reset_client,
)


class TestGetClient:
    """Tests for client creation and caching."""

    def setup_method(self):
        reset_client()

    def teardown_method(self):
        reset_client()

    def test_creates_client_with_api_key(self):
        with (
            patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}),
            patch("to_markdown.smart.llm.genai.Client") as mock_cls,
        ):
            client = get_client()
            mock_cls.assert_called_once_with(api_key="test-key")
            assert client == mock_cls.return_value

    def test_raises_without_api_key(self):
        with (
            patch.dict("os.environ", {}, clear=True),
            pytest.raises(LLMError, match="GEMINI_API_KEY"),
        ):
            get_client()

    def test_caches_client(self):
        with (
            patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}),
            patch("to_markdown.smart.llm.genai.Client") as mock_cls,
        ):
            client1 = get_client()
            client2 = get_client()
            mock_cls.assert_called_once()
            assert client1 is client2


class TestGenerate:
    """Tests for the generate function."""

    def setup_method(self):
        reset_client()

    def teardown_method(self):
        reset_client()

    def test_returns_response_text(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Generated text"
        mock_client.models.generate_content.return_value = mock_response

        with (
            patch("to_markdown.smart.llm.get_client", return_value=mock_client),
            patch.dict("os.environ", {"GEMINI_MODEL": "test-model"}),
        ):
            result = generate("Hello")
            assert result == "Generated text"

    def test_uses_default_model(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "ok"
        mock_client.models.generate_content.return_value = mock_response

        with (
            patch("to_markdown.smart.llm.get_client", return_value=mock_client),
            patch.dict("os.environ", {}, clear=True),
        ):
            generate("Hello")
            call_kwargs = mock_client.models.generate_content.call_args
            assert call_kwargs.kwargs["model"] == "gemini-2.5-flash"

    def test_uses_custom_model_from_env(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "ok"
        mock_client.models.generate_content.return_value = mock_response

        with (
            patch("to_markdown.smart.llm.get_client", return_value=mock_client),
            patch.dict("os.environ", {"GEMINI_MODEL": "custom-model"}),
        ):
            generate("Hello")
            call_kwargs = mock_client.models.generate_content.call_args
            assert call_kwargs.kwargs["model"] == "custom-model"

    def test_raises_llm_error_on_empty_response(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = ""
        mock_client.models.generate_content.return_value = mock_response

        with (
            patch("to_markdown.smart.llm.get_client", return_value=mock_client),
            pytest.raises(LLMError, match="empty response"),
        ):
            generate("Hello")

    def test_raises_llm_error_on_client_error(self):
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = genai_errors.ClientError(
            401,
            {"error": {"message": "Unauthorized"}},
        )

        with (
            patch("to_markdown.smart.llm.get_client", return_value=mock_client),
            pytest.raises(LLMError, match="LLM call failed"),
        ):
            generate("Hello")

    def test_passes_temperature_and_max_tokens(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "ok"
        mock_client.models.generate_content.return_value = mock_response

        with patch("to_markdown.smart.llm.get_client", return_value=mock_client):
            generate("Hello", temperature=0.5, max_output_tokens=100)
            call_kwargs = mock_client.models.generate_content.call_args
            config = call_kwargs.kwargs["config"]
            assert config.temperature == 0.5
            assert config.max_output_tokens == 100


class TestGenerateAsync:
    """Tests for the async generate_async function."""

    def setup_method(self):
        reset_client()

    def teardown_method(self):
        reset_client()

    async def test_returns_response_text(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Generated text"
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

        with (
            patch("to_markdown.smart.llm.get_client", return_value=mock_client),
            patch.dict("os.environ", {"GEMINI_MODEL": "test-model"}),
        ):
            result = await generate_async("Hello")
            assert result == "Generated text"

    async def test_uses_default_model(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "ok"
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

        with (
            patch("to_markdown.smart.llm.get_client", return_value=mock_client),
            patch.dict("os.environ", {}, clear=True),
        ):
            await generate_async("Hello")
            call_kwargs = mock_client.aio.models.generate_content.call_args
            assert call_kwargs.kwargs["model"] == "gemini-2.5-flash"

    async def test_uses_custom_model_from_env(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "ok"
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

        with (
            patch("to_markdown.smart.llm.get_client", return_value=mock_client),
            patch.dict("os.environ", {"GEMINI_MODEL": "custom-model"}),
        ):
            await generate_async("Hello")
            call_kwargs = mock_client.aio.models.generate_content.call_args
            assert call_kwargs.kwargs["model"] == "custom-model"

    async def test_raises_llm_error_on_empty_response(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = ""
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

        with (
            patch("to_markdown.smart.llm.get_client", return_value=mock_client),
            pytest.raises(LLMError, match="empty response"),
        ):
            await generate_async("Hello")

    async def test_raises_llm_error_on_client_error(self):
        mock_client = MagicMock()
        mock_client.aio.models.generate_content = AsyncMock(
            side_effect=genai_errors.ClientError(
                401,
                {"error": {"message": "Unauthorized"}},
            ),
        )

        with (
            patch("to_markdown.smart.llm.get_client", return_value=mock_client),
            pytest.raises(LLMError, match="LLM call failed"),
        ):
            await generate_async("Hello")

    async def test_passes_temperature_and_max_tokens(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "ok"
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

        with patch("to_markdown.smart.llm.get_client", return_value=mock_client):
            await generate_async("Hello", temperature=0.5, max_output_tokens=100)
            call_kwargs = mock_client.aio.models.generate_content.call_args
            config = call_kwargs.kwargs["config"]
            assert config.temperature == 0.5
            assert config.max_output_tokens == 100

    async def test_raises_llm_error_on_none_text(self):
        """None text response raises LLMError."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = None
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

        with (
            patch("to_markdown.smart.llm.get_client", return_value=mock_client),
            pytest.raises(LLMError, match="empty response"),
        ):
            await generate_async("Hello")

    async def test_calls_aio_not_sync(self):
        """Verify async path uses client.aio.models, not client.models."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "ok"
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

        with (
            patch("to_markdown.smart.llm.get_client", return_value=mock_client),
            patch.dict("os.environ", {"GEMINI_MODEL": "test-model"}),
        ):
            await generate_async("Hello")
            mock_client.aio.models.generate_content.assert_called_once()
            mock_client.models.generate_content.assert_not_called()
