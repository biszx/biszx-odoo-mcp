"""
Custom exception classes for Odoo MCP Server.

This module defines a comprehensive hierarchy of custom exceptions for better
error handling and debugging in the Odoo MCP Server application.

Exception Hierarchy:
===================

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
│   ├── RPCError
│   ├── InternalServerError
│   └── ConfigurationError
└── MCPError
    ├── ResourceError
    ├── ToolError
    └── ContextError
"""

from typing import Any, Optional, Union

from odoorpc.error import InternalError, RPCError
from odoorpc.rpc.error import ConnectorError


class OdooMCPError(Exception):
    """
    Base exception class for all Odoo MCP Server errors.

    This serves as the base class for all custom exceptions in the application,
    providing a consistent interface for error handling and logging.

    Attributes:
        message: Human-readable error message
        error_code: Machine-readable error code for programmatic handling
        details: Additional context information about the error
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ) -> None:
        """
        Initialize the exception.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional context information
            original_error: The original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper()
        self.details = details or {}
        self.original_error = original_error

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the exception to a dictionary for JSON serialization.

        Returns:
            Dictionary representation of the exception
        """
        result = {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }

        if self.original_error:
            result["original_error"] = {
                "type": self.original_error.__class__.__name__,
                "message": str(self.original_error),
            }

        return result

    def __str__(self) -> str:
        """String representation of the exception."""
        return f"{self.error_code}: {self.message}"


# =============================================================================
# CONNECTION RELATED ERRORS
# =============================================================================


class ConnectionTimeoutError(ConnectionError):
    """Raised when a connection to Odoo times out."""

    def __init__(
        self,
        message: str = "Connection to Odoo server timed out",
        timeout: Optional[float] = None,
        **kwargs,
    ) -> None:
        details = kwargs.get("details", {})
        if timeout is not None:
            details["timeout_seconds"] = timeout
        kwargs["details"] = details
        super().__init__(message, **kwargs)


class AuthenticationError(ConnectionError):
    """Raised when authentication with Odoo fails."""

    def __init__(
        self,
        message: str = "Authentication with Odoo failed",
        username: Optional[str] = None,
        database: Optional[str] = None,
        **kwargs,
    ) -> None:
        details = kwargs.get("details", {})
        if username:
            details["username"] = username
        if database:
            details["database"] = database
        kwargs["details"] = details
        super().__init__(message, **kwargs)


class SSLVerificationError(ConnectionError):
    """Raised when SSL certificate verification fails."""

    def __init__(
        self,
        message: str = "SSL certificate verification failed",
        hostname: Optional[str] = None,
        **kwargs,
    ) -> None:
        details = kwargs.get("details", {})
        if hostname:
            details["hostname"] = hostname
        kwargs["details"] = details
        super().__init__(message, **kwargs)


# =============================================================================
# MODEL RELATED ERRORS
# =============================================================================


class ModelError(OdooMCPError):
    """Base class for model-related errors."""


class ModelNotFoundError(ModelError):
    """Raised when a requested model doesn't exist."""

    def __init__(
        self, model_name: str, message: Optional[str] = None, **kwargs
    ) -> None:
        message = message or f"Model '{model_name}' not found"
        details = kwargs.get("details", {})
        details["model_name"] = model_name
        kwargs["details"] = details
        super().__init__(message, **kwargs)


class FieldNotFoundError(ModelError):
    """Raised when a requested field doesn't exist on a model."""

    def __init__(
        self,
        field_name: str,
        model_name: Optional[str] = None,
        message: Optional[str] = None,
        **kwargs,
    ) -> None:
        if model_name:
            message = (
                message or f"Field '{field_name}' not found on model '{model_name}'"
            )
        else:
            message = message or f"Field '{field_name}' not found"

        details = kwargs.get("details", {})
        details["field_name"] = field_name
        if model_name:
            details["model_name"] = model_name
        kwargs["details"] = details
        super().__init__(message, **kwargs)


class InvalidModelError(ModelError):
    """Raised when a model name or configuration is invalid."""

    def __init__(
        self,
        model_name: str,
        reason: Optional[str] = None,
        message: Optional[str] = None,
        **kwargs,
    ) -> None:
        if reason:
            message = message or f"Invalid model '{model_name}': {reason}"
        else:
            message = message or f"Invalid model '{model_name}'"

        details = kwargs.get("details", {})
        details["model_name"] = model_name
        if reason:
            details["reason"] = reason
        kwargs["details"] = details
        super().__init__(message, **kwargs)


# =============================================================================
# DATA RELATED ERRORS
# =============================================================================


class DataError(OdooMCPError):
    """Base class for data-related errors."""


class RecordNotFoundError(DataError):
    """Raised when a requested record doesn't exist."""

    def __init__(
        self,
        record_id: Union[int, str],
        model_name: Optional[str] = None,
        message: Optional[str] = None,
        **kwargs,
    ) -> None:
        if model_name:
            message = message or f"Record {record_id} not found in model '{model_name}'"
        else:
            message = message or f"Record {record_id} not found"

        details = kwargs.get("details", {})
        details["record_id"] = record_id
        if model_name:
            details["model_name"] = model_name
        kwargs["details"] = details
        super().__init__(message, **kwargs)


class ValidationError(DataError):
    """Raised when data validation fails."""

    def __init__(
        self,
        message: str = "Data validation failed",
        validation_errors: Optional[dict[str, str]] = None,
        **kwargs,
    ) -> None:
        details = kwargs.get("details", {})
        if validation_errors:
            details["validation_errors"] = validation_errors
        kwargs["details"] = details
        super().__init__(message, **kwargs)


class AccessDeniedError(DataError):
    """Raised when access to a resource is denied."""

    def __init__(
        self,
        message: str = "Access denied",
        resource: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs,
    ) -> None:
        details = kwargs.get("details", {})
        if resource:
            details["resource"] = resource
        if operation:
            details["operation"] = operation
        kwargs["details"] = details
        super().__init__(message, **kwargs)


class InvalidDataError(DataError):
    """Raised when provided data is invalid or malformed."""

    def __init__(
        self,
        message: str = "Invalid data provided",
        data_field: Optional[str] = None,
        expected_type: Optional[str] = None,
        **kwargs,
    ) -> None:
        details = kwargs.get("details", {})
        if data_field:
            details["data_field"] = data_field
        if expected_type:
            details["expected_type"] = expected_type
        kwargs["details"] = details
        super().__init__(message, **kwargs)


# =============================================================================
# SERVER RELATED ERRORS
# =============================================================================


class ServerError(OdooMCPError):
    """Base class for server-related errors."""


class OdooRPCError(ServerError):
    """Raised when an RPC call to Odoo fails."""

    def __init__(
        self,
        message: str = "RPC call failed",
        method: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs,
    ) -> None:
        details = kwargs.get("details", {})
        if method:
            details["method"] = method
        if model:
            details["model"] = model
        kwargs["details"] = details
        super().__init__(message, **kwargs)


class InternalServerError(ServerError):
    """Raised when an internal server error occurs."""


class ConfigurationError(ServerError):
    """Raised when there's a configuration problem."""

    def __init__(
        self,
        message: str = "Configuration error",
        config_key: Optional[str] = None,
        **kwargs,
    ) -> None:
        details = kwargs.get("details", {})
        if config_key:
            details["config_key"] = config_key
        kwargs["details"] = details
        super().__init__(message, **kwargs)


# =============================================================================
# MCP RELATED ERRORS
# =============================================================================


class MCPError(OdooMCPError):
    """Base class for MCP protocol-related errors."""


class ResourceError(MCPError):
    """Raised when an MCP resource operation fails."""

    def __init__(
        self,
        message: str = "Resource operation failed",
        resource_name: Optional[str] = None,
        **kwargs,
    ) -> None:
        details = kwargs.get("details", {})
        if resource_name:
            details["resource_name"] = resource_name
        kwargs["details"] = details
        super().__init__(message, **kwargs)


class ToolError(MCPError):
    """Raised when an MCP tool operation fails."""

    def __init__(
        self,
        message: str = "Tool operation failed",
        tool_name: Optional[str] = None,
        **kwargs,
    ) -> None:
        details = kwargs.get("details", {})
        if tool_name:
            details["tool_name"] = tool_name
        kwargs["details"] = details
        super().__init__(message, **kwargs)


class ContextError(MCPError):
    """Raised when there's an issue with the MCP context."""

    def __init__(
        self,
        message: str = "Context error",
        context_type: Optional[str] = None,
        **kwargs,
    ) -> None:
        details = kwargs.get("details", {})
        if context_type:
            details["context_type"] = context_type
        kwargs["details"] = details
        super().__init__(message, **kwargs)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def wrap_odoorpc_error(
    error: Exception, context: Optional[dict[str, Any]] = None
) -> OdooMCPError:
    """
    Wrap OdooRPC errors into our custom exception hierarchy.

    Args:
        error: The original OdooRPC error
        context: Additional context information

    Returns:
        Appropriate custom exception
    """

    context = context or {}
    error_obj = None

    if isinstance(error, ConnectorError):
        error_obj = ConnectionTimeoutError(
            message=f"Connection failed: {str(error)}",
            details=context,
            original_error=error,
        )
    elif isinstance(error, RPCError):
        # Check if it's an authentication error
        error_str = str(error).lower()
        if "access" in error_str or "denied" in error_str or "forbidden" in error_str:
            error_obj = AccessDeniedError(
                message=f"Access denied: {str(error)}",
                details=context,
                original_error=error,
            )
        elif "authenticate" in error_str or "login" in error_str:
            error_obj = AuthenticationError(
                message=f"Authentication failed: {str(error)}",
                details=context,
                original_error=error,
            )
        else:
            error_obj = OdooRPCError(
                message=f"RPC error: {str(error)}",
                details=context,
                original_error=error,
            )
    elif isinstance(error, InternalError):
        error_obj = InternalServerError(
            message=f"Internal server error: {str(error)}",
            details=context,
            original_error=error,
        )

    if error_obj:
        return error_obj
    # For any other exception, wrap it in a generic OdooMCPError
    return OdooMCPError(
        message=f"Unexpected error: {str(error)}",
        details=context,
        original_error=error,
    )


def handle_exception(
    func_name: str, error: Exception, context: Optional[dict[str, Any]] = None
) -> OdooMCPError:
    """
    Handle and convert exceptions to appropriate custom exceptions.

    Args:
        func_name: Name of the function where the error occurred
        error: The original exception
        context: Additional context information

    Returns:
        Appropriate custom exception
    """
    context = context or {}
    context["function"] = func_name

    # If it's already one of our custom exceptions, just add context
    if isinstance(error, OdooMCPError):
        if context:
            error.details.update(context)
        return error

    return wrap_odoorpc_error(error, context)
