"""Tests for the interactive compiler interface in the TUI."""

import asyncio
import pytest
from unittest.mock import patch, MagicMock
from src.tui import ScraperApp

def test_tui_compiler_ui(tmp_path):
    """Verify that the compiler tab allows input and triggers orchestrator."""
    from textual.widgets import Label, Input, Button, Select
    import asyncio

    app = ScraperApp()
    
    async def run_test_helper():
        async with app.run_test() as pilot:
            # Switch to Compiler tab
            from textual.widgets import TabbedContent
            app.query_one(TabbedContent).active = "compile_tab"
            await pilot.pause()
            
            # Verify UI components exist
            compile_start = app.query_one("#compile_start", Input)
            compile_end = app.query_one("#compile_end", Input)
            compile_output = app.query_one("#compile_output", Input)
            compile_format = app.query_one("#compile_format", Select)
            compile_btn = app.query_one("#compile_btn", Button)
            compile_status = app.query_one("#compile_status", Label)
            
            assert compile_start is not None
            assert compile_end is not None
            assert compile_output is not None
            assert compile_format is not None
            assert compile_btn is not None
            assert compile_status is not None
            
            # Change inputs
            compile_start.value = "10"
            compile_end.value = "15"
            compile_output.value = "test_novel"
            compile_format.value = "pdf"
            
            # Mock run_orchestrator
            with patch("src.tui.run_orchestrator") as mock_orchestrator:
                # Trigger compile button
                await pilot.click("#compile_btn")
                await pilot.pause()
                
                # Check that run_orchestrator was called
                mock_orchestrator.assert_called_once_with(
                    start=10,
                    end=15,
                    delay=1.0,
                    cache_dir="./cache",
                    output="test_novel",
                    format="pdf",
                    threads=4,
                    url=None,
                    status_callback=None
                )
                
                # Verify status message shows compilation status
                assert any(msg in str(compile_status.content) for msg in ("Compiling...", "Compilation complete!"))

    asyncio.run(run_test_helper())
