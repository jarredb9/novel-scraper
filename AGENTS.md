# AGENTS.md

This file provides persistent, project-specific context and operational guidelines for AI coding assistants (e.g., Cursor, Claude Code, Copilot, Antigravity).

---

## 1. Project Context & Architecture

**novel-scraper** is a command-line Python application that scrapes chapters of web novels from `freewebnovel.com`, caches the fetched HTML files, cleans/sanitizes the content, and compiles them into e-reader-optimized PDFs and/or EPUBs.

### Architecture Map
- [main.py](file:///C:/Users/jarre/OneDrive/Documents/Code/novel-scraper/main.py): Entry point of the application.
- [src/cli.py](file:///C:/Users/jarre/OneDrive/Documents/Code/novel-scraper/src/cli.py): Defines arguments (`--start`, `--end`, `--delay`, `--output`, `--format`, `--update`, `--cover`, `--threads`, `--url`, `--ad-pattern`).
- [src/orchestrator.py](file:///C:/Users/jarre/OneDrive/Documents/Code/novel-scraper/src/orchestrator.py): Unified workflow runner executing parsing, caching, scraping, and compiling. Automatically parses landing pages for chapter link mapping when `--url` is specified.
- [src/scraper.py](file:///C:/Users/jarre/OneDrive/Documents/Code/novel-scraper/src/scraper.py): Fetching engine with polite rate limiting, exponential backoff (retries on HTTP 429), and a thread lock for safe concurrent rate-limiting. Supports custom URL mapping.
- [src/cache.py](file:///C:/Users/jarre/OneDrive/Documents/Code/novel-scraper/src/cache.py): `CachingManager` storing/retrieving raw chapter HTML files under `./cache`.
- [src/parser.py](file:///C:/Users/jarre/OneDrive/Documents/Code/novel-scraper/src/parser.py): `lxml` parser utilizing target XPaths for chapter text extraction, with heuristic fallbacks for titles and bodies if XPaths fail.
- [src/sanitizer.py](file:///C:/Users/jarre/OneDrive/Documents/Code/novel-scraper/src/sanitizer.py): Cleans boilerplate/ads and outputs formatted paragraphs. Supports punctuation normalization, non-alphanumeric paragraph filtering, and fuzzy matching to remove branding statements.
- [src/pdf_compiler.py](file:///C:/Users/jarre/OneDrive/Documents/Code/novel-scraper/src/pdf_compiler.py): Builds flowing PDFs via ReportLab with clickable Table of Contents (TOC) and document outline sidebars.
- [src/pdf_reader.py](file:///C:/Users/jarre/OneDrive/Documents/Code/novel-scraper/src/pdf_reader.py): Extracts outline bookmark data from existing PDFs using `pypdf` to identify completed chapters.
- [src/epub_compiler.py](file:///C:/Users/jarre/OneDrive/Documents/Code/novel-scraper/src/epub_compiler.py): Formats and packages EPUB containers using `ebooklib`.

---

## 2. Executable Development Commands

Always run commands in the project root virtual environment.

### Setup Environment
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Running the Scraper
```powershell
# Scrape specific range and output both formats
python main.py --start 800 --end 850 --output fantasy_novel --format both

# Run auto-detecting chapter links from landing page URL
python main.py --url https://freewebnovel.com/the-first-legendary-beast-master.html --start 800 --end 805 --output novel.epub --format epub

# Run with custom delay (default: 1.0) and cover image
python main.py --start 800 --end 810 --delay 2.0 --cover ./cover.jpg --output novel.pdf

# Scrape concurrently using multi-threading (default: 4 threads)
python main.py --start 800 --end 850 --threads 4 --output novel.pdf

# Incrementally update an existing EPUB/PDF file with new chapters manually
python main.py --update novel.epub --start 811 --end 820

# Auto-update an existing EPUB/PDF file using metadata-driven URL extraction
python main.py --update novel.epub
```

### Running Tests and Linting
```powershell
# Run the entire test suite (Windows PowerShell)
$env:PYTHONPATH="."; python -m pytest

# Run tests with terminal coverage report
$env:PYTHONPATH="."; python -m pytest --cov=src --cov-report=term-missing
```


---

## 3. Style and Coding Conventions

Adhere strictly to the following standards when editing or generating Python code:

1. **Python Style Guide**: Follow the [Google Python Style Guide Summary](file:///C:/Users/jarre/OneDrive/Documents/Code/novel-scraper/conductor/code_styleguides/python.md).
2. **Indentation & Formatting**: 
   - 4 spaces indentation (no tabs).
   - Maximum line length: 80 characters.
   - Use f-strings for string formatting.
3. **Naming**:
   - Classes: `PascalCase`
   - Functions, methods, and variables: `snake_case`
   - Constants: `ALL_CAPS_WITH_UNDERSCORES`
   - Internal attributes: Prefix with a single underscore (`_helper_func`)
4. **Documentation**:
   - All modules, public functions, classes, and methods must have a detailed docstring:
     ```python
     def function_name(arg_a: int) -> str:
         """Short description of the function.

         Args:
             arg_a: Description of parameter.

         Returns:
             Description of return value.

         Raises:
             ValueError: If arguments are invalid.
         """
     ```
5. **Types**: Use Python type hints on all public APIs.

---

## 4. Boundaries and Guardrails (Forbidden Zones)

- **Do NOT bypass scraping policies**: Never decrease or remove the default 1.0-second delay `--delay` parameter unless requested explicitly. Politeness is critical to avoid IP bans.
- **Error Handling**: Do not write bare `except:` clauses. Always handle specific exceptions (e.g., `requests.exceptions.RequestException`, `lxml.etree.LxmlError`).
- **PDF Layout Guidelines**: Do not change ReportLab layout parameters unless modifying the cover design. Margins must be `0.5 inches / 36 points`, with `Times-Roman` and `Times-Bold` font families. Body text is `11pt` with a `16.5pt` line spacing leading.
- **Plan Protocol**: Follow the Conductor environment track planning and workflow steps defined in [conductor/workflow.md](file:///C:/Users/jarre/OneDrive/Documents/Code/novel-scraper/conductor/workflow.md).
- **Test-Driven Development (TDD)**: Ensure test coverage remains >80% for any new or modified logic.
