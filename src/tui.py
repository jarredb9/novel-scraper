"""Interactive Terminal User Interface for the novel scraper.

This module provides the Textual application interface for monitoring downloads,
managing cached files, and compiling novels.
"""

import logging
from typing import Optional, Callable
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent, TabPane, Label, Input, Button, ProgressBar, RichLog
from textual.containers import Vertical, Horizontal
from src.orchestrator import run_orchestrator

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
    .form-group {
        margin: 1 0;
        height: auto;
    }
    .field-row {
        layout: horizontal;
        height: 3;
        margin-bottom: 1;
    }
    .field-row Label {
        width: 25;
        align-vertical: middle;
    }
    .field-row Input {
        width: 1fr;
    }
    #start_scrape_btn {
        margin-top: 1;
        width: 100%;
        background: $success;
    }
    #log_pane_container {
        height: 1fr;
        border: tall $secondary;
        margin-top: 1;
    }
    #thread_status_pane {
        height: 5;
        border: tall $accent;
        margin-top: 1;
        background: $panel;
    }
    """

    TITLE = "Novel Scraper Dashboard"
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.log_handler = TUILogHandler(self.log_to_pane)
        self.log_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        logger = logging.getLogger("novel_scraper")
        logger.addHandler(self.log_handler)
        self.active_threads_status = {}

    def log_to_pane(self, message: str) -> None:
        """Route log messages to the TUI RichLog widget."""
        try:
            log_widget = self.query_one("#live_logs", RichLog)
            self.call_from_thread(log_widget.write, message)
        except Exception:
            pass

    def compose(self) -> ComposeResult:
        """Compose the layout of the application."""
        yield Header(show_clock=True)
        with TabbedContent():
            with TabPane("Scrape Dashboard", id="scrape_tab"):
                with Vertical(classes="form-group"):
                    with Horizontal(classes="field-row"):
                        yield Label("Novel / Landing URL:")
                        yield Input(
                            value="https://freewebnovel.com/the-first-legendary-beast-master.html",
                            id="scrape_url"
                        )
                    with Horizontal(classes="field-row"):
                        yield Label("Start Chapter:")
                        yield Input(value="800", id="scrape_start")
                    with Horizontal(classes="field-row"):
                        yield Label("End Chapter:")
                        yield Input(value="805", id="scrape_end")
                    with Horizontal(classes="field-row"):
                        yield Label("Threads:")
                        yield Input(value="4", id="scrape_threads")
                    with Horizontal(classes="field-row"):
                        yield Label("Delay (s):")
                        yield Input(value="1.0", id="scrape_delay")
                    yield Button("Start Scraping", id="start_scrape_btn")
                
                yield ProgressBar(id="scrape_progress", total=100, show_percentage=True)
                with Vertical(id="thread_status_pane"):
                    yield Label("Active Threads Status:", id="thread_status_title")
                    yield Label("Idle", id="thread_status_text")
                with Vertical(id="log_pane_container"):
                    yield Label("Live Logs:")
                    yield RichLog(id="live_logs", highlight=True, markup=True)

            with TabPane("Cache Browser", id="cache_tab"):
                yield Label("Cache Browser Content")
            with TabPane("Interactive Compiler", id="compile_tab"):
                yield Label("Interactive Compiler Content")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "start_scrape_btn":
            self.start_scraping_job()

    def start_scraping_job(self) -> None:
        """Initiate the background scraping task."""
        url = self.query_one("#scrape_url", Input).value
        try:
            start = int(self.query_one("#scrape_start", Input).value)
        except ValueError:
            start = None
        try:
            end = int(self.query_one("#scrape_end", Input).value)
        except ValueError:
            end = None
        try:
            threads = int(self.query_one("#scrape_threads", Input).value)
        except ValueError:
            threads = 4
        try:
            delay = float(self.query_one("#scrape_delay", Input).value)
        except ValueError:
            delay = 1.0

        # Disable button during scrape
        btn = self.query_one("#start_scrape_btn", Button)
        btn.disabled = True
        
        # Reset progress bar
        pbar = self.query_one("#scrape_progress", ProgressBar)
        pbar.progress = 0
        if start is not None and end is not None:
            pbar.update(total=max(1, end - start + 1))
        
        self.active_threads_status = {}
        self.query_one("#thread_status_text", Label).update("Starting...")

        self.run_worker(
            self.scrape_worker(start, end, delay, threads, url),
            exclusive=True
        )

    async def scrape_worker(self, start, end, delay, threads, url) -> None:
        """Background worker that calls the orchestrator."""
        def status_callback(chapter_num: int, status: str, message: str):
            self.call_from_thread(self.handle_scraper_status, chapter_num, status, message)

        try:
            # Run the blocking orchestrator in a thread pool via run_orchestrator
            await self.run_in_thread(
                run_orchestrator,
                start=start,
                end=end,
                delay=delay,
                cache_dir="./cache",
                output="novel_tui_download",
                format="both",
                threads=threads,
                url=url,
                status_callback=status_callback
            )
            self.call_from_thread(self.finish_scrape, True)
        except Exception as e:
            self.log_to_pane(f"[red]Scraping failed: {str(e)}[/red]")
            self.call_from_thread(self.finish_scrape, False)

    def handle_scraper_status(self, chapter_num: int, status: str, message: str) -> None:
        """Update TUI elements based on callback status from threads."""
        self.active_threads_status[chapter_num] = status
        
        # Update thread status label
        active_chaps = [
            f"Ch {ch} ({stat})"
            for ch, stat in sorted(self.active_threads_status.items())
            if stat in ("fetching", "sleep", "start")
        ]
        status_str = ", ".join(active_chaps) if active_chaps else "Idle"
        self.query_one("#thread_status_text", Label).update(status_str)

        # Update progress bar on success/hit
        if status in ("success", "hit"):
            pbar = self.query_one("#scrape_progress", ProgressBar)
            pbar.advance(1)

    def finish_scrape(self, success: bool) -> None:
        """Re-enable start button and update statuses on completion."""
        btn = self.query_one("#start_scrape_btn", Button)
        btn.disabled = False
        self.query_one("#thread_status_text", Label).update("Finished!")
        if success:
            self.log_to_pane("[green]Scraping and compilation complete![/green]")

def run_tui() -> None:
    """Run the interactive TUI application."""
    app = ScraperApp()
    app.run()
