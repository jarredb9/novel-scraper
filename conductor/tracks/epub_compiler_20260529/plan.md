# Implementation Plan - EPUB Compiler

This plan outlines the steps required to implement the EPUB compiler feature, allowing compilation of scraped web novels to `.epub` format alongside or instead of PDF format.

## Phase 1: Environment Setup & Core EPUB Compilation Engine [checkpoint: 2e2c8d4]

- [x] Task: Update Tech Stack and Requirements (5141c65)
    - [x] Add `ebooklib` to `requirements.txt`
    - [x] Update `conductor/tech-stack.md` to reflect the new dependency and compile target

- [x] Task: Write failing tests for EPUBCompiler (dd1b566)
    - [x] Create `tests/test_epub_compiler.py`
    - [x] Implement unit tests validating that the `EPUBCompiler` class initializes with an output path, formats chapters sequentially, handles metadata, embeds styles, and writes out a valid EPUB file
    - [x] Confirm tests fail as expected (Red phase)

- [x] Task: Implement EPUBCompiler (5eb21a4)
    - [x] Create `src/epub_compiler.py`
    - [x] Implement the `EPUBCompiler` class using `ebooklib.epub`
    - [x] Implement chapter creation, metadata injection, TOC generation, and custom CSS stylesheet styling
    - [x] Ensure all unit tests pass (Green phase)
    - [x] Verify test coverage is >80% for `src/epub_compiler.py`

- [x] Task: Conductor - User Manual Verification 'Phase 1: Environment Setup & Core EPUB Compilation Engine' (Protocol in workflow.md) (2e2c8d4)

## Phase 2: CLI Integration and Orchestrator Update

- [x] Task: Write failing tests for CLI & Orchestrator with format flag (d2d49b6)
    - [x] Update `tests/test_cli.py` to assert new `--format` parameter behavior, default value, and validation
    - [x] Update `tests/test_orchestrator.py` or create a new test case to test orchestration compiling both PDF and EPUB, just PDF, or just EPUB
    - [x] Confirm tests fail as expected (Red phase)

- [ ] Task: Update CLI Parser
    - [ ] Update `src/cli.py` to add `--format` parameter with choices `['pdf', 'epub', 'both']` and default `both`
    - [ ] Run tests to ensure CLI parser tests pass

- [ ] Task: Update Orchestrator
    - [ ] Update `src/orchestrator.py` to check the format option
    - [ ] When format is `pdf` or `both`, run the `PDFCompiler`
    - [ ] When format is `epub` or `both`, run the `EPUBCompiler`
    - [ ] Ensure proper output file paths are derived (e.g. replacing/appending suffix)
    - [ ] Run tests to verify all orchestrator, CLI, and compiler tests pass (Green phase)
    - [ ] Verify overall test coverage is >80% for new code

- [ ] Task: Conductor - User Manual Verification 'Phase 2: CLI Integration and Orchestrator Update' (Protocol in workflow.md)

## Phase: Review Fixes
- [x] Task: Apply review suggestions (8ec7e85)
