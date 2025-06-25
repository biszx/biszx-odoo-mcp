"""
MCP server for Odoo integration

Provides MCP tools and resources for interacting with Odoo ERP systems
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP

from odoo_mcp_server.mcp import resources, tools
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


# Register MCP Tools
@mcp.tool()
async def get_odoo_models() -> dict:
    """
    Get a list of all available models in the Odoo system.

    Returns:
        Dictionary with model information
    """
    return await tools.get_odoo_models(mcp)


@mcp.tool()
async def get_model_info(model_name: str) -> dict:
    """
    Get information about a specific Odoo model.

    Args:
        model_name: Name of the model (e.g., 'res.partner')

    Returns:
        Dictionary with model information
    """
    return await tools.get_model_info(mcp, model_name)


@mcp.tool()
async def get_model_fields(model_name: str) -> dict:
    """
    Get field definitions for a specific Odoo model.

    Args:
        model_name: Name of the model (e.g., 'res.partner')

    Returns:
        Dictionary with field definitions
    """
    return await tools.get_model_fields(mcp, model_name)


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
    return await tools.search_records(
        mcp, model_name, domain, fields, limit, offset, order
    )


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
    return await tools.read_records(mcp, model_name, ids, fields)


@mcp.tool()
async def create_record(
    model_name: str,
    values: dict,
) -> dict:
    """
    Create a new record in an Odoo model.

    Args:
        model_name: Name of the model (e.g., 'res.partner')
        values: Dictionary with field values for the new record

    Returns:
        Dictionary with the created record ID
    """
    return await tools.create_record(mcp, model_name, values)


@mcp.tool()
async def create_records(
    model_name: str,
    values_list: list[dict],
) -> dict:
    """
    Create multiple records in an Odoo model.

    Args:
        model_name: Name of the model (e.g., 'res.partner')
        values_list: List of dictionaries with field values for the new records

    Returns:
        Dictionary with the created record IDs
    """
    return await tools.create_records(mcp, model_name, values_list)


@mcp.tool()
async def write_record(
    model_name: str,
    record_id: int,
    values: dict,
) -> dict:
    """
    Update a single record in an Odoo model.

    Args:
        model_name: Name of the model (e.g., 'res.partner')
        record_id: ID of the record to update
        values: Dictionary with field values to update

    Returns:
        Dictionary with operation result
    """
    return await tools.write_record(mcp, model_name, record_id, values)


@mcp.tool()
async def write_records(
    model_name: str,
    record_ids: list[int],
    values: dict,
) -> dict:
    """
    Update multiple records in an Odoo model.

    Args:
        model_name: Name of the model (e.g., 'res.partner')
        record_ids: List of record IDs to update
        values: Dictionary with field values to update

    Returns:
        Dictionary with operation result
    """
    return await tools.write_records(mcp, model_name, record_ids, values)


@mcp.tool()
async def unlink_record(
    model_name: str,
    record_id: int,
) -> dict:
    """
    Delete a single record from an Odoo model.

    Args:
        model_name: Name of the model (e.g., 'res.partner')
        record_id: ID of the record to delete

    Returns:
        Dictionary with operation result
    """
    return await tools.unlink_record(mcp, model_name, record_id)


@mcp.tool()
async def unlink_records(
    model_name: str,
    record_ids: list[int],
) -> dict:
    """
    Delete multiple records from an Odoo model.

    Args:
        model_name: Name of the model (e.g., 'res.partner')
        record_ids: List of record IDs to delete

    Returns:
        Dictionary with operation result
    """
    return await tools.unlink_records(mcp, model_name, record_ids)


@mcp.tool()
async def search_count(
    model_name: str,
    domain: list,
) -> dict:
    """
    Count records that match a search domain.

    Args:
        model_name: Name of the model (e.g., 'res.partner')
        domain: Search domain as list of tuples (e.g., [['is_company', '=', True]])

    Returns:
        Dictionary with the count of matching records
    """
    return await tools.search_count(mcp, model_name, domain)


@mcp.tool()
async def search_ids(
    model_name: str,
    domain: list,
    offset: int | None = None,
    limit: int | None = None,
    order: str | None = None,
) -> dict:
    """
    Search for record IDs that match a domain.

    Args:
        model_name: Name of the model (e.g., 'res.partner')
        domain: Search domain as list of tuples (e.g., [['is_company', '=', True]])
        offset: Number of records to skip
        limit: Maximum number of records to return
        order: Sorting criteria (e.g., 'name ASC, id DESC')

    Returns:
        Dictionary with list of matching record IDs
    """
    return await tools.search_ids(mcp, model_name, domain, offset, limit, order)


@mcp.tool()
async def call_method(
    model_name: str,
    method_name: str,
    args: list | None = None,
    kwargs: dict | None = None,
) -> dict:
    """
    Call a custom method on an Odoo model.

    Args:
        model_name: Name of the model (e.g., 'res.partner')
        method_name: Name of the method to call
        args: Positional arguments to pass to the method
        kwargs: Keyword arguments to pass to the method

    Returns:
        Dictionary with method result
    """
    return await tools.call_method(mcp, model_name, method_name, args, kwargs)


@mcp.tool()
async def bulk_operation(
    operation: str,
    model_name: str,
    data: list[dict],
) -> dict:
    """
    Perform bulk operations on multiple records.

    Args:
        operation: Type of operation ('create', 'write', 'unlink')
        model_name: Name of the model (e.g., 'res.partner')
        data: List of data for the operation (format depends on operation)

    Returns:
        Dictionary with operation results
    """
    return await tools.bulk_operation(mcp, operation, model_name, data)


@mcp.tool()
async def search_and_update(
    model_name: str,
    domain: list,
    values: dict,
) -> dict:
    """
    Search for records and update them in one operation.

    Args:
        model_name: Name of the model (e.g., 'res.partner')
        domain: Search domain to find records to update
        values: Dictionary with field values to update

    Returns:
        Dictionary with operation results including affected record count
    """
    return await tools.search_and_update(mcp, model_name, domain, values)


# Register MCP Resources
@mcp.resource("odoo://models/list")
async def get_models_resource() -> str:
    """
    Resource containing list of all available Odoo models.

    Returns:
        JSON string with all available models and their descriptions
    """
    return await resources.get_models_resource(mcp)


@mcp.resource("odoo://models/{model_name}/fields")
async def get_model_fields_resource(model_name: str) -> str:
    """
    Resource containing field definitions for a specific model.

    Args:
        model_name: Name of the model (e.g., 'res.partner')

    Returns:
        JSON string with field definitions
    """
    return await resources.get_model_fields_resource(mcp, model_name)


@mcp.resource("odoo://models/{model_name}/info")
async def get_model_info_resource(model_name: str) -> str:
    """
    Resource containing information about a specific model.

    Args:
        model_name: Name of the model (e.g., 'res.partner')

    Returns:
        JSON string with model information
    """
    return await resources.get_model_info_resource(mcp, model_name)


@mcp.resource("odoo://help/domains")
async def get_domain_help_resource() -> str:
    """
    Resource containing help information about Odoo domain syntax.

    Returns:
        JSON string with domain syntax examples and explanations
    """
    return await resources.get_domain_help_resource()


@mcp.resource("odoo://help/operations")
async def get_operations_help_resource() -> str:
    """
    Resource containing help information about available MCP tools and operations.

    Returns:
        JSON string with operations documentation
    """
    return await resources.get_operations_help_resource()


@mcp.resource("odoo://models/search/{query}")
async def search_models_resource(query: str) -> str:
    """
    Resource for searching models from the Odoo application.

    Args:
        query: Search term to find models (searches in model name and display name)

    Returns:
        JSON string with matching models
    """
    return await resources.search_models_resource(mcp, query)
