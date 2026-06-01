# Specification: Fuzzy Branding Removal

## Overview
This feature introduces a dependable fuzzy matching-based cleanup system in `ContentSanitizer` to identify and remove website branding phrases (such as "Stay connected through freewebnovel", "Stay tuned with freewebnovel", and "Explore new worlds at freewebnovel") from crawled paragraphs. This cleanup handles cases where these branding statements are standalone paragraphs or embedded at the end of other sentences.

## Functional Requirements
1. **Fuzzy Search Integration**:
   - Integrate fuzzy matching using `difflib.SequenceMatcher` (standard library, highly reliable and deterministic).
   - Use a high threshold (e.g. `0.85` or `0.90`) to ensure 100% certainty that we do not remove actual story text.

2. **Parsing & Cleaning Mechanics**:
   - Process each paragraph by splitting it into sentences.
   - For each sentence, check it against standard branding patterns using fuzzy matching.
   - If a sentence matches a branding statement, remove it or strip the matched part.
   - Reconstruct the paragraph with the clean sentences.

3. **Configurable Default Branding Phrases**:
   - "Stay connected through freewebnovel"
   - "Stay tuned with freewebnovel"
   - "Explore new worlds at freewebnovel"

## Non-Functional Requirements
- Maintain test coverage above 80%.
- Maintain maximum line length of 80 characters.
- Ensure zero extra external dependencies are introduced if standard library `difflib` is sufficient.

## Out of Scope
- Modifying default HTML parsing rules.
- Removing non-branding boilerplate that is already addressed by existing regular expressions.
