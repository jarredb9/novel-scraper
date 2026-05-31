# Implementation Plan: Cover Art and EPUB Updating

## Phase 1: CLI and Cover Resolution & Caching [checkpoint: 13b513b]
- [x] Task: CLI Arguments and Configuration (b639738)
    - [ ] Write tests in `tests/test_cli.py` for new arguments `--cover` and `--update-epub` / `--merge-epub`
    - [ ] Implement `--cover` and `--update-epub` args in `src/cli.py`
    - [ ] Verify test suite passes and coverage is maintained
- [x] Task: Cover Art Downloader and Resolver (222551a)
    - [ ] Write failing unit tests in `tests/test_cover_resolver.py` for resolving local paths, downloading URLs, scraping from landing page, caching, and soft fallback
    - [ ] Implement cover art downloader and resolver (e.g. in `src/cover_resolver.py` or `src/scraper.py`)
    - [ ] Verify all tests pass with >80% coverage for the new code
- [x] Task: Conductor - User Manual Verification 'Phase 1: CLI and Cover Resolution & Caching' (Protocol in workflow.md) (13b513b)

## Phase 2: EPUB Chapter Extraction & Cover Embedding [checkpoint: e2970e7]
- [x] Task: EPUB Chapter Extraction (85c3154)
    - [ ] Write failing unit tests in `tests/test_epub_extractor.py` for extracting chapter title and text from existing EPUB
    - [ ] Implement EPUB extraction logic
    - [ ] Verify all tests pass with >80% coverage
- [x] Task: EPUB Cover Embedding (af22988)
    - [ ] Write failing unit tests in `tests/test_epub_cover_embedding.py` for setting EPUB cover metadata and generating dedicated cover XHTML page
    - [ ] Implement cover embedding in `src/epub_compiler.py`
    - [ ] Verify all tests pass with >80% coverage
- [x] Task: Conductor - User Manual Verification 'Phase 2: EPUB Chapter Extraction & Cover Embedding' (Protocol in workflow.md) (e2970e7)

## Phase 3: PDF Cover Page & Orchestrator Integration
- [x] Task: PDF Cover Page Generation (69ad54d)
    - [x] Write failing unit tests in `tests/test_pdf_cover.py` for creating a dedicated cover page with centered image and text
    - [x] Implement cover page layout rendering in `src/pdf_compiler.py`
    - [x] Verify tests pass with >80% coverage
- [x] Task: Orchestrator Integration (1fecd60)
    - [x] Write unit tests in `tests/test_orchestrator_integration.py` for the complete flow (scraping, resolving, extracting, compiling with cover)
    - [x] Modify `src/orchestrator.py` to coordinate cover download, extraction, and compilation
    - [x] Verify whole test suite passes and overall coverage meets quality gate (>80%)
- [~] Task: Conductor - User Manual Verification 'Phase 3: PDF Cover Page & Orchestrator Integration' (Protocol in workflow.md)
