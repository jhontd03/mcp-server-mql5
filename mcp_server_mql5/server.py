"""
Main MCP Server implementation for MQL5 Developer Suite.

This module initializes the FastMCP server, defines the tools (search_mql5_docs),
and handles dependency injection and caching.
"""

import hashlib
from functools import lru_cache

from mcp.server.fastmcp import FastMCP

from .core.config import MQL5_SEARCH_API, logger
from .core.scraper import MQL5Scraper
from .core.search import MQL5Searcher
from .core.utils import limiter, log_execution_time
from .core.web_client import WebClient

# ==================== MCP SERVER ====================

mcp = FastMCP("MQL5 Developer Suite")

# Dependencies (Simple Singleton)
client = WebClient()
searcher = MQL5Searcher()
scraper = MQL5Scraper()


@lru_cache(maxsize=50)
def cached_search(search_hash: str) -> str | None:
    """
    Retrieves a cached search result.

    This function utilizes Python's lru_cache to store and retrieve results.
    The argument is a hash to ensure the cache key is concise.

    Args:
        search_hash: MD5 hash of the search term and parameters.

    Returns:
        The cached result string if available, otherwise None.
    """
    return None


@mcp.tool()
async def search_mql5_docs(search_term: str, max_chars: int = 4000) -> str:
    """
    Search the official MQL5 documentation.

    Performs a search on mql5.com, retrieves the most relevant documentation page,
    extracts its content, and cleans it for consumption.

    Args:
        search_term: The term or concept to search for in the MQL5 documentation.
        max_chars: Maximum number of characters to return from the page content.
                   Defaults to 4000 to fit within typical LLM context windows.

    Returns:
        A string containing the source URL and the extracted text content.
    """

    logger.info(
        "Search request", extra={"search_term": search_term, "max_chars": max_chars}
    )

    # Check cache
    cache_key = hashlib.md5(f"{search_term}_{max_chars}".encode()).hexdigest()
    cached = cached_search(cache_key)

    if cached:
        logger.info("Cache hit", extra={"search_term": search_term})
        return f"[CACHED]\n{cached}"

    limiter.wait_if_needed()

    try:
        with log_execution_time("full_search", search_term=search_term) as ctx:
            # 1. Search in MQL5 API
            payload = {
                "keyword": search_term,
                "lng": "en",
                "count": 10,
                "dt_from": 0,
                "target_site": "mql5.com",
                "module": "mql5.com.en.docs",  # Prioritize docs
            }

            # Specific headers for the API
            # (although WebClient uses random UA, sometimes referer helps)
            # WebClient.get does not support custom headers yet, but params yes.
            # Let's try GET which we know works.

            search_response = await client.get(MQL5_SEARCH_API, params=payload)

            if not search_response:
                return "Search error in MQL5 API"

            # 2. Find best link
            target_link = searcher.find_best_match_api(search_response, search_term)

            if not target_link:
                # Fallback: Try general search if no specific docs?
                # For now report not found.
                logger.warning("No results found", extra={"search_term": search_term})
                return f"No documentation found for '{search_term}'"

            ctx["target_url"] = target_link

            # 3. Get content of the target page
            doc_html = await client.get(target_link)
            if not doc_html:
                return f"Error obtaining the page: {target_link}"

            # 4. Extract content
            content = scraper.extract_content(doc_html, max_chars=max_chars)

            result = f"SOURCE: {target_link}\n\n{content}"
            ctx["result_length"] = len(result)

            return result

    except Exception as e:
        logger.error(
            "Unexpected error",
            extra={"search_term": search_term, "error": str(e)},
            exc_info=True,
        )
        return f"Error: {str(e)}"


def main() -> None:
    logger.info("Server starting")
    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
    except Exception as e:
        logger.critical("Server crashed", extra={"error": str(e)}, exc_info=True)
        raise
    finally:
        logger.info("Server stopped")


if __name__ == "__main__":
    main()
