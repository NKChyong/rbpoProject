"""
Secure HTTP client with security policies for external service integration.
Implements timeouts, size limits, SSL verification, and retry policies.
"""

import asyncio
import logging
from ipaddress import ip_address, ip_network
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import httpx
from httpx import HTTPError, Limits, Timeout

logger = logging.getLogger(__name__)

_DISALLOWED_HOSTS = {"localhost"}
_PRIVATE_NETWORKS = (
    ip_network("0.0.0.0/8"),
    ip_network("10.0.0.0/8"),
    ip_network("127.0.0.0/8"),
    ip_network("169.254.0.0/16"),
    ip_network("172.16.0.0/12"),
    ip_network("192.168.0.0/16"),
    ip_network("::1/128"),
    ip_network("fc00::/7"),
    ip_network("fe80::/10"),
)


class SecureHTTPClient:
    """
    Secure HTTP client with comprehensive security policies.
    Implements timeouts, size limits, SSL verification, and retry logic.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        connect_timeout: float = 10.0,
        max_response_size: int = 10 * 1024 * 1024,  # 10MB
        max_redirects: int = 3,
        verify_ssl: bool = True,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize secure HTTP client.

        Args:
            base_url: Base URL for requests
            timeout: Total request timeout in seconds
            connect_timeout: Connection timeout in seconds
            max_response_size: Maximum response size in bytes
            max_redirects: Maximum number of redirects
            verify_ssl: Whether to verify SSL certificates
            max_retries: Maximum number of retry attempts
            retry_delay: Initial retry delay in seconds
        """
        self.base_url = base_url
        self.timeout = timeout
        self.connect_timeout = connect_timeout
        self.max_response_size = max_response_size
        self.max_redirects = max_redirects
        self.verify_ssl = verify_ssl
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Create timeout configuration
        self.timeout_config = Timeout(
            timeout=timeout,
            connect=connect_timeout,
            read=timeout,
            write=timeout,
            pool=connect_timeout,
        )

        # Create limits configuration
        self.limits = Limits(
            max_keepalive_connections=20, max_connections=100, keepalive_expiry=30.0
        )

    def _validate_url(self, url: str) -> bool:
        """
        Validate URL for security.

        Args:
            url: URL to validate

        Returns:
            True if URL is safe
        """
        try:
            parsed = urlparse(url)

            # Only allow HTTP/HTTPS
            if parsed.scheme not in ("http", "https"):
                return False

            host = (parsed.hostname or "").lower()
            if not host:
                return False

            # Disallow known local hosts
            if host in _DISALLOWED_HOSTS or host.endswith(".localhost"):
                return False

            # Block IP addresses within private or loopback networks
            try:
                ip = ip_address(host)
            except ValueError:
                # Not an IP address – disallow obvious local-only domains
                if host.endswith(".local"):
                    return False
            else:
                for network in _PRIVATE_NETWORKS:
                    if ip in network:
                        return False

            # Check for suspicious patterns
            suspicious_patterns = ["file://", "ftp://", "gopher://"]

            for pattern in suspicious_patterns:
                if pattern in url.lower():
                    return False

            return True

        except Exception:
            return False

    async def _make_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """
        Make HTTP request with security policies.

        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional request parameters

        Returns:
            HTTP response

        Raises:
            HTTPError: If request fails
            ValueError: If URL is invalid
        """
        # Validate URL
        if not self._validate_url(url):
            raise ValueError(f"Invalid or unsafe URL: {url}")

        # Prepare request parameters
        request_params = {
            "timeout": self.timeout_config,
            "follow_redirects": True,
            "max_redirects": self.max_redirects,
            "verify": self.verify_ssl,
            "limits": self.limits,
        }

        # Add any additional parameters
        request_params.update(kwargs)

        async with httpx.AsyncClient(**request_params) as client:
            try:
                response = await client.request(method, url)

                # Check response size
                if hasattr(response, "content") and len(response.content) > self.max_response_size:
                    raise HTTPError(f"Response too large: {len(response.content)} bytes")

                return response

            except httpx.TimeoutException as e:
                logger.warning(f"Request timeout for {url}: {e}")
                raise HTTPError(f"Request timeout: {e}")
            except httpx.ConnectError as e:
                logger.warning(f"Connection error for {url}: {e}")
                raise HTTPError(f"Connection error: {e}")
            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTP error for {url}: {e.response.status_code}")
                raise HTTPError(f"HTTP error {e.response.status_code}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error for {url}: {e}")
                raise HTTPError(f"Unexpected error: {e}")

    async def _retry_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """
        Make HTTP request with retry logic.

        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional request parameters

        Returns:
            HTTP response
        """
        last_exception = None
        delay = self.retry_delay

        for attempt in range(self.max_retries + 1):
            try:
                return await self._make_request(method, url, **kwargs)
            except (httpx.TimeoutException, httpx.ConnectError) as e:
                last_exception = e
                if attempt < self.max_retries:
                    logger.info(f"Retry {attempt + 1}/{self.max_retries} for {url} in {delay}s")
                    await asyncio.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    break
            except Exception as e:
                # Don't retry on other errors
                raise e

        # If we get here, all retries failed
        raise HTTPError(f"Request failed after {self.max_retries} retries: {last_exception}")

    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> httpx.Response:
        """
        Make GET request.

        Args:
            url: Request URL
            params: Query parameters
            headers: Request headers
            **kwargs: Additional request parameters

        Returns:
            HTTP response
        """
        return await self._retry_request("GET", url, params=params, headers=headers, **kwargs)

    async def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> httpx.Response:
        """
        Make POST request.

        Args:
            url: Request URL
            data: Form data
            json: JSON data
            headers: Request headers
            **kwargs: Additional request parameters

        Returns:
            HTTP response
        """
        return await self._retry_request(
            "POST", url, data=data, json=json, headers=headers, **kwargs
        )

    async def put(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> httpx.Response:
        """
        Make PUT request.

        Args:
            url: Request URL
            data: Form data
            json: JSON data
            headers: Request headers
            **kwargs: Additional request parameters

        Returns:
            HTTP response
        """
        return await self._retry_request(
            "PUT", url, data=data, json=json, headers=headers, **kwargs
        )

    async def delete(
        self, url: str, headers: Optional[Dict[str, str]] = None, **kwargs
    ) -> httpx.Response:
        """
        Make DELETE request.

        Args:
            url: Request URL
            headers: Request headers
            **kwargs: Additional request parameters

        Returns:
            HTTP response
        """
        return await self._retry_request("DELETE", url, headers=headers, **kwargs)


# Global secure HTTP client instance
secure_client = SecureHTTPClient()
