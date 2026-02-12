from typing import Any

import pytest

from mcp_server_mql5.core.search import MQL5Searcher


class TestMQL5Searcher:
    @pytest.fixture
    def searcher(self) -> MQL5Searcher:
        return MQL5Searcher()

    def test_find_best_match_api_success(self, searcher: Any) -> None:
        json_response = """
        {
            "results": [
                {
                    "module": "mql5.com.en.docs",
                    "info": {
                        "url": "https://www.mql5.com/en/docs/target",
                        "title": "Target Doc"
                    }
                }
            ]
        }
        """
        result = searcher.find_best_match_api(json_response, "term")
        assert result == "https://www.mql5.com/en/docs/target"

    def test_find_best_match_api_no_results(self, searcher: Any) -> None:
        json_response = '{"results": []}'
        result = searcher.find_best_match_api(json_response, "term")
        assert result is None

    def test_find_best_match_api_invalid_json(self, searcher: Any) -> None:
        json_response = "invalid json"
        result = searcher.find_best_match_api(json_response, "term")
        assert result is None

    def test_find_best_match_api_prioritize_docs(self, searcher: Any) -> None:
        json_response = """
        {
            "results": [
                {
                    "module": "mql5.com.en.forum",
                    "info": {"url": "https://forum", "title": "Forum"}
                },
                {
                    "module": "mql5.com.en.docs",
                    "info": {"url": "https://docs", "title": "Docs"}
                }
            ]
        }
        """
        result = searcher.find_best_match_api(json_response, "term")
        # Should pick docs even if it's second in the list (logic filters and
        # concatenates)
        # Actually my logic was: docs_results + other_results.
        # So docs should come first.
        assert result == "https://docs"

    def test_find_best_match_api_missing_url(self, searcher: Any) -> None:
        json_response = """
        {
            "results": [
                {
                    "module": "mql5.com.en.docs",
                    "info": {"title": "No URL"}
                }
            ]
        }
        """
        result = searcher.find_best_match_api(json_response, "term")
        assert result is None
