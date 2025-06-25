"""
Exceptions for the Easy Appointments API client.
"""
from typing import Any, Dict, Optional

import httpx


class EasyAppointmentsError(Exception):
    """Base exception for all Easy Appointments API errors."""

    def __init__(
        self,
        status_code: Optional[int] = None,
        message: str = "An error occurred",
        response_body: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        response: Optional[httpx.Response] = None,
    ):
        """
        Initialize a new EasyAppointmentsError.

        Args:
            status_code: HTTP status code
            message: Error message
            response_body: Response body from the API
            request_id: Request ID from the API
            response: Raw HTTP response
        """
        self.status_code = status_code
        self.message = message
        self.response_body = response_body
        self.request_id = request_id
        self.response = response
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return a string representation of the error."""
        parts = [self.message]
        if self.status_code:
            parts.append(f"Status code: {self.status_code}")
        if self.request_id:
            parts.append(f"Request ID: {self.request_id}")
        return " | ".join(parts)


class AuthenticationError(EasyAppointmentsError):
    """Raised when authentication fails."""
    pass


class ResourceNotFoundError(EasyAppointmentsError):
    """Raised when a resource is not found."""
    pass


class ValidationError(EasyAppointmentsError):
    """Raised when request validation fails."""
    pass


class RateLimitError(EasyAppointmentsError):
    """Raised when rate limit is exceeded."""
    pass


class ServerError(EasyAppointmentsError):
    """Raised when the server returns a 5xx error."""
    pass
