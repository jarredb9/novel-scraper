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
from src.pdf_reader import parse_pdf_outline, extract_chapter_number
from src.epub_compiler import EPUBCompiler
from src.cover_resolver import resolve_cover
from src.epub_extractor import extract_chapters_from_epub
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


def run_orchestrator(
    start: int,
    end: int,
    delay: float,
    cache_dir: str,
    output: str,
    update_pdf: Optional[str] = None,
    update_epub: Optional[str] = None,
    cover: Optional[str] = None,
    format: str = "both",
    threads: int = 4,
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
    """
    logger.info(f"Starting orchestration flow: chapters {start} to {end}")
    logger.info(
        f"Parameters: delay={delay}s, cache_dir='{cache_dir}', "
        f"output='{output}', update_pdf='{update_pdf}', "
        f"update_epub='{update_epub}', cover='{cover}', "
        f"format='{format}', threads={threads}"
    )

    cache_manager = CachingManager(cache_dir=cache_dir)
    scraper = NovelScraper(cache_manager=cache_manager, delay=delay)
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

    # Determine the range of chapter numbers to compile
    target_chapters = set(range(start, end + 1))
    existing_chapters = set()

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

    # Resolve cover image
    cover_path = resolve_cover(cover, scraper.base_url, cache_dir)

    # Extract chapters from existing EPUB if requested
    extracted_epub_chapters = {}
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
            if cover_path is not None:
                compiler.compile(chapters_data, cover_path=cover_path)
            else:
                compiler.compile(chapters_data)
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
            if cover_path is not None:
                compiler.compile(chapters_data, cover_path=cover_path)
            else:
                compiler.compile(chapters_data)
            logger.info(
                f"EPUB compilation completed successfully. "
                f"Saved to {epub_output}"
            )
        except Exception as e:
            logger.error(f"Failed to compile EPUB: {str(e)}", exc_info=True)
            raise

