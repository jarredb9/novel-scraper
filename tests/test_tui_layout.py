"""Tests for the TUI layout and basic structure."""

import asyncio
from src.tui import ScraperApp

def test_scraper_app_structure():
    """Verify that ScraperApp has the correct tabbed layout."""
    app = ScraperApp()
    
    async def run_test_helper():
        async with app.run_test() as pilot:
            # Check that the app is running and contains the TabbedContent widget
            from textual.widgets import TabbedContent, TabPane
            tabbed_content = app.query_one(TabbedContent)
            assert tabbed_content is not None
            
            # Verify the tabs are as expected by querying their IDs
            scrape_tab = app.query_one("#scrape_tab", TabPane)
            cache_tab = app.query_one("#cache_tab", TabPane)
            compile_tab = app.query_one("#compile_tab", TabPane)
            
            assert scrape_tab is not None
            assert cache_tab is not None
            assert compile_tab is not None

    asyncio.run(run_test_helper())
