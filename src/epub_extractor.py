"""Module for extracting chapters from an existing EPUB file."""

import os
import logging
from typing import List, Dict, Any, Optional
import ebooklib
from ebooklib import epub
from lxml import html

logger = logging.getLogger("novel_scraper")


def extract_chapters_from_epub(epub_path: str) -> List[Dict[str, Any]]:
    """Reads an existing EPUB file and extracts chapter titles and paragraph texts.

    Filters items of type ITEM_DOCUMENT whose base name starts with 'chap_'.

    Args:
        epub_path (str): Path to the existing EPUB file.

    Returns:
        List[Dict[str, Any]]: List of chapter dicts, each containing keys:
            - 'title': str
            - 'paragraphs': List[str]
    """
    logger.info(f"Extracting chapters from existing EPUB: {epub_path}")
    book = epub.read_epub(epub_path)

    chapters = []

    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        file_name = item.get_name()
        base_name = os.path.basename(file_name)
        if not base_name.startswith("chap_"):
            continue

        try:
            content = item.get_content()
            tree = html.fromstring(content)

            # Extract title from h1, fallback to title tag
            h1_tags = tree.xpath("//h1/text()")
            title = h1_tags[0].strip() if h1_tags else ""
            if not title:
                title_tags = tree.xpath("//title/text()")
                title = title_tags[0].strip() if title_tags else "Untitled"

            # Extract paragraphs
            paragraphs = []
            p_elements = tree.xpath("//p")
            for p in p_elements:
                text = "".join(p.xpath(".//text()")).strip()
                if text:
                    paragraphs.append(text)

            chapters.append({"title": title, "paragraphs": paragraphs})
            logger.debug(
                f"Extracted chapter '{title}' with {len(paragraphs)} "
                f"paragraphs from EPUB."
            )
        except Exception as e:
            logger.warning(
                f"Failed to parse EPUB chapter {file_name}: {str(e)}"
            )

    return chapters

from src.utils import extract_source_url
