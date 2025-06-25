"""
Command line entry point for the Odoo MCP Server
"""

import os
import sys
import traceback

from loguru import logger

from .exceptions import OdooMCPError
from .main import mcp


def main() -> int:
    """
    Run the MCP server
    """
    # Configure beautiful loguru formatting
    logger.remove()  # Remove default handler
    logger.add(
        sys.stderr,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        level="INFO",
        colorize=True,
    )

    try:
        logger.info("🚀 Odoo MCP Server Starting")
        logger.info(f"🐍 Python version: {sys.version.split()[0]}")

        # Log environment variables in a structured way
        odoo_vars = {k: v for k, v in os.environ.items() if k.startswith("ODOO_")}
        if odoo_vars:
            logger.info("🔧 Environment Configuration:")
            for key, value in odoo_vars.items():
                if key == "ODOO_PASSWORD":
                    logger.info(f"   • {key}: {'*' * 8}")
                else:
                    logger.info(f"   • {key}: {value}")
        else:
            logger.warning("⚠️  No ODOO_ environment variables found")

        # Check server capabilities
        methods = [method for method in dir(mcp) if not method.startswith("_")]
        methods_preview = ", ".join(methods[:5])
        methods_suffix = "..." if len(methods) > 5 else ""
        logger.info(f"🔍 MCP server capabilities: {methods_preview}{methods_suffix}")
        logger.debug(f"All available methods: {methods}")

        logger.info("▶️  Starting MCP server...")
        sys.stderr.flush()  # Ensure log information is written immediately

        # Use the run() method directly
        mcp.run()

        # If execution reaches here, the server exited normally
        logger.success("✅ MCP server stopped normally")
        return 0
    except KeyboardInterrupt:
        logger.info("⏹️  MCP server stopped by user")
        return 0
    except OdooMCPError as e:
        logger.error("❌ Odoo MCP Error occurred")
        logger.error(f"   └─ Error: {e}")
        logger.error(f"   └─ Type: {e.__class__.__name__}")
        logger.error(f"   └─ Code: {e.error_code}")
        if e.details:
            logger.error(f"   └─ Details: {e.details}")
        return 1
    except Exception as e:  # pylint: disable=broad-exception-caught
        # Justification: Top-level catch-all to ensure server errors are logged.
        # Prevents silent crashes.
        logger.critical("💥 Critical error starting server")
        logger.error(f"   └─ Error: {e}")
        logger.error("   └─ Exception details:")
        for line in traceback.format_exc().strip().split("\n"):
            logger.error(f"      {line}")
        logger.error("   └─ Server object information:")
        logger.error(f"      Type: {type(mcp)}")
        try:
            methods = dir(mcp)
            logger.error(f"      Methods: {methods}")
        except Exception as dir_error:
            logger.error(f"      Methods: <Error getting methods: {dir_error}>")
        return 1


if __name__ == "__main__":
    sys.exit(main())
