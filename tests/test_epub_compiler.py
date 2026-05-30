import os
import pytest
from unittest.mock import patch, MagicMock
from src.epub_compiler import EPUBCompiler

def test_compiler_initialization():
    compiler = EPUBCompiler(output_path="test.epub")
    assert compiler.output_path == "test.epub"

def test_compiler_empty_chapters(tmp_path):
    output_epub = tmp_path / "test_empty.epub"
    compiler = EPUBCompiler(output_path=str(output_epub))
    compiler.compile([])
    assert not output_epub.exists()

def test_compiler_build_epub(tmp_path):
    output_epub = tmp_path / "test_novel.epub"
    compiler = EPUBCompiler(output_path=str(output_epub))
    
    chapters = [
        {"title": "Chapter 1: The Beginning", "paragraphs": ["This is the first paragraph.", "This is the second paragraph."]},
        {"title": "Chapter 2: The Middle", "paragraphs": ["This is a paragraph in chapter two."]},
    ]
    
    compiler.compile(chapters)
    
    assert output_epub.exists()
    assert output_epub.stat().st_size > 0

def test_compiler_sorting(tmp_path):
    # Tests that chapters are sorted numerically prior to compilation.
    output_epub = tmp_path / "test_sorted.epub"
    compiler = EPUBCompiler(output_path=str(output_epub))
    
    # Pass chapters out of order
    chapters = [
        {"title": "Chapter 2: The Middle", "paragraphs": ["Chapter two content."]},
        {"title": "Chapter 1: The Beginning", "paragraphs": ["Chapter one content."]},
    ]
    
    with patch("ebooklib.epub.EpubBook.add_item") as mock_add_item:
        compiler.compile(chapters)
        # Verify the order of items added. We expect EpubHtml chapters to be sorted.
        # Let's inspect the names of added EpubHtml items.
        added_chapters = []
        for call in mock_add_item.call_args_list:
            item = call[0][0]
            # Duck typing to check if it's a chapter item
            if hasattr(item, "file_name") and item.file_name.startswith("chap_"):
                added_chapters.append(item.title)
        
        assert added_chapters == ["Chapter 1: The Beginning", "Chapter 2: The Middle"]

def test_compiler_metadata(tmp_path):
    output_epub = tmp_path / "test_metadata.epub"
    compiler = EPUBCompiler(output_path=str(output_epub), title="My Special Novel", author="Author Name")
    
    chapters = [
        {"title": "Chapter 1: Start", "paragraphs": ["Text."]},
    ]
    
    with patch("ebooklib.epub.EpubBook.set_title") as mock_set_title, \
         patch("ebooklib.epub.EpubBook.add_author") as mock_add_author, \
         patch("ebooklib.epub.EpubBook.set_language") as mock_set_language:
         
        compiler.compile(chapters)
        
        mock_set_title.assert_called_with("My Special Novel")
        mock_add_author.assert_called_with("Author Name")
        mock_set_language.assert_called_with("en")
