"""
Test Fixtures and Configuration for Odoo MCP Server

This file contains pytest fixtures that provide:
- Mock objects for Odoo clients, MCP servers, and configurations
- Sample test data for models, fields, and records
- Environment variable mocking for testing
- Shared test setup used across all test modules

Note: This file is named 'conftest.py' because it's the standard pytest
configuration file that is automatically discovered by pytest.
"""

import os
from unittest.mock import Mock, patch

import pytest
from odoo_mcp_server.server.context import AppContext
from odoo_mcp_server.tools.odoo_client import OdooClient
from odoorpc.error import RPCError


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing"""
    env_vars = {
        "ODOO_URL": "https://test.odoo.com",
        "ODOO_DB": "test_db",
        "ODOO_USERNAME": "test_user",
        "ODOO_PASSWORD": "test_password",
        "ODOO_TIMEOUT": "30",
        "ODOO_VERIFY_SSL": "1",
        "LOG_LEVEL": "DEBUG",
    }

    original_environ = os.environ.copy()

    # Clear relevant environment variables
    for key in env_vars:
        if key in os.environ:
            del os.environ[key]

    # Set mock values
    for key, value in env_vars.items():
        os.environ[key] = value

    yield env_vars

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_environ)


@pytest.fixture
def mock_config():
    """Mock Config instance for testing"""
    # Create a mock config object instead of trying to create a real one
    config = Mock()
    config.url = "https://test.odoo.com"
    config.database = "test_db"
    config.username = "test_user"
    config.password = "test_password"
    config.timeout = 30
    config.verify_ssl = True
    return config


@pytest.fixture
def mock_odoo_client(mock_config):
    """Mock OdooClient for testing"""
    with patch.object(OdooClient, "_connect"):
        client = OdooClient(mock_config)

        # Mock the odoo connection object
        client.odoo = Mock()
        client.uid = 1

        # Create a defaultdict-like behavior for env
        def env_getitem(_self, _key):
            """Return a mock model for any key"""
            mock_model = Mock()
            # Set up default return values for common methods
            mock_model.search_read.return_value = []
            mock_model.search.return_value = []
            mock_model.search_count.return_value = 0
            mock_model.fields_get.return_value = {}
            mock_model.browse.return_value = Mock()
            mock_model.create.return_value = []
            return mock_model

        client.odoo.env.__getitem__ = env_getitem

        return client


@pytest.fixture
def mock_app_context(mock_odoo_client):
    """Mock application context for testing"""
    return AppContext(odoo=mock_odoo_client)


@pytest.fixture
def mock_mcp_server(mock_app_context):
    """Mock MCP server with context for testing"""
    mock_mcp = Mock()
    mock_context = Mock()
    mock_request_context = Mock()
    mock_request_context.lifespan_context = mock_app_context
    mock_context.request_context = mock_request_context
    mock_mcp.get_context = Mock(return_value=mock_context)

    return mock_mcp


@pytest.fixture
def sample_model_data():
    """Sample model data for testing"""
    return [
        {"model": "res.partner", "name": "Contact"},
        {"model": "res.partner.bank", "name": "Bank Account"},
        {"model": "product.template", "name": "Product Template"},
    ]


@pytest.fixture
def sample_field_data():
    """Sample field data for testing"""
    return {
        "name": {
            "string": "Name",
            "type": "char",
            "required": True,
            "readonly": False,
            "searchable": True,
            "relation": False,
        },
        "email": {
            "string": "Email",
            "type": "char",
            "required": False,
            "readonly": False,
            "searchable": True,
            "relation": False,
        },
        "partner_id": {
            "string": "Partner",
            "type": "many2one",
            "required": False,
            "readonly": False,
            "searchable": True,
            "relation": "res.partner",
        },
    }


@pytest.fixture
def sample_record_data():
    """Sample record data for testing"""
    return [
        {"id": 1, "name": "Test Company", "email": "test@example.com"},
        {"id": 2, "name": "Another Company", "email": "another@example.com"},
    ]


@pytest.fixture
def sample_domain():
    """Sample search domain for testing"""
    return [("is_company", "=", True)]


@pytest.fixture
def mock_rpc_error():
    """Mock RPC error for testing error handling"""
    error = Mock(spec=RPCError)
    error.info = {"type": "access_denied", "message": "Access denied"}
    return error


@pytest.fixture
def mock_odoo_client_tools():
    """Mock OdooClient with Mock methods for tools testing"""
    mock_client = Mock()

    # Create Mock methods that support return_value and side_effect
    mock_client.search_models = Mock()
    mock_client.get_model_info = Mock()
    mock_client.get_model_fields = Mock()
    mock_client.search_read = Mock()
    mock_client.read_records = Mock()
    mock_client.create_records = Mock()
    mock_client.write_records = Mock()
    mock_client.unlink_records = Mock()
    mock_client.search_ids = Mock()
    mock_client.search_count = Mock()
    mock_client.call_method = Mock()
    mock_client.execute_method = Mock()

    return mock_client


@pytest.fixture
def mock_mcp_server_for_tools(mock_odoo_client_tools):
    """Mock MCP server with mock client for tools testing"""
    mock_mcp = Mock()
    mock_context = Mock()
    mock_request_context = Mock()
    mock_lifespan_context = Mock()
    mock_lifespan_context.odoo = mock_odoo_client_tools
    mock_request_context.lifespan_context = mock_lifespan_context
    mock_context.request_context = mock_request_context
    mock_mcp.get_context = Mock(return_value=mock_context)

    return mock_mcp
