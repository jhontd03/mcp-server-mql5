from typing import Any

from bs4 import BeautifulSoup

"""
Web scraping logic for MQL5 documentation.

This module handles parsing HTML content, extracting relevant text, and cleaning up
unwanted elements to provide clean context for the LLM.
"""


class MQL5Scraper:
    """
    Logic for extracting content from MQL5 pages.

    Uses BeautifulSoup to parse HTML and extract the main content text,
    applying cleaning strategies to remove clutter.
    """

    def extract_content(self, html_content: str, max_chars: int = 4000) -> str:
        """
        Extracts and cleans the main content of the page.

        Args:
            html_content: The raw HTML string.
            max_chars: Maximum number of characters to return. Defaults to 4000.

        Returns:
            A cleaned string containing the page's main text content,
            truncated if necessary. Returns a fallback message if no content is found.
        """
        doc_soup = BeautifulSoup(html_content, "html.parser")
        content_div = self._find_content_div(doc_soup)

        if not content_div:
            return "Page found, no extractable content"

        # Cleaning
        for junk in content_div(
            ["script", "style", "nav", "footer", "header", "form", "aside", "iframe"]
        ):
            junk.decompose()

        # Extract text
        sections = []
        char_count = 0

        for elem in content_div.find_all(["h1", "h2", "h3", "p", "pre"]):
            text = elem.get_text(separator=" ", strip=True)

            if char_count + len(text) > max_chars:
                sections.append("\n[truncated]")
                break

            sections.append(text)
            char_count += len(text)

        return "\n\n".join(sections)

    def _find_content_div(self, soup: BeautifulSoup) -> Any:
        """
        Robust strategies to find content.

        Tries multiple selectors to locate the main content area of the MQL5 page.

        Args:
            soup: The BeautifulSoup object of the page.

        Returns:
            The BeautifulSoup tag containing the main content, or None if not found.
        """
        strategies = [
            lambda: soup.find("div", class_="doc-content"),
            lambda: soup.find("div", id="content"),
            lambda: soup.find("main"),
            lambda: soup.find("article"),
            lambda: soup.find("body"),
        ]

        for strategy in strategies:
            result = strategy()
            if result:
                return result
        return None
