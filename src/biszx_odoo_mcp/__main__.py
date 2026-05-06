"""
Command line entry point for the Odoo MCP Server
"""

import sys

from loguru import logger

from biszx_odoo_mcp.exceptions import OdooMCPError
from biszx_odoo_mcp.main import mcp


def main() -> int:
    """
    Run the MCP server
    """
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
    except Exception:
        logger.exception("Traceback:", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
