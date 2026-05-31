"""Tests for auto-range detection and metadata embedding."""

import os
import pytest
from unittest.mock import MagicMock, patch
from src.epub_compiler import EPUBCompiler
from src.epub_extractor import extract_source_url_from_epub
from src.pdf_compiler import PDFCompiler
from src.pdf_reader import extract_source_url_from_pdf
from src.orchestrator import run_orchestrator
from src.cli import parse_args


def test_cli_defaults_to_none():
    """Verify cli defaults to None when url is specified."""
    args_no_url = parse_args([])
    assert args_no_url.start == 776
    assert args_no_url.end == 1780

    args_with_url = parse_args(["--url", "http://example.com"])
    assert args_with_url.start is None
    assert args_with_url.end is None


def test_epub_metadata_url_writing_reading(tmp_path):
    """Verify source URL is embedded and read from EPUB."""
    output_epub = tmp_path / "test_metadata.epub"
    compiler = EPUBCompiler(output_path=str(output_epub))
    test_url = "https://freewebnovel.com/some-novel.html"
    chapters = [
        {"title": "Chapter 1: Start", "paragraphs": ["Content"]}
    ]
    compiler.compile(chapters, source_url=test_url)
    
    assert output_epub.exists()
    
    source_url = extract_source_url_from_epub(str(output_epub))
    assert source_url == test_url



def test_pdf_metadata_url_writing_reading(tmp_path):
    """Verify source URL is embedded and read from PDF."""
    output_pdf = tmp_path / "test_metadata.pdf"
    compiler = PDFCompiler(output_path=str(output_pdf))
    test_url = "https://freewebnovel.com/some-novel.html"
    chapters = [
        {"title": "Chapter 1: Start", "paragraphs": ["Content"]}
    ]
    compiler.compile(chapters, source_url=test_url)
    
    assert output_pdf.exists()
    
    source_url = extract_source_url_from_pdf(str(output_pdf))
    assert source_url == test_url


def test_orchestrator_auto_range(tmp_path):
    """Verify orchestrator detects full range from url_map."""
    cache_dir = str(tmp_path / "cache")
    output_pdf = str(tmp_path / "output.pdf")
    landing_url = "https://freewebnovel.com/some-novel.html"

    landing_html = """
    <html>
        <body>
            <a href="/some-novel/chapter-5.html">Chapter 5</a>
            <a href="/some-novel/chapter-6.html">Chapter 6</a>
            <a href="/some-novel/chapter-7.html">Chapter 7</a>
        </body>
    </html>
    """
    dummy_chapter_html = "<html><body>Chapter Content</body></html>"

    with patch('src.orchestrator.CachingManager') as MockCacheManager, \
         patch('src.orchestrator.NovelScraper') as MockScraper, \
         patch('src.orchestrator.XPathParser') as MockParser, \
         patch('src.orchestrator.ContentSanitizer') as MockSanitizer, \
         patch('src.orchestrator.PDFCompiler') as MockCompiler, \
         patch('src.orchestrator.EPUBCompiler') as MockEpubCompiler, \
         patch('src.orchestrator.tqdm') as MockTqdm, \
         patch('requests.get') as mock_requests_get:

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = landing_html
        mock_requests_get.return_value = mock_response

        mock_cache = MagicMock()
        mock_scraper = MagicMock()
        mock_parser = MagicMock()
        mock_sanitizer = MagicMock()
        mock_compiler = MagicMock()
        mock_epub_compiler = MagicMock()

        MockCacheManager.return_value = mock_cache
        MockScraper.return_value = mock_scraper
        MockParser.return_value = mock_parser
        MockSanitizer.return_value = mock_sanitizer
        MockCompiler.return_value = mock_compiler
        MockEpubCompiler.return_value = mock_epub_compiler
        MockTqdm.side_effect = lambda x, **kwargs: x

        mock_scraper.fetch_chapter_html.return_value = dummy_chapter_html
        mock_parser.parse.return_value = ("Chapter Title", "<div>Body</div>")
        mock_sanitizer.sanitize.return_value = ["Para"]

        # Run orchestrator with start=None, end=None
        run_orchestrator(
            start=None,
            end=None,
            delay=1.0,
            cache_dir=cache_dir,
            output=output_pdf,
            url=landing_url,
            format="both"
        )

        MockScraper.assert_called_once_with(
            cache_manager=mock_cache,
            delay=1.0,
            url_map={
                5: "https://freewebnovel.com/some-novel/chapter-5.html",
                6: "https://freewebnovel.com/some-novel/chapter-6.html",
                7: "https://freewebnovel.com/some-novel/chapter-7.html",
            }
        )
        
        # Verify compile is called with source_url
        mock_compiler.compile.assert_called_once()
        _, kwargs = mock_compiler.compile.call_args
        assert kwargs.get("source_url") == landing_url

        mock_epub_compiler.compile.assert_called_once()
        _, epub_kwargs = mock_epub_compiler.compile.call_args
        assert epub_kwargs.get("source_url") == landing_url
