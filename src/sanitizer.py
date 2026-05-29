"""Content sanitization engine for web novel chapters.

This module parses raw chapter HTML text, strips unwanted elements (like ads,
boilerplate text, script, style, and iframe tags), and returns a list of
cleaned paragraphs.
"""

import logging
import re
from typing import List
from lxml import html

logger = logging.getLogger("novel_scraper")


class ContentSanitizer:
    """Cleans raw HTML chapter content into plain text paragraphs."""

    def __init__(self, boilerplate_patterns: List[str] = None):
        """Initializes the sanitizer.

        Args:
            boilerplate_patterns (List[str]): Regex patterns to match ads.
        """
        if boilerplate_patterns is None:
            # Default patterns seen on freewebnovel.com
            self.boilerplate_patterns = [
                r"if you find any errors",
                r"please let us know",
                r"visit.*freewebnovel",
                r"logo",
                r"advertising",
                r"advertisement",
            ]
        else:
            self.boilerplate_patterns = boilerplate_patterns

    def _should_exclude(self, text: str) -> bool:
        """Determines if a line of text is boilerplate or advertisement.

        Args:
            text (str): Cleaned text paragraph.

        Returns:
            bool: True if text should be excluded, False otherwise.
        """
        lower_text = text.lower()
        for pattern in self.boilerplate_patterns:
            if re.search(pattern, lower_text):
                return True
        return False

    def sanitize(self, raw_html: str) -> List[str]:
        """Sanitizes raw HTML to extract clean paragraph strings.

        Args:
            raw_html (str): Raw HTML body content.

        Returns:
            List[str]: A list of sanitized paragraph strings.
        """
        if not raw_html or not raw_html.strip():
            return []

        try:
            # Parse HTML wrapped in a div container to ensure proper fragment
            fragment = html.fromstring(f"<div>{raw_html}</div>")
        except Exception as e:
            logger.warning(
                f"Could not parse HTML segment in sanitizer: {str(e)}. "
                f"Treating as raw text."
            )
            # Fallback to simple parent element creation
            fragment = html.fragment_fromstring(
                f"<div>{raw_html}</div>", create_parent=True
            )

        # Remove script/style/iframe/noscript/subtxt tags while preserving tail text
        bad_tags_xpath = (
            ".//script | .//style | .//iframe | .//noscript | .//subtxt"
        )
        for bad_tag in fragment.xpath(bad_tags_xpath):
            parent = bad_tag.getparent()
            if parent is not None:
                if bad_tag.tail:
                    previous = bad_tag.getprevious()
                    if previous is not None:
                        previous.tail = (previous.tail or "") + bad_tag.tail
                    else:
                        parent.text = (parent.text or "") + bad_tag.tail
                parent.remove(bad_tag)

        paragraphs = []

        # Find all paragraph tags, or split by line breaks if none exist
        p_elements = fragment.xpath(".//p")

        if p_elements:
            for p in p_elements:
                text = p.text_content()
                cleaned = self.clean_text(text)
                if cleaned and not self._should_exclude(cleaned):
                    paragraphs.append(cleaned)
        else:
            # Fallback: split text content by lines
            text_content = fragment.text_content()
            for line in text_content.splitlines():
                cleaned = self.clean_text(line)
                if cleaned and not self._should_exclude(cleaned):
                    paragraphs.append(cleaned)

        return paragraphs

    def clean_text(self, text: str) -> str:
        """Cleans excess whitespace from a string.

        Args:
            text (str): The raw text string.

        Returns:
            str: Cleaned text with single spaces and trimmed ends.
        """
        if not text:
            return ""
        # Replace multiple whitespaces/newlines/tabs with a single space
        cleaned = re.sub(r"\s+", " ", text)
        return cleaned.strip()
