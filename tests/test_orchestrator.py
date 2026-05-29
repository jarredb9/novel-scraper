import unittest
from unittest.mock import MagicMock, patch
import pytest
from src.orchestrator import run_orchestrator

def test_orchestrator_successful_flow(tmp_path):
    # Setup mock components and inputs
    start_chap = 776
    end_chap = 778
    delay = 0.1
    cache_dir = str(tmp_path / "cache")
    output_pdf = str(tmp_path / "output.pdf")

    # Sample mock HTML content for parser to return
    dummy_html = "<html><body>Chapter Body</body></html>"

    with patch('src.orchestrator.CachingManager') as MockCacheManager, \
         patch('src.orchestrator.NovelScraper') as MockScraper, \
         patch('src.orchestrator.XPathParser') as MockParser, \
         patch('src.orchestrator.ContentSanitizer') as MockSanitizer, \
         patch('src.orchestrator.PDFCompiler') as MockCompiler, \
         patch('src.orchestrator.tqdm') as MockTqdm:

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
        
        # Configure tqdm mock to act as a pass-through identity function
        MockTqdm.side_effect = lambda x, **kwargs: x

        # Define behavior for mock scraper, parser, and sanitizer
        mock_scraper.fetch_chapter_html.return_value = dummy_html
        mock_parser.parse.return_value = ("Chapter 776: Title", "<div>Raw Body</div>")
        mock_sanitizer.sanitize.return_value = ["Paragraph 1", "Paragraph 2"]

        # Run the orchestrator
        run_orchestrator(
            start=start_chap,
            end=end_chap,
            delay=delay,
            cache_dir=cache_dir,
            output=output_pdf
        )

        # Assertions to verify the flow of download -> cache -> parse -> compile -> log
        MockCacheManager.assert_called_once_with(cache_dir=cache_dir)
        MockScraper.assert_called_once_with(cache_manager=mock_cache, delay=delay)
        MockParser.assert_called_once()
        MockSanitizer.assert_called_once()
        MockCompiler.assert_called_once_with(output_path=output_pdf)

        # The scraper should be called for each chapter in range (inclusive)
        assert mock_scraper.fetch_chapter_html.call_count == 3
        mock_scraper.fetch_chapter_html.assert_any_call(776)
        mock_scraper.fetch_chapter_html.assert_any_call(777)
        mock_scraper.fetch_chapter_html.assert_any_call(778)

        # Parser should have parsed HTML content for each chapter
        assert mock_parser.parse.call_count == 3
        mock_parser.parse.assert_any_call(dummy_html)

        # Sanitizer should have sanitized raw body for each chapter
        assert mock_sanitizer.sanitize.call_count == 3
        mock_sanitizer.sanitize.assert_any_call("<div>Raw Body</div>")

        # Compiler should have compiled the list of parsed chapters
        expected_chapters = [
            {"title": "Chapter 776: Title", "paragraphs": ["Paragraph 1", "Paragraph 2"]},
            {"title": "Chapter 776: Title", "paragraphs": ["Paragraph 1", "Paragraph 2"]},
            {"title": "Chapter 776: Title", "paragraphs": ["Paragraph 1", "Paragraph 2"]}
        ]
        mock_compiler.compile.assert_called_once_with(expected_chapters)
        
        # Progress bar (tqdm) should be initialized and iterated
        MockTqdm.assert_called_once()


def test_orchestrator_scraper_failure(tmp_path):
    with patch('src.orchestrator.CachingManager'), \
         patch('src.orchestrator.NovelScraper') as MockScraper, \
         patch('src.orchestrator.XPathParser'), \
         patch('src.orchestrator.ContentSanitizer'), \
         patch('src.orchestrator.PDFCompiler'), \
         patch('src.orchestrator.tqdm') as MockTqdm:

        MockTqdm.side_effect = lambda x, **kwargs: x
        mock_scraper = MagicMock()
        MockScraper.return_value = mock_scraper
        mock_scraper.fetch_chapter_html.side_effect = Exception("Scraping failed")

        with pytest.raises(Exception) as exc_info:
            run_orchestrator(start=776, end=776, delay=0.1, cache_dir=str(tmp_path), output="out.pdf")
        assert "Scraping failed" in str(exc_info.value)


def test_orchestrator_compiler_failure(tmp_path):
    with patch('src.orchestrator.CachingManager'), \
         patch('src.orchestrator.NovelScraper') as MockScraper, \
         patch('src.orchestrator.XPathParser') as MockParser, \
         patch('src.orchestrator.ContentSanitizer') as MockSanitizer, \
         patch('src.orchestrator.PDFCompiler') as MockCompiler, \
         patch('src.orchestrator.tqdm') as MockTqdm:

        MockTqdm.side_effect = lambda x, **kwargs: x
        mock_scraper = MagicMock()
        mock_parser = MagicMock()
        mock_sanitizer = MagicMock()
        mock_compiler = MagicMock()

        MockScraper.return_value = mock_scraper
        MockParser.return_value = mock_parser
        MockSanitizer.return_value = mock_sanitizer
        MockCompiler.return_value = mock_compiler

        mock_scraper.fetch_chapter_html.return_value = "html"
        mock_parser.parse.return_value = ("Title", "body")
        mock_sanitizer.sanitize.return_value = ["para"]
        mock_compiler.compile.side_effect = Exception("PDF generation failed")

        with pytest.raises(Exception) as exc_info:
            run_orchestrator(start=776, end=776, delay=0.1, cache_dir=str(tmp_path), output="out.pdf")
        assert "PDF generation failed" in str(exc_info.value)
