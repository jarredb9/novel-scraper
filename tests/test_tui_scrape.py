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

def test_tui_cancel_scraping():
    """Verify that clicking the Stop button sets cancel flag and cancels worker."""
    from src.tui import ScraperApp
    from textual.widgets import Button
    import asyncio
    from unittest.mock import MagicMock

    app = ScraperApp()

    async def run_test_helper():
        async with app.run_test() as pilot:
            stop_btn = app.query_one("#stop_scrape_btn", Button)
            assert stop_btn.disabled is True

            # Enable stop button to allow click
            stop_btn.disabled = False
            
            # Mock a running worker task
            mock_task = MagicMock()
            app.scrape_worker_task = mock_task
            
            # Click stop button
            stop_btn.press()
            await pilot.pause()
            
            # Verify cancel flag is set and task cancelled
            assert app.scrape_cancelled is True
            mock_task.cancel.assert_called_once()

    asyncio.run(run_test_helper())

def test_tui_cancelled_error_handling():
    """Verify that when scrape_worker raises CancelledError, UI status is set to Cancelled!"""
    from src.tui import ScraperApp
    from textual.widgets import Label
    import asyncio

    app = ScraperApp()
    app.scrape_cancelled = True

    async def run_test_helper():
        async with app.run_test() as pilot:
            # Manually trigger finish_scrape(False) with cancellation flag
            app.finish_scrape(False)
            
            # Check status label
            status_text = app.query_one("#thread_status_text", Label)
            assert "Cancelled!" in str(status_text.content)

    asyncio.run(run_test_helper())

def test_tui_scrape_scope_toggles():
    """Verify that scope dropdown selections dynamically toggle and populate fields."""
    from src.tui import ScraperApp
    from textual.widgets import Select, Input
    import asyncio

    app = ScraperApp()

    async def run_test_helper():
        async with app.run_test() as pilot:
            scope_select = app.query_one("#scrape_scope", Select)
            start_input = app.query_one("#scrape_start", Input)
            end_input = app.query_one("#scrape_end", Input)

            # 1. Custom Range (default)
            assert start_input.disabled is False
            assert end_input.disabled is False

            # 2. Beginning to Chapter X
            scope_select.value = "beg_to_x"
            await pilot.pause(0.05)
            assert start_input.disabled is True
            assert start_input.value == "Beginning"
            assert end_input.disabled is False

            # 3. Chapter X to End
            scope_select.value = "x_to_end"
            await pilot.pause(0.05)
            assert start_input.disabled is False
            assert end_input.disabled is True
            assert end_input.value == "End of Novel"

            # 4. Entire Novel
            scope_select.value = "entire"
            await pilot.pause(0.05)
            assert start_input.disabled is True
            assert start_input.value == "Beginning"
            assert end_input.disabled is True
            assert end_input.value == "End of Novel"

    asyncio.run(run_test_helper())




