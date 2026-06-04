"""Tests for Cache Browser backend logic used by the TUI."""

import pytest
from src.cache import CachingManager
from src.tui import get_cached_chapters, calculate_gaps

def test_get_cached_chapters(tmp_path):
    """Verify that get_cached_chapters scans the cache directory and parses numbers."""
    # Write some dummy chapter files
    (tmp_path / "chapter_1.html").write_text("Ch 1")
    (tmp_path / "chapter_5.html").write_text("Ch 5")
    (tmp_path / "chapter_10.html").write_text("Ch 10")
    (tmp_path / "other_file.txt").write_text("ignore")
    (tmp_path / "chapter_invalid.html").write_text("ignore")

    chapters = get_cached_chapters(str(tmp_path))
    assert chapters == [1, 5, 10]

def test_calculate_gaps():
    """Verify that calculate_gaps detects missing ranges correctly."""
    assert calculate_gaps([]) == []
    assert calculate_gaps([1, 2, 3]) == []
    assert calculate_gaps([1, 3, 5]) == [(2, 2), (4, 4)]
    assert calculate_gaps([1, 2, 5, 6, 10]) == [(3, 4), (7, 9)]

def test_cache_browser_ui(tmp_path):
    """Verify that the Cache Browser UI displays stats and lists files correctly."""
    from src.tui import ScraperApp
    from textual.widgets import OptionList, Label
    import asyncio

    # Write dummy cached files
    (tmp_path / "chapter_2.html").write_text("Ch 2")
    (tmp_path / "chapter_3.html").write_text("Ch 3")
    (tmp_path / "chapter_5.html").write_text("Ch 5")

    app = ScraperApp()
    # Point the app's cache directory to our tmp_path
    app.cache_dir = str(tmp_path)

    async def run_test_helper():
        async with app.run_test() as pilot:
            # Switch to Cache Browser tab
            from textual.widgets import TabbedContent
            app.query_one(TabbedContent).active = "cache_tab"
            await pilot.pause()
            
            # Verify UI components are present
            refresh_btn = app.query_one("#refresh_cache_btn")
            clear_btn = app.query_one("#clear_cache_btn")
            summary_lbl = app.query_one("#cache_summary", Label)
            chapters_list = app.query_one("#cached_chapters_list", OptionList)

            assert refresh_btn is not None
            assert clear_btn is not None
            assert summary_lbl is not None
            assert chapters_list is not None

            # Verify summary stats
            assert "Total Chapters Cached: 3" in str(summary_lbl.content)
            assert "Missing Chapter Gaps: 4" in str(summary_lbl.content)

            # Verify OptionList contains chapters
            assert chapters_list.option_count == 3
            assert "Chapter 2" in str(chapters_list.get_option_at_index(0).prompt)
            assert "Chapter 3" in str(chapters_list.get_option_at_index(1).prompt)
            assert "Chapter 5" in str(chapters_list.get_option_at_index(2).prompt)

            # Let's test clearing cache
            await pilot.click("#clear_cache_btn")
            
            # Verify files are deleted
            assert not (tmp_path / "chapter_2.html").exists()
            assert not (tmp_path / "chapter_3.html").exists()
            assert not (tmp_path / "chapter_5.html").exists()

            # Verify UI updated
            assert "Total Chapters Cached: 0" in str(summary_lbl.content)
            assert chapters_list.option_count == 0

    asyncio.run(run_test_helper())


