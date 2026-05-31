# Specification: Auto-Download & Auto-Update

## 1. Overview
This track introduces two enhancements to the `novel-scraper` utility:
1. **Auto-Range Downloader**: Simplifies initial downloading of novels by automatically fetching all chapters present on the landing page if `--url` is provided but `--start` and/or `--end` are omitted.
2. **Auto-Update Mechanism**: Periodically new chapters are uploaded to the source site. A simple update command `--update <path>` detects if new chapters are available on the web and automatically scrapes them, parses them, and compiles them alongside existing chapters into a new or updated PDF/EPUB.

## 2. Functional Requirements
### 2.1 Auto-Range Detection (Download All Chapters)
- If `--url <landing_page_url>` is provided, and `--start` and/or `--end` are omitted (defaulting to `None`), the orchestrator shall:
  1. Retrieve and parse the landing page to auto-detect all available chapter links.
  2. Set `--start` to the minimum chapter number found and `--end` to the maximum chapter number found.
- If `--url` is NOT provided, and `--start` and/or `--end` are omitted, default behavior falls back to scraping chapters `776` to `1780`.

### 2.2 Metadata-Driven Novel Source URL Caching
- When compiling an EPUB, the EPUB compiler shall write the novel's landing page URL (if available) to the `DC:source` metadata field of the EPUB file using `ebooklib`.
- When compiling a PDF, the PDF compiler shall write the novel's landing page URL (if available) to the document Subject metadata field using ReportLab.
- Provide helper utility functions to read this metadata back:
  - From EPUB: Read `DC:source` using `ebooklib`.
  - From PDF: Read document metadata using `pypdf`.

### 2.3 Auto-Update CLI and Orchestration
- Introduce a new CLI parameter `--update <path>` (e.g., `--update novel.epub` or `--update novel.pdf`).
- When `--update <path>` is executed:
  1. Determine the landing page URL:
     - Check if `--url` is explicitly provided.
     - If not, try to extract the landing page URL from the metadata of the file at `<path>`.
     - If no URL is found, abort with a user-friendly error message.
  2. Detect the existing chapters already compiled in the target file at `<path>` (using the existing PDF outline parser or EPUB extractor).
  3. Fetch the landing page URL and extract all available chapters.
  4. Compare the landing page chapter list with the existing compiled chapters to find any new/missing chapters.
  5. If there are no new chapters, notify the user and exit.
  6. Otherwise, scrape, parse, and sanitize only the new/missing chapters.
  7. Combine the previously compiled chapters (either from cache or by reading them from the EPUB/PDF) and the new chapters.
  8. Compile and overwrite the file at `<path>` with the complete, updated set of chapters.

## 3. Non-Functional Requirements
- **Robust Error Handling**: If metadata is corrupted or missing, print a clear message asking the user to provide the `--url` argument manually.
- **Efficiency**: Only fetch missing chapters from the web, respecting rate limits. Do not fetch already cached chapters unless forced.
- **Strict Adherence to Guidelines**: Ensure all public APIs have type hints and complete Google-style docstrings.

## 4. Acceptance Criteria
- Running `python main.py --url https://freewebnovel.com/the-first-legendary-beast-master.html --format epub --output mynovel.epub` (without `--start` or `--end`) downloads all chapters automatically.
- Running `python main.py --update mynovel.epub` (without `--url`) reads the source URL from `mynovel.epub`'s metadata, fetches the site, detects new chapters, scrapes them, and updates `mynovel.epub`.
- Running `python main.py --update mynovel.pdf` works similarly, reading the source URL from PDF metadata.
- Unit/integration tests cover all metadata reading/writing, range auto-detection, and update logic, maintaining test coverage >80%.
