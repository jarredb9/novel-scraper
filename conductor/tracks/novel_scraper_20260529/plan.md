# Implementation Plan - Build Core Novel Scraper and PDF Compiler

This plan outlines the task breakdown following a strict Test-Driven Development (TDD) cycle and Conductor verification protocols.

## Phase 1: Project Setup and Scraper & Cache Implementation [checkpoint: d6e5ea4]
- [x] Task: Environment Setup and Caching Module (9f21ab2)
    - [x] Write unit tests for local caching (checking if directory exists, saving HTML files, reading cache hits, and handling cache misses).
    - [x] Create Python project structure, dependency manifest `requirements.txt`, and implement the caching manager class.
- [x] Task: Scraping Engine with Rate-Limiting (7e43409)
    - [x] Write unit tests for the scraper helper (verifying HTTP requests, custom headers, timeout handling, retries, and sleep delays).
    - [x] Implement the scraper utility to fetch URLs (`https://freewebnovel.com/novel/the-first-legendary-beast-X`) and store them in the cache folder.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Project Setup and Scraper & Cache Implementation' (Protocol in workflow.md) (d6e5ea4)

## Phase 2: HTML Parser Module [checkpoint: 58620c5]
- [x] Task: XPath Parser (c589520)
    - [x] Write unit tests verifying XPath parsing accuracy (checking successful extraction of title and body text using the specified XPaths, and handling empty/missing elements).
    - [x] Implement the XPath parser module using the `lxml` library.
- [x] Task: Content Sanitizer (233df08)
    - [x] Write unit tests for text sanitization (verifying removal of ads, HTML tags, excess whitespace, and paragraph formatting).
    - [x] Implement the sanitizer module to clean raw parsed HTML text into readable plain text paragraphs.
- [x] Task: Conductor - User Manual Verification 'Phase 2: HTML Parser Module' (Protocol in workflow.md) (58620c5)

## Phase 3: PDF Generation & Navigation Module
- [ ] Task: Basic PDF Layout and Chapter Flow
    - [ ] Write unit tests for the PDF document structure (checking page layout, margins, page-number footer format, and chapter page-breaks).
    - [ ] Implement basic PDF generation with ReportLab, applying the ereader margin styles (0.5 in) and page flow.
- [ ] Task: Clickable TOC and Sidebar Bookmarks
    - [ ] Write unit tests for Table of Contents layout (verifying anchor target generation and hyperlink routing within the PDF document).
    - [ ] Implement clickable Table of Contents (TOC) page and outline bookmark generation in the final PDF.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: PDF Generation & Navigation Module' (Protocol in workflow.md)

## Phase 4: CLI and Main Orchestrator
- [ ] Task: CLI Configuration
    - [ ] Write unit tests for CLI argument parser (checking default values and custom inputs for range, delay, cache directory, and output filename).
    - [ ] Implement the command-line interface argument parser.
- [ ] Task: Progress Tracker and Main Orchestrator
    - [ ] Write unit tests for the main orchestration flow (verifying flow of download -> cache -> parse -> compile -> log).
    - [ ] Implement orchestrator combining caching, scraping, parsing, PDF generation, progress bar (tqdm), and file logging.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: CLI and Main Orchestrator' (Protocol in workflow.md)
