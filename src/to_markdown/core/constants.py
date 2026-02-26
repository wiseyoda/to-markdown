"""All project constants. Single source of truth - never define constants elsewhere."""

# --- Application ---
APP_NAME = "to-markdown"

# --- Exit Codes ---
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_UNSUPPORTED = 2
EXIT_ALREADY_EXISTS = 3
EXIT_PARTIAL = 4

# --- File Processing ---
DEFAULT_OUTPUT_EXTENSION = ".md"

# --- Batch Processing ---
GLOB_CHARS = frozenset("*?[")

# --- LLM ---
GEMINI_DEFAULT_MODEL = "gemini-2.5-flash"
GEMINI_API_KEY_ENV = "GEMINI_API_KEY"
GEMINI_MODEL_ENV = "GEMINI_MODEL"

# --- LLM Retry ---
LLM_RETRY_MAX_ATTEMPTS = 5
LLM_RETRY_MIN_WAIT_SECONDS = 1
LLM_RETRY_MAX_WAIT_SECONDS = 60

# --- LLM Token Limits ---
MAX_CLEAN_TOKENS = 100_000
MAX_SUMMARY_TOKENS = 4_096
CHARS_PER_TOKEN_ESTIMATE = 4

# --- LLM Temperature ---
CLEAN_TEMPERATURE = 0.1
SUMMARY_TEMPERATURE = 0.3
IMAGE_DESCRIPTION_TEMPERATURE = 0.2

# --- Smart Feature Output ---
SUMMARY_SECTION_HEADING = "## Summary"
IMAGE_SECTION_HEADING = "## Image Descriptions"

# --- LLM Prompts ---
CLEAN_PROMPT = """\
You are a document formatting repair tool. Your ONLY job is to fix extraction \
artifacts in the following text that was extracted from a {format_type} document.

Fix ONLY these artifact types:
- Word concatenation from column/line breaks (e.g. "inBangkok" -> "in Bangkok")
- Decorative letter spacing (e.g. "L E A D E R S H I P" -> "LEADERSHIP")
- Wall-of-text paragraphs containing labeled data: restructure into markdown lists or tables
- Collapsed line breaks where two items run together on one line
- Truncated fragments from multi-column extraction (recover from context if possible)

CRITICAL RULES:
- NEVER add new information that is not in the original text
- NEVER remove any information from the original text
- NEVER rephrase or reword the content
- ONLY fix formatting and structural issues
- Output valid markdown
- Preserve all headings, lists, and other markdown structure that is already correct

Text to repair:
{content}\
"""

SUMMARY_PROMPT = """\
Summarize the following document content in a concise paragraph. The summary should:
- Capture the key facts, topics, and conclusions
- Be useful for an LLM that needs to quickly assess document relevance
- Be 3-5 sentences long
- Focus on factual content, not formatting or structure

Document content:
{content}\
"""

IMAGE_DESCRIPTION_PROMPT = """\
Describe this image in detail. The description should be:
- Factual and objective (not artistic interpretation)
- Useful for accessibility (screen readers) and LLM consumption
- Include key visual elements: text, charts, diagrams, photos, colors, layout
- If it contains a chart or graph, describe the data relationships and trends
- If it contains text, transcribe the text exactly
- 2-4 sentences long\
"""
