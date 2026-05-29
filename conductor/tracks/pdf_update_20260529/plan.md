# Implementation Plan - PDF Update and Chapter Integration

## Phase 1: Setup and Dependency Integration [checkpoint: abc779a]
- [x] Task: Update project dependencies and stack documentation [5162c1a]
    - [ ] Update `conductor/tech-stack.md` to document the addition of `pypdf`
    - [ ] Add `pypdf` to `requirements.txt`
    - [ ] Install the new dependency using pip
- [x] Task: Conductor - User Manual Verification 'Phase 1: Setup and Dependency Integration' (Protocol in workflow.md)

## Phase 2: PDF Bookmark and Outline Parsing [checkpoint: a092e7a]
- [x] Task: Write failing unit tests for PDF metadata outline parser [effb4b2]
    - [x] Create `tests/test_pdf_reader.py` with tests for extracting chapter titles and numbers from an existing PDF file using pypdf
- [x] Task: Implement PDF outline reader functionality [23e667e]
    - [x] Create `src/pdf_reader.py` and implement outline parser
    - [x] Run the tests and ensure they pass (Green phase)
    - [x] Verify test coverage for `src/pdf_reader.py` is >80%
- [x] Task: Conductor - User Manual Verification 'Phase 2: PDF Bookmark and Outline Parsing' (Protocol in workflow.md)

## Phase 3: Update Orchestrator and Range Determination [checkpoint: 6ec043c]
- [x] Task: Write failing unit tests for update orchestration [d0ec36f]
    - [x] Add unit tests verifying range comparison logic (comparing PDF outline chapters vs. target start/end CLI range)
    - [x] Test the download planning output (figuring out exactly which chapters need to be fetched)
- [x] Task: Implement range selection and orchestrator logic [d0ec36f]
    - [x] Update `src/orchestrator.py` to compare PDF chapters with CLI range and determine which are missing
    - [x] Update `src/cli.py` to support the new `--update-pdf` (and optional alias `--merge-pdf`) CLI argument
    - [x] Run the tests and ensure they pass (Green phase)
- [x] Task: Conductor - User Manual Verification 'Phase 3: Update Orchestrator and Range Determination' (Protocol in workflow.md)

## Phase 4: Sequential Merging, Compilation, and Final Quality Check
- [x] Task: Write unit tests for sorted PDF compilation [94aa1c2]
    - [x] Add tests to verify chapters are compiled in sorted numerical order regardless of their scraper/cache load order
- [x] Task: Update compilation behavior and final run [94aa1c2]
    - [x] Ensure `src/pdf_compiler.py` handles custom/arbitrary sorted inputs gracefully and generates matching bookmarks and TOC
    - [x] Verify all automated tests pass with >80% code coverage across the codebase
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Sequential Merging, Compilation, and Final Quality Check' (Protocol in workflow.md)
