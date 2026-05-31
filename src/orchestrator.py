"""Orchestrator for the web novel scraper.

Combines the caching, scraping, parsing, sanitizing, and PDF compilation
sub-components into a single unified extraction and assembly workflow.
"""

import logging
from typing import Optional
from tqdm import tqdm
from src.cache import CachingManager
from src.scraper import NovelScraper
from src.parser import XPathParser
from src.sanitizer import ContentSanitizer
from src.pdf_compiler import PDFCompiler
from src.pdf_reader import (
    parse_pdf_outline,
    extract_chapter_number,
    extract_source_url_from_pdf,
)
from src.epub_compiler import EPUBCompiler
from src.cover_resolver import resolve_cover
from src.epub_extractor import (
    extract_chapters_from_epub,
    extract_source_url_from_epub,
)
import os

# Retrieve the same logger configured in scraper.py
logger = logging.getLogger("novel_scraper")


def derive_novel_title(base_url: str) -> str:
    """Derive the novel title from the scraper's base URL.

    Args:
        base_url (str): The base URL of the novel.

    Returns:
        str: The derived title of the novel.
    """
    if not isinstance(base_url, str):
        return "Compiled Novel"
    url = base_url.strip()
    if url.endswith("/"):
        url = url[:-1]
    
    for suffix in ["/chapter-", "/chapter", "/"]:
        if url.endswith(suffix):
            url = url[:-len(suffix)]
            break
            
    parts = url.split("/")
    if parts:
        slug = parts[-1]
        title = slug.replace("-", " ").title()
        if title:
            return title
            
    return "Compiled Novel"


def extract_chapters_from_landing_page(
    html_content: str, landing_page_url: str
) -> dict:
    """Extract chapter numbers and absolute URLs from landing page HTML.

    Args:
        html_content (str): The HTML contents of the landing page.
        landing_page_url (str): The landing page URL.

    Returns:
        dict: A dictionary mapping chapter number (int/float) to absolute URL.
    """
    from lxml import html
    from urllib.parse import urljoin
    import re

    tree = html.fromstring(html_content)
    anchors = tree.xpath("//a")
    url_map = {}

    text_pattern = re.compile(
        r'(?i)\b(?:chapter|chap|ch\.?|ep\.?|episode)\s*(\d+(?:\.\d+)?)'
    )
    href_pattern = re.compile(r'(?i)chapter[-_](\d+(?:\.\d+)?)')
    number_pattern = re.compile(r'^\s*(\d+(?:\.\d+)?)\s*$')

    for anchor in anchors:
        href = anchor.get("href")
        if not href:
            continue
        text = "".join(anchor.itertext()).strip()

        chap_num = None

        text_match = text_pattern.search(text)
        if text_match:
            try:
                val = float(text_match.group(1))
                chap_num = int(val) if val.is_integer() else val
            except ValueError:
                pass

        if chap_num is None:
            href_match = href_pattern.search(href)
            if href_match:
                try:
                    val = float(href_match.group(1))
                    chap_num = int(val) if val.is_integer() else val
                except ValueError:
                    pass

        if chap_num is None:
            num_match = number_pattern.search(text)
            if num_match:
                try:
                    val = float(num_match.group(1))
                    chap_num = int(val) if val.is_integer() else val
                except ValueError:
                    pass

        if chap_num is not None:
            absolute_url = urljoin(landing_page_url, href)
            url_map[chap_num] = absolute_url

    return url_map


def run_orchestrator(
    start: Optional[int],
    end: Optional[int],
    delay: float,
    cache_dir: str,
    output: str,
    update_pdf: Optional[str] = None,
    update_epub: Optional[str] = None,
    cover: Optional[str] = None,
    format: str = "both",
    threads: int = 4,
    url: Optional[str] = None,
    update: Optional[str] = None,
) -> None:
    """Orchestrates novel scraping and PDF/EPUB compilation.

    Args:
        start (int): Start chapter number.
        end (int): End chapter number.
        delay (float): Politeness delay in seconds.
        cache_dir (str): Cache directory for HTML files.
        output (str): Filename for compiled PDF/EPUB output.
        update_pdf (str, optional): Path to existing PDF to update.
        update_epub (str, optional): Path to existing EPUB to update.
        cover (str, optional): Optional path or URL to the cover image.
        format (str): Compilation format ('pdf', 'epub', 'both').
        threads (int): Number of concurrent scraper threads.
        url (str, optional): Landing page URL for chapter auto-detection.
        update (str, optional): Path to existing PDF/EPUB file to update.
    """
    if update:
        output = update
        _, ext = os.path.splitext(update)
        if ext.lower() == ".epub":
            update_epub = update
            format = "epub"
            if not url:
                url = extract_source_url_from_epub(update)
        elif ext.lower() == ".pdf":
            update_pdf = update
            format = "pdf"
            if not url:
                url = extract_source_url_from_pdf(update)
        if not url:
            raise ValueError(
                f"No landing page URL found in metadata of the file {update}. "
                "Please provide the landing page URL manually via --url."
            )

    logger.info(f"Starting orchestration flow: chapters {start} to {end}")
    logger.info(
        f"Parameters: delay={delay}s, cache_dir='{cache_dir}', "
        f"output='{output}', update_pdf='{update_pdf}', "
        f"update_epub='{update_epub}', cover='{cover}', "
        f"format='{format}', threads={threads}, url='{url}', update='{update}'"
    )

    url_map = None
    if url:
        logger.info(f"Auto-detecting chapter links from landing page: {url}")
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        try:
            import requests
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            url_map = extract_chapters_from_landing_page(response.text, url)
            if not url_map:
                raise ValueError(
                    f"No chapter links could be auto-detected from: {url}"
                )
            logger.info(
                f"Extracted {len(url_map)} chapter links from landing page."
            )
        except Exception as e:
            logger.error(f"Failed to fetch or parse landing page: {str(e)}")
            raise

    cache_manager = CachingManager(cache_dir=cache_dir)
    scraper = NovelScraper(
        cache_manager=cache_manager,
        delay=delay,
        url_map=url_map,
    )
    if url:
        scraper.base_url = url
    parser = XPathParser()
    sanitizer = ContentSanitizer()

    # Determine output paths
    base, ext = os.path.splitext(output)
    if ext.lower() == ".pdf":
        pdf_output = output
        epub_output = base + ".epub"
    elif ext.lower() == ".epub":
        pdf_output = base + ".pdf"
        epub_output = output
    else:
        pdf_output = output + ".pdf"
        epub_output = output + ".epub"

    existing_chapters = set()
    extracted_epub_chapters = {}

    if update_pdf and (format == "pdf" or format == "both"):
        logger.info(f"Scanning outline of existing PDF: {update_pdf}")
        outline = parse_pdf_outline(update_pdf)
        for chap in outline:
            if chap.get("number") is not None:
                existing_chapters.add(chap["number"])
        logger.info(
            f"Found existing chapters in PDF: "
            f"{sorted(list(existing_chapters))}"
        )

    # Extract chapters from existing EPUB if requested
    if update_epub and (format == "epub" or format == "both"):
        if os.path.exists(update_epub):
            logger.info(
                f"Extracting chapters from existing EPUB: {update_epub}"
            )
            try:
                raw_extracted = extract_chapters_from_epub(update_epub)
                for chap in raw_extracted:
                    num = extract_chapter_number(chap["title"])
                    if num is not None:
                        extracted_epub_chapters[num] = chap
                        existing_chapters.add(num)
            except Exception as e:
                logger.warning(
                    "Failed to extract chapters from existing EPUB: "
                    f"{str(e)}"
                )
        else:
            logger.warning(f"Existing EPUB file not found: {update_epub}")

    # Resolve cover image
    cover_path = resolve_cover(cover, scraper.base_url, cache_dir)

    # Determine the range of chapter numbers to compile
    if url_map is not None:
        if start is None:
            if existing_chapters:
                start = min(existing_chapters)
            else:
                start = min(url_map.keys())
        if end is None:
            end = max(url_map.keys())
        target_chapters = {
            chap for chap in url_map.keys() if start <= chap <= end
        }
    else:
        target_chapters = set(range(start, end + 1))

    if update:
        missing_chapters = target_chapters - existing_chapters
        if not missing_chapters and os.path.exists(update):
            logger.info(
                "No new chapters found. "
                "The file is already up to date."
            )
            return

    # Combine existing and new chapters, then sort sequentially
    all_chap_nums = sorted(list(target_chapters | existing_chapters))
    logger.info(f"Combined chapter range to compile: {all_chap_nums}")

    # Helper function to fetch, parse, and sanitize a single chapter
    def process_chapter(chap_num: int) -> dict:
        if chap_num in extracted_epub_chapters:
            logger.info(f"Using extracted EPUB data for chapter {chap_num}")
            return extracted_epub_chapters[chap_num]

        logger.info(f"Processing chapter {chap_num}")
        # Step 1: Download & Cache
        html_content = scraper.fetch_chapter_html(chap_num)
        # Step 2: Parse
        title, raw_body = parser.parse(html_content)
        # Step 3: Sanitize
        paragraphs = sanitizer.sanitize(raw_body)
        return {"title": title, "paragraphs": paragraphs}

    # Thread-safe mapping of chapters with concurrency control
    from concurrent.futures import ThreadPoolExecutor, as_completed

    chapters_data_map = {}
    total_chapters = len(all_chap_nums)

    # Wrap the chapter iteration in a tqdm progress bar
    pbar = tqdm(all_chap_nums, desc="Compiling Novel")
    has_update = hasattr(pbar, "update")
    has_close = hasattr(pbar, "close")

    if threads > 1 and total_chapters > 0:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            # Submit all tasks
            future_to_chap = {
                executor.submit(process_chapter, chap_num): chap_num
                for chap_num in all_chap_nums
            }
            
            try:
                for future in as_completed(future_to_chap):
                    chap_num = future_to_chap[future]
                    # This raises any exception encountered during execution
                    result = future.result()
                    chapters_data_map[chap_num] = result
                    # Update progress bar manually or iterate over it.
                    if has_update:
                        pbar.update(1)
            except Exception as e:
                logger.error(
                    f"Error in multi-threaded scraping: {str(e)}",
                    exc_info=True,
                )
                # Shutdown executor immediately and cancel pending futures
                executor.shutdown(wait=False, cancel_futures=True)
                if has_close:
                    pbar.close()
                raise
        if has_close:
            pbar.close()
    else:
        # Sequential execution (fallback or when threads=1)
        for chap_num in pbar:
            try:
                result = process_chapter(chap_num)
                chapters_data_map[chap_num] = result
            except Exception as e:
                logger.error(
                    f"Error processing chapter {chap_num}: {str(e)}",
                    exc_info=True,
                )
                if has_close:
                    pbar.close()
                raise

    # Reconstruct chapters list in sorted order
    chapters_data = [chapters_data_map[chap_num] for chap_num in all_chap_nums]

    # Step 4: Compile output
    logger.info(
        "All chapters successfully downloaded, parsed, and sanitized. "
        "Compiling output..."
    )

    novel_title = derive_novel_title(scraper.base_url)

    if format in ("pdf", "both"):
        try:
            compiler = PDFCompiler(output_path=pdf_output)
            compiler.title = novel_title
            compiler.compile(
                chapters_data,
                cover_path=cover_path,
                source_url=scraper.base_url
            )
            logger.info(
                f"PDF compilation completed successfully. "
                f"Saved to {pdf_output}"
            )
        except Exception as e:
            logger.error(f"Failed to compile PDF: {str(e)}", exc_info=True)
            raise

    if format in ("epub", "both"):
        try:
            compiler = EPUBCompiler(output_path=epub_output)
            compiler.title = novel_title
            compiler.compile(
                chapters_data,
                cover_path=cover_path,
                source_url=scraper.base_url
            )
            logger.info(
                f"EPUB compilation completed successfully. "
                f"Saved to {epub_output}"
            )
        except Exception as e:
            logger.error(f"Failed to compile EPUB: {str(e)}", exc_info=True)
            raise

