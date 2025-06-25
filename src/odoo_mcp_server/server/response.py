"""
Odoo MCP Server Response
"""

import json


class Response:
    """
    Standard response wrapper for OdooClient methods.
    """

    def __init__(self, data=None, error=None):
        self.data = data
        self.error = error
        self.success = error is None

    def to_dict(self):
        """
        Return the response as a dictionary with either 'data' or 'error' key.
        """
        if self.error is not None:
            return {"success": self.success, "error": self.error}
        return {"success": self.success, "data": self.data}

    def to_json_string(self, indent=2):
        """
        Return the response as a JSON string.
        """

        return json.dumps(self.to_dict(), indent=indent)
