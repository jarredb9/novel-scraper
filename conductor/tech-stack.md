# Technology Stack - Novel Scraper & PDF Compiler

This document specifies the chosen technology stack, development environments, and dependencies for the project.

## Core Language & Runtime
- **Language**: Python 3.11+
- **Rationale**: Python is standard for web scraping and data compiling, with mature packages for HTML parsing and PDF generation.

## Dependencies & Libraries
### Scraping & Parsing
- **`requests`**: Synchronous HTTP library for fetching web pages.
- **`lxml`**: High-performance XML/HTML parser that natively supports XPath querying.
  - Used for parsing `/html/body/div[3]/div[1]/div/div[1]/span` and `/html/body/div[3]/div[1]/div/div[5]/div[1]`.

### PDF Compilation
- **`reportlab`**: Programmatic PDF layout generation.
  - Utilized for building flowing text documents, embedding page numbers, and generating clickable anchors (for the Table of Contents and PDF bookmarks sidebar).

### Developer UX & Tooling
- **`tqdm`**: Command-line visual progress bar framework.
- **`pytest`**: Python testing framework to write tests for HTML fetching, parsing selectors, and cache directories.

## Project Structure & Tooling
- **Virtual Environment**: Python `venv` virtual environment.
- **Package Management**: Standard `pip` with `requirements.txt`.
