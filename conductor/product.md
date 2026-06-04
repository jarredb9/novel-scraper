# Initial Concept

A Python script that scrapes novel chapters from a website (specifically freewebnovel.com) and compiles them into a single PDF document containing a clickable Table of Contents (TOC) / Appendix.

---

# Product Definition - Novel Scraper & PDF/EPUB Compiler

## Overview
A robust Python utility to scrape chapters of a novel (specifically "The First Legendary Beast") from freewebnovel.com and compile them into beautifully formatted ebook-style PDF and/or EPUB documents, with support for multi-threaded/concurrent scraping, cover art caching/embedding, and existing EPUB updating.

## Product Vision
For readers who want to enjoy web novels offline on their ereaders or PDF viewers without being interrupted by internet connectivity issues or site popups.

## Key Features (Functional Requirements)
1. **Polite, Incremental Scraper**:
   - Sequential or concurrent scraper iterating through chapters 776 to 1780.
   - Built-in delays (configurable, default 1.0s) and User-Agent headers to prevent IP blocking.
   - Incremental local caching: Downloads and stores HTML content locally first. If the process is interrupted, it can resume without redownloading.
2. **Robust HTML Parser**:
   - Uses `lxml` to query the specific XPaths:
     - Chapter Title/Number: `/html/body/div[3]/div[1]/div/div[1]/span`
     - Article Text Content: `/html/body/div[3]/div[1]/div/div[5]/div[1]`
   - Falls back to heuristic parsing (e.g., header tags, class names, and p-tag density) if the configured/default XPaths fail.
   - Sanitizes text content, stripping unnecessary scripts, styles, wrapper HTML tags, performing automatic punctuation normalization (converting curly quotes to straight ones, consecutive dashes to em-dashes, and multiple dots to ellipses), filtering empty or symbol-only paragraphs, and using fuzzy matching to remove website branding phrases (such as freewebnovel promotion notices) embedded in paragraphs or at the end of sentences.
3. **Ebook-Style PDF Compiler**:
   - Generates a PDF file `the_first_legendary_beast_chapters_776_1780.pdf`.
   - Starts with a clickable Table of Contents (TOC) page mapping every chapter directly to its starting page in the document.
   - Embeds sidebar PDF bookmarks (document outline) for easy reader navigation.
   - Styles pages with a book/novel theme: standard margins, custom fonts, page numbers, and page breaks between chapters.
   - Supports sorting chapters sequentially by chapter number regardless of compilation load order.
4. **Ebook-Style EPUB Compiler**:
   - Generates a standard `.epub` file using `ebooklib`.
   - Includes navigation metadata, a Table of Contents (TOC), book spine, and styled pages using an embedded stylesheet.
5. **Command Line Interface (CLI)**:
   - Configurable CLI parameters for start/end chapters, rate limiting, concurrent scraping threads using `--threads` / `-t` (default: 4), output path, updating/merging existing EPUB or PDF files using `--update <path>`, cover art using `--cover`, compiling to specific formats using `--format` (choices: `pdf`, `epub`, or `both`), landing page URL for chapter link auto-detection using `--url`, custom ad/branding filtering patterns using `--ad-pattern`, and launching the interactive TUI using `--tui`/`-i`.
6. **Cover Art & EPUB Updating**:
   - Automatically scraping the cover image from the landing page using XPath, downloading from a URL, or using a local path.
   - Caching the cover image locally as `cache/cover.jpg` to avoid redundant network requests.
   - Embedding the cover page at the beginning of compiled PDFs and as a native cover page in EPUBs.
   - Reading/extracting chapters from an existing EPUB to allow merging new chapters without redownloading.
   - Preserving the landing page URL in EPUB `DC:source` and PDF `Subject` metadata to support subsequent auto-updates.
7. **Interactive TUI Dashboard**:
   - A visual terminal user interface utilizing the `textual` framework. Includes a Scrape Dashboard tab with download configurations, live logging, and thread state tracking, a Cache Browser tab showing range gap summaries, and an Interactive Compiler tab for selecting ranges/formats and triggering compilation.

## Non-Functional Requirements
- **Performance**: Graceful recovery on socket timeouts or 404 errors.
- **Dependencies**: Restrict to standard Python library and lightweight packages: `requests`, `lxml`, `reportlab`, and `tqdm`.
- **Maintainability**: Clear separation between scraper, parser, and PDF generator components.

## Out of Scope
- A graphical user interface (GUI) or mobile app.
- Scraping sites other than freewebnovel.com (though selectors are configurable).
