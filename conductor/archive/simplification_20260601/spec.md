# Specification: Codebase Simplification and Refactoring

## Overview
As the application has evolved, some redundant code blocks and legacy CLI options have accumulated. This track aims to simplify and condense the application structure by:
1. Moving `extract_chapter_number` to a shared helper and using it consistently in `orchestrator.py`, `epub_extractor.py`, and `pdf_reader.py`.
2. Consolidating the landing page source URL metadata extraction logic (`extract_source_url_from_pdf` and `extract_source_url_from_epub`) into a single utility helper `extract_source_url(file_path: str)` that auto-detects file types.
3. Streamlining the CLI by removing the legacy and redundant `--update-pdf` / `--merge-pdf` and `--update-epub` / `--merge-epub` parameters, keeping `--update <path>` as the single unified entry point for updates.

## Functional Requirements
1. **Shared Utilities Module**:
   - Create/modify `src/utils.py` (or export from an existing helper) to house:
     - `extract_chapter_number(title: str) -> Optional[int]`
     - `extract_source_url(file_path: str) -> Optional[str]`
   - Update `src/pdf_reader.py`, `src/epub_extractor.py`, and `src/orchestrator.py` to use these shared utilities instead of duplicate local regexes or functions.
2. **CLI Streamlining**:
   - In `src/cli.py`, remove the arguments `--update-pdf`/`--merge-pdf` and `--update-epub`/`--merge-epub`.
   - Update `src/orchestrator.py` to only expect the `update` parameter, which handles both EPUB and PDF based on the file extension.
3. **Robust Tests**:
   - Update existing test files to match the new imports and verify that all functionality remains intact and coverage is maintained above 80%.

## Non-Functional Requirements
- Maintain backward compatibility of core functionality (scraping, parsing, and compiling).
- Keep code coverage >80%.
- Strictly follow the Google Python Style Guide (4 spaces, max 80 chars, type hints, docstrings).
