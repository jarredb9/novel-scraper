"""HTML XPath parsing engine for web novel chapters.

This module uses lxml and XPath queries to locate and extract the chapter
title and main body text from raw chapter HTML documents.
"""

import logging
from typing import Tuple
from lxml import html

logger = logging.getLogger("novel_scraper")


class XPathParser:
    """Parses HTML content of web novel chapters using lxml XPath selectors."""

    DEFAULT_TITLE_XPATH = "/html/body/div[3]/div[1]/div/div[1]/span"
    DEFAULT_BODY_XPATH = "/html/body/div[3]/div[1]/div/div[5]/div[1]"

    def __init__(
        self,
        title_xpath: str = DEFAULT_TITLE_XPATH,
        body_xpath: str = DEFAULT_BODY_XPATH,
    ):
        """Initializes the XPath parser with custom or default selectors.

        Args:
            title_xpath (str): XPath to locate the chapter title element.
            body_xpath (str): XPath to locate the chapter body element.
        """
        self.title_xpath = title_xpath
        self.body_xpath = body_xpath

    def parse(self, html_content: str) -> Tuple[str, str]:
        """Parses chapter HTML content to extract title and raw body HTML/text.

        Args:
            html_content (str): Raw HTML string of the chapter.

        Returns:
            Tuple[str, str]: (chapter_title, raw_body_text)

        Raises:
            ValueError: If title or body elements cannot be found.
        """
        if not html_content or not html_content.strip():
            raise ValueError("HTML content is empty.")

        try:
            tree = html.fromstring(html_content)
        except Exception as e:
            logger.error(f"Failed to parse HTML structure: {str(e)}")
            raise ValueError(f"Failed to parse HTML: {str(e)}")

        # Extract Title
        title = None
        title_elements = tree.xpath(self.title_xpath)
        if title_elements:
            title = title_elements[0].text_content().strip()

        if not title:
            logger.info(
                "Default title XPath failed or empty. "
                "Falling back to title heuristics."
            )
            try:
                title = self._extract_title_heuristically(tree)
            except ValueError:
                if title_elements:
                    raise ValueError("Chapter title is empty.")
                else:
                    raise ValueError("Could not extract chapter title.")

        # Extract Body
        raw_body = None
        body_elements = tree.xpath(self.body_xpath)
        if body_elements:
            raw_body = html.tostring(
                body_elements[0], encoding="utf-8"
            ).decode("utf-8")

        if not raw_body:
            logger.info("Default body XPath failed. Falling back to body heuristics.")
            raw_body = self._extract_body_heuristically(tree)

        return title, raw_body

    def _extract_title_heuristically(self, tree) -> str:
        """Extract chapter title using heuristic patterns.

        Args:
            tree: parsed HTML lxml tree.

        Returns:
            str: extracted title.

        Raises:
            ValueError: if no title is found.
        """
        # 1. first <h1> text content
        h1s = tree.xpath("//h1")
        if h1s:
            title = h1s[0].text_content().strip()
            if title:
                return title

        # 2. fallback to <h2>
        h2s = tree.xpath("//h2")
        if h2s:
            title = h2s[0].text_content().strip()
            if title:
                return title

        # 3. fallback to elements with class names containing "title"
        title_classes = tree.xpath(
            "//*[contains(@class, 'title') or contains(@class, 'Title')]"
        )
        for elem in title_classes:
            title = elem.text_content().strip()
            if title:
                return title

        # 4. fallback to cleaning up the document's <title> tag.
        html_title = tree.xpath("//title")
        if html_title:
            title = html_title[0].text_content().strip()
            # Cleanup common site name suffixes
            for suffix in [
                " - FreeWebNovel",
                " FreeWebNovel",
                " - freewebnovel.com",
                " freewebnovel.com",
            ]:
                if title.lower().endswith(suffix.lower()):
                    title = title[:-len(suffix)].strip()
            if title:
                return title

        raise ValueError("Could not extract chapter title.")

    def _extract_body_heuristically(self, tree) -> str:
        """Extract chapter body using heuristic patterns.

        Args:
            tree: parsed HTML lxml tree.

        Returns:
            str: serialized raw body HTML string.

        Raises:
            ValueError: if no body container is found.
        """
        # Select the container element containing the largest number of
        # <p> tag descendants.
        containers = tree.xpath("//div | //article | //section")
        best_container = None
        max_p_count = 0

        for container in containers:
            p_descendants = container.xpath(".//p")
            p_count = len(p_descendants)
            if p_count > max_p_count:
                max_p_count = p_count
                best_container = container

        if best_container is not None:
            return html.tostring(
                best_container, encoding="utf-8"
            ).decode("utf-8")

        # Fallback to raw text/breaks if <p> tags are absent
        fallbacks = tree.xpath(
            "//article | //div[contains(@class, 'content') "
            "or contains(@class, 'body')] | //body"
        )
        for container in fallbacks:
            text = container.text_content().strip()
            if text:
                return html.tostring(
                    container, encoding="utf-8"
                ).decode("utf-8")

        raise ValueError("Could not extract chapter body.")
