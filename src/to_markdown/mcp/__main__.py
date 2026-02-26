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

    from to_markdown.mcp.server import run_server

    run_server()


main()
