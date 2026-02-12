from unittest.mock import AsyncMock, patch

import pytest

from mcp_server_mql5.server import search_mql5_docs


@pytest.mark.asyncio
async def test_search_mql5_docs_success() -> None:
    # Mock dependencies
    with (
        patch("mcp_server_mql5.server.client") as mock_client,
        patch("mcp_server_mql5.server.searcher") as mock_searcher,
        patch("mcp_server_mql5.server.scraper") as mock_scraper,
        patch("mcp_server_mql5.server.cached_search", return_value=None),
    ):
        # Setup mocks
        mock_client.get = AsyncMock(
            return_value='{"results": []}'
        )  # Initial search response (mocked below actually)
        # Wait, the server code calls client.get(API) now.

        # 1. API Search response
        mock_client.get.side_effect = [
            '{"results": ["stuff"]}',  # First call: API search
            "<html>doc content</html>",  # Second call: Fetch doc
        ]

        # 2. Searcher logic
        mock_searcher.find_best_match_api.return_value = "https://found-url"

        # 3. Scraper logic
        mock_scraper.extract_content.return_value = "Cleaned Content"

        # Execute
        result = await search_mql5_docs("term")

        # Verify
        assert "Cleaned Content" in result
        assert "SOURCE: https://found-url" in result


@pytest.mark.asyncio
async def test_search_mql5_docs_cached() -> None:
    # If cached_search returns value, we should get it immediately
    with patch("mcp_server_mql5.server.cached_search", return_value="Cached Result"):
        result = await search_mql5_docs("term")
        assert "[CACHED]" in result
        assert "Cached Result" in result


@pytest.mark.asyncio
async def test_search_mql5_docs_no_results() -> None:
    with (
        patch("mcp_server_mql5.server.client") as mock_client,
        patch("mcp_server_mql5.server.searcher") as mock_searcher,
        patch("mcp_server_mql5.server.cached_search", return_value=None),
    ):
        mock_client.get = AsyncMock(return_value="{}")
        mock_searcher.find_best_match_api.return_value = None

        result = await search_mql5_docs("term")
        assert "No documentation found" in result
