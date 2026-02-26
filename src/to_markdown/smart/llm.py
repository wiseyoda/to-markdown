"""Gemini client wrapper with retry logic for smart features."""

import logging
import os

from google import genai
from google.genai import errors as genai_errors
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from to_markdown.core.constants import (
    GEMINI_API_KEY_ENV,
    GEMINI_DEFAULT_MODEL,
    GEMINI_MODEL_ENV,
    LLM_RETRY_MAX_ATTEMPTS,
    LLM_RETRY_MAX_WAIT_SECONDS,
    LLM_RETRY_MIN_WAIT_SECONDS,
)

logger = logging.getLogger(__name__)

_client: genai.Client | None = None


class LLMError(Exception):
    """Raised when an LLM operation fails after retries."""


def get_client() -> genai.Client:
    """Get or create the Gemini client from GEMINI_API_KEY env var."""
    global _client
    if _client is None:
        api_key = os.environ.get(GEMINI_API_KEY_ENV)
        if not api_key:
            msg = f"{GEMINI_API_KEY_ENV} environment variable is not set"
            raise LLMError(msg)
        _client = genai.Client(api_key=api_key)
    return _client


def reset_client() -> None:
    """Reset the cached client (for testing)."""
    global _client
    _client = None


def _is_retryable(exc: BaseException) -> bool:
    """Return True for retryable errors (429 rate limit, 503 server error)."""
    if isinstance(exc, genai_errors.ServerError):
        return True
    return isinstance(exc, genai_errors.ClientError) and getattr(exc, "code", None) == 429


@retry(
    retry=retry_if_exception(_is_retryable),
    wait=wait_exponential(
        min=LLM_RETRY_MIN_WAIT_SECONDS,
        max=LLM_RETRY_MAX_WAIT_SECONDS,
    ),
    stop=stop_after_attempt(LLM_RETRY_MAX_ATTEMPTS),
    reraise=True,
)
def _generate_with_retry(
    client: genai.Client,
    *,
    model: str,
    contents: list | str,
    max_output_tokens: int | None = None,
    temperature: float | None = None,
) -> str:
    """Call Gemini with retry logic. Raises on failure."""
    config_kwargs: dict = {}
    if max_output_tokens is not None:
        config_kwargs["max_output_tokens"] = max_output_tokens
    if temperature is not None:
        config_kwargs["temperature"] = temperature

    config = genai.types.GenerateContentConfig(**config_kwargs) if config_kwargs else None

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )
    text = response.text
    if not text:
        msg = "Gemini returned empty response"
        raise LLMError(msg)
    return text


def generate(
    contents: list | str,
    *,
    max_output_tokens: int | None = None,
    temperature: float | None = None,
) -> str:
    """Generate content via Gemini with retry logic.

    Args:
        contents: Text or multimodal content to send to the model.
        max_output_tokens: Maximum tokens in the response.
        temperature: Sampling temperature.

    Returns:
        The generated text response.

    Raises:
        LLMError: If the LLM call fails after retries.
    """
    client = get_client()
    model = os.environ.get(GEMINI_MODEL_ENV, GEMINI_DEFAULT_MODEL)

    try:
        return _generate_with_retry(
            client,
            model=model,
            contents=contents,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
        )
    except (genai_errors.ClientError, genai_errors.ServerError, genai_errors.APIError) as exc:
        msg = f"LLM call failed: {exc}"
        raise LLMError(msg) from exc
