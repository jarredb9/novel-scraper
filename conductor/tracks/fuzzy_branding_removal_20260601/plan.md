# Implementation Plan - Fuzzy Branding Removal

## Phase 1: Setup & Testing (TDD Red Phase) [checkpoint: 00ebc78]
- [x] 13f8174 Task: Add failing unit tests in `tests/test_sanitizer.py` verifying fuzzy matching on branding phrases.
    - [x] Test standalone branding paragraphs (e.g. "Stay connected through freewebnovel").
    - [x] Test branding text at the end of sentence (e.g. "The beast roared. Stay connected through freewebnovel").
    - [x] Test fuzzy variation (e.g. "Stay connected through freewebnovel.").
    - [x] Verify that non-branding sentences containing similar words (but below the ratio threshold) are NOT removed.
    - [x] Verify tests fail as expected.
- [x] 00ebc78 Task: Conductor - User Manual Verification 'Phase 1: Setup & Testing' (Protocol in workflow.md)

## Phase 2: Implementation (TDD Green Phase)
- [x] 5fe8b3c Task: Modify `src/sanitizer.py` to implement fuzzy branding removal.
    - [x] Import `difflib` standard library.
    - [x] Add branding phrases/sentences templates to `ContentSanitizer`.
    - [x] Define sentence-splitting logic to check sentences individually.
    - [x] Implement `SequenceMatcher` comparison against targets with a high similarity threshold (e.g., >= 0.85).
    - [x] Re-assemble paragraphs after removing/stripping matched sentences.
    - [x] Verify that all unit tests pass successfully.
- [x] 5fe8b3c Task: Verify overall codebase test coverage remains >80%.
- [~] Task: Conductor - User Manual Verification 'Phase 2: Implementation' (Protocol in workflow.md)
