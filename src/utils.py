"""Shared utilities for novel-scraper."""

import logging
import os
import re
from typing import Optional

import ebooklib
from ebooklib import epub
import pypdf

logger = logging.getLogger("novel_scraper")


def extract_chapter_number(title: str) -> Optional[int]:
    """Extracts the first continuous block of digits from the title.

    Args:
        title: The string title to extract the chapter number from.

    Returns:
        The extracted chapter number as an integer, or None if not found.
    """
    if not title:
        return None
    # Find word boundaries around digits to avoid matching parts of words
    match = re.search(r"\b\d+\b", title)
    if match:
        return int(match.group())
    # Fallback to any digits if no word boundary match
    match = re.search(r"\d+", title)
    if match:
        return int(match.group())
    return None


def extract_source_url(file_path: str) -> Optional[str]:
    """Extracts the source landing page URL from a file's metadata.

    Supports both EPUB and PDF formats based on file extension.

    Args:
        file_path: Path to the file.

    Returns:
        Optional[str]: The source URL if found, otherwise None.
    """
    if not os.path.exists(file_path):
        return None

    _, ext = os.path.splitext(file_path.lower())
    if ext == ".epub":
        try:
            book = epub.read_epub(file_path)
            source_meta = book.get_metadata("DC", "source")
            if source_meta and len(source_meta) > 0:
                return source_meta[0][0]
        except Exception as e:
            logger.warning(
                f"Failed to read source URL from EPUB metadata: {str(e)}"
            )
    elif ext == ".pdf":
        try:
            reader = pypdf.PdfReader(file_path)
            meta = reader.metadata
            if meta and meta.subject:
                return meta.subject
        except Exception as e:
            logger.warning(
                f"Failed to read source URL from PDF metadata: {str(e)}"
            )
    return None
