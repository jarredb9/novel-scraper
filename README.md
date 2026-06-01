# Web Novel Scraper & PDF Compiler

A modular Python command-line application that scrapes a specified range of chapters from a web novel on [freewebnovel.com](https://freewebnovel.com/), parses and cleans the content, and compiles them into a single, e-reader-optimized PDF file complete with a clickable Table of Contents (TOC) and PDF bookmark outlines.

---

## Key Features

- **Chapter Link Auto-Detection**: Accepts a novel's landing page URL via `--url`, parses it dynamically, and maps chapter numbers to URLs, avoiding the need to construct sequential URLs manually.
- **Heuristic Content Parsing Fallback**: Dynamically extracts chapter titles and main body content (using tags like `<h1>`, `<h2>`, CSS classes, and `p`-tag density) if the default XPath selectors fail to locate them.
- **Polite & Rate-Limited Concurrent Scraping**: Employs browser headers and enforces a default 1-second delay between requests. Thread-safe lock guarantees rate limits are respected across concurrent requests. Automatically detects HTTP 429 rate-limiting status codes and backs off exponentially. Supports multi-threaded fetching via ThreadPoolExecutor.
- **Resume-Friendly Caching**: Automatically saves fetched chapter HTML files locally. If execution is interrupted, the system skips already-cached chapters and resumes where it left off.
- **HTML Parsing & Sanitization**: Uses `lxml` to query specific elements via XPaths. Cleans raw HTML text, strips advertising/boilerplate code, and formats text into readable paragraphs. Employs a dependable fuzzy matching-based cleanup system (using standard library `difflib`) to identify and remove website branding statements from paragraphs.
- **E-Reader Optimized PDF & EPUB Compilation**:
  - **PDF Layout**: Narrow margins (0.5 inches / 36 points) to maximize text area, Times-Bold titles, Times-Roman 11pt body text with 1.5 line spacing (16.5pt leading), clickable Table of Contents, and document outline sidebar bookmarks. Includes a dedicated front cover page if a cover image is provided.
  - **EPUB Layout**: Generates standardized EPUB packages containing structured XHTML chapters, a Table of Contents, custom CSS stylesheets, and embedded cover art metadata/pages.
- **Incremental PDF & EPUB Updating & Merging**:
  - **PDF**: Scans bookmarks/outlines from an existing PDF (using `pypdf`), extracts existing chapter numbers, automatically determines which target chapters are missing, downloads/caches them, and compiles the entire combined set in correct sequential numerical order.
  - **EPUB**: Extracts chapters directly from an existing EPUB (using `ebooklib`), merging them with newly requested chapters without needing HTML cache files or redownloading.
- **Cover Art Caching & Embedding**: Auto-scrapes the novel's cover from the landing page using XPath, downloads from a URL, or accepts a local path, caching it as `cache/cover.jpg` to avoid redundant requests.
- **CLI Configuration**: Fully configurable execution using arguments for start chapter, end chapter, delay, cache directory, output filename, compilation format, existing PDF/EPUB merging, cover art, concurrent threads, and landing page URL.
- **Verbose Logging**: Detailed network events, HTTP statuses, and errors are written directly to `scraper.log` to keep standard console output clean.
- **Interactive UI**: CLI progress tracking is animated using `tqdm`.

---

## Project Structure

```
├── conductor/               # Conductor environment and style guides
├── src/                     # Core application source modules
│   ├── __init__.py
│   ├── cache.py             # CachingManager for storing/retrieving HTML chapters
│   ├── cli.py               # Argument parser for CLI flags
│   ├── epub_compiler.py     # ebooklib EPUB compilation engine
│   ├── orchestrator.py      # Unified workflow runner
│   ├── parser.py            # XPathParser module using lxml
│   ├── pdf_compiler.py      # ReportLab PDF compiler and canvas manager
│   ├── pdf_reader.py        # PDF outline and bookmark parser
│   ├── sanitizer.py         # ContentSanitizer for raw text extraction
│   └── scraper.py           # HTTP Scraping engine with rate limiting
├── tests/                   # Python unit tests matching the src modules
├── main.py                  # Entry point script
├── requirements.txt         # Project package dependencies
└── README.md                # Project documentation
```

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository_url>
   cd novel-scraper
   ```

2. **Set up a Virtual Environment** (Recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

Run the orchestrator using the entry point script `main.py`:

```bash
python3 main.py
```

### CLI Arguments

Customize the scrape range, politeness delay, and output file path using the command-line flags below:

| Flag | Type | Default | Description |
|---|---|---|---|
| `--start` | `int` | `None` | Chapter number to start scraping from. Falls back to 776 if no url/update specified. |
| `--end` | `int` | `None` | Chapter number to end scraping at. Falls back to 1780 if no url/update specified. |
| `--delay` | `float` | `1.0` | Delay in seconds between successive requests. |
| `--cache-dir` | `str` | `./cache` | Local folder directory to store chapter cache. |
| `--output` | `str` | `novel.pdf` | Filename of the compiled output. |
| `--update` | `str` | `None` | Path to an existing compiled PDF/EPUB to update with new chapters automatically. |
| `--cover` | `str` | `None` | Optional path or URL to the cover image. Defaults to scraping from landing page. |
| `--format` | `str` | `both` | Output format choices: `pdf`, `epub`, or `both` (default: `both`). |
| `--threads` / `-t` | `int` | `4` | Number of concurrent scraper threads. |
| `--url` | `str` | `None` | Landing page URL for chapter link auto-detection. |

### Example

To scrape chapters 800 through 850 with a 2-second rate-limiting delay and compile them into a file called `fantasy_novel.pdf`:

```bash
python3 main.py --start 800 --end 850 --delay 2.0 --output fantasy_novel.pdf
```

To auto-detect all chapters on the landing page and compile them as an EPUB:

```bash
python3 main.py --url https://freewebnovel.com/the-first-legendary-beast-master.html --output mynovel.epub --format epub
```

To auto-update an existing EPUB with newly released chapters using metadata-driven source URL detection:

```bash
python3 main.py --update mynovel.epub
```

To update/merge an existing `fantasy_novel.pdf` by fetching chapters 851 through 860 manually and appending them sequentially:

```bash
python3 main.py --update fantasy_novel.pdf --start 851 --end 860
```

To compile chapters 800 through 850 as an EPUB book only:

```bash
python3 main.py --start 800 --end 850 --output fantasy_novel.epub --format epub
```

To compile with a custom cover image URL or local path:

```bash
python3 main.py --start 800 --end 850 --output fantasy_novel.pdf --cover https://example.com/cover.jpg
```

To update/merge an existing `fantasy_novel.epub` by fetching chapters 851 through 860 manually and appending them sequentially without redownloading existing chapters:

```bash
python3 main.py --update fantasy_novel.epub --start 851 --end 860
```

---

## Testing

The project is fully unit-tested with **pytest**. To run the test suite and verify implementation:

```bash
PYTHONPATH=. pytest
```

---

## Logging

Console outputs are kept to clean progress bars. Verbose information, redirects, HTTP request attempts, cache status (hits/misses), and errors are logged under:
- **`scraper.log`**
