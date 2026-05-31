# Implementation Plan: Chapter Link Auto-Detection & Heuristic Content Parsing

## Phase 1: Chapter Link Auto-Detection
- [ ] Task: Scrape landing page and extract chapter URLs in [src/orchestrator.py](file:///C:/Users/jarre/OneDrive/Documents/Code/novel-scraper/src/orchestrator.py)
- [ ] Task: Add URL mapping support in [src/scraper.py](file:///C:/Users/jarre/OneDrive/Documents/Code/novel-scraper/src/scraper.py)
- [ ] Task: Add unit and integration tests for chapter link auto-detection
- [ ] Task: Conductor - User Manual Verification 'Chapter Link Auto-Detection' (Protocol in workflow.md)

## Phase 2: Heuristic Content Extraction
- [ ] Task: Implement heuristic title/body extraction in [src/parser.py](file:///C:/Users/jarre/OneDrive/Documents/Code/novel-scraper/src/parser.py)
- [ ] Task: Fallback to heuristic parser in XPathParser when XPaths fail
- [ ] Task: Add unit tests for heuristic content extraction
- [ ] Task: Conductor - User Manual Verification 'Heuristic Content Extraction' (Protocol in workflow.md)
