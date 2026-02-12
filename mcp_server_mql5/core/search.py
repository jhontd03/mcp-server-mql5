import json

from .config import logger

"""
Search logic for MQL5 documentation.

This module processes search results from the MQL5 API, filtering and prioritizing
official documentation links to provide the most relevant information.
"""


class MQL5Searcher:
    """
    Logic to search MQL5 documentation using its API.

    Handles response parsing and result selection, favoring documentation modules
    over forum posts or code base entries.
    """

    def find_best_match_api(self, json_response: str, search_term: str) -> str | None:
        """
        Parses the JSON response from the MQL5 API and returns the best URL.

        Prioritizes results from the documentation module. Falls back to other
        modules if no documentation match is found.

        Args:
            json_response: The raw JSON string returned by the API.
            search_term: The term that was searched (for logging purposes).

        Returns:
            The URL of the best matching result, or None if no valid result is found
            or if parsing fails.
        """
        try:
            data = json.loads(json_response)
            results = data.get("results", [])

            if not results:
                return None

            # 1. Filter by documentation module if possible, or prioritize it
            docs_results = [r for r in results if "docs" in r.get("module", "")]
            other_results = [r for r in results if "docs" not in r.get("module", "")]

            # Combine, prefer documentation
            candidates = docs_results + other_results

            if not candidates:
                return None

            # 2. Take the first relevant result
            best_match = candidates[0]

            # Extract URL
            info = best_match.get("info", {})
            url = info.get("url")

            if not url:
                # Sometimes the URL might be constructed differently,
                # but the API seems to return it in info.url
                return None

            if not isinstance(url, str):
                return None

            logger.info(
                "Best match found via API",
                extra={
                    "search_term": search_term,
                    "url": url,
                    "title": info.get("title"),
                },
            )

            return url

        except json.JSONDecodeError:
            logger.error("Failed to decode JSON response from search API")
            return None
        except Exception as e:
            logger.error(f"Error parsing search results: {e}", exc_info=True)
            return None
