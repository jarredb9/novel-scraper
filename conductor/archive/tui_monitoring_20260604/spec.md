# Specification - Interactive TUI & Monitoring Dashboard

## Overview
This track introduces an interactive Terminal User Interface (TUI) to `novel-scraper` using the `textual` framework. Users can launch the TUI to monitor active downloads in real-time, view local cached chapters, manage cache files, and compile novel chapters to PDF/EPUB interactively.

## Functional Requirements
1. **CLI Flag Integration**:
   - Introduce a new command-line argument `--tui` (and shorthand `-i`) in [src/cli.py](file:///C:/Users/jarre/OneDrive/Documents/Code/novel-scraper/src/cli.py) and handle it in [main.py](file:///C:/Users/jarre/OneDrive/Documents/Code/novel-scraper/main.py).
   - Triggering `--tui` bypasses standard command-line argument parsing requirements (e.g., start/end chapters, output files) and launches the interactive interface directly.

2. **Dashboard Application Structure (`src/tui.py`)**:
   - Built using the `textual` library with a clean, grid/flex-based tabbed interface containing three main tabs:
     - **Scrape Dashboard**: Start a new scraping job with configurable threads/delays. Shows progress bars, thread status (active, sleeping, error), and a live log pane displaying warnings/exceptions.
     - **Cache Browser**: Scan the `./cache` folder, displaying summary stats (total chapters cached, missing gaps in the chapter range). Provide options to inspect cached titles and delete/clean cache files.
     - **Interactive Compiler**: Select chapter ranges and formats (EPUB, PDF, both), specify the output filename, and launch the compiler. Show compilation progress and a success/failure notification.

3. **Multi-threading and Logging integration**:
   - Scraper threads should report progress and status updates to the TUI event loop safely without blocking.
   - Redirect standard scraping logs (or use a custom log handler) to feed the live TUI log window widget.

## Non-Functional Requirements
- **Responsive Layout**: Design must adapt gracefully to different terminal sizes.
- **Robustness**: The TUI must catch and report network exceptions, rate-limit warnings (429), and parsing errors without crashing.
- **Dependencies**: Add `textual>=0.50.0` to the project's dependencies (`requirements.txt`).

## Acceptance Criteria
1. Running `python main.py --tui` successfully launches the textual console UI.
2. The user can navigate between "Scrape", "Cache", and "Compile" tabs.
3. Starting a scrape from the TUI correctly starts scraper threads and displays visual progress.
4. The cache screen correctly displays the files in `./cache` and summarizes completed ranges.
5. The compiler tab correctly generates `.pdf` and `.epub` files of chosen ranges.
6. The test suite includes unit tests for CLI argument routing and mocks for key TUI components.

## Out of Scope
- Support for multiple concurrent scrape jobs of different novels.
- A mouse-only or non-terminal interface.
