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
from src.pdf_reader import parse_pdf_outline

# Retrieve the same logger configured in scraper.py
logger = logging.getLogger("novel_scraper")


def run_orchestrator(
    start: int,
    end: int,
    delay: float,
    cache_dir: str,
    output: str,
    update_pdf: Optional[str] = None,
) -> None:
    """Orchestrates novel scraping and PDF compilation.

    Args:
        start (int): Start chapter number.
        end (int): End chapter number.
        delay (float): Politeness delay in seconds.
        cache_dir (str): Cache directory for HTML files.
        output (str): Filename for compiled PDF output.
        update_pdf (str, optional): Path to existing PDF to update.
    """
    logger.info(f"Starting orchestration flow: chapters {start} to {end}")
    logger.info(
        f"Parameters: delay={delay}s, cache_dir='{cache_dir}', "
        f"output='{output}', update_pdf='{update_pdf}'"
    )

    cache_manager = CachingManager(cache_dir=cache_dir)
    scraper = NovelScraper(cache_manager=cache_manager, delay=delay)
    parser = XPathParser()
    sanitizer = ContentSanitizer()
    compiler = PDFCompiler(output_path=output)

    # Determine the range of chapter numbers to compile
    target_chapters = set(range(start, end + 1))
    existing_chapters = set()

    if update_pdf:
        logger.info(f"Scanning outline of existing PDF: {update_pdf}")
        outline = parse_pdf_outline(update_pdf)
        for chap in outline:
            if chap.get("number") is not None:
                existing_chapters.add(chap["number"])
        logger.info(f"Found existing chapters in PDF: {sorted(list(existing_chapters))}")

    # Combine existing and new chapters, then sort sequentially
    all_chap_nums = sorted(list(target_chapters | existing_chapters))
    logger.info(f"Combined chapter range to compile: {all_chap_nums}")

    chapters_data = []

    # Wrap the chapter iteration in a tqdm progress bar
    for chap_num in tqdm(all_chap_nums, desc="Compiling Novel"):
        logger.info(f"Processing chapter {chap_num}")
        try:
            # Step 1: Download & Cache
            html_content = scraper.fetch_chapter_html(chap_num)

            # Step 2: Parse
            title, raw_body = parser.parse(html_content)

            # Step 3: Sanitize
            paragraphs = sanitizer.sanitize(raw_body)

            # Save processed data
            chapters_data.append({"title": title, "paragraphs": paragraphs})

        except Exception as e:
            logger.error(
                f"Error processing chapter {chap_num}: {str(e)}",
                exc_info=True,
            )
            # Re-raise the exception to abort the execution cleanly
            raise

    # Step 4: Compile PDF
    logger.info(
        "All chapters successfully downloaded, parsed, and sanitized. "
        "Compiling PDF..."
    )
    try:
        compiler.compile(chapters_data)
        logger.info(
            f"PDF compilation completed successfully. Saved to {output}"
        )
    except Exception as e:
        logger.error(f"Failed to compile PDF: {str(e)}", exc_info=True)
        raise
