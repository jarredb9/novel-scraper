import os
import re
from typing import Optional, List, Dict, Any
import pypdf

def extract_chapter_number(title: str) -> Optional[int]:
    """Extracts the first continuous block of digits from the title.

    Args:
        title: The string title to extract the chapter number from.

    Returns:
        The extracted chapter number as an integer, or None if not found.
    """
    if not title:
        return None
    # Find word boundaries around digits to avoid matching parts of words (e.g. Chapter123 vs Chapter 123)
    match = re.search(r'\b\d+\b', title)
    if match:
        return int(match.group())
    # Fallback to any digits if no word boundary match
    match = re.search(r'\d+', title)
    if match:
        return int(match.group())
    return None

def parse_pdf_outline(pdf_path: str) -> List[Dict[str, Any]]:
    """Extracts the outline (bookmarks) of the PDF.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        A list of dicts representing chapter bookmarks, each containing:
            - 'title': The bookmark title.
            - 'number': The parsed chapter number (int) or None.
    """
    if not os.path.exists(pdf_path):
        return []
    try:
        reader = pypdf.PdfReader(pdf_path)
        outline = reader.outline
        if not outline:
            return []
        
        titles = []
        def traverse(outline_list):
            for item in outline_list:
                if isinstance(item, list):
                    traverse(item)
                else:
                    # item should be a Destination or Destination-like object with 'title'
                    title = getattr(item, 'title', None)
                    if title:
                        titles.append(title)
        
        traverse(outline)
        
        chapters = []
        for title in titles:
            num = extract_chapter_number(title)
            if num is not None:
                chapters.append({
                    "title": title,
                    "number": num
                })
        return chapters
    except Exception:
        return []


def extract_source_url_from_pdf(pdf_path: str) -> Optional[str]:
    """Extracts the source landing page URL from PDF subject metadata.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        The extracted URL string if found, otherwise None.
    """
    if not os.path.exists(pdf_path):
        return None
    try:
        reader = pypdf.PdfReader(pdf_path)
        meta = reader.metadata
        if meta and meta.subject:
            return meta.subject
    except Exception:
        pass
    return None

