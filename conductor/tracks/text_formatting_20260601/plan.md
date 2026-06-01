# Implementation Plan - Text Cleaning and Formatting Improvements

## Phase 1: Punctuation Normalization & Paragraph Filtering
- [x] Task: Write failing unit tests for punctuation normalization and paragraph filtering (96ed95c)
    - [x] Add tests in `tests/test_sanitizer.py` verifying smart quotes mapping to straight quotes.
    - [x] Add tests verifying `--` and `---` mapping to `—`.
    - [x] Add tests verifying `...` mapping to `…`.
    - [x] Add tests verifying empty/non-alphanumeric paragraphs are filtered out.
- [x] Task: Implement punctuation normalization and paragraph filtering in `src/sanitizer.py` (2c4b01c)
    - [x] Add translation mappings or regex-based replacement rules in `ContentSanitizer.clean_text` or a helper.
    - [x] Update `ContentSanitizer.sanitize` to filter out paragraphs with no alphanumeric characters.
    - [x] Run tests and verify they pass.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Punctuation Normalization & Paragraph Filtering' (Protocol in workflow.md)

## Phase 2: Configurable Ad & Branding Filtering
- [ ] Task: Write failing unit tests for configurable ad and branding patterns
    - [ ] Add tests in `tests/test_sanitizer.py` to verify that custom regex patterns filter matching paragraphs.
    - [ ] Add integration/orchestrator tests verifying CLI arguments pass custom ad patterns to the sanitizer.
- [ ] Task: Implement configurable ad/branding patterns
    - [ ] Update `ContentSanitizer.__init__` in `src/sanitizer.py` to allow merging custom ad patterns with defaults.
    - [ ] Update `src/cli.py` to add CLI option `--ad-pattern` (multiple allowed or comma-separated).
    - [ ] Update `src/orchestrator.py` to extract ad patterns from CLI arguments and inject them into `ContentSanitizer`.
    - [ ] Run tests and verify they pass.
- [ ] Task: Update README.md and AGENTS.md documentation
    - [ ] Update `README.md` to document the new `--ad-pattern` CLI parameter and the punctuation normalization behaviors.
    - [ ] Update `AGENTS.md` to reflect CLI and sanitizer changes.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Configurable Ad & Branding Filtering' (Protocol in workflow.md)
