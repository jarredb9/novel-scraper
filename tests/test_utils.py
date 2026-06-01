"""Tests for shared utility functions."""

import os
from unittest.mock import MagicMock, patch
import pytest
from src.utils import extract_chapter_number, extract_source_url

def test_extract_chapter_number():
    assert extract_chapter_number("Chapter 1: Start") == 1
    assert extract_chapter_number("Chapter 776: Middle") == 776
    assert extract_chapter_number("Chapter 1234") == 1234
    assert extract_chapter_number("Introduction") is None
    assert extract_chapter_number("Chapter 12.5") == 12
    assert extract_chapter_number("Chapter  99 - Text") == 99
    assert extract_chapter_number("") is None
    assert extract_chapter_number(None) is None

def test_extract_source_url_nonexistent():
    assert extract_source_url("nonexistent.pdf") is None
    assert extract_source_url("nonexistent.epub") is None

def test_extract_source_url_unsupported(tmp_path):
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("hello")
    assert extract_source_url(str(txt_file)) is None

@patch("src.utils.epub.read_epub")
def test_extract_source_url_epub_success(mock_read_epub, tmp_path):
    epub_file = tmp_path / "test.epub"
    epub_file.write_text("dummy content")
    
    mock_book = MagicMock()
    mock_book.get_metadata.return_value = [("http://epub-source.com", {})]
    mock_read_epub.return_value = mock_book
    
    assert extract_source_url(str(epub_file)) == "http://epub-source.com"
    mock_read_epub.assert_called_once_with(str(epub_file))
    mock_book.get_metadata.assert_called_once_with("DC", "source")

@patch("src.utils.epub.read_epub")
def test_extract_source_url_epub_no_metadata(mock_read_epub, tmp_path):
    epub_file = tmp_path / "test.epub"
    epub_file.write_text("dummy content")
    
    mock_book = MagicMock()
    mock_book.get_metadata.return_value = []
    mock_read_epub.return_value = mock_book
    
    assert extract_source_url(str(epub_file)) is None

@patch("src.utils.epub.read_epub")
def test_extract_source_url_epub_exception(mock_read_epub, tmp_path):
    epub_file = tmp_path / "test.epub"
    epub_file.write_text("dummy content")
    mock_read_epub.side_effect = Exception("failed to read epub")
    
    assert extract_source_url(str(epub_file)) is None

@patch("src.utils.pypdf.PdfReader")
def test_extract_source_url_pdf_success(mock_pdf_reader, tmp_path):
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_text("dummy content")
    
    mock_reader = MagicMock()
    mock_reader.metadata.subject = "http://pdf-source.com"
    mock_pdf_reader.return_value = mock_reader
    
    assert extract_source_url(str(pdf_file)) == "http://pdf-source.com"
    mock_pdf_reader.assert_called_once_with(str(pdf_file))

@patch("src.utils.pypdf.PdfReader")
def test_extract_source_url_pdf_no_subject(mock_pdf_reader, tmp_path):
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_text("dummy content")
    
    mock_reader = MagicMock()
    mock_reader.metadata = None
    mock_pdf_reader.return_value = mock_reader
    
    assert extract_source_url(str(pdf_file)) is None

@patch("src.utils.pypdf.PdfReader")
def test_extract_source_url_pdf_exception(mock_pdf_reader, tmp_path):
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_text("dummy content")
    mock_pdf_reader.side_effect = Exception("failed to read pdf")
    
    assert extract_source_url(str(pdf_file)) is None
