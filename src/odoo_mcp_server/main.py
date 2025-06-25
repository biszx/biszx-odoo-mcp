"""
MCP server for Odoo integration

Provides MCP tools and resources for interacting with Odoo ERP systems
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import cast

from mcp.server.fastmcp import FastMCP

from odoo_mcp_server.server.response import Response
from odoo_mcp_server.tools.odoo_client import OdooClient, get_odoo_client


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


# Helper function to convert Response objects to dict
def handle_response(response):
    """
    Convert Response objects to dict format for MCP tools.

    Args:
        response: Either a Response object or raw data

    Returns:
        Dictionary representation of the response
    """

    if isinstance(response, Response):
        return response.to_dict()
    return response


@mcp.tool()
async def get_odoo_models() -> dict:
    """
    Get a list of all available models in the Odoo system.

    Returns:
        Dictionary with model information
    """
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    response = app_context.odoo.get_models()
    return handle_response(response)


@mcp.tool()
async def get_model_info(model_name: str) -> dict:
    """
    Get information about a specific Odoo model.

    Args:
        model_name: Name of the model (e.g., 'res.partner')

    Returns:
        Dictionary with model information
    """
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    response = app_context.odoo.get_model_info(model_name)
    return handle_response(response)


@mcp.tool()
async def get_model_fields(model_name: str) -> dict:
    """
    Get field definitions for a specific Odoo model.

    Args:
        model_name: Name of the model (e.g., 'res.partner')

    Returns:
        Dictionary with field definitions
    """
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    response = app_context.odoo.get_model_fields(model_name)
    return handle_response(response)


@mcp.tool()
async def search_records(
    model_name: str,
    domain: list,
    fields: list[str] | None = None,
    limit: int | None = None,
    offset: int | None = None,
    order: str | None = None,
) -> dict:
    """
    Search for records in an Odoo model.

    Args:
        model_name: Name of the model (e.g., 'res.partner')
        domain: Search domain as list of tuples (e.g., [['is_company', '=', True]])
        fields: List of field names to return (None for all fields)
        limit: Maximum number of records to return
        offset: Number of records to skip
        order: Sorting criteria (e.g., 'name ASC, id DESC')

    Returns:
        Dictionary with search results
    """
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    response = app_context.odoo.search_read(
        model_name, domain, fields=fields, limit=limit, offset=offset, order=order
    )
    return handle_response(response)


@mcp.tool()
async def read_records(
    model_name: str,
    ids: list[int],
    fields: list[str] | None = None,
) -> dict:
    """
    Read specific records by their IDs.

    Args:
        model_name: Name of the model (e.g., 'res.partner')
        ids: List of record IDs to read
        fields: List of field names to return (None for all fields)

    Returns:
        Dictionary with record data
    """
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    response = app_context.odoo.read_records(model_name, ids, fields=fields)
    return handle_response(response)
