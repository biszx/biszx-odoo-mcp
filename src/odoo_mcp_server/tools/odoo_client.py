"""
Odoo JSON-RPC client for MCP server integration
"""

import urllib.parse

import odoorpc
from loguru import logger

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
            Dictionary with model information

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> models = client.get_models()
            >>> print(len(models['model_names']))
            125
            >>> print(models['model_names'][:5])
            ['res.partner', 'res.users', 'res.company', 'res.groups', 'ir.model']
        """
        model_ids = self._execute("ir.model", "search", [])
        if not model_ids:
            raise ValueError("No models found")
        result = self._execute("ir.model", "read", model_ids, ["model", "name"])
        if result is None:
            raise ValueError("Failed to read models")
        models = sorted([rec["model"] for rec in result])
        return {
            "model_names": models,
            "models_details": {
                rec["model"]: {"name": rec.get("name", "")} for rec in result
            },
        }

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
            raise ValueError(f"Model {model_name} not found")
        return result[0]

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
            raise ValueError(f"Failed to get fields for {model_name}")
        return fields

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
            raise ValueError("Failed to search and read records")
        return result

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
            raise ValueError("Failed to read records")
        return result

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
        result = self._execute(model_name, "create", values)
        if result is None:
            raise ValueError("Failed to create record")
        return result

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
        result = self._execute(model_name, "create", values_list)
        if result is None:
            raise ValueError("Failed to create records")
        return result

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
        result = self._execute(model_name, "write", record_ids, values)
        if result is None:
            raise ValueError("Failed to write records")
        return result

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
        result = self._execute(model_name, "unlink", record_ids)
        if result is None:
            raise ValueError("Failed to unlink records")
        return result

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
        result = self._execute(model_name, "search_count", domain)
        if result is None:
            raise ValueError("Failed to count records")
        return result

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
        args = [domain]
        if offset is not None:
            args.append(offset)
        if limit is not None:
            args.append(limit)
        if order is not None:
            args.append(order)

        result = self._execute(model_name, "search", *args)
        if result is None:
            raise ValueError("Failed to search record IDs")
        return result

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
            result = self._execute(model_name, method_name, *args, **kwargs)
            if result is None:
                raise ValueError(f"Failed to call method {method_name}")
            return result
        except Exception as e:
            raise ValueError(f"Error calling method {method_name}: {str(e)}") from e

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
            version_info = self.odoo.version
            server_info = {
                "server_version": version_info.get("server_version", "Unknown"),
                "server_serie": version_info.get("server_serie", "Unknown"),
                "protocol_version": version_info.get("protocol_version", "Unknown"),
                "database": self.config.db,
                "hostname": self.hostname,
            }
            return server_info
        except Exception as e:
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
                result = self._execute(
                    "res.users",
                    "read",
                    [self.uid],
                    {"fields": ["name", "login", "email", "company_id", "groups_id"]},
                )
                if result:
                    return result[0]
            raise ValueError("Failed to get user info")
        except Exception as e:
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
            # Get current user's company
            user_info = self._execute(
                "res.users", "read", [self.uid], {"fields": ["company_id"]}
            )
            if user_info and user_info[0].get("company_id"):
                company_id = user_info[0]["company_id"][0]
                company_info = self._execute(
                    "res.company",
                    "read",
                    [company_id],
                    {
                        "fields": [
                            "name",
                            "email",
                            "phone",
                            "website",
                            "vat",
                            "country_id",
                            "currency_id",
                        ]
                    },
                )
                if company_info:
                    return company_info[0]
            raise ValueError("Failed to get company info")
        except Exception as e:
            raise ValueError(f"Error getting company info: {str(e)}") from e

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
            result = self._execute(model_name, "copy", record_id, default_values)
            if result is None:
                raise ValueError("Failed to copy record")
            return result
        except Exception as e:
            raise ValueError(f"Error copying record: {str(e)}") from e

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
            result = self._execute(
                model_name, "check_access_rights", operation, raise_exception
            )
            return result
        except Exception as e:
            raise ValueError(f"Error checking access rights: {str(e)}") from e

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
        # Search for models that match the query
        domain = ["|", ("model", "ilike", query), ("name", "ilike", query)]

        matching_models = self._execute(
            "ir.model", "search_read", domain, {"fields": ["model", "name", "info"]}
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

    def _execute(self, model, method, *args, **kwargs):
        """Execute a method on an Odoo model via OdooRPC"""
        try:
            return self.odoo.execute(model, method, *args, **kwargs)
        except Exception as e:  # pylint: disable=broad-exception-caught
            # Justification: Odoo RPC and network errors can be unpredictable; catch-all
            # to ensure error reporting and graceful fallback.
            logger.error(f"Error executing {model}.{method}: {str(e)}")
            raise ValueError(f"Error executing {model}.{method}: {str(e)}") from e


def get_odoo_client():
    """
    Get a configured Odoo client instance

    Returns:
        OdooClient: A configured Odoo client instance
    """
    return OdooClient(config=Config())
