"""
MCP Server Application Context

This module defines the application context for the MCP server, which includes
the Odoo client used to interact with the Odoo server.
"""

from dataclasses import dataclass

from odoo_mcp_server.tools.odoo_client import OdooClient


@dataclass
class AppContext:
    """
    Application context for the MCP server
    """

    odoo: OdooClient
