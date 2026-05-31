import os
import pytest
from unittest.mock import MagicMock, patch
from src.cli import parse_args
from src.orchestrator import run_orchestrator

def test_cli_update_argument():
    """Verify that the new --update argument is parsed."""
    args = parse_args(["--update", "novel.epub"])
    assert args.update == "novel.epub"

def test_auto_update_raises_if_no_url_and_no_metadata(tmp_path):
    """Verify that run_orchestrator raises ValueError if --update path has no url and no metadata."""
    dummy_file = tmp_path / "empty.epub"
    dummy_file.write_text("dummy")

    with pytest.raises(ValueError) as exc_info:
        run_orchestrator(
            start=None,
            end=None,
            delay=1.0,
            cache_dir=str(tmp_path / "cache"),
            output=str(dummy_file),
            update=str(dummy_file)
        )
    assert "No landing page URL found" in str(exc_info.value)

def test_auto_update_flow_no_new_chapters(tmp_path):
    """Verify that auto-update exits early if there are no new chapters."""
    output_epub = tmp_path / "novel.epub"
    output_epub.write_text("dummy")
    
    # We will mock the metadata reading to return a landing URL
    landing_url = "https://freewebnovel.com/some-novel.html"
    
    # Mocking landing page to have chapters 1 and 2
    landing_html = """
    <html>
        <body>
            <a href="/some-novel/chapter-1.html">Chapter 1</a>
            <a href="/some-novel/chapter-2.html">Chapter 2</a>
        </body>
    </html>
    """

    with patch('src.orchestrator.extract_source_url_from_epub') as mock_extract_url, \
         patch('src.orchestrator.extract_chapters_from_epub') as mock_extract_chapters, \
         patch('src.orchestrator.EPUBCompiler') as MockCompiler, \
         patch('src.orchestrator.NovelScraper') as MockScraper, \
         patch('requests.get') as mock_requests_get:

        mock_extract_url.return_value = landing_url
        mock_extract_chapters.return_value = [
            {"title": "Chapter 1", "paragraphs": ["P1"]},
            {"title": "Chapter 2", "paragraphs": ["P2"]}
        ]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = landing_html
        mock_requests_get.return_value = mock_response

        # Run orchestrator with update
        # Since chapters 1 & 2 are already present, it should find no new chapters and do nothing
        run_orchestrator(
            start=None,
            end=None,
            delay=1.0,
            cache_dir=str(tmp_path / "cache"),
            output=str(output_epub),
            update=str(output_epub)
        )
        
        # EPUBCompiler should NOT be instantiated to compile new stuff
        MockCompiler.assert_not_called()

def test_auto_update_flow_with_new_chapters(tmp_path):
    """Verify that auto-update fetches and compiles new chapters alongside existing ones."""
    output_epub = tmp_path / "novel.epub"
    output_epub.write_text("dummy")
    
    landing_url = "https://freewebnovel.com/some-novel.html"
    
    # Mocking landing page to have chapters 1, 2, and 3 (chapter 3 is new!)
    landing_html = """
    <html>
        <body>
            <a href="/some-novel/chapter-1.html">Chapter 1</a>
            <a href="/some-novel/chapter-2.html">Chapter 2</a>
            <a href="/some-novel/chapter-3.html">Chapter 3</a>
        </body>
    </html>
    """
    dummy_chapter_html = "<html><body>Chapter 3 content</body></html>"

    with patch('src.orchestrator.extract_source_url_from_epub') as mock_extract_url, \
         patch('src.orchestrator.extract_chapters_from_epub') as mock_extract_chapters, \
         patch('src.orchestrator.CachingManager'), \
         patch('src.orchestrator.NovelScraper') as MockScraper, \
         patch('src.orchestrator.XPathParser') as MockParser, \
         patch('src.orchestrator.ContentSanitizer') as MockSanitizer, \
         patch('src.orchestrator.EPUBCompiler') as MockCompiler, \
         patch('src.orchestrator.tqdm') as MockTqdm, \
         patch('requests.get') as mock_requests_get:

        mock_extract_url.return_value = landing_url
        mock_extract_chapters.return_value = [
            {"title": "Chapter 1", "paragraphs": ["P1"]},
            {"title": "Chapter 2", "paragraphs": ["P2"]}
        ]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = landing_html
        mock_requests_get.return_value = mock_response

        mock_scraper = MagicMock()
        mock_parser = MagicMock()
        mock_sanitizer = MagicMock()
        mock_compiler = MagicMock()

        MockScraper.return_value = mock_scraper
        MockParser.return_value = mock_parser
        MockSanitizer.return_value = mock_sanitizer
        MockCompiler.return_value = mock_compiler
        MockTqdm.side_effect = lambda x, **kwargs: x

        mock_scraper.fetch_chapter_html.return_value = dummy_chapter_html
        mock_parser.parse.return_value = ("Chapter 3", "<div>Body 3</div>")
        mock_sanitizer.sanitize.return_value = ["Paragraph 3"]

        # Run orchestrator with update
        run_orchestrator(
            start=None,
            end=None,
            delay=1.0,
            cache_dir=str(tmp_path / "cache"),
            output=str(output_epub),
            update=str(output_epub),
            format="epub"
        )
        
        # Scraper should only be called for chapter 3!
        mock_scraper.fetch_chapter_html.assert_called_once_with(3)
        
        # EPUBCompiler should compile the combined chapters: 1, 2, and 3
        mock_compiler.compile.assert_called_once()
        args, kwargs = mock_compiler.compile.call_args
        compiled_chapters = args[0]
        assert len(compiled_chapters) == 3
        assert compiled_chapters[0]["title"] == "Chapter 1"
        assert compiled_chapters[1]["title"] == "Chapter 2"
        assert compiled_chapters[2]["title"] == "Chapter 3"


def test_auto_update_ignores_chapters_before_existing_start(tmp_path):
    """Verify that auto-update ignores any new/missing chapters on landing page that are before the existing minimum chapter."""
    output_epub = tmp_path / "novel.epub"
    output_epub.write_text("dummy")
    
    landing_url = "https://freewebnovel.com/some-novel.html"
    
    # Mocking landing page to have chapters 1, 2, 3, and 4
    landing_html = """
    <html>
        <body>
            <a href="/some-novel/chapter-1.html">Chapter 1</a>
            <a href="/some-novel/chapter-2.html">Chapter 2</a>
            <a href="/some-novel/chapter-3.html">Chapter 3</a>
            <a href="/some-novel/chapter-4.html">Chapter 4</a>
        </body>
    </html>
    """
    dummy_chapter_html = "<html><body>Chapter 4 content</body></html>"

    with patch('src.orchestrator.extract_source_url_from_epub') as mock_extract_url, \
         patch('src.orchestrator.extract_chapters_from_epub') as mock_extract_chapters, \
         patch('src.orchestrator.CachingManager'), \
         patch('src.orchestrator.NovelScraper') as MockScraper, \
         patch('src.orchestrator.XPathParser') as MockParser, \
         patch('src.orchestrator.ContentSanitizer') as MockSanitizer, \
         patch('src.orchestrator.EPUBCompiler') as MockCompiler, \
         patch('src.orchestrator.tqdm') as MockTqdm, \
         patch('requests.get') as mock_requests_get:

        mock_extract_url.return_value = landing_url
        # Existing EPUB starts at Chapter 3, completely omitting 1 and 2
        mock_extract_chapters.return_value = [
            {"title": "Chapter 3", "paragraphs": ["P3"]}
        ]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = landing_html
        mock_requests_get.return_value = mock_response

        mock_scraper = MagicMock()
        mock_parser = MagicMock()
        mock_sanitizer = MagicMock()
        mock_compiler = MagicMock()

        MockScraper.return_value = mock_scraper
        MockParser.return_value = mock_parser
        MockSanitizer.return_value = mock_sanitizer
        MockCompiler.return_value = mock_compiler
        MockTqdm.side_effect = lambda x, **kwargs: x

        mock_scraper.fetch_chapter_html.return_value = dummy_chapter_html
        mock_parser.parse.return_value = ("Chapter 4", "<div>Body 4</div>")
        mock_sanitizer.sanitize.return_value = ["Paragraph 4"]

        # Run orchestrator with update
        run_orchestrator(
            start=None,
            end=None,
            delay=1.0,
            cache_dir=str(tmp_path / "cache"),
            output=str(output_epub),
            update=str(output_epub),
            format="epub"
        )
        
        # Scraper should only be called for chapter 4! NOT 1 or 2!
        mock_scraper.fetch_chapter_html.assert_called_once_with(4)
        
        # EPUBCompiler should compile the combined chapters: 3 and 4
        mock_compiler.compile.assert_called_once()
        args, _ = mock_compiler.compile.call_args
        compiled_chapters = args[0]
        assert len(compiled_chapters) == 2
        assert compiled_chapters[0]["title"] == "Chapter 3"
        assert compiled_chapters[1]["title"] == "Chapter 4"
