"""Tests for the interactive compiler interface in the TUI."""

import asyncio
import pytest
from unittest.mock import patch, MagicMock
from src.tui import ScraperApp

def test_tui_compiler_ui():
    """Verify that the compiler tab allows input and triggers orchestrator."""
    from textual.widgets import Label, Input, Button, Select

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
            await pilot.pause()
            
            # Mock run_orchestrator
            with patch("src.tui.run_orchestrator") as mock_orchestrator:
                # Trigger compile button
                compile_btn.press()
                
                # Allow the event to dispatch and disable the button
                await pilot.pause(0.05)
                
                # Wait for compilation worker to finish and re-enable button
                for _ in range(50):
                    if not compile_btn.disabled:
                        break
                    await pilot.pause(0.01)
                
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

def test_tui_compile_scope_toggles():
    """Verify that scope dropdown selections dynamically toggle and populate fields."""
    from textual.widgets import Select, Input
    app = ScraperApp()

    async def run_test_helper():
        async with app.run_test() as pilot:
            from textual.widgets import TabbedContent
            app.query_one(TabbedContent).active = "compile_tab"
            await pilot.pause()

            scope_select = app.query_one("#compile_scope", Select)
            start_input = app.query_one("#compile_start", Input)
            end_input = app.query_one("#compile_end", Input)

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

            # 5. Back to Custom
            scope_select.value = "custom"
            await pilot.pause(0.05)
            assert start_input.disabled is False
            assert start_input.value == ""
            assert end_input.disabled is False
            assert end_input.value == ""

    asyncio.run(run_test_helper())

def test_tui_compile_blank_defaults():
    """Verify that open-ended/blank values resolve to cached range min/max."""
    from textual.widgets import Input, Button, Label
    app = ScraperApp()

    async def run_test_helper():
        async with app.run_test() as pilot:
            from textual.widgets import TabbedContent
            app.query_one(TabbedContent).active = "compile_tab"
            await pilot.pause()

            compile_start = app.query_one("#compile_start", Input)
            compile_end = app.query_one("#compile_end", Input)
            compile_btn = app.query_one("#compile_btn", Button)

            # Clear inputs under custom scope to test blank handling
            compile_start.value = ""
            compile_end.value = ""
            await pilot.pause()

            # Mock get_cached_chapters to simulate cached range [50, 100, 200]
            with patch("src.tui.get_cached_chapters", return_value=[50, 100, 200]):
                with patch("src.tui.run_orchestrator") as mock_orchestrator:
                    compile_btn.press()
                    
                    # Allow the event to dispatch and disable the button
                    await pilot.pause(0.05)
                    
                    # Wait for compilation worker to finish and re-enable button
                    for _ in range(50):
                        if not compile_btn.disabled:
                            break
                        await pilot.pause(0.01)

                    # Both blank (start/end) should resolve to 50/200 respectively
                    mock_orchestrator.assert_called_once_with(
                        start=50,
                        end=200,
                        delay=1.0,
                        cache_dir="./cache",
                        output="novel_compiled",
                        format="both",
                        threads=4,
                        url=None,
                        status_callback=None
                    )

    asyncio.run(run_test_helper())
