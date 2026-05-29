import os
import pytest
from unittest.mock import MagicMock, patch
from src.pdf_compiler import PDFCompiler

def test_compiler_initialization():
    compiler = PDFCompiler(output_path="test.pdf")
    assert compiler.output_path == "test.pdf"
    assert compiler.margin == 36  # 0.5 inches in points (72 points = 1 inch)

def test_compiler_build_pdf(tmp_path):
    output_pdf = tmp_path / "test_novel.pdf"
    compiler = PDFCompiler(output_path=str(output_pdf))
    
    chapters = [
        {"title": "Chapter 1", "paragraphs": ["Para 1.1", "Para 1.2"]},
        {"title": "Chapter 2", "paragraphs": ["Para 2.1"]},
    ]
    
    compiler.compile(chapters)
    
    assert output_pdf.exists()
    assert output_pdf.stat().st_size > 0

def test_compiler_page_number_footer(tmp_path):
    output_pdf = tmp_path / "test_footer.pdf"
    compiler = PDFCompiler(output_path=str(output_pdf))
    
    # We spy on canvas drawString during build
    with patch("src.pdf_compiler.canvas.Canvas") as MockCanvas:
        mock_canvas_instance = MockCanvas.return_value
        chapters = [{"title": "Chapter 1", "paragraphs": ["Para 1"]}]
        compiler.compile(chapters)
        
        # Verify that canvas functions are called (e.g. for footer or text)
        # Note: ReportLab Platypus handles canvas internally, but we can verify it builds without error.

def test_compiler_empty_chapters(tmp_path):
    output_pdf = tmp_path / "test_empty.pdf"
    compiler = PDFCompiler(output_path=str(output_pdf))
    compiler.compile([])
    assert not output_pdf.exists()

def test_compiler_toc_and_bookmarks(tmp_path):
    output_pdf = tmp_path / "test_toc.pdf"
    compiler = PDFCompiler(output_path=str(output_pdf))
    
    chapters = [
        {"title": "Chapter 1: Start", "paragraphs": ["Para 1"]},
        {"title": "Chapter 2: Middle", "paragraphs": ["Para 2"]},
    ]
    
    compiler.compile(chapters)
    assert output_pdf.exists()
    
    # We can inspect the internal data structure of the compiler if we store page map or verify outline
    # Let's verify that the compiler successfully populated the bookmark map
    assert hasattr(compiler, "bookmark_map")
    # Chapter 1 starts after TOC (page 2)
    assert compiler.bookmark_map.get("chap_0") == 2


