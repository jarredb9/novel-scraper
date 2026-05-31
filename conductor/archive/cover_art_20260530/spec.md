# Specification: Cover Art Downloader, Embedder, and EPUB Updating

## Overview
Add support for automatically downloading or specifying a cover art image and embedding it inside compiled EPUB and PDF files. Additionally, support reading and extracting chapters from an existing EPUB to allow adding/updating the cover image (and merging new chapters) without needing cached HTML files or redownloading.

## Functional Requirements
1. **CLI Arguments**:
   - `--cover`: Optional path or URL to the cover image. Default is `None` (automatic detection/scraping).
   - `--update-epub` (alias `--merge-epub`): Path to an existing EPUB file to update.

2. **Cover Image Resolver & Caching**:
   - If `--cover` is a URL, download it; if a file path, copy/use it.
   - If `--cover` is not provided, derive the landing page URL from the scraper's `base_url` (e.g. replace `/chapter-` with `.html`), fetch the landing page, and parse the cover image source URL using XPath:
     `//div[@class="m-imgtxt"]/div[@class="pic"]/img/@src`
   - Cache the cover image as `cache/cover.jpg` to avoid redownloading.
   - Soft Fallback: If cover image resolution/download fails, log a warning to `scraper.log` and continue compiling without a cover.

3. **Existing EPUB Chapter Extraction**:
   - If `--update-epub` is specified, read the existing EPUB file (using `ebooklib.epub.read_epub`).
   - Extract the chapter title and paragraph text from each `EpubHtml` chapter (typically starting with `chap_`).
   - Merge these extracted chapters with any newly requested chapters (downloading only the new ones if necessary).

4. **EPUB Cover Embedding**:
   - Set the image as the native EPUB cover using `ebooklib.epub.EpubBook.set_cover`.
   - Create a dedicated cover XHTML page containing the cover image (centered, scaled) as the first page of the book spine.

5. **PDF Cover Embedding**:
   - Create a dedicated cover page at the beginning of the PDF (before the Table of Contents).
   - The cover page should display the cover image centered, followed by the novel's title and metadata.

## Non-Functional Requirements
- **Dependencies**: Use existing libraries (`requests`, `reportlab`, `ebooklib`, `lxml`).
- **Coverage**: Ensure unit tests for the cover art downloader, resolver, and embedding/updating logic maintain >80% test coverage.

## Acceptance Criteria
- Run compilation with `--cover https://example.com/custom.jpg` embeds that custom cover image in both outputs.
- Run compilation with `--update-epub novel.epub --cover cover.jpg` updates the existing EPUB with the new cover image without redownloading.
- Run compilation without `--cover` automatically scrapes the cover image from freewebnovel.com and embeds it.
- Failed download/resolution of the cover logs a warning and proceeds compilation without failure.
