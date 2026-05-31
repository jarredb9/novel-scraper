# Specification: Chapter Link Auto-Detection & Heuristic Content Parsing

## Overview
Web novel formats and structures differ across sites and pages. This track implements:
1. **Chapter Link Auto-Detection**: Accepts a novel's landing page URL via CLI, downloads it, and parses all chapter links automatically instead of requiring users to construct sequential URL patterns manually.
2. **Content Heuristic Parsing**: Dynamically extracts chapter titles and main body text based on paragraph density and headings if specific/default XPaths fail to find elements.

## Functional Requirements
### 1. Chapter Link Auto-Detection
- Add a new CLI argument `--url` to [src/cli.py](file:///C:/Users/jarre/OneDrive/Documents/Code/novel-scraper/src/cli.py).
- If `--url` is specified, the orchestrator must download the landing page, search for all chapter links, and extract their numerical order (e.g. from the href or text).
- Map the extracted chapter numbers to their URLs in `NovelScraper`.
- Sort the chapter list numerically and filter using `--start` and `--end` if provided.

### 2. Heuristic Content Parsing
- Modify [src/parser.py](file:///C:/Users/jarre/OneDrive/Documents/Code/novel-scraper/src/parser.py) to fall back to heuristic extraction if the configured XPaths fail.
- **Title Heuristics**: Find the first `<h1>` text content, fallback to `<h2>`, fallback to elements with class names containing `title`, fallback to cleaning up the document's `<title>` tag.
- **Body Heuristics**: Select the container element (`div`, `article`, `section`) containing the largest number of `<p>` tag descendants. Fallback to raw text/breaks if `<p>` tags are absent.

## Non-Functional Requirements
- Maintain backward compatibility.
- Standard test coverage target of >80%.

## Acceptance Criteria
- Running `main.py` with `--url <landing_page>` successfully resolves, downloads, and compiles the selected chapter range.
- Heuristic parsing correctly handles variations in chapter page DOM layout without throwing `ValueError` exceptions when default selectors fail.
