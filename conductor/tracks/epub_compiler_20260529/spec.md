# Specification: EPUB Compiler Feature

## Overview
Add an EPUB compilation engine to the web novel scraper, allowing users to compile web novels into standard `.epub` files (alongside or instead of `.pdf` files). This allows compatibility with e-readers and the ability to sync reading progress across multiple devices.

## Functional Requirements
1. **EPUB Compiler (`EPUBCompiler`)**:
   - Create a module `src/epub_compiler.py` hosting the `EPUBCompiler` class.
   - Use `ebooklib` to programmatically build the EPUB container structure.
   - Generate chapter files dynamically using the existing sanitized chapter text.
   - Support sorting chapters sequentially by chapter number prior to compilation.

2. **Table of Contents & Navigation**:
   - Leverage `ebooklib`'s navigation structure to define the Table of Contents (`toc`) and book `spine`.
   - Embed proper book metadata (Title, Language, Author/Creator).

3. **Styling and Layout**:
   - Embed a CSS stylesheet in the EPUB to support basic styling: margins, font hierarchies, standard paragraph indentation, clean chapter titles, and line heights.
   - Inject the stylesheet as a separate style sheet element in the EPUB package and link it in each chapter.

4. **CLI Integration**:
   - Add a `--format` option to the CLI (`src/cli.py`) with choices: `pdf`, `epub`, `both`. The default is `both`.
   - Update the output file generation in `src/orchestrator.py`:
     - If `--format pdf` is specified, generate only the PDF.
     - If `--format epub` is specified, generate only the EPUB (derived from the output filename, replacing `.pdf` with `.epub` if applicable, or using the extension `.epub`).
     - If `--format both` (default) is specified, compile and save both `.pdf` and `.epub` formats.

5. **Caching & Incremental Support**:
   - Ensure the EPUB compiler uses the cached chapter HTML files in the same manner as the PDF compiler, allowing it to build from local cache without redownloading.

## Non-Functional Requirements
- **Dependencies**: Add `ebooklib` to `requirements.txt`.
- **Test Coverage**: Keep test coverage of the new code above 80%.
- **Robustness**: Gracefully handle character encoding issues or HTML structure anomalies during EPUB compilation.

## Acceptance Criteria
- Running `python main.py --start 776 --end 778` generates both `novel.pdf` and `novel.epub` in the current working directory.
- Running `python main.py --start 776 --end 778 --format epub` generates only `novel.epub`.
- Running `python main.py --start 776 --end 778 --format pdf` generates only `novel.pdf`.
- The generated `.epub` file passes basic EPUB verification checks and opens cleanly in standard readers (e.g. Calibre, Apple Books) with a navigable Table of Contents.

## Out of Scope
- Direct device synchronization protocols (e.g., Send to Kindle, Calibre server integration).
- Fetching cover images or generating custom cover graphics.
