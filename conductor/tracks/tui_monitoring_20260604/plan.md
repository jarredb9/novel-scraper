# Implementation Plan - Interactive TUI & Monitoring Dashboard

## Phase 1: Environment Setup & CLI Integration [checkpoint: 2f759cd]

- [x] Task: Setup Dependencies and Requirements (129dae1)
    - [x] Add `textual>=0.50.0` to `requirements.txt`
    - [x] Install dependency in the virtual environment
- [x] Task: Integrate `--tui` / `-i` CLI Flags (df12029)
    - [x] Write failing test in `tests/test_cli.py` for routing `--tui` and bypassing default required args
    - [x] Implement CLI flag parsing in `src/cli.py` and action routing in `main.py`
    - [x] Verify test passes
- [x] Task: Conductor - User Manual Verification 'Phase 1: Environment Setup & CLI Integration' (Protocol in workflow.md) (2f759cd)

## Phase 2: Core TUI Layout and Navigation

- [ ] Task: Design Base Textual App and Screens
    - [ ] Write tests in `tests/test_tui_layout.py` that mock the Textual App and verify structure/tabs
    - [ ] Implement `src/tui.py` with standard textual application tabs (Dashboard, Cache, Compile)
    - [ ] Run test suite and confirm tests pass
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Core TUI Layout and Navigation' (Protocol in workflow.md)

## Phase 3: Active Scrape Dashboard & Live Logging

- [ ] Task: Scraping Progress & Thread Dashboard
    - [ ] Write tests for thread status updating and log event formatting
    - [ ] Implement thread activity display in TUI and progress indicators linked to downloader
    - [ ] Run test suite and confirm tests pass
- [ ] Task: Live Log Pane
    - [ ] Write tests for TUI log handler
    - [ ] Implement custom Log Handler sending scraper/orchestrator log logs directly to Textual's Rich Log widget
    - [ ] Run test suite and confirm tests pass
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Active Scrape Dashboard & Live Logging' (Protocol in workflow.md)

## Phase 4: Cache Browser & Compiler Launcher

- [ ] Task: Cache Browser Screen
    - [ ] Write tests for cache checking and range gap calculation functions used by TUI
    - [ ] Implement list view of cached chapters and logic to detect gap ranges in `./cache`
    - [ ] Run test suite and confirm tests pass
- [ ] Task: Compiler Interactive Interface
    - [ ] Write tests verifying compiler triggering logic and output handling
    - [ ] Implement inputs (start, end, formats, output path) and trigger orchestrated compile
    - [ ] Run test suite and confirm tests pass
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Cache Browser & Compiler Launcher' (Protocol in workflow.md)
