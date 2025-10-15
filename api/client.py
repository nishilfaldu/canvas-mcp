"""
Canvas API HTTP client with comprehensive error handling.
Handles authentication, pagination, and request/response processing.
"""

from typing import Any, Dict, List, Optional, Union
import httpx
from urllib.parse import urljoin, urlencode

from .exceptions import (
    CanvasAPIError,
    CanvasAuthError,
    CanvasNotFoundError,
    CanvasValidationError,
    CanvasRateLimitError,
    CanvasServerError,
)
from config import config


class CanvasAPIClient:
    """
    Async HTTP client for Canvas LMS API.

    Handles:
    - Authentication via Bearer token
    - Automatic pagination
    - Comprehensive error handling
    - Request/response logging in debug mode
    """

    def __init__(self, api_url: str, api_token: str):
        """
        Initialize Canvas API client.

        Args:
            api_url: Base Canvas API URL (e.g., https://canvas.instructure.com)
            api_token: Canvas API access token
        """
        self.api_url = api_url.rstrip("/")
        self.api_token = api_token
        # Ensure base_url includes /api/v1
        if self.api_url.endswith("/api/v1"):
            self.base_url = self.api_url
        else:
            self.base_url = f"{self.api_url}/api/v1"

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for Canvas API requests."""
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _build_url(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Build full API URL with query parameters.

        Args:
            endpoint: API endpoint (e.g., "/courses")
            params: Query parameters

        Returns:
            Complete URL with encoded parameters
        """
        # Ensure endpoint starts with /
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"

        # Don't use urljoin as it replaces the base path when endpoint starts with /
        # Instead, concatenate directly
        url = f"{self.base_url}{endpoint}"

        if params:
            # Convert lists to multiple params (Canvas API format)
            query_parts = []
            for key, value in params.items():
                if isinstance(value, list):
                    for item in value:
                        query_parts.append(f"{key}={item}")
                elif value is not None:
                    query_parts.append(f"{key}={value}")

            if query_parts:
                url = f"{url}?{'&'.join(query_parts)}"

        return url

    def _handle_error_response(self, response: httpx.Response, endpoint: str) -> None:
        """
        Handle error responses from Canvas API.

        Args:
            response: HTTP response object
            endpoint: API endpoint that was called

        Raises:
            Appropriate CanvasAPIError subclass based on status code
        """
        status_code = response.status_code

        # Try to parse error message from response
        try:
            error_data = response.json()
            error_message = error_data.get("message") or error_data.get("error", "Unknown error")
        except Exception:
            error_message = response.text or "Unknown error"

        # Map status codes to specific exceptions
        if status_code == 401:
            raise CanvasAuthError(endpoint=endpoint)
        elif status_code == 404:
            raise CanvasNotFoundError(resource=endpoint, endpoint=endpoint)
        elif status_code in (400, 422):
            raise CanvasValidationError(
                message=error_message,
                status_code=status_code,
                endpoint=endpoint,
                errors=error_data if isinstance(error_data, dict) else None,
            )
        elif status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise CanvasRateLimitError(
                retry_after=int(retry_after) if retry_after else None,
                endpoint=endpoint,
            )
        elif status_code >= 500:
            raise CanvasServerError(status_code=status_code, endpoint=endpoint)
        else:
            raise CanvasAPIError(
                message=error_message,
                status_code=status_code,
                endpoint=endpoint,
            )

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        paginate: bool = False,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Make GET request to Canvas API.

        Args:
            endpoint: API endpoint (e.g., "/courses")
            params: Query parameters
            paginate: If True, automatically fetch all pages

        Returns:
            Response data (dict or list depending on endpoint)

        Raises:
            CanvasAPIError: On API errors
        """
        # Set default per_page if not specified and paginate is True
        if params is None:
            params = {}

        if paginate and "per_page" not in params:
            params["per_page"] = config.default_per_page

        async with httpx.AsyncClient(timeout=config.request_timeout) as client:
            url = self._build_url(endpoint, params)

            if config.enable_debug:
                print(f"[DEBUG] GET {url}")

            response = await client.get(url, headers=self._get_headers())

            if not response.is_success:
                self._handle_error_response(response, endpoint)

            data = response.json()

            # Handle pagination if requested
            if paginate and isinstance(data, list):
                all_data = data
                next_url = self._get_next_page_url(response)

                while next_url:
                    if config.enable_debug:
                        print(f"[DEBUG] GET {next_url} (pagination)")

                    response = await client.get(next_url, headers=self._get_headers())

                    if not response.is_success:
                        self._handle_error_response(response, endpoint)

                    page_data = response.json()
                    all_data.extend(page_data)
                    next_url = self._get_next_page_url(response)

                return all_data

            return data

    async def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make POST request to Canvas API.

        Args:
            endpoint: API endpoint
            json_data: JSON body data
            params: Query parameters

        Returns:
            Response data

        Raises:
            CanvasAPIError: On API errors
        """
        async with httpx.AsyncClient(timeout=config.request_timeout) as client:
            url = self._build_url(endpoint, params)

            if config.enable_debug:
                print(f"[DEBUG] POST {url}")

            response = await client.post(
                url,
                headers=self._get_headers(),
                json=json_data,
            )

            if not response.is_success:
                self._handle_error_response(response, endpoint)

            return response.json()

    async def put(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make PUT request to Canvas API.

        Args:
            endpoint: API endpoint
            json_data: JSON body data
            params: Query parameters

        Returns:
            Response data

        Raises:
            CanvasAPIError: On API errors
        """
        async with httpx.AsyncClient(timeout=config.request_timeout) as client:
            url = self._build_url(endpoint, params)

            if config.enable_debug:
                print(f"[DEBUG] PUT {url}")

            response = await client.put(
                url,
                headers=self._get_headers(),
                json=json_data,
            )

            if not response.is_success:
                self._handle_error_response(response, endpoint)

            return response.json()

    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make DELETE request to Canvas API.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Response data

        Raises:
            CanvasAPIError: On API errors
        """
        async with httpx.AsyncClient(timeout=config.request_timeout) as client:
            url = self._build_url(endpoint, params)

            if config.enable_debug:
                print(f"[DEBUG] DELETE {url}")

            response = await client.delete(url, headers=self._get_headers())

            if not response.is_success:
                self._handle_error_response(response, endpoint)

            # DELETE might return empty response
            try:
                return response.json()
            except Exception:
                return {}

    def _get_next_page_url(self, response: httpx.Response) -> Optional[str]:
        """
        Extract next page URL from Link header.

        Canvas API uses Link headers for pagination:
        Link: <https://canvas.example.com/api/v1/courses?page=2>; rel="next"

        Args:
            response: HTTP response object

        Returns:
            Next page URL or None if no more pages
        """
        link_header = response.headers.get("Link")
        if not link_header:
            return None

        # Parse Link header to find rel="next"
        links = link_header.split(",")
        for link in links:
            if 'rel="next"' in link:
                # Extract URL between < and >
                url_part = link.split(";")[0].strip()
                return url_part.strip("<>")

        return None
