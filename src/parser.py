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
        title_elements = tree.xpath(self.title_xpath)
        if not title_elements:
            logger.warning(
                f"Title element not found with XPath: {self.title_xpath}"
            )
            raise ValueError("Could not extract chapter title.")

        # Get text content of the title element
        title = title_elements[0].text_content().strip()
        if not title:
            raise ValueError("Chapter title is empty.")

        # Extract Body
        body_elements = tree.xpath(self.body_xpath)
        if not body_elements:
            logger.warning(
                f"Body element not found with XPath: {self.body_xpath}"
            )
            raise ValueError("Could not extract chapter body.")

        # Serialize body to string for sanitization
        raw_body = html.tostring(
            body_elements[0], encoding="utf-8"
        ).decode("utf-8")

        return title, raw_body
