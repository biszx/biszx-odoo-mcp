"""
Odoo MCP Server Response
"""


class Response:
    """
    Standard response wrapper for OdooClient methods.
    """

    success: bool
    data: dict | None
    error: str | None

    def __init__(self, data=None, error=None):
        self.data = data
        self.error = error

    def to_dict(self):
        """Return the response as a dictionary with either 'data' or 'error' key."""
        if self.error is not None:
            return {"success": False, "error": self.error}
        return {"success": True, "data": self.data}
