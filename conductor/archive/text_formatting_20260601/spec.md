# Specification - Text Cleaning and Formatting Improvements

## Overview
This feature introduces enhancements to the `ContentSanitizer` in [sanitizer.py](file:///home/byrnesjd4821/Git/novel-scraper/src/sanitizer.py) to improve the quality of the scraped novel chapters. It focuses on punctuation normalization (smart quotes, em-dashes, ellipses), removal of empty/redundant paragraphs containing only non-alphanumeric or branding content, and customizable/configurable ad/branding filter patterns through the CLI and configuration.

## Functional Requirements
1. **Punctuation Normalization**:
   - Convert all smart/curly double quotes (`“`, `”`) and single quotes/apostrophes (`‘`, `’`) to standard straight ones (`"` and `'`).
   - Convert multiple consecutive dashes (e.g., `--` and `---`) to a standard em-dash (`—`).
   - Convert triple dots (`...`) or other multi-dot sequences (e.g. `..`) to a single unicode ellipsis character (`…`).
2. **Redundant/Empty Paragraph Filtering**:
   - Filter out any paragraphs that, after sanitization and whitespace cleaning, contain no alphanumeric characters (e.g., lines containing only separators like `* * *`, `---`, or empty space).
3. **Configurable Ad & Branding Filtering**:
   - Extend the `ContentSanitizer` to accept custom ad patterns/regexes during initialization.
   - Update the CLI (`src/cli.py`) and orchestrator (`src/orchestrator.py`) to allow passing custom ad patterns via a command-line argument `--ad-patterns` (or similar) or from configuration.

## Non-Functional Requirements
- **Performance**: Punctuation translation must be fast and execute in O(N) using pre-compiled regexes or translation tables.
- **Backward Compatibility**: Ensure that default ad filtering still runs if no custom patterns are provided.

## Acceptance Criteria
1. Curly quotes/apostrophes are fully normalized to straight ones in the output PDF/EPUB.
2. Double/triple dashes are normalized to em-dashes (`—`).
3. Triple dots are normalized to ellipsis (`…`).
4. Empty or symbol-only paragraphs are excluded from output chapters.
5. Custom ad patterns passed via CLI successfully filter matches from raw HTML.
6. Existing tests and new unit tests for sanitization improvements all pass.

## Out of Scope
- Support for other file format compilation (only EPUB and PDF are supported).
