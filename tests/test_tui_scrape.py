"""Tests for TUI scraping progress and live log pane features."""

import pytest
import logging
from unittest.mock import MagicMock
from src.scraper import NovelScraper
from src.cache import CachingManager

def test_scraper_status_callback():
    """Verify that NovelScraper triggers the status_callback at key moments."""
    callback_events = []
    
    def dummy_callback(chapter_num: int, status: str, message: str):
        callback_events.append((chapter_num, status, message))
        
    mock_cache = MagicMock(spec=CachingManager)
    # Simulate a cache hit
    mock_cache.is_cached.return_value = True
    mock_cache.read_chapter.return_value = "<html>Content</html>"
    
    scraper = NovelScraper(
        cache_manager=mock_cache,
        delay=0.1,
    )
    # Check that status_callback attribute exists or can be set/passed
    scraper.status_callback = dummy_callback
    
    scraper.fetch_chapter_html(1)
    
    # We should have a hit callback event
    assert len(callback_events) > 0
    assert any(status == "hit" or status == "success" for _, status, _ in callback_events)

def test_tui_log_handler():
    """Verify that a custom TUI log handler exists and routes log messages."""
    from src.tui import TUILogHandler
    
    # Create handler with a mock widget or queue
    handler = TUILogHandler()
    mock_write = MagicMock()
    handler.write_func = mock_write
    
    logger = logging.getLogger("test_tui_logger")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    logger.info("Test message for TUI")
    
    mock_write.assert_called_once()
    args, _ = mock_write.call_args
    assert "Test message for TUI" in args[0]

def test_tui_finish_scrape_warning():
    """Verify that finish_scrape displays errors/warnings on failure."""
    from src.tui import ScraperApp
    from textual.widgets import Label
    import asyncio

    app = ScraperApp()

    async def run_test_helper():
        async with app.run_test() as pilot:
            # Set thread status with an error
            app.active_threads_status[804] = "error"
            
            # Call finish_scrape with success=False
            app.finish_scrape(False)
            
            # Check status label
            status_text = app.query_one("#thread_status_text", Label)
            assert "Failed! Errors in chapters: 804" in str(status_text.content)

    asyncio.run(run_test_helper())

