"""Entry point for `python -m to_markdown.mcp`."""

import logging
import sys


def main() -> None:
    """Configure logging and start the MCP server."""
    # Configure logging to stderr (critical for stdio transport - stdout is JSON-RPC)
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stderr,
        format="%(levelname)s: %(message)s",
    )

    # Load .env file so GEMINI_API_KEY is available for smart features
    from to_markdown.core.cli_helpers import load_dotenv

    load_dotenv()

    from to_markdown.mcp.server import run_server

    run_server()


main()
