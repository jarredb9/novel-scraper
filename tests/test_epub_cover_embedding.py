import os
import pytest
from unittest.mock import patch, MagicMock
from src.epub_compiler import EPUBCompiler

def test_compile_with_cover(tmp_path):
    output_epub = tmp_path / "test_cover.epub"
    cover_image = tmp_path / "test_cover.jpg"
    cover_image.write_bytes(b"mock cover image data")
    
    compiler = EPUBCompiler(output_path=str(output_epub))
    chapters = [
        {"title": "Chapter 1: The Beginning", "paragraphs": ["This is a paragraph."]},
    ]
    
    # We patch set_cover and write_epub to verify details without writing to disk
    with patch("ebooklib.epub.EpubBook.set_cover") as mock_set_cover, \
         patch("ebooklib.epub.write_epub") as mock_write_epub:
        
        compiler.compile(chapters, cover_path=str(cover_image))
        
        # Verify set_cover was called
        mock_set_cover.assert_called_once_with("images/cover.jpg", b"mock cover image data", create_page=False)
        
        # Verify the book object passed to write_epub
        book = mock_write_epub.call_args[0][1]
        
        # The cover page should be in the spine
        assert len(book.spine) > 0
        cover_page = book.spine[0]
        # Cover page can be either the string uid 'cover' or the EpubHtml object for it
        if isinstance(cover_page, str):
            assert cover_page == "cover"
        else:
            assert cover_page.title == "Cover"
            assert cover_page.file_name == "cover.xhtml"
            assert "images/cover.jpg" in cover_page.content

def test_compile_without_cover(tmp_path):
    output_epub = tmp_path / "test_no_cover.epub"
    compiler = EPUBCompiler(output_path=str(output_epub))
    chapters = [
        {"title": "Chapter 1: The Beginning", "paragraphs": ["This is a paragraph."]},
    ]
    
    with patch("ebooklib.epub.EpubBook.set_cover") as mock_set_cover, \
         patch("ebooklib.epub.write_epub") as mock_write_epub:
        
        compiler.compile(chapters, cover_path=None)
        
        mock_set_cover.assert_not_called()
        
        book = mock_write_epub.call_args[0][1]
        # First item in spine should be "nav" if there's no cover
        assert book.spine[0] == "nav"
