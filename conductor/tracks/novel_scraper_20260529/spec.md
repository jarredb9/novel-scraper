# Specification - Build Core Novel Scraper and PDF Compiler

## Overview
Build a modular, command-line Python application that scrapes a specified range of chapters (776 to 1780) of a web novel from freewebnovel.com, parses the contents using XPaths, and compiles them into a single, ereader-optimized PDF file with a clickable Table of Contents (TOC).

## Requirements

### 1. Scraping & Local Caching
- **Endpoint**: Scraping URLs in the format `https://freewebnovel.com/novel/the-first-legendary-beast-X` (where X is 776 to 1780).
- **Polite Scraping**: Wait 1.0 seconds between network requests. Send standard `User-Agent` headers.
- **Caching**: Prior to fetching a chapter URL, check if a cached HTML file exists in a local cache directory (e.g., `./cache/chapter_X.html`). If it exists, read it locally. If not, download the HTML and save it to the cache directory. This ensures the script is resume-friendly.

### 2. Parsing
- **Engine**: Use the `lxml` parser.
- **XPath Selectors**:
  - **Chapter Title & Number**: `/html/body/div[3]/div[1]/div/div[1]/span`
  - **Chapter Body/Article Text**: `/html/body/div[3]/div[1]/div/div[5]/div[1]`
- **Sanitization**: Clean HTML tags and excessive whitespace from the body text, transforming it into plain paragraphs suitable for PDF generation.

### 3. PDF Generation (ReportLab)
- **Document Layout**: Ereader-optimized with 0.5-inch margins.
- **Table of Contents**:
  - A clickable TOC page at the beginning of the PDF.
  - Clicking any TOC chapter item navigates the viewer to the first page of that chapter.
  - Generate PDF bookmarks (outline panel) corresponding to each chapter.
- **Chapter Formatting**:
  - Each chapter starts on a new page.
  - Chapter titles are styled as large bold headings.
  - Body text uses 1.5 line spacing (or equivalent leading) for comfortable viewing.
  - Center page numbers in the footer of each page (starting after the TOC page).

### 4. CLI & Logging
- **Command Line Arguments**: Supports optional flags for `--start`, `--end`, `--delay`, and `--output`.
- **User Interface**: Render a CLI progress bar (using `tqdm`) tracking scraping and parsing progress.
- **Logging**: Write verbose events, HTTP statuses, and errors to `scraper.log`. Do not dump tracebacks or request messages to standard output.

## Acceptance Criteria
- [ ] A self-contained Python script or modular application can be executed from the CLI.
- [ ] Successfully downloads and caches chapters 776 to 1780 locally.
- [ ] Successfully parses chapter content using the designated XPaths.
- [ ] Generates a single output PDF that starts with a clickable Table of Contents and has correct page routing.
- [ ] The generated PDF has 0.5-inch margins, ereader-friendly font sizes, and centered footer page numbers.
- [ ] Unit tests cover at least 80% of scraping, parsing, caching, and PDF generation code.
