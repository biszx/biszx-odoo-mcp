"""
MCP Tools for Odoo integration

This module contains all the MCP tool functions for interacting with Odoo.
"""

from typing import cast

from odoo_mcp_server.exceptions import OdooMCPError, ToolError
from odoo_mcp_server.server.context import AppContext
from odoo_mcp_server.server.response import Response


async def get_odoo_models(mcp) -> dict:
    """
    Get a list of all available models in the Odoo system.

    Returns:
        Dictionary with model information
    """
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        data = app_context.odoo.get_models()
        return Response(data=data).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()
    except Exception as e:
        tool_error = ToolError(
            f"Unexpected error getting models: {str(e)}",
            tool_name="get_odoo_models",
            original_error=e,
        )
        return Response(error=tool_error.to_dict()).to_dict()


async def get_model_info(mcp, model_name: str) -> dict:
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

    try:
        data = app_context.odoo.get_model_info(model_name)
        return Response(data=data).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()
    except Exception as e:
        tool_error = ToolError(
            f"Unexpected error getting model info: {str(e)}",
            tool_name="get_model_info",
            details={"model_name": model_name},
            original_error=e,
        )
        return Response(error=tool_error.to_dict()).to_dict()


async def get_model_fields(mcp, model_name: str) -> dict:
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

    try:
        data = app_context.odoo.get_model_fields(model_name)
        return Response(data=data).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()
    except Exception as e:
        tool_error = ToolError(
            f"Unexpected error getting model fields: {str(e)}",
            tool_name="get_model_fields",
            details={"model_name": model_name},
            original_error=e,
        )
        return Response(error=tool_error.to_dict()).to_dict()


async def search_records(
    mcp,
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
        domain: Search domain as list of tuples (e.g., [['is_company', '=', true]])
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

    try:
        data = app_context.odoo.search_read(
            model_name, domain, fields=fields, limit=limit, offset=offset, order=order
        )
        return Response(data=data).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()


async def read_records(
    mcp,
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

    try:
        data = app_context.odoo.read_records(model_name, ids, fields=fields)
        return Response(data=data).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()


async def create_record(
    mcp,
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
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        record_id = app_context.odoo.create_records(model_name, [values])
        return Response(data={"id": record_id}).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()


async def create_records(
    mcp,
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
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        record_ids = app_context.odoo.create_records(model_name, values_list)
        return Response(data={"ids": record_ids}).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()


async def write_record(
    mcp,
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
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        result = app_context.odoo.write_records(model_name, [record_id], values)
        return Response(data={"success": result}).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()


async def write_records(
    mcp,
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
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        result = app_context.odoo.write_records(model_name, record_ids, values)
        return Response(data={"success": result}).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()


async def unlink_record(
    mcp,
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
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        result = app_context.odoo.unlink_records(model_name, [record_id])
        return Response(data={"success": result}).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()


async def unlink_records(
    mcp,
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
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        result = app_context.odoo.unlink_records(model_name, record_ids)
        return Response(data={"success": result}).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()


async def search_count(
    mcp,
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
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        count = app_context.odoo.search_count(model_name, domain)
        return Response(data={"count": count}).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()


async def search_ids(
    mcp,
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
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        ids = app_context.odoo.search_ids(
            model_name, domain, offset=offset, limit=limit, order=order
        )
        return Response(data={"ids": ids}).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()


async def call_method(
    mcp,
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
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}

    try:
        result = app_context.odoo.call_method(model_name, method_name, args, kwargs)
        return Response(data=result).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()


# Additional utility tools for better Odoo integration


async def search_and_update(
    mcp,
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
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        # First search for IDs
        record_ids = app_context.odoo.search_ids(model_name, domain)
        if not record_ids:
            return Response(
                data={"affected_records": 0, "message": "No records found"}
            ).to_dict()

        # Then update the found records
        result = app_context.odoo.write_records(model_name, record_ids, values)
        return Response(
            data={
                "affected_records": len(record_ids),
                "record_ids": record_ids,
                "updated": result,
                "update_result": result,  # For backward compatibility
            }
        ).to_dict()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_dict()
