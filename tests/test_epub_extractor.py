import os
import pytest
from ebooklib import epub
from src.epub_extractor import extract_chapters_from_epub

def test_extract_chapters_from_epub(tmp_path):
    # 1. Create a dummy EPUB file
    epub_path = tmp_path / "test_novel.epub"
    
    book = epub.EpubBook()
    book.set_identifier("test_id_123")
    book.set_title("Test Novel")
    book.set_language("en")
    
    # Create two chapter items
    c1 = epub.EpubHtml(title="Chapter 1: Start", file_name="chap_1.xhtml", lang="en")
    c1.content = """<html>
    <body>
        <h1>Chapter 1: Start</h1>
        <p>Paragraph one of chapter one.</p>
        <p>Paragraph two of chapter one.</p>
    </body>
    </html>"""
    
    c2 = epub.EpubHtml(title="Chapter 2: Middle", file_name="chap_2.xhtml", lang="en")
    c2.content = """<html>
    <body>
        <h1>Chapter 2: Middle</h1>
        <p>First paragraph of chapter two.</p>
        <p>Second paragraph.</p>
        <p> Third paragraph with whitespace. </p>
    </body>
    </html>"""
    
    # Add non-chapter HTML item (like nav or metadata) to verify we exclude it
    nav = epub.EpubNav()
    nav.content = "<html><body><h1>Table of Contents</h1></body></html>"
    
    ncx = epub.EpubNcx()
    
    book.add_item(c1)
    book.add_item(c2)
    book.add_item(nav)
    book.add_item(ncx)
    book.toc = (c1, c2)
    book.spine = ["nav", c1, c2]
    
    epub.write_epub(str(epub_path), book, {})
    
    # 2. Extract chapters from the EPUB
    extracted = extract_chapters_from_epub(str(epub_path))
    
    # 3. Assert
    assert len(extracted) == 2
    
    assert extracted[0]["title"] == "Chapter 1: Start"
    assert extracted[0]["paragraphs"] == [
        "Paragraph one of chapter one.",
        "Paragraph two of chapter one."
    ]
    
    assert extracted[1]["title"] == "Chapter 2: Middle"
    assert extracted[1]["paragraphs"] == [
        "First paragraph of chapter two.",
        "Second paragraph.",
        "Third paragraph with whitespace."
    ]
