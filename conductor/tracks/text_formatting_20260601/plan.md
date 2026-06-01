# Implementation Plan - Text Cleaning and Formatting Improvements

## Phase 1: Punctuation Normalization & Paragraph Filtering [checkpoint: b3ad126]
- [x] Task: Write failing unit tests for punctuation normalization and paragraph filtering (96ed95c)
    - [x] Add tests in `tests/test_sanitizer.py` verifying smart quotes mapping to straight quotes.
    - [x] Add tests verifying `--` and `---` mapping to `—`.
    - [x] Add tests verifying `...` mapping to `…`.
    - [x] Add tests verifying empty/non-alphanumeric paragraphs are filtered out.
- [x] Task: Implement punctuation normalization and paragraph filtering in `src/sanitizer.py` (2c4b01c)
    - [x] Add translation mappings or regex-based replacement rules in `ContentSanitizer.clean_text` or a helper.
    - [x] Update `ContentSanitizer.sanitize` to filter out paragraphs with no alphanumeric characters.
    - [x] Run tests and verify they pass.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Punctuation Normalization & Paragraph Filtering' (Protocol in workflow.md) (b3ad126)

## Phase 2: Configurable Ad & Branding Filtering [checkpoint: f1cbbc9]
- [x] Task: Write failing unit tests for configurable ad and branding patterns (1a347e2)
    - [x] Add tests in `tests/test_sanitizer.py` to verify that custom regex patterns filter matching paragraphs.
    - [x] Add integration/orchestrator tests verifying CLI arguments pass custom ad patterns to the sanitizer.
- [x] Task: Implement configurable ad/branding patterns (5f12235)
    - [x] Update `ContentSanitizer.__init__` in `src/sanitizer.py` to allow merging custom ad patterns with defaults.
    - [x] Update `src/cli.py` to add CLI option `--ad-pattern` (multiple allowed or comma-separated).
    - [x] Update `src/orchestrator.py` to extract ad patterns from CLI arguments and inject them into `ContentSanitizer`.
    - [x] Run tests and verify they pass.
- [x] Task: Update README.md and AGENTS.md documentation (bf62c06)
    - [x] Update `README.md` to document the new `--ad-pattern` CLI parameter and the punctuation normalization behaviors.
    - [x] Update `AGENTS.md` to reflect CLI and sanitizer changes.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Configurable Ad & Branding Filtering' (Protocol in workflow.md) (f1cbbc9)

## Phase: Review Fixes
- [x] Task: Apply review suggestions (98e8bd2)
