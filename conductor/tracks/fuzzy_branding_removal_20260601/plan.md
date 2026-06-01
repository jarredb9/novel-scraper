# Implementation Plan - Fuzzy Branding Removal

## Phase 1: Setup & Testing (TDD Red Phase)
- [x] 13f8174 Task: Add failing unit tests in `tests/test_sanitizer.py` verifying fuzzy matching on branding phrases.
    - [ ] Test standalone branding paragraphs (e.g. "Stay connected through freewebnovel").
    - [ ] Test branding text at the end of sentence (e.g. "The beast roared. Stay connected through freewebnovel").
    - [ ] Test fuzzy variation (e.g. "Stay connected through freewebnovel.").
    - [ ] Verify that non-branding sentences containing similar words (but below the ratio threshold) are NOT removed.
    - [ ] Verify tests fail as expected.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Setup & Testing' (Protocol in workflow.md)

## Phase 2: Implementation (TDD Green Phase)
- [ ] Task: Modify `src/sanitizer.py` to implement fuzzy branding removal.
    - [ ] Import `difflib` standard library.
    - [ ] Add branding phrases/sentences templates to `ContentSanitizer`.
    - [ ] Define sentence-splitting logic to check sentences individually.
    - [ ] Implement `SequenceMatcher` comparison against targets with a high similarity threshold (e.g., >= 0.85).
    - [ ] Re-assemble paragraphs after removing/stripping matched sentences.
    - [ ] Verify that all unit tests pass successfully.
- [ ] Task: Verify overall codebase test coverage remains >80%.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Implementation' (Protocol in workflow.md)
