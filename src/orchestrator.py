import logging
from tqdm import tqdm
from src.cache import CachingManager
from src.scraper import NovelScraper
from src.parser import XPathParser
from src.sanitizer import ContentSanitizer
from src.pdf_compiler import PDFCompiler

# Retrieve the same logger configured in scraper.py
logger = logging.getLogger("novel_scraper")

def run_orchestrator(start: int, end: int, delay: float, cache_dir: str, output: str) -> None:
    """Orchestrates the caching, scraping, parsing, sanitizing, and compiling of novel chapters.

    Args:
        start (int): Start chapter number.
        end (int): End chapter number.
        delay (float): Politeness delay in seconds between network requests.
        cache_dir (str): Cache directory for HTML files.
        output (str): Filename for the compiled PDF output.
    """
    logger.info(f"Starting orchestration flow: chapters {start} to {end}")
    logger.info(f"Parameters: delay={delay}s, cache_dir='{cache_dir}', output='{output}'")

    cache_manager = CachingManager(cache_dir=cache_dir)
    scraper = NovelScraper(cache_manager=cache_manager, delay=delay)
    parser = XPathParser()
    sanitizer = ContentSanitizer()
    compiler = PDFCompiler(output_path=output)

    chapters_data = []

    # Wrap the chapter iteration in a tqdm progress bar
    for chap_num in tqdm(range(start, end + 1), desc="Compiling Novel"):
        logger.info(f"Processing chapter {chap_num}")
        try:
            # Step 1: Download & Cache
            html_content = scraper.fetch_chapter_html(chap_num)
            
            # Step 2: Parse
            title, raw_body = parser.parse(html_content)
            
            # Step 3: Sanitize
            paragraphs = sanitizer.sanitize(raw_body)
            
            # Save processed data
            chapters_data.append({
                "title": title,
                "paragraphs": paragraphs
            })
            
        except Exception as e:
            logger.error(f"Error processing chapter {chap_num}: {str(e)}", exc_info=True)
            # We can re-raise or handle it. Based on the flow, we should fail fast or log. Let's raise the exception to let the user know.
            raise

    # Step 4: Compile PDF
    logger.info("All chapters successfully downloaded, parsed, and sanitized. Compiling PDF...")
    try:
        compiler.compile(chapters_data)
        logger.info(f"PDF compilation completed successfully. Saved to {output}")
    except Exception as e:
        logger.error(f"Failed to compile PDF: {str(e)}", exc_info=True)
        raise
