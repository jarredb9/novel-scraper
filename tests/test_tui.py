from unittest.mock import patch
from src.tui import run_tui

def test_run_tui():
    """Verify that run_tui instantiates and runs the ScraperApp."""
    with patch('src.tui.ScraperApp.run') as mock_run:
        run_tui()
        mock_run.assert_called_once()

def test_parse_field_chapter():
    """Verify that parse_field_chapter correctly parses single numbers and boundaries."""
    from src.tui import parse_field_chapter
    import pytest

    assert parse_field_chapter("100") == 100
    assert parse_field_chapter(" 100 ") == 100
    assert parse_field_chapter("") is None
    assert parse_field_chapter("Beginning") is None
    assert parse_field_chapter("End of Novel") is None
    
    with pytest.raises(ValueError, match="must be >= 1"):
        parse_field_chapter("0")
    with pytest.raises(ValueError, match="must be >= 1"):
        parse_field_chapter("-5")
    with pytest.raises(ValueError, match="Invalid chapter number"):
        parse_field_chapter("abc")

def test_tui_escape_unfocus():
    """Verify that pressing Escape removes focus from inputs in the TUI."""
    from src.tui import ScraperApp
    from textual.widgets import Input
    import asyncio

    app = ScraperApp()

    async def run_test_helper():
        async with app.run_test() as pilot:
            # Set focus to scrape URL input
            url_input = app.query_one("#scrape_url", Input)
            app.set_focus(url_input)
            await pilot.pause()
            assert app.focused == url_input

            # Press escape key
            await pilot.press("escape")
            await pilot.pause()
            
            # Focus should be cleared
            assert app.focused is None

    asyncio.run(run_test_helper())

