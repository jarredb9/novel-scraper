"""Content sanitization engine for web novel chapters.

This module parses raw chapter HTML text, strips unwanted elements (like ads,
boilerplate text, script, style, and iframe tags), and returns a list of
cleaned paragraphs.
"""

import difflib
import logging
import re
from typing import List
from lxml import html

logger = logging.getLogger("novel_scraper")

# Pre-allocated punctuation translation tables and regex patterns
_QUOTE_TRANSLATION = str.maketrans({
    "“": '"',
    "”": '"',
    "‘": "'",
    "’": "'"
})
_DASH_RE = re.compile(r"-{2,}")
_DOT_RE = re.compile(r"\.{2,}")
_WHITESPACE_RE = re.compile(r"\s+")


class ContentSanitizer:
    """Cleans raw HTML chapter content into plain text paragraphs."""

    def __init__(
        self,
        boilerplate_patterns: List[str] = None,
        custom_ad_patterns: List[str] = None,
    ):
        """Initializes the sanitizer.

        Args:
            boilerplate_patterns (List[str]): Regex patterns to match ads.
            custom_ad_patterns (List[str]): Additional regex patterns to match ads.
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

        if custom_ad_patterns:
            self.boilerplate_patterns = list(self.boilerplate_patterns) + list(
                custom_ad_patterns
            )

        self.branding_templates = [
            "stay connected through freewebnovel",
            "stay tuned with freewebnovel",
            "stay updated through freewebnovel",
            "explore new worlds at freewebnovel",
            "your journey continues on freewebnovel",
            "your journey continues at freewebnovel",
            "read new chapters at freewebnovel",
            "find adventures at freewebnovel",
            "explore stories on freewebnovel",
            "continue your adventure with freewebnovel",
            "experience more tales on freewebnovel",
            "discover exclusive tales on freewebnovel",
            # Additional permutations discovered during validation
            "read latest stories on freewebnovel",
            "find your next read on freewebnovel",
            "your next journey awaits at freewebnovel",
            "find more to read at freewebnovel",
            "enjoy new adventures from freewebnovel",
            "explore more at freewebnovel",
            "read exclusive content at freewebnovel",
            "discover hidden stories at freewebnovel",
            "find your next adventure on freewebnovel",
            "discover hidden tales at freewebnovel",
            "enjoy new chapters from freewebnovel",
            "enjoy exclusive content from freewebnovel",
            # More permutations discovered in the second validation scan
            "read the latest on freewebnovel",
            "continue your journey on freewebnovel",
            "continue reading stories on freewebnovel",
            "continue reading on freewebnovel",
            "experience tales at freewebnovel",
            "explore hidden tales at freewebnovel",
            "find exclusive stories on freewebnovel",
            "discover more content at freewebnovel",
            "enjoy new adventures at freewebnovel",
            "discover stories with freewebnovel",
            "enjoy more content from freewebnovel",
            "experience tales with freewebnovel",
            "continue reading at freewebnovel",
            "explore more stories with freewebnovel",
        ]

        # Dynamically build a strict regex matching the branding templates
        patterns = []
        for template in self.branding_templates:
            words = [re.escape(w) for w in template.split()]
            pattern_str = r"\s+".join(words)
            pattern_str = pattern_str.replace("freewebnovel", r"freewebnovel(?:\.com)?")
            patterns.append(pattern_str)
        self.branding_pattern = re.compile(
            r"\s*\b(?:" + "|".join(patterns) + r")([.!?])?", re.IGNORECASE
        )

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

    def _is_branding_sentence(self, sentence: str) -> bool:
        """Helper to check if a sentence matches branding templates.

        Args:
            sentence (str): Single sentence to check.

        Returns:
            bool: True if sentence matches branding, False otherwise.
        """
        if "freeweb" not in sentence.lower():
            return False

        clean_sentence = re.sub(r"[.!?\s]+$", "", sentence.lower()).strip()
        for template in self.branding_templates:
            clean_template = re.sub(r"[.!?\s]+$", "", template.lower()).strip()
            matcher = difflib.SequenceMatcher(
                None, clean_sentence, clean_template
            )
            if matcher.ratio() >= 0.85:
                return True
        return False

    def _clean_paragraph_fuzzy(self, paragraph: str) -> str:
        """Splits a paragraph into sentences and removes branding sentences.

        Args:
            paragraph (str): Cleaned paragraph text.

        Returns:
            str: Paragraph with fuzzy branding sentences removed.
        """
        # 1. Direct regex cleaning to remove branding phrases anywhere in the paragraph
        # (even if mashed without spaces or punctuation)
        paragraph = self.branding_pattern.sub("", paragraph)

        # 2. Split paragraph into sentences as a backup/refinement
        sentences = re.split(r"(?<=[.!?])\s+", paragraph)
        cleaned_sentences = []
        for sentence in sentences:
            sentence_stripped = sentence.strip()
            if not sentence_stripped:
                continue
            if self._is_branding_sentence(sentence_stripped):
                continue
            cleaned_sentences.append(sentence)
        return " ".join(cleaned_sentences).strip()

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
                cleaned = self._clean_paragraph_fuzzy(cleaned)
                if (
                    cleaned
                    and any(c.isalnum() for c in cleaned)
                    and not self._should_exclude(cleaned)
                ):
                    paragraphs.append(cleaned)
        else:
            # Fallback: split text content by lines
            text_content = fragment.text_content()
            for line in text_content.splitlines():
                cleaned = self.clean_text(line)
                cleaned = self._clean_paragraph_fuzzy(cleaned)
                if (
                    cleaned
                    and any(c.isalnum() for c in cleaned)
                    and not self._should_exclude(cleaned)
                ):
                    paragraphs.append(cleaned)

        return paragraphs

    def clean_text(self, text: str) -> str:
        """Cleans excess whitespace and normalizes punctuation from a string.

        Args:
            text (str): The raw text string.

        Returns:
            str: Cleaned text with single spaces and trimmed ends.
        """
        if not text:
            return ""

        # Normalize curly quotes and apostrophes
        text = text.translate(_QUOTE_TRANSLATION)

        # Normalize dashes (two or more consecutive hyphens to standard em-dash)
        text = _DASH_RE.sub("—", text)

        # Normalize dots (two or more consecutive dots to standard ellipsis)
        text = _DOT_RE.sub("…", text)

        # Replace multiple whitespaces/newlines/tabs with a single space
        cleaned = _WHITESPACE_RE.sub(" ", text)
        return cleaned.strip()
