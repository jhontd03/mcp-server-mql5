import random
from typing import Any

import aiohttp

from .config import DEFAULT_HEADERS, USER_AGENTS, logger

"""
HTTP Client for the MQL5 MCP Server.

This module provides a robust HTTP client wrapper using aiohttp, featuring
automatic User-Agent rotation, default headers, and error handling.
"""


class WebClient:
    """
    Abstraction for HTTP client with User-Agent rotation and error handling.

    Provides simplified async methods for GET and POST requests, managing
    sessions and headers automatically.
    """

    def __init__(self) -> None:
        self.headers = DEFAULT_HEADERS.copy()

    def _get_headers(
        self, custom_headers: dict[str, str] | None = None
    ) -> dict[str, str]:
        headers = self.headers.copy()
        headers["User-Agent"] = random.choice(USER_AGENTS)
        if custom_headers:
            headers.update(custom_headers)
        return headers

    async def post(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> str | None:
        """
        Performs a POST request and returns the response text.

        Args:
            url: The target URL.
            data: Form data to send in the body.
            json_data: JSON data to send in the body.
            headers: Custom headers to merge with default headers.

        Returns:
            The response text if successful, or None if the request failed
            or returned a non-success status code.

        Raises:
            Exception: If a network error occurs (logged before raising).
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, data=data, json=json_data, headers=self._get_headers(headers)
                ) as response:
                    status = response.status
                    # DDG sometimes returns 202 Accepted but with content
                    if status not in (200, 202):
                        logger.error(
                            f"HTTP POST error: {status}",
                            extra={"url": url, "status_code": status},
                        )
                        return None  # Or raise custom exception

                    return await response.text()
        except Exception as e:
            logger.error(
                f"Network error in POST {url}", extra={"error": str(e)}, exc_info=True
            )
            raise

    async def get(self, url: str, params: dict[str, Any] | None = None) -> str | None:
        """
        Performs a GET request and returns the response text.

        Args:
            url: The target URL.
            params: Query parameters to append to the URL.

        Returns:
            The response text if successful, or None if the request failed
            or returned a non-200 status code.

        Raises:
            Exception: If a network error occurs (logged before raising).
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, params=params, headers=self._get_headers()
                ) as response:
                    status = response.status
                    if status != 200:
                        logger.error(
                            f"HTTP GET error: {status}",
                            extra={"url": url, "status_code": status},
                        )
                        return None

                    return await response.text()
        except Exception as e:
            logger.error(
                f"Network error in GET {url}", extra={"error": str(e)}, exc_info=True
            )
            raise
