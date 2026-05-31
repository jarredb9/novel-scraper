# Plan: Auto-Download & Auto-Update

## Phase 1: Auto-Range Downloader and Metadata Storage
- [ ] Task: Write tests for Auto-Range Detection and EPUB/PDF metadata reading/writing
    - [ ] Write unit tests verifying that when `--url` is provided and `--start` / `--end` are `None`, the scraper auto-detects and processes the full chapter range.
    - [ ] Write unit tests for writing the landing page URL to EPUB metadata and extracting it.
    - [ ] Write unit tests for writing the landing page URL to PDF metadata and extracting it.
- [ ] Task: Implement Auto-Range Detection and Metadata storage/extraction
    - [ ] Modify `src/cli.py` to change default value of `--start` and `--end` to `None`. If `--url` is not provided and start/end are None, fallback to default range `776` to `1780`.
    - [ ] Modify `src/orchestrator.py` to calculate start and end values dynamically from `url_map` keys if they are `None`.
    - [ ] Modify `src/epub_compiler.py` to embed the landing page URL into `DC:source` metadata.
    - [ ] Modify `src/pdf_compiler.py` to embed the landing page URL into PDF Subject/Keywords metadata.
    - [ ] Implement metadata extraction helper in `src/epub_extractor.py`.
    - [ ] Implement metadata extraction helper in `src/pdf_reader.py`.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Auto-Range Downloader and Metadata Storage' (Protocol in workflow.md)

## Phase 2: Auto-Update CLI & Orchestrator Flow
- [ ] Task: Write tests for Auto-Update command logic
    - [ ] Write unit and integration tests for the `--update` CLI argument.
    - [ ] Write tests verifying that auto-update reads metadata to find the source URL, detects missing chapters, downloads only the missing ones, and compiles them correctly.
- [ ] Task: Implement CLI `--update` and update orchestration logic
    - [ ] Add the `--update` parameter to `src/cli.py`.
    - [ ] Implement update detection logic in `src/orchestrator.py`.
    - [ ] Connect the `--update` execution path in `main.py` and `src/orchestrator.py`.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Auto-Update CLI & Orchestrator Flow' (Protocol in workflow.md)
