import os
from typing import Optional, List, Dict, Any
import pypdf
from src.utils import extract_chapter_number



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

