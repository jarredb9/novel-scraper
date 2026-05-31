# Specification: Support Multi-threaded / Concurrent Scraping

## Overview
Scraping chapters sequentially can be slow for long novels. This track adds support for concurrent scraping using multi-threading to speed up downloads, while ensuring that we still respect rate limits globally to avoid overloading the server.

## Functional Requirements
1. **CLI Thread Argument**: Add a `--threads` / `-t` argument in [src/cli.py](file:///C:/Users/jarre/OneDrive/Documents/Code/novel-scraper/src/cli.py) to specify the number of scraper threads (default: 4).
2. **Thread-Safe Rate Limiting**: Ensure that the politeness delay is enforced globally in [src/scraper.py](file:///C:/Users/jarre/OneDrive/Documents/Code/novel-scraper/src/scraper.py) using a thread lock, avoiding simultaneous overlapping requests that could trigger IP blocks.
3. **Concurrent Download Orchestration**: Update the download loop in [src/orchestrator.py](file:///C:/Users/jarre/OneDrive/Documents/Code/novel-scraper/src/orchestrator.py) to use `concurrent.futures.ThreadPoolExecutor`.
4. **Dynamic Progress Updates**: The `tqdm` progress bar must update dynamically as threads complete their scraping tasks.
5. **Fail-Fast Error Handling**: If any thread raises a fatal exception (network or parsing failure), remaining tasks must be cancelled, and execution must abort to prevent compiling a corrupted/incomplete novel.

## Non-Functional Requirements
- Maintain backwards compatibility (running sequentially if `--threads 1`).
- All code changes must pass the test suite.
- Aim for >80% unit test coverage.

## Acceptance Criteria
- Running `main.py` with `--threads 4` successfully parallelizes the scrape.
- Global request intervals are rate-limited appropriately.
- If a chapter download fails after all retries, the entire process aborts cleanly.
