"""Interactive Terminal User Interface for the novel scraper.

This module provides the Textual application interface for monitoring downloads,
managing cached files, and compiling novels.
"""

import logging
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent, TabPane, Label

class TUILogHandler(logging.Handler):
    """Custom logging handler to redirect logs to Textual widgets."""

    def __init__(self, write_func=None):
        super().__init__()
        self.write_func = write_func

    def emit(self, record):
        try:
            msg = self.format(record)
            if self.write_func:
                self.write_func(msg)
        except Exception:
            self.handleError(record)

class ScraperApp(App[None]):
    """The main Textual application for the novel scraper."""

    CSS = """
    Screen {
        background: $background;
        color: $text;
    }
    """

    TITLE = "Novel Scraper Dashboard"
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the layout of the application."""
        yield Header(show_clock=True)
        with TabbedContent():
            with TabPane("Scrape Dashboard", id="scrape_tab"):
                yield Label("Scrape Dashboard Content")
            with TabPane("Cache Browser", id="cache_tab"):
                yield Label("Cache Browser Content")
            with TabPane("Interactive Compiler", id="compile_tab"):
                yield Label("Interactive Compiler Content")
        yield Footer()

def run_tui() -> None:
    """Run the interactive TUI application."""
    app = ScraperApp()
    app.run()
