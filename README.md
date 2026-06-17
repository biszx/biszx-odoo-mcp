# Odoo MCP Server

An MCP server implementation for Odoo ERP systems, providing a set of tools for managing Odoo records, models, and custom methods.
Inspired by [tuanle96/mcp-odoo](https://github.com/tuanle96/mcp-odoo).

## Tools

All tools support an optional `save_to` parameter to save results to a JSON file.

### Data Retrieval

- **search_records**: Search for records with advanced filtering
  - Inputs: `model_name` (string), `domain` (array), `fields` (optional array), `limit` (optional number), `offset` (optional number), `order` (optional string)
  - Returns: Dictionary with matching records

- **search_ids**: Get only IDs of matching records
  - Inputs: `model_name` (string), `domain` (array), `offset` (optional number), `limit` (optional number), `order` (optional string)
  - Returns: Dictionary with list of IDs

- **search_count**: Count records matching a domain
  - Inputs: `model_name` (string), `domain` (array)
  - Returns: Dictionary with count

- **read_records**: Read specific records by their IDs
  - Inputs: `model_name` (string), `ids` (array of ints), `fields` (optional array)
  - Returns: Dictionary with record data

- **read_group**: Group and aggregate records
  - Inputs: `model_name` (string), `domain` (array), `fields` (array with optional aggregations), `groupby` (array), `offset` (optional number), `limit` (optional number), `order` (optional string)
  - Returns: Dictionary with grouped results

### Data Modification

- **create_records**: Create records
  - Inputs: `model_name` (string), `values_list` (array of objects)
  - Returns: Dictionary with created record IDs

- **write_records**: Update records by ID
  - Inputs: `model_name` (string), `record_ids` (array of ints), `values` (object)
  - Returns: Dictionary with operation result

- **search_and_write**: Search for records, then update matched records
  - Inputs: `model_name` (string), `domain` (array), `values` (object)
  - Returns: Dictionary with affected record count and IDs

- **unlink_records**: Delete records by ID
  - Inputs: `model_name` (string), `record_ids` (array of ints)
  - Returns: Dictionary with operation result

- **search_and_unlink**: Search for records, then delete matched records
  - Inputs: `model_name` (string), `domain` (array)
  - Returns: Dictionary with affected record count and IDs

### Model Metadata

- **search_models**: Search for available models
  - Inputs: `query` (string) — search term for model names and display names
  - Returns: Dictionary with matching models

- **get_model_info**: Get information about a specific model
  - Inputs: `model_name` (string)
  - Returns: Dictionary with model information

- **get_model_fields**: Get field definitions for a model
  - Inputs: `model_name` (string), `query_field` (string) — search term for field names and labels
  - Returns: Dictionary with field definitions

### Utility

- **get_current_user**: Retrieve information about the currently authenticated Odoo user
  - Inputs: `fields` (optional array of strings)
  - Returns: Dictionary with current user data

- **call_method**: Call an arbitrary method on a model
  - Inputs: `model_name` (string), `method_name` (string), `args` (optional array), `kwargs` (optional object)
  - Returns: Dictionary with method result

## Resources

### Model Information

- **odoo://models/search/{query}**: Search for models by name or description
- **odoo://models/{model_name}/info**: Information about a specific model
- **odoo://models/{model_name}/fields**: Field definitions for a specific model

### Documentation

- **odoo://help/domains**: Complete guide to Odoo domain syntax with examples
- **odoo://help/operations**: Documentation of all available MCP tools and workflows

## Configuration

### Odoo Connection Setup

To connect to your Odoo instance, set the following environment variables:

- `ODOO_URL`: Your Odoo server URL
- `ODOO_DB`: Database name
- `ODOO_USERNAME`: Login username
- `ODOO_PASSWORD`: Password or API key
- `ODOO_TIMEOUT`: Connection timeout in seconds (default: 30)
- `ODOO_VERIFY_SSL`: Whether to verify SSL certificates (default: true)
- `LOG_LEVEL`: Logging level (default: INFO)

### Usage with Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "odoo": {
      "command": "uvx",
      "args": ["biszx-odoo-mcp"],
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
pip install biszx-odoo-mcp
```

### Running the Server

```bash
# Using the installed package
biszx-odoo-mcp

# Using uv for development
uv run biszx-odoo-mcp

# Using the MCP development tools
uv run mcp dev src/biszx_odoo_mcp/main.py
```

## License

This MCP server is licensed under the MIT License.
