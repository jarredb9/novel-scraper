import os
import re
from pypdf import PdfReader

def extract_chapter_number(title: str):
    """
    Extracts the first continuous block of digits from the title as the chapter number.
    e.g., 'Chapter 776: Middle' -> 776
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

def parse_pdf_outline(pdf_path: str):
    """
    Extracts the outline (bookmarks) of the PDF and returns a list of dicts with:
    - 'title': The bookmark title.
    - 'number': The parsed chapter number (int) or None.
    """
    if not os.path.exists(pdf_path):
        return []
    try:
        reader = PdfReader(pdf_path)
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
