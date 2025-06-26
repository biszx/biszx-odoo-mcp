"""
Command line entry point for the Odoo MCP Server
"""

import os
import sys

from loguru import logger

from odoo_mcp_server.exceptions import OdooMCPError
from odoo_mcp_server.main import mcp


def init() -> None:
    """
    Initialize the Odoo MCP Server environment
    """
    try:
        from dotenv import load_dotenv  # pylint: disable=import-outside-toplevel

        load_dotenv()
    except ImportError:
        pass

    # Configure loguru with appropriate log level
    logger.remove()
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logger.add(
        sys.stderr,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<level>{message}</level>"
        ),
        level=log_level,
        colorize=True,
    )


def main() -> int:
    """
    Run the MCP server
    """
    init()
    try:
        logger.info("🚀 Odoo MCP Server starting")

        # Simplified capability check
        logger.debug(f"Python version: {sys.version.split()[0]}")
        logger.debug("MCP server initialized with tools and resources")

        logger.info("▶️ Starting MCP server...")

        mcp.run()

        logger.info("✅ MCP server stopped")
        return 0
    except KeyboardInterrupt:
        logger.info("⏹️ Server stopped by user")
        return 0
    except OdooMCPError as e:
        logger.error(f"Odoo MCP Error: {e}")
        logger.debug(
            f"Error details - Type: {e.__class__.__name__}, Code: {e.error_code}"
        )
        if e.details:
            logger.debug(f"Additional details: {e.details}")
        return 1
    except Exception as e:
        logger.error(f"Critical server error: {e}")
        logger.debug(f"Exception type: {type(e)}")
        logger.debug("Traceback:", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
