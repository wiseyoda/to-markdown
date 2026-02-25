# Research: LLM Integration

## Date: 2026-02-25

## Candidates

### google-genai SDK

- **Latest version**: ~v1.59.0 (released Jan 15, 2026)
- **Status**: GA (Generally Available) since May 2025
- **Python requirement**: 3.9+
- **License**: Apache-2.0
- **HTTP backend**: httpx (default), optional aiohttp
- **Install**: `pip install google-genai`
- **Pros**: Unified SDK for Gemini API + Vertex AI, clean Pythonic API, active releases
  (multiple per month), lightweight (httpx-based, no gRPC)
- **Cons**: Google-only (no multi-provider)

### Gemini Models

| Model | ID | Status | Pricing (input/output per 1M tokens) | Free Tier |
|-------|-----|--------|--------------------------------------|-----------|
| 2.5 Flash | `gemini-2.5-flash` | GA/stable | $0.30 / $2.50 | Yes (10 RPM, 250K TPM) |
| 3.0 Flash | `gemini-3-flash-preview` | Preview | $0.50 / $3.00 | No |

### Alternatives Evaluated

**LiteLLM**: Unified interface to 100+ providers. Rejected - massive dependency footprint,
unnecessary abstraction for single-provider use. Violates Principle IV (simplicity).

**Vercel AI SDK (Python)**: Beta, web-server oriented. Not relevant for CLI tools.

**Direct HTTP (no SDK)**: Rejected - SDK handles auth, serialization, multipart uploads,
error mapping. Custom HTTP client would be more maintenance, not less.

## Recommendation

| Component | Selection | Version | Rationale |
|-----------|-----------|---------|-----------|
| SDK | google-genai | 1.59.0+ | GA, lightweight, well-maintained |
| Default model | gemini-2.5-flash | GA | Stable ID, free tier, cheaper |
| Override | GEMINI_MODEL env var | - | Users can upgrade to 3.0 Flash |
| Retry | tenacity | 8.0+ | Exponential backoff for transient errors |
| LLM deps | Optional extras [llm] | - | Core works offline without Gemini SDK |

### Usage Patterns

```python
# Text generation (--summary)
from google import genai
client = genai.Client(api_key="...")
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=["Summarize this document:", document_text],
)

# Vision / image description (--images)
from google.genai import types
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
        "Describe this image in detail for someone who cannot see it.",
    ],
)
```

### Error Handling

- Retry with exponential backoff for 429 (rate limit) and 503 (service unavailable)
- Fail fast on 401 (invalid key) and 400 (bad request)
- Graceful degradation: if LLM fails, output Markdown without summary/descriptions + warning
- Core conversion MUST never be blocked by LLM failures

### API Key Management

- `GEMINI_API_KEY` env var (primary)
- `python-dotenv` for .env file loading (convenience)
- Clear error message if --summary/--images used without API key

### Vision API: Descriptions Not OCR

- Use Gemini vision for `--images` flag: semantic description of images/charts
- Use Kreuzberg's OCR backends (Tesseract/PaddleOCR) for text extraction from scanned pages
- Gemini is optimized for "what does this show?" not character-level OCR

## Human Decision

- **Confirmed**: 2026-02-25
- **Default model**: Gemini 2.5 Flash (user confirmed)
- **SDK**: google-genai (no alternatives needed)
- **LLM deps**: Optional extras confirmed

## Sources

- [google-genai on PyPI](https://pypi.org/project/google-genai/)
- [google-genai GitHub](https://github.com/googleapis/python-genai)
- [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Gemini models list](https://ai.google.dev/gemini-api/docs/models)
