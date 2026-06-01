# Plan: Codebase Simplification and Refactoring

## Phase 1: Shared Utilities & Metadata Reader Consolidation [checkpoint: e31c872]
- [x] Task: Create `src/utils.py` and implement unit tests for it. (8ce30fc)
    - [x] Create `tests/test_utils.py` with failing tests checking `extract_chapter_number` and `extract_source_url`.
    - [x] Implement `extract_chapter_number` and `extract_source_url` in `src/utils.py`.
    - [x] Run test suite to verify tests pass.
- [x] Task: Integrate shared utilities into `pdf_reader.py` and `epub_extractor.py`. (262746d)
    - [x] Update tests to verify that new imports from `src.utils` are used and behave exactly the same.
    - [x] Refactor `src/pdf_reader.py` and `src/epub_extractor.py` to import and call `extract_chapter_number` and `extract_source_url` from `src.utils`.
    - [x] Run test suite and check code coverage.
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)


## Phase 2: CLI Simplification, Orchestrator Refactor, and Documentation Updates
- [x] Task: Simplify CLI and clean orchestrator update logic. (46d7e28)
    - [x] Update CLI parser tests in `tests/test_cli.py` to remove references to the old update parameters and ensure only `--update` remains.
    - [x] Modify `src/cli.py` to remove `--update-pdf`, `--merge-pdf`, `--update-epub`, `--merge-epub`.
    - [x] Modify `src/orchestrator.py` to remove update parameters other than `update` (path). Simplify how it calls the consolidated `extract_source_url` helper.
    - [x] Run test suite, update tests to reflect changed orchestrator arguments, and ensure 100% test pass rate and >80% coverage.
- [x] Task: Update documentation to reflect simplified parameters. (63122ad)
    - [x] Update command-line usage examples in `README.md` to remove `--update-epub` and `--update-pdf`.
    - [x] Update `AGENTS.md` (and any related rules files) to remove references to `--update-epub` and `--update-pdf`.
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)
