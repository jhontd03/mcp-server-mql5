from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_server_mql5.core.web_client import WebClient


@pytest.mark.asyncio
class TestWebClient:
    @pytest.fixture
    def client(self) -> WebClient:
        return WebClient()

    async def test_get_success(self, client: Any) -> None:
        # Setup the mock response object
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = "content"

        # Setup the context manager returned by session.get()
        # when we do: async with session.get(...) as response
        mock_get_ctx = MagicMock()
        mock_get_ctx.__aenter__.return_value = mock_response
        mock_get_ctx.__aexit__.return_value = None

        # Setup the session object
        mock_session = MagicMock()
        mock_session.get.return_value = mock_get_ctx

        # Setup the context manager returned by aiohttp.ClientSession()
        # when we do: async with aiohttp.ClientSession() as session
        mock_session_ctx = MagicMock()
        mock_session_ctx.__aenter__.return_value = mock_session
        mock_session_ctx.__aexit__.return_value = None

        with patch("aiohttp.ClientSession", return_value=mock_session_ctx):
            result = await client.get("http://test.com")
            assert result == "content"

    async def test_get_failure(self, client: Any) -> None:
        mock_response = AsyncMock()
        mock_response.status = 404

        mock_get_ctx = MagicMock()
        mock_get_ctx.__aenter__.return_value = mock_response
        mock_get_ctx.__aexit__.return_value = None

        mock_session = MagicMock()
        mock_session.get.return_value = mock_get_ctx

        mock_session_ctx = MagicMock()
        mock_session_ctx.__aenter__.return_value = mock_session
        mock_session_ctx.__aexit__.return_value = None

        with patch("aiohttp.ClientSession", return_value=mock_session_ctx):
            result = await client.get("http://test.com")
            assert result is None

    async def test_post_success(self, client: Any) -> None:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = "posted"

        mock_post_ctx = MagicMock()
        mock_post_ctx.__aenter__.return_value = mock_response
        mock_post_ctx.__aexit__.return_value = None

        mock_session = MagicMock()
        mock_session.post.return_value = mock_post_ctx

        mock_session_ctx = MagicMock()
        mock_session_ctx.__aenter__.return_value = mock_session
        mock_session_ctx.__aexit__.return_value = None

        with patch("aiohttp.ClientSession", return_value=mock_session_ctx):
            result = await client.post("http://test.com", data={})
            assert result == "posted"
