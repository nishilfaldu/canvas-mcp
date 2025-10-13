"""
Custom exceptions for Canvas API interactions.
Provides detailed error information for better debugging.
"""

from typing import Optional, Dict, Any


class CanvasAPIError(Exception):
    """Base exception for all Canvas API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        endpoint: Optional[str] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.endpoint = endpoint
        self.response_data = response_data

        error_msg = f"Canvas API Error: {message}"
        if status_code:
            error_msg = f"[{status_code}] {error_msg}"
        if endpoint:
            error_msg = f"{error_msg} (endpoint: {endpoint})"

        super().__init__(error_msg)


class CanvasAuthError(CanvasAPIError):
    """Raised when authentication fails (401)."""

    def __init__(self, endpoint: Optional[str] = None):
        super().__init__(
            message="Authentication failed. Invalid or expired Canvas API token.",
            status_code=401,
            endpoint=endpoint,
        )


class CanvasNotFoundError(CanvasAPIError):
    """Raised when a resource is not found (404)."""

    def __init__(self, resource: str, endpoint: Optional[str] = None):
        super().__init__(
            message=f"Resource not found: {resource}",
            status_code=404,
            endpoint=endpoint,
        )


class CanvasValidationError(CanvasAPIError):
    """Raised when request validation fails (400, 422)."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        endpoint: Optional[str] = None,
        errors: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=f"Validation error: {message}",
            status_code=status_code,
            endpoint=endpoint,
            response_data=errors,
        )


class CanvasRateLimitError(CanvasAPIError):
    """Raised when rate limit is exceeded (429)."""

    def __init__(self, retry_after: Optional[int] = None, endpoint: Optional[str] = None):
        message = "Rate limit exceeded."
        if retry_after:
            message += f" Retry after {retry_after} seconds."

        super().__init__(
            message=message,
            status_code=429,
            endpoint=endpoint,
            response_data={"retry_after": retry_after} if retry_after else None,
        )


class CanvasServerError(CanvasAPIError):
    """Raised when Canvas server returns 5xx error."""

    def __init__(self, status_code: int, endpoint: Optional[str] = None):
        super().__init__(
            message="Canvas server error. Please try again later.",
            status_code=status_code,
            endpoint=endpoint,
        )
