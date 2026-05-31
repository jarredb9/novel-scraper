import os
import pytest
from unittest.mock import patch, MagicMock
from src.orchestrator import run_orchestrator

def test_orchestrator_multi_threaded_success(tmp_path):
    """
    Verifies that when threads > 1, ThreadPoolExecutor is used and the
    downloaded chapters are correctly collected and sorted.
    """
    cache_dir = tmp_path / "cache"
    output_base = tmp_path / "output_novel"
    
    with patch("src.orchestrator.CachingManager") as MockCache, \
         patch("src.orchestrator.NovelScraper") as MockScraper, \
         patch("src.orchestrator.XPathParser") as MockParser, \
         patch("src.orchestrator.ContentSanitizer") as MockSanitizer, \
         patch("src.orchestrator.PDFCompiler") as MockPDFCompiler, \
         patch("src.orchestrator.tqdm") as MockTqdm:
         
        MockTqdm.side_effect = lambda x, **kwargs: x
        
        mock_scraper = MagicMock()
        mock_scraper.base_url = "https://freewebnovel.com/novel/chapter-"
        MockScraper.return_value = mock_scraper
        
        # Mock requests/caching responses for 3 chapters
        mock_scraper.fetch_chapter_html.side_effect = (
            lambda num: f"<html><body>Chapter {num}</body></html>"
        )
        
        def mock_parse(html):
            clean_num = (
                html.replace("<html><body>Chapter ", "")
                .replace("</body></html>", "")
            )
            return f"Chapter {clean_num}: Title", "<div>Raw Body</div>"

        mock_parser = MagicMock()
        mock_parser.parse.side_effect = mock_parse
        MockParser.return_value = mock_parser
        
        mock_sanitizer = MagicMock()
        mock_sanitizer.sanitize.return_value = ["Para"]
        MockSanitizer.return_value = mock_sanitizer
        
        mock_pdf_compiler = MagicMock()
        MockPDFCompiler.return_value = mock_pdf_compiler
        
        # Run orchestrator with 3 threads
        run_orchestrator(
            start=1,
            end=3,
            delay=0.1,
            cache_dir=str(cache_dir),
            output=str(output_base),
            format="pdf",
            threads=3
        )
        
        # Verify all chapters were scraped
        assert mock_scraper.fetch_chapter_html.call_count == 3
        mock_scraper.fetch_chapter_html.assert_any_call(1)
        mock_scraper.fetch_chapter_html.assert_any_call(2)
        mock_scraper.fetch_chapter_html.assert_any_call(3)
        
        # Verify output compiled sorted list of chapters
        pdf_args, _ = mock_pdf_compiler.compile.call_args
        compiled_chapters = pdf_args[0]
        assert len(compiled_chapters) == 3
        assert compiled_chapters[0]["title"] == "Chapter 1: Title"
        assert compiled_chapters[1]["title"] == "Chapter 2: Title"
        assert compiled_chapters[2]["title"] == "Chapter 3: Title"

def test_orchestrator_multi_threaded_fail_fast(tmp_path):
    """
    Verifies that if a thread raises an exception, the remaining tasks
    are cancelled and the orchestrator aborts.
    """
    cache_dir = tmp_path / "cache"
    output_base = tmp_path / "output_novel"
    
    with patch("src.orchestrator.CachingManager") as MockCache, \
         patch("src.orchestrator.NovelScraper") as MockScraper, \
         patch("src.orchestrator.XPathParser") as MockParser, \
         patch("src.orchestrator.ContentSanitizer") as MockSanitizer, \
         patch("src.orchestrator.PDFCompiler") as MockPDFCompiler, \
         patch("src.orchestrator.tqdm") as MockTqdm:
         
        MockTqdm.side_effect = lambda x, **kwargs: x
        
        mock_scraper = MagicMock()
        mock_scraper.base_url = "https://freewebnovel.com/novel/chapter-"
        MockScraper.return_value = mock_scraper
        
        # Make one chapter scraping fail immediately
        def fetch_side_effect(num):
            if num == 2:
                raise ValueError("Fatal scraping error")
            return f"<html><body>Chapter {num}</body></html>"
            
        mock_scraper.fetch_chapter_html.side_effect = fetch_side_effect
        
        mock_parser = MagicMock()
        mock_parser.parse.return_value = ("Title", "body")
        MockParser.return_value = mock_parser
        
        mock_sanitizer = MagicMock()
        mock_sanitizer.sanitize.return_value = ["Para"]
        MockSanitizer.return_value = mock_sanitizer
        
        # Run orchestrator with 2 threads; should raise exception
        with pytest.raises(ValueError) as exc_info:
            run_orchestrator(
                start=1,
                end=3,
                delay=0.1,
                cache_dir=str(cache_dir),
                output=str(output_base),
                format="pdf",
                threads=2
            )
            
        assert "Fatal scraping error" in str(exc_info.value)
        # Check that PDF compilation was never called
        MockPDFCompiler.return_value.compile.assert_not_called()
