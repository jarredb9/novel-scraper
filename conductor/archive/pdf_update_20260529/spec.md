# Specification - PDF Update and Chapter Integration

## Overview
This feature adds the capability to update an existing compiled web novel PDF with earlier or later chapters without re-scraping already-cached content. The utility will automatically scan the existing PDF's bookmarks (outline) to determine which chapters are already present, download/parse any missing chapters requested by the user, combine the existing and new chapters, sort them sequentially by chapter number, and compile them into a new, unified PDF.

## Functional Requirements
1. **Existing Chapter Detection**:
   - Extract the chapter titles/numbers already compiled inside an existing PDF by parsing its PDF outline (bookmarks).
   - Supplement this list with the local HTML files in the `cache` directory to ensure full capability to reconstruct the text of the existing chapters.
   - If a chapter's HTML cache is missing, but it is listed in the PDF, or if the PDF is not present, fetch it from the web novel source.

2. **Chapter Integration & Sorting**:
   - Merge the detected existing chapters with the newly specified earlier or later chapters.
   - Sort all chapters in ascending order based on their parsed chapter numbers (e.g., Chapter 775, Chapter 776, Chapter 777).
   - Ensure the compiled output PDF has a single, updated Table of Contents (TOC) page and matching PDF bookmarks (outline panel) for all integrated chapters.

3. **CLI Interface Updates**:
   - Introduce a new CLI parameter `--update-pdf <path_to_existing_pdf>` to target a PDF to update.
   - Example usage: `python main.py --update-pdf current_novel.pdf --start 770 --end 1790`
     - This will inspect `current_novel.pdf` to see which chapters are already present.
     - If `current_novel.pdf` has chapters 776 to 1780, it will scrape chapters 770-775 and 1781-1790 (if not already cached).
     - It will then generate a new unified PDF containing all chapters 770 to 1790.

4. **Robust Error Handling**:
   - If the targeted PDF does not exist or is corrupted, default to compiling a new PDF for the specified range.
   - Log warnings if a chapter is found in the PDF outline but has no corresponding cache file and cannot be scraped.

## Tech Stack Changes
- Add `pypdf` to read and parse the outline/bookmarks structure of existing PDF files.

## Acceptance Criteria
- [ ] Running the CLI with `--update-pdf` successfully parses the chapter outline of an existing PDF.
- [ ] Automatically detects which chapters are already present in the PDF and avoids re-scraping them if they are cached.
- [ ] Successfully scrapes/parses new earlier and later chapters in the target range.
- [ ] Generates a single updated PDF containing all chapters, sorted sequentially, with a correct Table of Contents and bookmark navigation.
- [ ] At least 80% test coverage is maintained for the new detection and merging modules.

## Out of Scope
- Re-downloading already existing chapters unless explicitly requested.
- In-place modification of the PDF file (it is safer to write a new PDF and overwrite/rename).
