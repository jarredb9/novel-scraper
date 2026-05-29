import unittest
from unittest.mock import MagicMock, patch
import pytest
from src.cli import parse_args
from src.orchestrator import run_orchestrator

def test_cli_update_pdf_argument():
    # Verify that --update-pdf parameter is correctly parsed
    args = parse_args(["--update-pdf", "my_novel.pdf", "--start", "770", "--end", "780"])
    assert args.update_pdf == "my_novel.pdf"
    assert args.start == 770
    assert args.end == 780

def test_orchestrator_update_pdf_flow(tmp_path):
    """
    Test that running run_orchestrator with update_pdf:
    1. Parses the existing PDF bookmarks/outline.
    2. Identifies present chapters and target range chapters.
    3. Feeds correct sorted list to compile.
    """
    start_chap = 770
    end_chap = 775
    delay = 0.1
    cache_dir = str(tmp_path / "cache")
    output_pdf = str(tmp_path / "output.pdf")
    existing_pdf = str(tmp_path / "existing.pdf")

    # The existing PDF contains chapters 772, 773
    mock_outline = [
        {"title": "Chapter 772: Middle Two", "number": 772},
        {"title": "Chapter 773: Middle Three", "number": 773},
    ]

    with patch('src.orchestrator.parse_pdf_outline') as mock_parse_outline, \
         patch('src.orchestrator.CachingManager') as MockCacheManager, \
         patch('src.orchestrator.NovelScraper') as MockScraper, \
         patch('src.orchestrator.XPathParser') as MockParser, \
         patch('src.orchestrator.ContentSanitizer') as MockSanitizer, \
         patch('src.orchestrator.PDFCompiler') as MockCompiler, \
         patch('src.orchestrator.tqdm') as MockTqdm:

        mock_parse_outline.return_value = mock_outline

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

        # Mock HTML and parsing output
        mock_scraper.fetch_chapter_html.side_effect = lambda num: f"<html><body>Chapter {num}</body></html>"
        mock_parser.parse.side_effect = lambda html: (f"Chapter {html.split()[-1][:-7]}: Title", "<div>Raw Body</div>")
        mock_sanitizer.sanitize.return_value = ["Para"]

        # Run orchestrator with update_pdf
        run_orchestrator(
            start=start_chap,
            end=end_chap,
            delay=delay,
            cache_dir=cache_dir,
            output=output_pdf,
            update_pdf=existing_pdf
        )

        # parse_pdf_outline should be called with existing_pdf
        mock_parse_outline.assert_called_once_with(existing_pdf)

        # Check that scraper.fetch_chapter_html is called for all chapters in target range
        # since we want to ensure cache/scraping occurs for chapters.
        # Wait, if a chapter is in the existing PDF, does it need to be fetched?
        # If they are already in the PDF, and not in cache, they should be scraped/fetched.
        # Here we mock that we fetch them (or if they are in cache).
        # We need all chapters 770, 771, 772, 773, 774, 775.
        assert mock_scraper.fetch_chapter_html.call_count == 6
        for ch in range(770, 776):
            mock_scraper.fetch_chapter_html.assert_any_call(ch)

        # compile should be called with chapters sorted from 770 to 775
        args, kwargs = mock_compiler.compile.call_args
        compiled_chaps = args[0]
        assert len(compiled_chaps) == 6
        assert [extract_chap_num(c["title"]) for c in compiled_chaps] == [770, 771, 772, 773, 774, 775]


def extract_chap_num(title):
    import re
    match = re.search(r'\d+', title)
    return int(match.group()) if match else None
