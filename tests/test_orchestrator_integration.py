import os
import pytest
from unittest.mock import patch, MagicMock
from src.orchestrator import run_orchestrator

def test_run_orchestrator_integration(tmp_path):
    """
    Test the full orchestrator flow with cover and update_epub.
    """
    cache_dir = tmp_path / "cache"
    output_base = tmp_path / "output_novel"
    cover_input = tmp_path / "custom_cover.jpg"
    existing_epub = tmp_path / "existing.epub"
    
    # Create files
    cover_input.write_bytes(b"dummy image content")
    existing_epub.write_bytes(b"dummy epub content")
    
    # Chapters inside the existing EPUB
    mock_epub_chapters = [
        {"title": "Chapter 1: The Beginning", "paragraphs": ["Para 1.1"]},
        {"title": "Chapter 2: The Journey", "paragraphs": ["Para 2.1"]},
    ]
    
    # Mock all the components to check how they coordinate
    with patch("src.orchestrator.resolve_cover") as mock_resolve, \
         patch("src.orchestrator.extract_chapters_from_epub") as mock_extract, \
         patch("src.orchestrator.CachingManager") as MockCache, \
         patch("src.orchestrator.NovelScraper") as MockScraper, \
         patch("src.orchestrator.XPathParser") as MockParser, \
         patch("src.orchestrator.ContentSanitizer") as MockSanitizer, \
         patch("src.orchestrator.PDFCompiler") as MockPDFCompiler, \
         patch("src.orchestrator.EPUBCompiler") as MockEPUBCompiler, \
         patch("src.orchestrator.tqdm") as MockTqdm:
         
        # Set up mocks
        mock_resolve.return_value = str(cache_dir / "cover.jpg")
        mock_extract.return_value = mock_epub_chapters
        MockTqdm.side_effect = lambda x, **kwargs: x
        
        mock_scraper = MagicMock()
        mock_scraper.base_url = "https://freewebnovel.com/the-first-legendary-beast-master/chapter-"
        MockScraper.return_value = mock_scraper
        
        # We request chapters 2 to 3.
        # Chapter 2 is in existing EPUB. Chapter 3 is new and must be downloaded.
        mock_scraper.fetch_chapter_html.return_value = "<html><body>Chapter 3 content</body></html>"
        
        mock_parser = MagicMock()
        mock_parser.parse.return_value = ("Chapter 3: The Climax", "<div>Body 3</div>")
        MockParser.return_value = mock_parser
        
        mock_sanitizer = MagicMock()
        mock_sanitizer.sanitize.return_value = ["Para 3.1"]
        MockSanitizer.return_value = mock_sanitizer
        
        mock_pdf_compiler = MagicMock()
        MockPDFCompiler.return_value = mock_pdf_compiler
        
        mock_epub_compiler = MagicMock()
        MockEPUBCompiler.return_value = mock_epub_compiler
        
        # Run orchestrator
        run_orchestrator(
            start=2,
            end=3,
            delay=0.1,
            cache_dir=str(cache_dir),
            output=str(output_base),
            update_epub=str(existing_epub),
            cover=str(cover_input),
            format="both"
        )
        
        # Verify cover resolution was invoked with correct arguments
        mock_resolve.assert_called_once_with(str(cover_input), mock_scraper.base_url, str(cache_dir))
        
        # Verify EPUB extraction was called
        mock_extract.assert_called_once_with(str(existing_epub))
        
        # Verify that scraper.fetch_chapter_html was only called for Chapter 3, NOT Chapter 2
        mock_scraper.fetch_chapter_html.assert_called_once_with(3)
        mock_scraper.fetch_chapter_html.assert_any_call(3)
        with pytest.raises(AssertionError):
            mock_scraper.fetch_chapter_html.assert_any_call(2)
            
        # Verify compilation calls have all compiled chapters (1, 2, 3)
        # Wait, Chapter 1 was in the EPUB, so it should be included even if it was not in start/end!
        # Chapter 2 was in the EPUB, Chapter 3 is new. So we merge all.
        pdf_args, pdf_kwargs = mock_pdf_compiler.compile.call_args
        pdf_chapters = pdf_args[0]
        assert len(pdf_chapters) == 3
        # Check order is sorted
        assert pdf_chapters[0]["title"] == "Chapter 1: The Beginning"
        assert pdf_chapters[1]["title"] == "Chapter 2: The Journey"
        assert pdf_chapters[2]["title"] == "Chapter 3: The Climax"
        
        # Check cover path passed to compile
        assert pdf_kwargs.get("cover_path") == str(cache_dir / "cover.jpg")
        
        epub_args, epub_kwargs = mock_epub_compiler.compile.call_args
        assert len(epub_args[0]) == 3
        assert epub_kwargs.get("cover_path") == str(cache_dir / "cover.jpg")
