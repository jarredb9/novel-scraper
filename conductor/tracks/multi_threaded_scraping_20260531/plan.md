# Implementation Plan: Support Multi-threaded / Concurrent Scraping

## Phase 1: CLI and Scraper Core Updates
- [x] Task: Add CLI flags in [src/cli.py](file:///C:/Users/jarre/OneDrive/Documents/Code/novel-scraper/src/cli.py) (080be79)
- [~] Task: Implement thread-safe rate-limiting in [src/scraper.py](file:///C:/Users/jarre/OneDrive/Documents/Code/novel-scraper/src/scraper.py)
- [ ] Task: Add tests for CLI/Scraper thread safety and verify they pass
- [ ] Task: Conductor - User Manual Verification 'CLI and Scraper Core Updates' (Protocol in workflow.md)

## Phase 2: Multi-threaded Orchestration
- [ ] Task: Parallelize chapter scraping in [src/orchestrator.py](file:///C:/Users/jarre/OneDrive/Documents/Code/novel-scraper/src/orchestrator.py)
- [ ] Task: Integrate safe tqdm progress bar updates and error handling
- [ ] Task: Write integration tests for multi-threaded scraping and verify they pass
- [ ] Task: Conductor - User Manual Verification 'Multi-threaded Orchestration' (Protocol in workflow.md)
