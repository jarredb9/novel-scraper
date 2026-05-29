import re
import logging
from typing import List
from lxml import html

logger = logging.getLogger("novel_scraper")

class ContentSanitizer:
    """Cleans and sanitizes raw HTML chapter content into plain text paragraphs."""

    def __init__(self, boilerplate_patterns: List[str] = None):
        """Initializes the sanitizer.

        Args:
            boilerplate_patterns (List[str]): Regex patterns or substrings matching ads/boilerplate.
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
            bool: True if the text should be excluded, False otherwise.
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
            # Parse HTML element wrapped in a div container to ensure all input tags are descendants
            fragment = html.fromstring(f"<div>{raw_html}</div>")
        except Exception as e:
            logger.warning(f"Could not parse HTML segment in sanitizer: {str(e)}. Treating as raw text.")
            # Fallback to simple string-based element creation
            fragment = html.fragment_fromstring(f"<div>{raw_html}</div>", create_parent=True)

        # Remove script and style tags completely while preserving their tails
        for bad_tag in fragment.xpath(".//script | .//style | .//iframe | .//noscript"):
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

        # Find all paragraph tags, or line breaks. If no <p> tags, split by <br> or newlines.
        p_elements = fragment.xpath(".//p")

        if p_elements:
            for p in p_elements:
                text = p.text_content()
                cleaned = self.clean_text(text)
                if cleaned and not self._should_exclude(cleaned):
                    paragraphs.append(cleaned)
        else:
            # Fallback: split by newlines or block elements if no <p> tags are present
            # We can traverse the tree and extract block-like texts or split text_content by newlines
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
