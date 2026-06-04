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

## Phase 2: Core TUI Layout and Navigation [checkpoint: f518435]

- [x] Task: Design Base Textual App and Screens (687067c)
  - [x] Write tests in `tests/test_tui_layout.py` that mock the Textual App and verify structure/tabs
  - [x] Implement `src/tui.py` with standard textual application tabs (Dashboard, Cache, Compile)
  - [x] Run test suite and confirm tests pass
- [x] Task: Conductor - User Manual Verification 'Phase 2: Core TUI Layout and Navigation' (Protocol in workflow.md) (f518435)

## Phase 3: Active Scrape Dashboard & Live Logging [checkpoint: e4412cb]

- [x] Task: Scraping Progress & Thread Dashboard (a4a3c10)
  - [x] Write tests for thread status updating and log event formatting
  - [x] Implement thread activity display in TUI and progress indicators linked to downloader
  - [x] Run test suite and confirm tests pass
- [x] Task: Live Log Pane (c6a96e8)
  - [x] Write tests for TUI log handler
  - [x] Implement custom Log Handler sending scraper/orchestrator log logs directly to Textual's Rich Log widget
  - [x] Run test suite and confirm tests pass
- [x] Task: Conductor - User Manual Verification 'Phase 3: Active Scrape Dashboard & Live Logging' (Protocol in workflow.md) (e4412cb)

## Phase 4: Cache Browser & Compiler Launcher

- [x] Task: Cache Browser Screen (56f51b8)
  - [x] Write tests for cache checking and range gap calculation functions used by TUI
  - [x] Implement list view of cached chapters and logic to detect gap ranges in `./cache`
  - [x] Run test suite and confirm tests pass
- [x] Task: Compiler Interactive Interface (3f9c96f)
  - [x] Write tests verifying compiler triggering logic and output handling
  - [x] Implement inputs (start, end, formats, output path) and trigger orchestrated compile
  - [x] Run test suite and confirm tests pass
- [x] Task: Extra Features and TUI UX Improvements (Post-Feedback)
  - [x] Fix thread status finished warning message on download failure
  - [x] Add Stop button to abort ongoing scrapes mid-action with worker cancellation cleanup
  - [x] Implement Scope Preset dropdown to dynamically disable and auto-populate start/end inputs
  - [x] Decouple compilation from scrape dashboard tab to resolve compiler tab redundancy
  - [x] Bind Escape key to unfocus active text inputs, enabling global 'q' hotkey exits
- [~] Task: Conductor - User Manual Verification 'Phase 4: Cache Browser & Compiler Launcher' (Protocol in workflow.md)
- [ ] Task: Update project documentation
  - [ ] Update README.md
  - [ ] Update AGENTS.md
