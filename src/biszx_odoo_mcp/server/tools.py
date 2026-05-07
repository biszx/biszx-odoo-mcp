"""
MCP Tools for Odoo integration

This module contains all the MCP tool functions for interacting with Odoo.
"""

from typing import Any, cast

from biszx_odoo_mcp.exceptions import OdooMCPError, ToolError
from biszx_odoo_mcp.server.context import AppContext
from biszx_odoo_mcp.server.response import Response


async def search_models(mcp: Any, query: str) -> Response:
    """Get a list of all available models in the Odoo system."""
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        data = app_context.odoo.search_models(query)
        return Response(data=data)
    except OdooMCPError as e:
        return Response(error=e.to_dict())
    except Exception as e:
        tool_error = ToolError(
            f"Unexpected error getting models: {str(e)}",
            tool_name="search_models",
            original_error=e,
        )
        return Response(error=tool_error.to_dict())


async def get_model_info(mcp: Any, model_name: str) -> Response:
    """Get information about a specific Odoo model."""
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        data = app_context.odoo.get_model_info(model_name)
        return Response(data=data)
    except OdooMCPError as e:
        return Response(error=e.to_dict())
    except Exception as e:
        tool_error = ToolError(
            f"Unexpected error getting model info: {str(e)}",
            tool_name="get_model_info",
            details={"model_name": model_name},
            original_error=e,
        )
        return Response(error=tool_error.to_dict())


async def get_model_fields(mcp: Any, model_name: str, query_field: str) -> Response:
    """Get field definitions for a specific Odoo model."""
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        data = app_context.odoo.get_model_fields(model_name, query_field)
        return Response(data=data)
    except OdooMCPError as e:
        return Response(error=e.to_dict())
    except Exception as e:
        tool_error = ToolError(
            f"Unexpected error getting model fields: {str(e)}",
            tool_name="get_model_fields",
            details={"model_name": model_name},
            original_error=e,
        )
        return Response(error=tool_error.to_dict())


async def get_current_user(mcp: Any, fields: list[str] | None = None) -> Response:
    """Get information about the currently authenticated Odoo user."""
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        data = app_context.odoo.get_current_user(fields=fields)
        return Response(data=data)
    except OdooMCPError as e:
        return Response(error=e.to_dict())
    except Exception as e:
        tool_error = ToolError(
            f"Unexpected error getting current user: {str(e)}",
            tool_name="get_current_user",
            original_error=e,
        )
        return Response(error=tool_error.to_dict())


async def search_records(
    mcp: Any,
    model_name: str,
    domain: list[Any],
    fields: list[str] | None = None,
    limit: int | None = None,
    offset: int | None = None,
    order: str | None = None,
) -> Response:
    """Search for records in an Odoo model."""
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        data = app_context.odoo.search_read(
            model_name, domain, fields=fields, limit=limit, offset=offset, order=order
        )
        return Response(data=data)
    except OdooMCPError as e:
        return Response(error=e.to_dict())


async def search_count(
    mcp: Any,
    model_name: str,
    domain: list[Any],
) -> Response:
    """Count records that match a search domain."""
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        count = app_context.odoo.search_count(model_name, domain)
        return Response(data={"count": count})
    except OdooMCPError as e:
        return Response(error=e.to_dict())


async def search_ids(
    mcp: Any,
    model_name: str,
    domain: list[Any],
    offset: int | None = None,
    limit: int | None = None,
    order: str | None = None,
) -> Response:
    """Search for record IDs that match a domain."""
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        ids = app_context.odoo.search_ids(
            model_name, domain, offset=offset, limit=limit, order=order
        )
        return Response(data={"ids": ids})
    except OdooMCPError as e:
        return Response(error=e.to_dict())


async def read_records(
    mcp: Any,
    model_name: str,
    ids: list[int],
    fields: list[str] | None = None,
) -> Response:
    """Read specific records by their IDs."""
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        data = app_context.odoo.read_records(model_name, ids, fields=fields)
        return Response(data=data)
    except OdooMCPError as e:
        return Response(error=e.to_dict())


async def create_records(
    mcp: Any,
    model_name: str,
    values_list: list[dict[str, Any]],
) -> Response:
    """Create multiple records in an Odoo model."""
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        record_ids = app_context.odoo.create_records(model_name, values_list)
        return Response(data={"ids": record_ids})
    except OdooMCPError as e:
        return Response(error=e.to_dict())


async def write_records(
    mcp: Any,
    model_name: str,
    record_ids: list[int],
    values: dict[str, Any],
) -> Response:
    """Update multiple records in an Odoo model."""
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        result = app_context.odoo.write_records(model_name, record_ids, values)
        return Response(data={"success": result})
    except OdooMCPError as e:
        return Response(error=e.to_dict())


async def search_and_write(
    mcp: Any,
    model_name: str,
    domain: list[Any],
    values: dict[str, Any],
) -> Response:
    """Search for records and update them in one operation."""
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        # First search for IDs
        record_ids = app_context.odoo.search_ids(model_name, domain)
        if not record_ids:
            return Response(data={"affected_records": 0, "message": "No records found"})

        # Then update the found records
        app_context.odoo.write_records(model_name, record_ids, values)
        return Response(
            data={
                "affected_records": len(record_ids),
                "record_ids": record_ids,
            }
        )
    except OdooMCPError as e:
        return Response(error=e.to_dict())


async def unlink_records(
    mcp: Any,
    model_name: str,
    record_ids: list[int],
) -> Response:
    """Delete multiple records from an Odoo model."""
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        app_context.odoo.unlink_records(model_name, record_ids)
        return Response()
    except OdooMCPError as e:
        return Response(error=e.to_dict())


async def search_and_unlink(
    mcp: Any,
    model_name: str,
    domain: list[Any],
) -> Response:
    """Search for records and delete them in one operation."""
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        # First search for IDs
        record_ids = app_context.odoo.search_ids(model_name, domain)
        if not record_ids:
            return Response(error={"error": "No records found"})

        # Then delete the found records
        app_context.odoo.unlink_records(model_name, record_ids)
        return Response(
            data={"affected_records": len(record_ids), "record_ids": record_ids}
        )
    except OdooMCPError as e:
        return Response(error=e.to_dict())


async def call_method(
    mcp: Any,
    model_name: str,
    method_name: str,
    args: list[Any] | None = None,
    kwargs: dict[str, Any] | None = None,
) -> Response:
    """Call a custom method on an Odoo model."""
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}

    try:
        result = app_context.odoo.call_method(model_name, method_name, args, kwargs)
        return Response(data=result)
    except OdooMCPError as e:
        return Response(error=e.to_dict())


async def read_group(
    mcp: Any,
    model_name: str,
    domain: list[Any],
    fields: list[str],
    groupby: list[str],
    offset: int | None = None,
    limit: int | None = None,
    order: str | None = None,
) -> Response:
    """Group records and perform aggregations on an Odoo model."""
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        data = app_context.odoo.read_group(
            model_name,
            domain,
            fields=fields,
            groupby=groupby,
            offset=offset,
            limit=limit,
            order=order,
        )
        return Response(data=data)
    except OdooMCPError as e:
        return Response(error=e.to_dict())
