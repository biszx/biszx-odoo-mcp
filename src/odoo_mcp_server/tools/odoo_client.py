"""
Odoo client for interacting with Odoo via JSON-RPC using OdooRPC library.

TABLE OF CONTENTS:
=================

1. INITIALIZATION AND CONNECTION MANAGEMENT
   - __init__()
   - _connect()
   - _ensure_connected()

2. MODEL INTROSPECTION
   - get_models()
   - get_model_info()
   - get_model_fields()
   - search_models()

3. SEARCH AND READ OPERATIONS
   - search_ids()
   - search_count()
   - search_read()
   - read_records()

4. CRUD OPERATIONS
   - create_record()
   - create_records()
   - write_records()
   - unlink_records()
   - copy_record()

5. ACCESS CONTROL
   - check_access_rights()

6. SYSTEM INFORMATION
   - get_server_info()
   - get_user_info()
   - get_company_info()

7. GENERIC METHOD EXECUTION
   - execute_method()
   - call_method()
"""

import urllib.parse
from typing import Optional

import odoorpc
from loguru import logger
from odoorpc.error import InternalError, RPCError
from odoorpc.rpc.error import ConnectorError

from odoo_mcp_server.exceptions import (
    AuthenticationError,
    ConnectionTimeoutError,
    InternalServerError,
    InvalidDataError,
    ModelNotFoundError,
    OdooRPCError,
)
from odoo_mcp_server.tools.config import Config


class OdooClient:
    """
    Client for interacting with Odoo via JSON-RPC
    """

    # ============================================================================
    # INITIALIZATION AND CONNECTION MANAGEMENT
    # ============================================================================

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
        self.odoo: Optional[odoorpc.ODOO] = None  # Will be initialized in _connect
        self.uid: Optional[int] = None  # Will be set after login
        self._connect()

    def _ensure_connected(self) -> odoorpc.ODOO:
        """Ensure we have a valid connection"""
        if self.odoo is None:
            raise InternalServerError("Not connected to Odoo")
        return self.odoo

    def _connect(self):
        """Initialize the OdooRPC connection and authenticate"""
        logger.debug(f"Connecting to Odoo at: {self.config.url}")
        logger.debug(f"Database: {self.config.db}, User: {self.config.username}")

        try:
            # Determine protocol and port based on URL scheme
            is_https = self.config.url.startswith("https://")
            protocol = "jsonrpc+ssl" if is_https else "jsonrpc"
            port = 443 if is_https else 80

            self.odoo = odoorpc.ODOO(
                self.hostname,
                protocol=protocol,
                port=port,
                timeout=self.config.timeout,
                version=None,
            )
            self.odoo.login(self.config.db, self.config.username, self.config.password)

            # Get user ID for later use
            odoo_conn = self._ensure_connected()
            user_model = odoo_conn.env["res.users"]  # type: ignore
            user_records = user_model.search([("login", "=", self.config.username)])
            self.uid = user_records[0] if user_records else None

            logger.info("✅ Successfully connected to Odoo")

        except (RPCError, InternalError, ConnectorError) as e:
            # Log connection errors as they're important for debugging
            logger.error(f"🔴 Failed to connect to Odoo: {str(e)}")

            # Check specific error types and raise appropriate custom exceptions
            error_msg = str(e).lower()
            if isinstance(e, RPCError):
                if "access" in error_msg or "denied" in error_msg:
                    raise AuthenticationError(
                        f"Authentication failed: {str(e)}",
                        username=self.config.username,
                        database=self.config.db,
                    ) from e
                raise OdooRPCError(f"RPC error: {str(e)}") from e
            if isinstance(e, ConnectorError):
                raise ConnectionTimeoutError(
                    f"Connection failed: {str(e)}", timeout=self.config.timeout
                ) from e
            raise InternalServerError(f"Internal error: {str(e)}") from e

    # ============================================================================
    # MODEL INTROSPECTION
    # ============================================================================

    def get_models(self):
        """
        Get a list of all available models in the system

        Returns:
            Dictionary with model information

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> models = client.get_models()
            >>> print(len(models['model_names']))
            125
            >>> print(models['model_names'][:5])
            ['res.partner', 'res.users', 'res.company', 'res.groups', 'ir.model']
        """
        try:
            odoo_conn = self._ensure_connected()
            IrModel = odoo_conn.env["ir.model"]  # type: ignore
            model_records = IrModel.search_read([], ["model", "name"])

            if not model_records:
                raise InvalidDataError("No models found in the system")

            models = sorted([rec["model"] for rec in model_records])
            return {
                "model_names": models,
                "models_details": {
                    rec["model"]: {"name": rec.get("name", "")} for rec in model_records
                },
            }
        except RPCError as e:
            raise OdooRPCError(f"Failed to get models: {str(e)}") from e

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
        try:
            odoo_conn = self._ensure_connected()
            IrModel = odoo_conn.env["ir.model"]  # type: ignore
            result = IrModel.search_read(
                [("model", "=", model_name)], ["name", "model"]
            )
            if not result:
                raise ModelNotFoundError(model_name)
            return result[0]
        except RPCError as e:
            raise OdooRPCError(f"Failed to get model info: {str(e)}") from e

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
        try:
            odoo_conn = self._ensure_connected()
            Model = odoo_conn.env[model_name]  # type: ignore
            fields = Model.fields_get()
            if fields is None:
                raise ValueError(f"Failed to get fields for {model_name}")
            return fields
        except RPCError as e:
            raise ValueError(f"Failed to get fields for {model_name}: {str(e)}") from e

    def search_models(self, query):
        """
        Search for models that match a query term

        This searches through model names and display names to find models that
        match the given query term.

        Args:
            query: Search term to find models (searches in model name and display name)

        Returns:
            Dictionary with search results

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> results = client.search_models('partner')
            >>> print(results['found_models'])
            3
            >>> print([m['model'] for m in results['models']])
            ['res.partner', 'res.partner.bank', 'res.partner.category']
        """
        try:
            # Search for models that match the query
            domain = ["|", ("model", "ilike", query), ("name", "ilike", query)]

            odoo_conn = self._ensure_connected()
            IrModel = odoo_conn.env["ir.model"]  # type: ignore
            matching_models = IrModel.search_read(
                domain, {"fields": ["model", "name", "info"]}
            )

            if matching_models is None:
                raise ValueError("Failed to search models")

            # Format the results
            return {
                "query": query,
                "found_models": len(matching_models),
                "models": [
                    {
                        "model": model["model"],
                        "name": model["name"],
                        "info": model.get("info", ""),
                    }
                    for model in matching_models
                ],
            }
        except RPCError as e:
            raise ValueError(f"RPC error searching models: {str(e)}") from e
        except InternalError as e:
            raise ValueError(f"Internal error searching models: {str(e)}") from e

    # ============================================================================
    # SEARCH AND READ OPERATIONS
    # ============================================================================

    def search_ids(self, model_name, domain, offset=None, limit=None, order=None):
        """
        Search for record IDs that match a domain

        Args:
            model_name: Name of the model (e.g., 'res.partner')
            domain: Search domain (e.g., [('is_company', '=', True)])
            offset: Number of records to skip
            limit: Maximum number of records to return
            order: Sorting criteria (e.g., 'name ASC, id DESC')

        Returns:
            List of matching record IDs

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> ids = client.search_ids(
            ...     'res.partner', [('is_company', '=', True)], limit=5
            ... )
            >>> print(ids)
            [1, 2, 3, 4, 5]
        """
        try:
            odoo_conn = self._ensure_connected()
            Model = odoo_conn.env[model_name]  # type: ignore

            # Build search kwargs
            search_kwargs = {}
            if offset is not None:
                search_kwargs["offset"] = offset
            if limit is not None:
                search_kwargs["limit"] = limit
            if order is not None:
                search_kwargs["order"] = order

            result = Model.search(domain, **search_kwargs)
            if result is None:
                raise ValueError("Failed to search record IDs")
            return result
        except RPCError as e:
            raise ValueError(f"Failed to search record IDs: {str(e)}") from e

    def search_count(self, model_name, domain):
        """
        Count records that match a search domain

        Args:
            model_name: Name of the model (e.g., 'res.partner')
            domain: Search domain (e.g., [('is_company', '=', True)])

        Returns:
            Integer count of matching records

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> count = client.search_count('res.partner', [('is_company', '=', True)])
            >>> print(count)
            25
        """
        try:
            odoo_conn = self._ensure_connected()
            Model = odoo_conn.env[model_name]  # type: ignore
            result = Model.search_count(domain)
            if result is None:
                raise ValueError("Failed to count records")
            return result
        except RPCError as e:
            raise ValueError(f"Failed to count records: {str(e)}") from e

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
        try:
            odoo_conn = self._ensure_connected()
            Model = odoo_conn.env[model_name]  # type: ignore

            # Build search_read arguments
            search_kwargs = {}
            if offset is not None:
                search_kwargs["offset"] = offset
            if fields is not None:
                search_kwargs["fields"] = fields
            if limit is not None:
                search_kwargs["limit"] = limit
            if order is not None:
                search_kwargs["order"] = order

            result = Model.search_read(domain, **search_kwargs)
            if result is None:
                raise ValueError("Failed to search and read records")
            return result
        except RPCError as e:
            raise ValueError(f"Failed to search and read records: {str(e)}") from e

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
        try:
            odoo_conn = self._ensure_connected()
            Model = odoo_conn.env[model_name]  # type: ignore

            if fields is not None:
                result = Model.browse(ids).read(fields)
            else:
                result = Model.browse(ids).read()

            if result is None:
                raise ValueError("Failed to read records")
            return result
        except RPCError as e:
            raise ValueError(f"Failed to read records: {str(e)}") from e

    # ============================================================================
    # CRUD OPERATIONS
    # ============================================================================

    def create_record(self, model_name, values):
        """
        Create a new record in an Odoo model

        Args:
            model_name: Name of the model (e.g., 'res.partner')
            values: Dictionary with field values for the new record

        Returns:
            The created record ID

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> record_id = client.create_record('res.partner', {'name': 'New Company'})
            >>> print(record_id)
            42
        """
        try:
            odoo_conn = self._ensure_connected()
            Model = odoo_conn.env[model_name]  # type: ignore
            result = Model.create(values)
            if result is None:
                raise ValueError("Failed to create record")
            return result
        except RPCError as e:
            raise ValueError(f"Failed to create record: {str(e)}") from e

    def create_records(self, model_name, values_list):
        """
        Create multiple records in an Odoo model

        Args:
            model_name: Name of the model (e.g., 'res.partner')
            values_list: List of dictionaries with field values for the new records

        Returns:
            List of created record IDs

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> record_ids = client.create_records('res.partner', [
                    {'name': 'Company 1'}, {'name': 'Company 2'}
                ])
            >>> print(record_ids)
            [42, 43]
        """
        try:
            odoo_conn = self._ensure_connected()
            Model = odoo_conn.env[model_name]  # type: ignore
            result = Model.create(values_list)
            if result is None:
                raise ValueError("Failed to create records")
            return result
        except RPCError as e:
            raise ValueError(f"Failed to create records: {str(e)}") from e

    def write_records(self, model_name, record_ids, values):
        """
        Update records in an Odoo model

        Args:
            model_name: Name of the model (e.g., 'res.partner')
            record_ids: List of record IDs to update
            values: Dictionary with field values to update

        Returns:
            Boolean indicating success

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> success = client.write_records(
            ...     'res.partner', [1], {'name': 'Updated Name'}
            ... )
            >>> print(success)
            True
        """
        try:
            odoo_conn = self._ensure_connected()
            Model = odoo_conn.env[model_name]  # type: ignore
            records = Model.browse(record_ids)
            result = records.write(values)
            if result is None:
                raise ValueError("Failed to write records")
            return result
        except RPCError as e:
            raise ValueError(f"Failed to write records: {str(e)}") from e

    def unlink_records(self, model_name, record_ids):
        """
        Delete records from an Odoo model

        Args:
            model_name: Name of the model (e.g., 'res.partner')
            record_ids: List of record IDs to delete

        Returns:
            Boolean indicating success

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> success = client.unlink_records('res.partner', [42])
            >>> print(success)
            True
        """
        try:
            odoo_conn = self._ensure_connected()
            Model = odoo_conn.env[model_name]  # type: ignore
            records = Model.browse(record_ids)
            result = records.unlink()
            if result is None:
                raise ValueError("Failed to unlink records")
            return result
        except RPCError as e:
            raise ValueError(f"Failed to unlink records: {str(e)}") from e

    def copy_record(self, model_name, record_id, default_values=None):
        """
        Copy a record with optional default values

        Args:
            model_name: Name of the model (e.g., 'res.partner')
            record_id: ID of the record to copy
            default_values: Dictionary with default values for the copied record

        Returns:
            The copied record ID

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> new_id = client.copy_record(
            ...     'res.partner', 1, {'name': 'Copy of Company'}
            ... )
            >>> print(new_id)
            43
        """
        try:
            if default_values is None:
                default_values = {}
            odoo_conn = self._ensure_connected()
            model_proxy = odoo_conn.env[model_name]  # type: ignore
            record = model_proxy.browse(record_id)
            result = record.copy(default_values)
            if result is None:
                raise ValueError("Failed to copy record")
            return result.id
        except RPCError as e:
            raise ValueError(f"RPC error copying record: {str(e)}") from e
        except InternalError as e:
            raise ValueError(f"Internal error copying record: {str(e)}") from e

    # ============================================================================
    # ACCESS CONTROL
    # ============================================================================

    def check_access_rights(self, model_name, operation, raise_exception=False):
        """
        Check access rights for a model operation

        Args:
            model_name: Name of the model (e.g., 'res.partner')
            operation: Operation to check ('read', 'write', 'create', 'unlink')
            raise_exception: Whether to raise exception if access denied

        Returns:
            Boolean indicating if user has access

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> has_access = client.check_access_rights('res.partner', 'read')
            >>> print(has_access)
            True
        """
        try:
            odoo_conn = self._ensure_connected()
            model_proxy = odoo_conn.env[model_name]  # type: ignore
            result = model_proxy.check_access_rights(operation, raise_exception)
            return result
        except RPCError as e:
            raise ValueError(f"RPC error checking access rights: {str(e)}") from e
        except InternalError as e:
            raise ValueError(f"Internal error checking access rights: {str(e)}") from e

    # ============================================================================
    # SYSTEM INFORMATION
    # ============================================================================

    def get_server_info(self):
        """
        Get information about the Odoo server

        Returns:
            Dictionary with server information

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> info = client.get_server_info()
            >>> print(info['server_version'])
            '16.0'
        """
        try:
            odoo_conn = self._ensure_connected()
            version_info = odoo_conn.version  # type: ignore
            server_info = {
                "server_version": version_info.get("server_version", "Unknown"),
                "server_serie": version_info.get("server_serie", "Unknown"),
                "protocol_version": version_info.get("protocol_version", "Unknown"),
                "database": self.config.db,
                "hostname": self.hostname,
            }
            return server_info
        except RPCError as e:
            raise ValueError(f"Failed to get server info: {str(e)}") from e

    def get_user_info(self):
        """
        Get information about the current user

        Returns:
            Dictionary with user information

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> info = client.get_user_info()
            >>> print(info['name'])
            'Administrator'
        """
        try:
            if self.uid:
                odoo_conn = self._ensure_connected()
                ResUsers = odoo_conn.env["res.users"]  # type: ignore
                user = ResUsers.browse(self.uid)
                result = user.read(
                    ["name", "login", "email", "company_id", "groups_id"]
                )
                if result:
                    return result[0]
            raise ValueError("Failed to get user info")
        except RPCError as e:
            raise ValueError(f"Error getting user info: {str(e)}") from e

    def get_company_info(self):
        """
        Get information about the current company

        Returns:
            Dictionary with company information

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> info = client.get_company_info()
            >>> print(info['name'])
            'YourCompany'
        """
        try:
            odoo_conn = self._ensure_connected()
            ResUsers = odoo_conn.env["res.users"]  # type: ignore
            ResCompany = odoo_conn.env["res.company"]  # type: ignore

            # Get current user's company
            user = ResUsers.browse(self.uid)
            user_info = user.read(["company_id"])

            if user_info and user_info[0].get("company_id"):
                company_id = user_info[0]["company_id"][0]
                company = ResCompany.browse(company_id)
                company_info = company.read(
                    [
                        "name",
                        "email",
                        "phone",
                        "website",
                        "vat",
                        "country_id",
                        "currency_id",
                    ]
                )
                if company_info:
                    return company_info[0]
            raise ValueError("Failed to get company info")
        except RPCError as e:
            raise ValueError(f"Error getting company info: {str(e)}") from e

    # ============================================================================
    # GENERIC METHOD EXECUTION
    # ============================================================================

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
        try:
            odoo_conn = self._ensure_connected()
            model_proxy = odoo_conn.env[model]  # type: ignore
            # Use getattr to dynamically call the method on the model proxy
            method_func = getattr(model_proxy, method)
            return method_func(*args, **kwargs)
        except RPCError as e:
            raise ValueError(f"RPC error executing {model}.{method}: {str(e)}") from e
        except InternalError as e:
            raise ValueError(
                f"Internal error executing {model}.{method}: {str(e)}"
            ) from e
        except AttributeError as e:
            raise ValueError(
                f"Method {method} not found on model {model}: {str(e)}"
            ) from e

    def call_method(self, model_name, method_name, args, kwargs):
        """
        Call a custom method on an Odoo model

        Args:
            model_name: Name of the model (e.g., 'res.partner')
            method_name: Name of the method to call
            args: Positional arguments to pass to the method
            kwargs: Keyword arguments to pass to the method

        Returns:
            Method result

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> result = client.call_method('res.partner', 'name_get', [1], {})
            >>> print(result)
            [(1, 'YourCompany')]
        """
        try:
            odoo_conn = self._ensure_connected()
            model_proxy = odoo_conn.env[model_name]  # type: ignore
            # Use getattr to dynamically call the method on the model proxy
            method_func = getattr(model_proxy, method_name)
            result = method_func(*args, **kwargs)
            if result is None:
                raise ValueError(f"Failed to call method {method_name}")
            return result
        except RPCError as e:
            raise ValueError(f"RPC error calling {method_name}: {str(e)}") from e
        except InternalError as e:
            raise ValueError(f"Internal error calling {method_name}: {str(e)}") from e
        except AttributeError as e:
            raise ValueError(f"Method {method_name} not found: {str(e)}") from e


def get_odoo_client():
    """
    Get a configured Odoo client instance

    Returns:
        OdooClient: A configured Odoo client instance
    """
    return OdooClient(config=Config())
