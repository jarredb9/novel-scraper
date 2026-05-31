import os
import pytest
from unittest.mock import patch, MagicMock
from src.pdf_compiler import PDFCompiler

def test_compile_with_pdf_cover(tmp_path):
    output_pdf = tmp_path / "test_cover.pdf"
    cover_image = tmp_path / "test_cover.jpg"
    
    # Create a dummy image file (1x1 pixel JPEG or just some bytes for mocking)
    # ReportLab Image flowable expects a valid image file if not mocked.
    # We will mock the reportlab.platypus.Image class or write a small valid mock/real image,
    # or patch Image to avoid format checks.
    cover_image.write_bytes(b"mock cover image data")
    
    compiler = PDFCompiler(
        output_path=str(output_pdf),
        title="My Custom Novel Title",
        author="Author Name"
    )
    
    chapters = [
        {"title": "Chapter 1", "paragraphs": ["Para 1.1", "Para 1.2"]},
    ]
    
    # Mock reportlab's Image flowable to avoid needing a real JPEG file format
    with patch("src.pdf_compiler.Image") as MockImage:
        mock_image_instance = MagicMock()
        MockImage.return_value = mock_image_instance
        
        compiler.compile(chapters, cover_path=str(cover_image))
        
        # Verify Image flowable was initialized with cover_path
        assert MockImage.call_count >= 1
        args, kwargs = MockImage.call_args_list[0]
        assert args[0] == str(cover_image)
        
    assert output_pdf.exists()

def test_compile_without_pdf_cover(tmp_path):
    output_pdf = tmp_path / "test_no_cover.pdf"
    compiler = PDFCompiler(
        output_path=str(output_pdf),
        title="My Custom Novel Title",
        author="Author Name"
    )
    
    chapters = [
        {"title": "Chapter 1", "paragraphs": ["Para 1.1", "Para 1.2"]},
    ]
    
    # Compile without cover path
    compiler.compile(chapters, cover_path=None)
    assert output_pdf.exists()
    
    # Verify that the first page in the outline is Table of Contents, not Cover
    # Wait, we can test that the bookmark map starts chap_0 at page 2 (TOC is page 1)
    # rather than page 3 (Cover is page 1, TOC is page 2, chap_0 is page 3)
    assert compiler.bookmark_map.get("chap_0") == 2
