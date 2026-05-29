# Product Guidelines - Novel Scraper & PDF Compiler

This document details the user experience (UX), formatting, and coding guidelines for the Novel Scraper project.

## PDF Layout & Typography Guidelines
To provide an optimized reading experience on mobile ereader screens:
- **Margins**: Narrow margins (0.5 inches / 36 points) on all sides to maximize the text display area on smaller screens.
- **Typography**: Ereader-optimized styling:
  - Font Size: 11pt or 12pt for the body text.
  - Line Spacing: 1.5 line spacing (or equivalent leading, e.g., 16-18pt leading) to ensure highly readable text.
  - Headings: Bold, clear, and distinct serif headings for Chapter Titles, sized at 18pt or 20pt.
- **Page Breaks**: Every chapter MUST start on a new page.
- **Page Numbers**: Placed at the bottom-center of every page, starting after the Table of Contents.

## CLI & Output UX Guidelines
- **Console Output**:
  - The script must display a visual progress bar (using `tqdm`) tracking the scraping progress (e.g., "Scraping: 75% [750/1005] [1.2s/it]").
  - Console prints should be kept clean. Avoid cluttered prints for every page request.
- **Logging**:
  - Save verbose network, parse, and generation details to a log file (`scraper.log`).
  - Capture HTTP status codes, redirection, failed elements, and cache hits.
- **Resumption & Caching**:
  - Store fetched HTML chapters in a local directory (e.g., `./cache/`).
  - If a chapter's HTML already exists in `./cache/`, skip fetching and parse it from the local cache.

## Python Coding Guidelines
- **Formatting**: Adhere to clean PEP 8 Python coding standards.
- **Scraper Politeness**:
  - Never flood the server; enforce a minimum 1-second delay between requests.
  - Use custom headers (mimicking a standard web browser).
