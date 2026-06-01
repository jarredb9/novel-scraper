import os
import pytest
from unittest.mock import MagicMock, patch
from src.pdf_compiler import PDFCompiler
from src.pdf_reader import parse_pdf_outline
from src.utils import extract_chapter_number


def test_extract_chapter_number():
    assert extract_chapter_number("Chapter 1: Start") == 1
    assert extract_chapter_number("Chapter 776: Middle") == 776
    assert extract_chapter_number("Chapter 1234") == 1234
    assert extract_chapter_number("Introduction") is None
    assert extract_chapter_number("Chapter 12.5") == 12  # simple integer extraction
    assert extract_chapter_number("Chapter  99 - Text") == 99

def test_parse_pdf_outline_real_pdf(tmp_path):
    output_pdf = tmp_path / "test_outline.pdf"
    compiler = PDFCompiler(output_path=str(output_pdf))
    chapters = [
        {"title": "Chapter 1: The Beginning", "paragraphs": ["Once upon a time..."]},
        {"title": "Chapter 2: The Journey", "paragraphs": ["And then they walked..."]},
    ]
    compiler.compile(chapters)
    
    assert output_pdf.exists()
    
    # Parse outline using the implementation
    parsed_chapters = parse_pdf_outline(str(output_pdf))
    assert len(parsed_chapters) == 2
    assert parsed_chapters[0]["title"] == "Chapter 1: The Beginning"
    assert parsed_chapters[0]["number"] == 1
    assert parsed_chapters[1]["title"] == "Chapter 2: The Journey"
    assert parsed_chapters[1]["number"] == 2

def test_parse_pdf_outline_non_existent():
    # If the PDF does not exist, return an empty list or raise (according to implementation)
    # The spec says "If the targeted PDF does not exist or is corrupted, default to compiling a new PDF..."
    # So parse_pdf_outline should return an empty list or raise FileNotFoundError.
    # Let's verify it returns empty list or handles it gracefully.
    assert parse_pdf_outline("non_existent_file.pdf") == []

def test_parse_pdf_outline_corrupted(tmp_path):
    corrupted_pdf = tmp_path / "corrupted.pdf"
    corrupted_pdf.write_text("not a pdf content")
    assert parse_pdf_outline(str(corrupted_pdf)) == []

def test_parse_pdf_outline_no_bookmarks(tmp_path):
    output_pdf = tmp_path / "no_bookmarks.pdf"
    # Create simple file, we can mock PdfReader outline as empty
    with patch("src.pdf_reader.pypdf.PdfReader") as MockReader:
        mock_reader = MockReader.return_value
        mock_reader.outline = None
        
        parsed = parse_pdf_outline(str(output_pdf))
        assert parsed == []
