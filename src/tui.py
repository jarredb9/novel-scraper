"""Interactive Terminal User Interface for the novel scraper.

This module provides the Textual application interface for monitoring downloads,
managing cached files, and compiling novels.
"""

import asyncio
import logging
import os
from pathlib import Path
import re
from typing import Optional, Callable

from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import (
    Header,
    Footer,
    TabbedContent,
    TabPane,
    Label,
    Input,
    Button,
    ProgressBar,
    RichLog,
    OptionList,
    Select,
)

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
        background: $success;
        margin-right: 1;
        width: 1fr;
    }
    #stop_scrape_btn {
        width: 1fr;
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
    #refresh_cache_btn, #clear_cache_btn {
        margin-right: 1;
    }
    #cache_summary {
        margin: 1 0;
        background: $panel;
        padding: 1;
        border: solid $primary;
        height: auto;
    }
    #cached_chapters_list {
        height: 1fr;
        border: tall $secondary;
    }
    #compile_status {
        margin-top: 1;
        padding: 1;
        background: $panel;
        border: solid $primary;
        height: auto;
    }
    #compile_btn {
        margin-top: 1;
        width: 100%;
        background: $success;
    }
    """

    TITLE = "Novel Scraper Dashboard"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
        ("escape", "escape_field", "Unfocus Field"),
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
        self.cache_dir = "./cache"
        self.scrape_cancelled = False
        self.scrape_worker_task = None

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
                            value=(
                                "https://freewebnovel.com/"
                                "the-first-legendary-beast-master.html"
                            ),
                            id="scrape_url",
                        )
                    with Horizontal(classes="field-row"):
                        yield Label("Scope Preset:")
                        yield Select(
                            options=[
                                ("Custom Range", "custom"),
                                ("Beginning to Chapter X", "beg_to_x"),
                                ("Chapter X to End", "x_to_end"),
                                ("Entire Novel", "entire"),
                            ],
                            value="custom",
                            id="scrape_scope",
                            allow_blank=False,
                        )
                    with Horizontal(classes="field-row"):
                        yield Label("Start Chapter:")
                        yield Input(
                            value="800",
                            placeholder="Start Chapter",
                            id="scrape_start",
                        )
                    with Horizontal(classes="field-row"):
                        yield Label("End Chapter:")
                        yield Input(
                            value="805",
                            placeholder="End Chapter",
                            id="scrape_end",
                        )
                    with Horizontal(classes="field-row"):
                        yield Label("Threads:")
                        yield Input(value="4", id="scrape_threads")
                    with Horizontal(classes="field-row"):
                        yield Label("Delay (s):")
                        yield Input(value="1.0", id="scrape_delay")
                    with Horizontal(classes="field-row"):
                        yield Button("Start Scraping", id="start_scrape_btn")
                        yield Button(
                            "Stop Scraping",
                            id="stop_scrape_btn",
                            variant="error",
                            disabled=True,
                        )

                yield ProgressBar(
                    id="scrape_progress", total=100, show_percentage=True
                )
                with Vertical(id="thread_status_pane"):
                    yield Label(
                        "Active Threads Status:", id="thread_status_title"
                    )
                    yield Label("Idle", id="thread_status_text")
                with Vertical(id="log_pane_container"):
                    yield Label("Live Logs:")
                    yield RichLog(id="live_logs", highlight=True, markup=True)

            with TabPane("Cache Browser", id="cache_tab"):
                with Horizontal(classes="form-group"):
                    yield Button("Refresh Cache", id="refresh_cache_btn")
                    yield Button(
                        "Clear Cache", id="clear_cache_btn", variant="error"
                    )
                yield Label(
                    "Total Chapters Cached: 0\nMissing Chapter Gaps: None",
                    id="cache_summary",
                )
                yield OptionList(id="cached_chapters_list")
            with TabPane("Interactive Compiler", id="compile_tab"):
                with Vertical(classes="form-group"):
                    with Horizontal(classes="field-row"):
                        yield Label("Scope Preset:")
                        yield Select(
                            options=[
                                ("Custom Range", "custom"),
                                ("Beginning to Chapter X", "beg_to_x"),
                                ("Chapter X to End", "x_to_end"),
                                ("Entire Novel", "entire"),
                            ],
                            value="custom",
                            id="compile_scope",
                            allow_blank=False,
                        )
                    with Horizontal(classes="field-row"):
                        yield Label("Start Chapter:")
                        yield Input(
                            value="800",
                            placeholder="Start Chapter",
                            id="compile_start",
                        )
                    with Horizontal(classes="field-row"):
                        yield Label("End Chapter:")
                        yield Input(
                            value="805",
                            placeholder="End Chapter",
                            id="compile_end",
                        )
                    with Horizontal(classes="field-row"):
                        yield Label("Output Filename:")
                        yield Input(value="novel_compiled", id="compile_output")
                    with Horizontal(classes="field-row"):
                        yield Label("Format:")
                        yield Select(
                            options=[
                                ("EPUB", "epub"),
                                ("PDF", "pdf"),
                                ("Both", "both"),
                            ],
                            value="both",
                            id="compile_format",
                            allow_blank=False,
                        )
                    yield Button("Compile Chapters", id="compile_btn")
                yield Label("Idle", id="compile_status")
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.refresh_cache()

    def action_escape_field(self) -> None:
        """Remove focus from the currently focused widget."""
        if self.focused:
            self.set_focus(None)

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select dropdown selection changes."""
        if event.control.id == "scrape_scope":
            self._update_scope_inputs("scrape", event.value)
        elif event.control.id == "compile_scope":
            self._update_scope_inputs("compile", event.value)

    def _update_scope_inputs(self, prefix: str, scope: str) -> None:
        """Helper to toggle and update start/end inputs based on scope preset."""
        start_input = self.query_one(f"#{prefix}_start", Input)
        end_input = self.query_one(f"#{prefix}_end", Input)

        if scope == "entire":
            start_input.disabled = True
            start_input.value = "Beginning"
            end_input.disabled = True
            end_input.value = "End of Novel"
        elif scope == "beg_to_x":
            start_input.disabled = True
            start_input.value = "Beginning"
            end_input.disabled = False
            if end_input.value == "End of Novel":
                end_input.value = ""
            end_input.placeholder = "Chapter X"
        elif scope == "x_to_end":
            start_input.disabled = False
            if start_input.value == "Beginning":
                start_input.value = ""
            start_input.placeholder = "Chapter X"
            end_input.disabled = True
            end_input.value = "End of Novel"
        else:  # custom
            start_input.disabled = False
            if start_input.value == "Beginning":
                start_input.value = ""
            start_input.placeholder = "Start Chapter"
            
            end_input.disabled = False
            if end_input.value == "End of Novel":
                end_input.value = ""
            end_input.placeholder = "End Chapter"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "start_scrape_btn":
            self.start_scraping_job()
        elif event.button.id == "stop_scrape_btn":
            self.stop_scraping_job()
        elif event.button.id == "refresh_cache_btn":
            self.refresh_cache()
        elif event.button.id == "clear_cache_btn":
            self.clear_cache()
        elif event.button.id == "compile_btn":
            self.start_compilation_job()

    def refresh_cache(self) -> None:
        """Scan the cache directory and update the UI list and summary."""
        chapters = get_cached_chapters(self.cache_dir)
        gaps = calculate_gaps(chapters)

        if gaps:
            gaps_str = ", ".join(
                f"{g[0]}" if g[0] == g[1] else f"{g[0]}-{g[1]}" for g in gaps
            )
        else:
            gaps_str = "None"

        summary_text = (
            f"Total Chapters Cached: {len(chapters)}\n"
            f"Missing Chapter Gaps: {gaps_str}"
        )
        self.query_one("#cache_summary", Label).update(summary_text)

        opt_list = self.query_one("#cached_chapters_list", OptionList)
        opt_list.clear_options()
        for ch in chapters:
            opt_list.add_option(f"Chapter {ch}")

    def clear_cache(self) -> None:
        """Delete all chapter files from the cache directory and update the UI."""
        path = Path(self.cache_dir)
        if path.exists():
            pattern = re.compile(r"^chapter_\d+\.html$")
            for item in path.iterdir():
                if item.is_file() and pattern.match(item.name):
                    try:
                        item.unlink()
                    except Exception:
                        pass
        self.refresh_cache()

    def start_compilation_job(self) -> None:
        """Initiate the background compilation task."""
        scope = self.query_one("#compile_scope", Select).value
        try:
            start_val = self.query_one("#compile_start", Input).value
            start = parse_field_chapter(start_val)
        except ValueError as e:
            self.query_one("#compile_status", Label).update(
                f"[red]Cannot compile: {str(e)}[/red]"
            )
            return

        try:
            end_val = self.query_one("#compile_end", Input).value
            end = parse_field_chapter(end_val)
        except ValueError as e:
            self.query_one("#compile_status", Label).update(
                f"[red]Cannot compile: {str(e)}[/red]"
            )
            return

        if scope == "beg_to_x":
            start = None
            if end is None:
                self.query_one("#compile_status", Label).update(
                    "[red]Error: End Chapter X is required[/red]"
                )
                return
        elif scope == "x_to_end":
            end = None
            if start is None:
                self.query_one("#compile_status", Label).update(
                    "[red]Error: Start Chapter X is required[/red]"
                )
                return
        elif scope == "entire":
            start = None
            end = None

        if start is not None and end is not None and start > end:
            self.query_one("#compile_status", Label).update(
                "[red]Error: Start chapter must be <= End chapter[/red]"
            )
            return

        # Resolve None values to beginning/end of cache
        if start is None or end is None:
            cached = get_cached_chapters(self.cache_dir)
            if start is None:
                start = min(cached) if cached else 1
            if end is None:
                end = max(cached) if cached else 1

        output = self.query_one("#compile_output", Input).value
        fmt = self.query_one("#compile_format", Select).value

        if not output:
            self.query_one("#compile_status", Label).update(
                "[red]Error: Invalid output name[/red]"
            )
            return

        self.query_one("#compile_btn", Button).disabled = True
        self.query_one("#compile_status", Label).update("Compiling...")

        self.run_worker(
            self.compile_worker(start, end, output, fmt),
            exclusive=True
        )

    async def compile_worker(
        self, start: int, end: int, output: str, fmt: str
    ) -> None:
        """Background worker that calls the orchestrator for compilation."""
        try:
            # Run the blocking orchestrator in a thread pool via asyncio.to_thread
            await asyncio.to_thread(
                run_orchestrator,
                start=start,
                end=end,
                delay=1.0,
                cache_dir=self.cache_dir,
                output=output,
                format=fmt,
                threads=4,
                url=None,
                status_callback=None
            )
            self.query_one("#compile_status", Label).update(
                "[green]Compilation complete![/green]"
            )
        except Exception as e:
            self.query_one("#compile_status", Label).update(
                f"[red]Compilation failed: {str(e)}[/red]"
            )
        finally:
            self.query_one("#compile_btn", Button).disabled = False

    def stop_scraping_job(self) -> None:
        """Cancel the active scraping job."""
        if self.scrape_worker_task:
            self.scrape_cancelled = True
            self.scrape_worker_task.cancel()
            self.log_to_pane("[yellow]Stopping scraper...[/yellow]")
            self.query_one("#thread_status_text", Label).update("Stopping...")

    def start_scraping_job(self) -> None:
        """Initiate the background scraping task."""
        url_val = self.query_one("#scrape_url", Input).value.strip()
        url = url_val if url_val else None
        scope = self.query_one("#scrape_scope", Select).value

        try:
            start_val = self.query_one("#scrape_start", Input).value
            start = parse_field_chapter(start_val)
        except ValueError as e:
            self.query_one("#thread_status_text", Label).update(
                "Error: Invalid Start Chapter"
            )
            self.log_to_pane(f"[red]Cannot start scrape: {str(e)}[/red]")
            return

        try:
            end_val = self.query_one("#scrape_end", Input).value
            end = parse_field_chapter(end_val)
        except ValueError as e:
            self.query_one("#thread_status_text", Label).update(
                "Error: Invalid End Chapter"
            )
            self.log_to_pane(f"[red]Cannot start scrape: {str(e)}[/red]")
            return

        if scope == "beg_to_x":
            start = None
            if end is None:
                self.query_one("#thread_status_text", Label).update(
                    "Error: End chapter required"
                )
                self.log_to_pane(
                    "[red]Cannot start scrape: End Chapter X is required "
                    "for 'Beginning to Chapter X'[/red]"
                )
                return
        elif scope == "x_to_end":
            end = None
            if start is None:
                self.query_one("#thread_status_text", Label).update(
                    "Error: Start chapter required"
                )
                self.log_to_pane(
                    "[red]Cannot start scrape: Start Chapter X is required "
                    "for 'Chapter X to End'[/red]"
                )
                return
        elif scope == "entire":
            start = None
            end = None

        if start is not None and end is not None and start > end:
            self.query_one("#thread_status_text", Label).update(
                "Error: Start > End"
            )
            self.log_to_pane(
                "[red]Cannot start scrape: Start chapter must be "
                "<= End chapter[/red]"
            )
            return

        if not url and (start is None or end is None):
            self.query_one("#thread_status_text", Label).update(
                "Error: URL required"
            )
            self.log_to_pane(
                "[red]Cannot start scrape: A landing page URL is required "
                "when using open-ended ranges or entire novel preset[/red]"
            )
            return

        try:
            threads = int(self.query_one("#scrape_threads", Input).value)
        except ValueError:
            threads = 4
        try:
            delay = float(self.query_one("#scrape_delay", Input).value)
        except ValueError:
            delay = 1.0

        # Disable start button, enable stop button during scrape
        btn = self.query_one("#start_scrape_btn", Button)
        btn.disabled = True
        stop_btn = self.query_one("#stop_scrape_btn", Button)
        stop_btn.disabled = False

        # Reset progress bar
        pbar = self.query_one("#scrape_progress", ProgressBar)
        pbar.progress = 0
        if start is not None and end is not None:
            pbar.update(total=max(1, end - start + 1))

        self.active_threads_status = {}
        self.query_one("#thread_status_text", Label).update("Starting...")
        self.scrape_cancelled = False

        self.scrape_worker_task = self.run_worker(
            self.scrape_worker(start, end, delay, threads, url),
            exclusive=True
        )

    async def scrape_worker(
        self,
        start: Optional[int],
        end: Optional[int],
        delay: float,
        threads: int,
        url: Optional[str],
    ) -> None:
        """Background worker that calls the orchestrator."""
        def status_callback(chapter_num: int, status: str, message: str):
            if self.scrape_cancelled:
                raise RuntimeError("Scrape cancelled by user")
            self.call_from_thread(
                self.handle_scraper_status, chapter_num, status, message
            )

        try:
            # Run the blocking orchestrator in a thread pool via asyncio.to_thread
            await asyncio.to_thread(
                run_orchestrator,
                start=start,
                end=end,
                delay=delay,
                cache_dir="./cache",
                output="novel_tui_download",
                format="none",
                threads=threads,
                url=url,
                status_callback=status_callback
            )
            self.finish_scrape(True)
        except asyncio.CancelledError:
            self.log_to_pane("[yellow]Scraping cancelled by user.[/yellow]")
            self.finish_scrape(False)
        except Exception as e:
            self.log_to_pane(f"[red]Scraping failed: {str(e)}[/red]")
            self.finish_scrape(False)

    def handle_scraper_status(
        self, chapter_num: int, status: str, message: str
    ) -> None:
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
        stop_btn = self.query_one("#stop_scrape_btn", Button)
        stop_btn.disabled = True
        self.scrape_worker_task = None

        # Reset progress bar to stop the ETA timer countdown
        pbar = self.query_one("#scrape_progress", ProgressBar)
        pbar.progress = 0

        if success:
            self.query_one("#thread_status_text", Label).update("Finished!")
            self.log_to_pane(
                "[green]Scraping complete! Chapters cached.[/green]"
            )
        elif self.scrape_cancelled:
            self.query_one("#thread_status_text", Label).update("Cancelled!")
        else:
            failed_chaps = [
                ch
                for ch, stat in self.active_threads_status.items()
                if stat == "error"
            ]
            if failed_chaps:
                err_str = ", ".join(map(str, failed_chaps))
                self.query_one("#thread_status_text", Label).update(
                    f"Failed! Errors in chapters: {err_str}"
                )
            else:
                self.query_one("#thread_status_text", Label).update(
                    "Finished with errors!"
                )
            self.log_to_pane(
                "[red]Scraping failed. See scraper.log for "
                "full details.[/red]"
            )


def run_tui() -> None:
    """Run the interactive TUI application."""
    app = ScraperApp()
    app.run()


def get_cached_chapters(cache_dir: str) -> list[int]:
    """Scan the cache directory and return a sorted list of cached chapter numbers.

    Args:
        cache_dir: The path to the cache directory.

    Returns:
        A sorted list of chapter numbers (integers).
    """
    chapters = []
    pattern = re.compile(r"^chapter_(\d+)\.html$")
    path = Path(cache_dir)
    if path.exists():
        for item in path.iterdir():
            if item.is_file():
                match = pattern.match(item.name)
                if match:
                    chapters.append(int(match.group(1)))
    return sorted(chapters)


def calculate_gaps(cached_chapters: list[int]) -> list[tuple[int, int]]:
    """Identify missing chapter ranges in a sorted list of chapter numbers.

    Args:
        cached_chapters: A sorted list of chapter numbers.

    Returns:
        A list of tuples (start, end) representing missing ranges.
    """
    if not cached_chapters:
        return []

    gaps = []
    # Find gaps between the first and last chapters
    for i in range(len(cached_chapters) - 1):
        curr = cached_chapters[i]
        nxt = cached_chapters[i + 1]
        if nxt > curr + 1:
            gaps.append((curr + 1, nxt - 1))

    return gaps


def parse_field_chapter(val: str) -> Optional[int]:
    """Parse a chapter field string into an integer or None if blank/boundary.

    Args:
        val: The raw input string value.

    Returns:
        The integer chapter number, or None if blank, "Beginning", or "End of
        Novel".

    Raises:
        ValueError: If the string is non-blank and cannot be parsed as an
            integer.
    """
    s = val.strip()
    if not s or s in ("Beginning", "End of Novel"):
        return None
    try:
        val_int = int(s)
        if val_int < 1:
            raise ValueError(f"Chapter number must be >= 1: {s}")
        return val_int
    except ValueError as e:
        if "must be >= 1" in str(e):
            raise
        raise ValueError(f"Invalid chapter number: {s}")
