from typing import Any

import pytest

from mcp_server_mql5.core.scraper import MQL5Scraper


class TestMQL5Scraper:
    @pytest.fixture
    def scraper(self) -> MQL5Scraper:
        return MQL5Scraper()

    def test_extract_content_success(self, scraper: Any) -> None:
        html = """
        <html>
            <body>
                <div class="doc-content">
                    <h1>Title</h1>
                    <p>Paragraph 1</p>
                    <script>console.log('junk')</script>
                </div>
            </body>
        </html>
        """
        content = scraper.extract_content(html)
        assert "Title" in content
        assert "Paragraph 1" in content
        assert "console.log" not in content

    def test_extract_content_no_match(self, scraper: Any) -> None:
        html = ""
        content = scraper.extract_content(html)
        # Verify specific substring that indicates failure
        assert "Page found" in content
        assert "no extractable content" in content

    def test_extract_content_truncation(self, scraper: Any) -> None:
        html = """
        <html>
            <div id="content">
                <p>Hello</p>
                <p>World</p>
            </div>
        </html>
        """
        # Limit chars to just include "Hello" (5 chars)
        content = scraper.extract_content(html, max_chars=5)
        assert "Hello" in content
        assert "World" not in content
        assert "[truncated]" in content
