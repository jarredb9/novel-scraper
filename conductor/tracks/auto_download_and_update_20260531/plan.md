# Plan: Auto-Download & Auto-Update

## Phase 1: Auto-Range Downloader and Metadata Storage [checkpoint: dc3215c]
- [x] Task: Write tests for Auto-Range Detection and EPUB/PDF metadata reading/writing (f5f2a13)
    - [x] Write unit tests verifying that when `--url` is provided and `--start` / `--end` are `None`, the scraper auto-detects and processes the full chapter range.
    - [x] Write unit tests for writing the landing page URL to EPUB metadata and extracting it.
    - [x] Write unit tests for writing the landing page URL to PDF metadata and extracting it.
- [x] Task: Implement Auto-Range Detection and Metadata storage/extraction (f5f2a13)
    - [x] Modify `src/cli.py` to change default value of `--start` and `--end` to `None`. If `--url` is not provided and start/end are None, fallback to default range `776` to `1780`.
    - [x] Modify `src/orchestrator.py` to calculate start and end values dynamically from `url_map` keys if they are `None`.
    - [x] Modify `src/epub_compiler.py` to embed the landing page URL into `DC:source` metadata.
    - [x] Modify `src/pdf_compiler.py` to embed the landing page URL into PDF Subject/Keywords metadata.
    - [x] Implement metadata extraction helper in `src/epub_extractor.py`.
    - [x] Implement metadata extraction helper in `src/pdf_reader.py`.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Auto-Range Downloader and Metadata Storage' (Protocol in workflow.md) (dc3215c)

## Phase 2: Auto-Update CLI & Orchestrator Flow [checkpoint: 28a296f]
- [x] Task: Write tests for Auto-Update command logic (8ccf36c)
    - [x] Write unit and integration tests for the `--update` CLI argument.
    - [x] Write tests verifying that auto-update reads metadata to find the source URL, detects missing chapters, downloads only the missing ones, and compiles them correctly.
- [x] Task: Implement CLI `--update` and update orchestration logic (8ccf36c)
    - [x] Add the `--update` parameter to `src/cli.py`.
    - [x] Implement update detection logic in `src/orchestrator.py`.
    - [x] Connect the `--update` execution path in `main.py` and `src/orchestrator.py`.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Auto-Update CLI & Orchestrator Flow' (Protocol in workflow.md) (28a296f)
