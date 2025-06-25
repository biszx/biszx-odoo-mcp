"""
Odoo JSON-RPC client for MCP server integration
"""

import urllib.parse

import odoorpc
from loguru import logger

from odoo_mcp_server.server.response import Response
from odoo_mcp_server.tools.config import Config


class OdooClient:
    """
    Client for interacting with Odoo via JSON-RPC
    """

    config: Config
    hostname: str
    odoo: odoorpc.ODOO

    def __init__(
        self,
        config: Config,
    ) -> None:
        """
        Initialize the Odoo client with connection parameters

        Args:
            config: Odoo client configuration
        """
        self.config = config
        parsed_url = urllib.parse.urlparse(self.config.url)
        self.hostname = parsed_url.netloc
        self._connect()

    def _connect(self):
        """Initialize the OdooRPC connection and authenticate"""
        logger.info(f"Connecting to Odoo at: {self.config.url}")
        logger.info(f"  Hostname: {self.hostname}")
        logger.info(
            f"  Timeout: {self.config.timeout}s, Verify SSL: {self.config.verify_ssl}"
        )
        logger.info(
            f"Authenticating with database: {self.config.db}, "
            f"username: {self.config.username}"
        )
        try:
            protocol = (
                "jsonrpc" if self.config.url.startswith("https://") else "jsonrpc"
            )
            self.odoo = odoorpc.ODOO(
                self.hostname,
                protocol=protocol,
                port=443 if self.config.url.startswith("https://") else 80,
                timeout=self.config.timeout,
                version=None,
            )
            self.odoo.login(self.config.db, self.config.username, self.config.password)
            self.uid = self.odoo.execute(
                "res.users", "search", [("login", "=", self.config.username)]
            )
            if self.uid:
                self.uid = self.uid[0]
            else:
                self.uid = None
        except Exception as e:
            logger.error(f"Failed to authenticate with Odoo: {str(e)}")
            raise ValueError(f"Failed to authenticate with Odoo: {str(e)}") from e

    def execute_method(self, model, method, *args, **kwargs):
        """
        Execute an arbitrary method on a model

        Args:
            model: The model name (e.g., 'res.partner')
            method: Method name to execute
            *args: Positional arguments to pass to the method
            **kwargs: Keyword arguments to pass to the method

        Returns:
            Result of the method execution
        """
        return self._execute(model, method, *args, **kwargs)

    def get_models(self):
        """
        Get a list of all available models in the system

        Returns:
            List of model names

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> models = client.get_models()
            >>> print(len(models))
            125
            >>> print(models[:5])
            ['res.partner', 'res.users', 'res.company', 'res.groups', 'ir.model']
        """
        model_ids = self._execute("ir.model", "search", [])
        if not model_ids:
            return Response(error="No models found")
        result = self._execute("ir.model", "read", model_ids, ["model", "name"])
        if result is None:
            return Response(error="Failed to read models")
        models = sorted([rec["model"] for rec in result])
        models_info = {
            "model_names": models,
            "models_details": {
                rec["model"]: {"name": rec.get("name", "")} for rec in result
            },
        }
        return Response(data=models_info)

    def get_model_info(self, model_name):
        """
        Get information about a specific model

        Args:
            model_name: Name of the model (e.g., 'res.partner')

        Returns:
            Dictionary with model information

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> info = client.get_model_info('res.partner')
            >>> print(info['name'])
            'Contact'
        """
        result = self._execute(
            "ir.model",
            "search_read",
            [("model", "=", model_name)],
            {"fields": ["name", "model"]},
        )
        if not result:
            return Response(error=f"Model {model_name} not found")
        return Response(data=result[0])

    def get_model_fields(self, model_name):
        """
        Get field definitions for a specific model

        Args:
            model_name: Name of the model (e.g., 'res.partner')

        Returns:
            Dictionary mapping field names to their definitions

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> fields = client.get_model_fields('res.partner')
            >>> print(fields['name']['type'])
            'char'
        """
        fields = self._execute(model_name, "fields_get")
        if fields is None:
            return Response(error=f"Failed to get fields for {model_name}")
        return Response(data=fields)

    def search_read(
        self, model_name, domain, fields=None, offset=None, limit=None, order=None
    ):
        """
        Search for records and read their data in a single call

        Args:
            model_name: Name of the model (e.g., 'res.partner')
            domain: Search domain (e.g., [('is_company', '=', True)])
            fields: List of field names to return (None for all)
            offset: Number of records to skip
            limit: Maximum number of records to return
            order: Sorting criteria (e.g., 'name ASC, id DESC')

        Returns:
            List of dictionaries with the matching records

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> records = client.search_read('res.partner', [
                    ('is_company', '=', True)
                ], limit=5)
            >>> print(len(records))
            5
        """
        kwargs = {}
        if offset:
            kwargs["offset"] = offset
        if fields is not None:
            kwargs["fields"] = fields
        if limit is not None:
            kwargs["limit"] = limit
        if order is not None:
            kwargs["order"] = order
        result = self._execute(model_name, "search_read", domain, kwargs)
        if result is None:
            return Response(error="Failed to search and read records")
        return Response(data=result)

    def read_records(self, model_name, ids, fields=None):
        """
        Read data of records by IDs

        Args:
            model_name: Name of the model (e.g., 'res.partner')
            ids: List of record IDs to read
            fields: List of field names to return (None for all)

        Returns:
            List of dictionaries with the requested records

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> records = client.read_records('res.partner', [1])
            >>> print(records[0]['name'])
            'YourCompany'
        """
        kwargs = {}
        if fields is not None:
            kwargs["fields"] = fields
        result = self._execute(model_name, "read", ids, kwargs)
        if result is None:
            return Response(error="Failed to read records")
        return Response(data=result)

    def _execute(self, model, method, *args, **kwargs):
        """Execute a method on an Odoo model via OdooRPC"""
        try:
            return self.odoo.execute(model, method, *args, **kwargs)
        except Exception as e:  # pylint: disable=broad-exception-caught
            # Justification: Odoo RPC and network errors can be unpredictable; catch-all
            # to ensure error reporting and graceful fallback.
            logger.error(f"Error executing {model}.{method}: {str(e)}")
            return None


def get_odoo_client():
    """
    Get a configured Odoo client instance

    Returns:
        OdooClient: A configured Odoo client instance
    """
    return OdooClient(config=Config())
