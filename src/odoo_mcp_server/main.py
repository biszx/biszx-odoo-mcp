"""
MCP server for Odoo integration

Provides MCP tools and resources for interacting with Odoo ERP systems
"""

import inspect
import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from loguru import logger
from mcp.server.fastmcp import FastMCP

from odoo_mcp_server.mcp import resources, tools
from odoo_mcp_server.mcp.context import AppContext
from odoo_mcp_server.tools.odoo_client import get_odoo_client

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Configure loguru with appropriate log level
logger.remove()  # Remove default handler

# Determine log level from environment
log_level = os.environ.get("LOG_LEVEL", "INFO").upper()

logger.add(
    sys.stderr,
    format=(
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<level>{message}</level>"
    ),
    level=log_level,
    colorize=True,
)


@asynccontextmanager
async def app_lifespan(_: FastMCP) -> AsyncIterator[AppContext]:
    """Application lifespan for initialization and cleanup"""
    odoo_client = get_odoo_client()
    try:
        yield AppContext(odoo=odoo_client)
    finally:
        pass


# Create MCP server
mcp = FastMCP(
    name="Odoo MCP Server",
    instructions="MCP Server for interacting with Odoo ERP systems",
    dependencies=["requests"],
    lifespan=app_lifespan,
)


# Tool registration helper
def tool(func):
    """Decorator to register a tool that calls the underlying function with mcp"""

    # Get the original function signature
    sig = inspect.signature(func)

    # Create a new signature excluding the 'mcp' parameter
    new_params = [p for name, p in sig.parameters.items() if name != "mcp"]
    new_sig = sig.replace(parameters=new_params)

    async def wrapper(*args, **kwargs):
        return await func(mcp, *args, **kwargs)

    # Set wrapper properties manually to match the new signature
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__annotations__ = {
        k: v for k, v in func.__annotations__.items() if k != "mcp"
    }

    # Set the corrected signature
    object.__setattr__(wrapper, "__signature__", new_sig)

    return mcp.tool()(wrapper)


# Resource wrapper functions
async def models_list_resource():
    """Get list of all available Odoo models"""
    return await resources.get_models_resource(mcp)


async def model_fields_resource(model_name: str):
    """Get field definitions for a specific model"""
    return await resources.get_model_fields_resource(mcp, model_name)


async def model_info_resource(model_name: str):
    """Get information about a specific model"""
    return await resources.get_model_info_resource(mcp, model_name)


async def search_models_resource(query: str):
    """Search for models by name or description"""
    return await resources.search_models_resource(mcp, query)


# Register all resources directly
mcp.resource("odoo://models/list")(models_list_resource)
mcp.resource("odoo://models/{model_name}/fields")(model_fields_resource)
mcp.resource("odoo://models/{model_name}/info")(model_info_resource)
mcp.resource("odoo://help/domains")(resources.get_domain_help_resource)
mcp.resource("odoo://help/operations")(resources.get_operations_help_resource)
mcp.resource("odoo://models/search/{query}")(search_models_resource)


# Register all tools using the helper
tool(tools.get_odoo_models)
tool(tools.get_model_info)
tool(tools.get_model_fields)
tool(tools.search_records)
tool(tools.read_records)
tool(tools.create_record)
tool(tools.create_records)
tool(tools.write_record)
tool(tools.write_records)
tool(tools.unlink_record)
tool(tools.unlink_records)
tool(tools.search_count)
tool(tools.search_ids)
tool(tools.call_method)
tool(tools.bulk_operation)
tool(tools.search_and_update)
