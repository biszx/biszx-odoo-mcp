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

- **get_odoo_models**: Get list of all available models

  - Returns: Dictionary with model information

- **get_model_info**: Get information about a specific model

  - Inputs: `model_name` (string)
  - Returns: Dictionary with model information

- **get_model_fields**: Get field definitions for a model
  - Inputs: `model_name` (string)
  - Returns: Dictionary with field definitions

### System Information

- **get_server_info**: Get Odoo server information

  - Returns: Dictionary with server details

- **get_user_info**: Get current user information

  - Returns: Dictionary with user details

- **get_company_info**: Get current company information
  - Returns: Dictionary with company details

### Utility Operations

- **bulk_operation**: Perform bulk operations

  - Inputs: `operation` (string: 'create' or 'unlink'), `model_name` (string), `data` (array)
  - Returns: Dictionary with operation results

- **search_and_update**: Search and update records in one operation

  - Inputs: `model_name` (string), `domain` (array), `values` (object)
  - Returns: Dictionary with affected record count and IDs

- **copy_record**: Copy a record with optional defaults

  - Inputs: `model_name` (string), `record_id` (number), `default_values` (optional object)
  - Returns: Dictionary with copied record ID

- **check_access_rights**: Check access rights for operations

  - Inputs: `model_name` (string), `operation` (string), `raise_exception` (optional boolean)
  - Returns: Dictionary with access rights information

- **call_method**: Call custom methods on models

  - Inputs: `model_name` (string), `method_name` (string), `args` (optional array), `kwargs` (optional object)
  - Returns: Dictionary with method result

- **get_record_history**: Get change history for a record (requires audit module)
  - Inputs: `model_name` (string), `record_id` (number)
  - Returns: Dictionary with change history

## Resources

### Model Information

- **odoo://models/list**: Complete list of all available models with descriptions
- **odoo://models/{model_name}/fields**: Field definitions for a specific model
- **odoo://models/{model_name}/info**: Information about a specific model
- **odoo://models/common**: Information about commonly used Odoo models

### System Information

- **odoo://server/info**: Odoo server information
- **odoo://user/info**: Current user information
- **odoo://company/info**: Current company information

### Documentation

- **odoo://help/domains**: Complete guide to Odoo domain syntax with examples
- **odoo://help/operations**: Documentation of all available MCP tools and workflows

## Common Use Cases

### Creating Records

```python
# Create a new customer
await create_record("res.partner", {
    "name": "Acme Corporation",
    "email": "contact@acme.com",
    "is_company": True
})

# Create multiple products at once
await create_records("product.template", [
    {"name": "Product A", "list_price": 100.0},
    {"name": "Product B", "list_price": 150.0}
])
```

### Searching and Filtering

```python
# Find all companies
await search_records("res.partner", [["is_company", "=", True]], fields=["name", "email"])

# Search for products in a price range
await search_records("product.template", [
    ["list_price", ">=", 10.0],
    ["list_price", "<=", 100.0]
], limit=20)

# Count active users
await search_count("res.users", [["active", "=", True]])
```

### Updating Records

```python
# Update a single customer's email
await write_record("res.partner", 42, {"email": "newemail@acme.com"})

# Bulk update: deactivate all draft sales orders
await search_and_update("sale.order", [["state", "=", "draft"]], {"active": False})
```

### Advanced Operations

```python
# Copy a product with new name
await copy_record("product.template", 1, {"name": "Copy of Original Product"})

# Check if user can create partners
await check_access_rights("res.partner", "create")
```

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

### Examples

```python
# Companies with Gmail email
[["is_company", "=", True], ["email", "ilike", "gmail"]]

# Products between $10-100 OR on sale
["|",
 ["&", ["list_price", ">=", 10], ["list_price", "<=", 100]],
 ["on_sale", "=", True]]

# Not draft invoices
[["!", ["state", "=", "draft"]]]
```

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

- `INFO` (default): Shows essential operational information with friendly emojis
- `DEBUG`: Shows detailed debugging information including connection details and environment variables
- `WARNING`: Shows only warnings and errors
- `ERROR`: Shows only error messages

Example usage:

```bash
# Default info level with friendly emojis
python -m odoo_mcp_server

# Debug level for troubleshooting
LOG_LEVEL=DEBUG python -m odoo_mcp_server

# Minimal logging
LOG_LEVEL=WARNING python -m odoo_mcp_server
```

### Usage with Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "odoo": {
      "command": "python",
      "args": ["-m", "odoo_mcp"],
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

### Docker

```json
{
  "mcpServers": {
    "odoo": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "ODOO_URL",
        "-e",
        "ODOO_DB",
        "-e",
        "ODOO_USERNAME",
        "-e",
        "ODOO_PASSWORD",
        "mcp/odoo"
      ],
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
pip install odoo-mcp
```

### Running the Server

```bash
# Using the installed package
odoo-mcp

# Using the MCP development tools
mcp dev odoo_mcp/server.py

# With additional dependencies
mcp dev odoo_mcp/server.py --with pandas --with numpy

# Mount local code for development
mcp dev odoo_mcp/server.py --with-editable .
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
├── ConnectionError
│   ├── ConnectionTimeoutError
│   ├── AuthenticationError
│   └── SSLVerificationError
├── ModelError
│   ├── ModelNotFoundError
│   ├── FieldNotFoundError
│   └── InvalidModelError
├── DataError
│   ├── RecordNotFoundError
│   ├── ValidationError
│   ├── AccessDeniedError
│   └── InvalidDataError
├── ServerError
│   ├── OdooRPCError
│   ├── InternalServerError
│   └── ConfigurationError
└── MCPError
    ├── ResourceError
    ├── ToolError
    └── ContextError
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
