"""Unit tests for chapter link auto-detection."""

import pytest
from unittest.mock import MagicMock, patch
import requests
from src.cli import parse_args
from src.orchestrator import run_orchestrator

def test_cli_url_argument():
    """Verify that the --url argument is successfully parsed."""
    args = parse_args(["--url", "https://freewebnovel.com/some-novel.html"])
    assert args.url == "https://freewebnovel.com/some-novel.html"

def test_extract_chapters_logic():
    """Verify that chapter numbers and URLs are correctly extracted from landing page HTML."""
    from src.orchestrator import extract_chapters_from_landing_page
    
    html = """
    <html>
        <body>
            <div class="chapters">
                <a href="/some-novel/chapter-1.html">Chapter 1: The Start</a>
                <a href="/some-novel/chapter-2.html">Chapter 2: The Journey</a>
                <a href="/some-novel/chapter-3.html">Chapter 3</a>
                <a href="/some-novel/chapter-4.html">4. The End</a>
                <a href="https://freewebnovel.com/some-novel/chapter-5.html">ch. 5: Epilogue</a>
                <a href="/about.html">About Us</a>
            </div>
        </body>
    </html>
    """
    url_map = extract_chapters_from_landing_page(html, "https://freewebnovel.com/some-novel.html")
    assert url_map == {
        1: "https://freewebnovel.com/some-novel/chapter-1.html",
        2: "https://freewebnovel.com/some-novel/chapter-2.html",
        3: "https://freewebnovel.com/some-novel/chapter-3.html",
        4: "https://freewebnovel.com/some-novel/chapter-4.html",
        5: "https://freewebnovel.com/some-novel/chapter-5.html",
    }

def test_orchestrator_uses_url(tmp_path):
    """Verify that orchestrator fetches the landing page and routes scraping through detected URLs."""
    start_chap = 1
    end_chap = 3
    cache_dir = str(tmp_path / "cache")
    output_pdf = str(tmp_path / "output.pdf")
    landing_url = "https://freewebnovel.com/some-novel.html"

    landing_html = """
    <html>
        <body>
            <a href="/some-novel/chapter-1.html">Chapter 1</a>
            <a href="/some-novel/chapter-2.html">Chapter 2</a>
            <a href="/some-novel/chapter-3.html">Chapter 3</a>
        </body>
    </html>
    """
    dummy_chapter_html = "<html><body>Chapter Content</body></html>"

    with patch('src.orchestrator.CachingManager') as MockCacheManager, \
         patch('src.orchestrator.NovelScraper') as MockScraper, \
         patch('src.orchestrator.XPathParser') as MockParser, \
         patch('src.orchestrator.ContentSanitizer') as MockSanitizer, \
         patch('src.orchestrator.PDFCompiler') as MockCompiler, \
         patch('src.orchestrator.tqdm') as MockTqdm, \
         patch('requests.get') as mock_requests_get:

        # Mock requests.get for the landing page
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = landing_html
        mock_requests_get.return_value = mock_response

        # Instantiate mock objects
        mock_cache = MagicMock()
        mock_scraper = MagicMock()
        mock_parser = MagicMock()
        mock_sanitizer = MagicMock()
        mock_compiler = MagicMock()

        MockCacheManager.return_value = mock_cache
        MockScraper.return_value = mock_scraper
        MockParser.return_value = mock_parser
        MockSanitizer.return_value = mock_sanitizer
        MockCompiler.return_value = mock_compiler
        MockTqdm.side_effect = lambda x, **kwargs: x

        mock_scraper.fetch_chapter_html.return_value = dummy_chapter_html
        mock_parser.parse.return_value = ("Chapter Title", "<div>Body</div>")
        mock_sanitizer.sanitize.return_value = ["Para"]

        # Run orchestrator passing url
        run_orchestrator(
            start=start_chap,
            end=end_chap,
            delay=0.1,
            cache_dir=cache_dir,
            output=output_pdf,
            url=landing_url
        )

        # Ensure landing page was fetched
        expected_headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        mock_requests_get.assert_any_call(landing_url, headers=expected_headers, timeout=10)
        
        # Ensure the url_map was passed to scraper constructor
        MockScraper.assert_called_once_with(
            cache_manager=mock_cache,
            delay=0.1,
            url_map={
                1: "https://freewebnovel.com/some-novel/chapter-1.html",
                2: "https://freewebnovel.com/some-novel/chapter-2.html",
                3: "https://freewebnovel.com/some-novel/chapter-3.html",
            }
        )
