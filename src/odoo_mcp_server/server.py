"""
MCP server for Odoo integration

Provides MCP tools and resources for interacting with Odoo ERP systems
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastmcp import FastMCP

from .tools.odoo_client import OdooClient, get_odoo_client


@dataclass
class AppContext:
    """
    Application context for the MCP server
    """

    odoo: OdooClient


@asynccontextmanager
async def app_lifespan(_: FastMCP) -> AsyncIterator[AppContext]:
    """
    Application lifespan for initialization and cleanup
    """
    # Initialize Odoo client on startup
    odoo_client = get_odoo_client()

    try:
        yield AppContext(odoo=odoo_client)
    finally:
        # No cleanup needed for Odoo client
        pass


# Create MCP server
mcp = FastMCP(
    name="Odoo MCP Server",
    instructions="MCP Server for interacting with Odoo ERP systems",
    dependencies=["requests"],
    lifespan=app_lifespan,
)
