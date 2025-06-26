# Odoo MCP Server

An MCP server implementation that integrates with Odoo ERP systems, enabling AI assistants to interact with Odoo data and functionality through the Model Context Protocol.

## Features

- **Comprehensive CRUD Operations**: Full Create, Read, Update, Delete functionality for Odoo records
- **Advanced Search Capabilities**: Powerful domain-based filtering and searching
- **Model Introspection**: Access to model definitions, fields, and metadata
- **Bulk Operations**: Efficient handling of multiple records at once
- **Resource System**: URI-based access to Odoo data structures and documentation
- **XML-RPC Communication**: Secure connection to Odoo instances via XML-RPC
- **Flexible Configuration**: Support for config files and environment variables
- **Error Handling**: Comprehensive custom exception system with detailed error context
- **Exception Hierarchy**: Structured exception classes for better error handling and debugging
- **Comprehensive Testing**: Full test coverage with pytest

## Tools

### Core CRUD Operations

- **create_record**: Create a single new record

  - Inputs: `model_name` (string), `values` (object)
  - Returns: Dictionary with created record ID

- **create_records**: Create multiple records at once

  - Inputs: `model_name` (string), `values_list` (array of objects)
  - Returns: Dictionary with created record IDs

- **read_records**: Read specific records by their IDs

  - Inputs: `model_name` (string), `ids` (array), `fields` (optional array)
  - Returns: Dictionary with record data

- **write_record**: Update a single record

  - Inputs: `model_name` (string), `record_id` (number), `values` (object)
  - Returns: Dictionary with operation result

- **write_records**: Update multiple records

  - Inputs: `model_name` (string), `record_ids` (array), `values` (object)
  - Returns: Dictionary with operation result

- **unlink_record**: Delete a single record

  - Inputs: `model_name` (string), `record_id` (number)
  - Returns: Dictionary with operation result

- **unlink_records**: Delete multiple records
  - Inputs: `model_name` (string), `record_ids` (array)
  - Returns: Dictionary with operation result

### Search and Query Operations

- **search_records**: Search for records with advanced filtering

  - Inputs: `model_name` (string), `domain` (array), `fields` (optional array), `limit` (optional number), `offset` (optional number), `order` (optional string)
  - Returns: Dictionary with matching records

- **search_ids**: Get only IDs of matching records

  - Inputs: `model_name` (string), `domain` (array), `offset` (optional number), `limit` (optional number), `order` (optional string)
  - Returns: Dictionary with list of IDs

- **search_count**: Count records matching a domain
  - Inputs: `model_name` (string), `domain` (array)
  - Returns: Dictionary with count

### Model Operations

- **get_model_fields**: Get field definitions for a model
  - Inputs: `model_name` (string), `query_field` (string)
  - Returns: Dictionary with field definitions

### Utility Operations

- **search_and_update**: Search and update records in one operation

  - Inputs: `model_name` (string), `domain` (array), `values` (object)
  - Returns: Dictionary with affected record count and IDs

- **call_method**: Call custom methods on models

  - Inputs: `model_name` (string), `method_name` (string), `args` (optional array), `kwargs` (optional object)
  - Returns: Dictionary with method result

## Resources

### Model Information

- **odoo://models/{model_name}/fields**: Field definitions for a specific model

### Documentation

- **odoo://help/domains**: Complete guide to Odoo domain syntax with examples
- **odoo://help/operations**: Documentation of all available MCP tools and workflows

## Domain Syntax Guide

Odoo uses domain syntax for filtering records. Here are common patterns:

### Basic Operators

- `["field", "=", value]` - Equals
- `["field", "!=", value]` - Not equals
- `["field", ">", value]` - Greater than
- `["field", ">=", value]` - Greater than or equal
- `["field", "<", value]` - Less than
- `["field", "<=", value]` - Less than or equal
- `["field", "in", [value1, value2]]` - In list
- `["field", "not in", [value1, value2]]` - Not in list
- `["field", "like", "pattern"]` - Contains (case sensitive)
- `["field", "ilike", "pattern"]` - Contains (case insensitive)

### Logical Operators

- `["&", condition1, condition2]` - AND (default between conditions)
- `["|", condition1, condition2]` - OR
- `["!", condition]` - NOT

## Configuration

### Odoo Connection Setup

1. Create a configuration file named `odoo_config.json`:

```json
{
  "url": "https://your-odoo-instance.com",
  "db": "your-database-name",
  "username": "your-username",
  "password": "your-password-or-api-key"
}
```

2. Alternatively, use environment variables:
   - `ODOO_URL`: Your Odoo server URL
   - `ODOO_DB`: Database name
   - `ODOO_USERNAME`: Login username
   - `ODOO_PASSWORD`: Password or API key
   - `ODOO_TIMEOUT`: Connection timeout in seconds (default: 30)
   - `ODOO_VERIFY_SSL`: Whether to verify SSL certificates (default: true)
   - `HTTP_PROXY`: Force the ODOO connection to use an HTTP proxy

### Logging Configuration

The server supports configurable logging levels via the `LOG_LEVEL` environment variable:

- `INFO` (default): Shows essential operational information
- `DEBUG`: Shows detailed debugging information including connection details and environment variables
- `WARNING`: Shows only warnings and errors
- `ERROR`: Shows only error messages

### Usage with Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "odoo": {
      "command": "uvx",
      "args": ["odoo-mcp-server"],
      "env": {
        "ODOO_URL": "https://your-odoo-instance.com",
        "ODOO_DB": "your-database-name",
        "ODOO_USERNAME": "your-username",
        "ODOO_PASSWORD": "your-password-or-api-key"
      }
    }
  }
}
```

## Installation

### Python Package

```bash
pip install odoo-mcp-server
```

### Running the Server

```bash
# Using the installed package
odoo-mcp-server

# Using the MCP development tools
uv run mcp dev src/odoo_mcp_server/__main__.py
```

## Build

Docker build:

```bash
docker build -t mcp/odoo:latest -f Dockerfile .
```

## Parameter Formatting Guidelines

When using the MCP tools for Odoo, pay attention to these parameter formatting guidelines:

1. **Domain Parameter**:

   - The following domain formats are supported:
     - List format: `[["field", "operator", value], ...]`
     - Object format: `{"conditions": [{"field": "...", "operator": "...", "value": "..."}]}`
     - JSON string of either format
   - Examples:
     - List format: `[["is_company", "=", true]]`
     - Object format: `{"conditions": [{"field": "date_order", "operator": ">=", "value": "2025-03-01"}]}`
     - Multiple conditions: `[["date_order", ">=", "2025-03-01"], ["date_order", "<=", "2025-03-31"]]`

2. **Fields Parameter**:
   - Should be an array of field names: `["name", "email", "phone"]`
   - The server will try to parse string inputs as JSON

## Exception System

The Odoo MCP Server features a comprehensive custom exception system that provides detailed error context and facilitates better debugging and error handling.

### Exception Hierarchy

```
OdooMCPError (Base)
├── OdooConnectionError
│   ├── ConnectionTimeoutError
│   ├── AuthenticationError
│   └── SSLVerificationError
├── ModelError
│   └── ModelNotFoundError
├── ServerError
│   ├── OdooRPCError
│   └── InternalServerError
└── MCPError
    ├── ResourceError
    └── ToolError
```

### Key Exception Features

- **Structured Error Information**: Each exception includes error codes, detailed messages, and contextual data
- **JSON Serialization**: All exceptions can be converted to JSON format for easy transmission
- **Exception Chaining**: Original exceptions are preserved while adding custom context
- **Automatic Error Wrapping**: Common Python exceptions are automatically wrapped with appropriate custom exceptions

### Example Exception Usage

```python
try:
    # Odoo operation that might fail
    result = odoo_client.get_model_info("nonexistent.model")
except ModelNotFoundError as e:
    print(f"Model error: {e.message}")
    print(f"Error code: {e.error_code}")
    print(f"Model name: {e.details['model_name']}")

    # Convert to JSON for API responses
    error_response = e.to_dict()
```

### Error Handling Best Practices

1. **Catch Specific Exceptions**: Use specific exception types rather than generic `Exception`
2. **Preserve Context**: Use the `details` parameter to add relevant context information
3. **Chain Exceptions**: Use `from` keyword to preserve original exception information
4. **Use Error Codes**: Leverage error codes for programmatic error handling

## License

This MCP server is licensed under the MIT License.
