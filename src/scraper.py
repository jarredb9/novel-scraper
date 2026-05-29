import time
import logging
import requests
from typing import Dict, Optional
from src.cache import CachingManager

# Set up logging to scraper.log
logger = logging.getLogger("novel_scraper")
logger.setLevel(logging.DEBUG)
# Prevent propagation or duplicate handlers
if not logger.handlers:
    file_handler = logging.FileHandler("scraper.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

class NovelScraper:
    """Scrapes novel chapters from freewebnovel.com with caching and rate limiting."""
    
    def __init__(
        self,
        cache_manager: CachingManager,
        base_url: str = "https://freewebnovel.com/novel/the-first-legendary-beast-",
        delay: float = 1.0,
        timeout: int = 10,
        retries: int = 3,
    ):
        """Initializes the scraper with a caching manager and networking options.
        
        Args:
            cache_manager (CachingManager): Cache manager instance.
            base_url (str): Base URL prefix before chapter number.
            delay (float): Politeness delay in seconds between network requests.
            timeout (int): HTTP request timeout in seconds.
            retries (int): Number of retries on request failure.
        """
        self.cache_manager = cache_manager
        self.base_url = base_url
        self.delay = delay
        self.timeout = timeout
        self.retries = retries
        self.last_request_time: float = 0.0
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

    def _get_url(self, chapter_num: int) -> str:
        """Constructs the chapter URL.
        
        Args:
            chapter_num (int): Chapter number.
            
        Returns:
            str: URL for the chapter.
        """
        # The requirements say: https://freewebnovel.com/novel/the-first-legendary-beast-X.html
        # We append .html to match the pattern or just let the base url guide it.
        if self.base_url.endswith("/"):
            return f"{self.base_url}the-first-legendary-beast-{chapter_num}.html"
        return f"{self.base_url}{chapter_num}.html"

    def fetch_chapter_html(self, chapter_num: int) -> str:
        """Fetches the chapter HTML content, using cache if available.
        
        Args:
            chapter_num (int): Chapter number.
            
        Returns:
            str: Chapter HTML content.
        
        Raises:
            requests.RequestException: If HTTP request fails after all retries.
        """
        # Check cache first
        if self.cache_manager.is_cached(chapter_num):
            logger.info(f"Cache hit for chapter {chapter_num}")
            content = self.cache_manager.read_chapter(chapter_num)
            if content is not None:
                return content

        # Cache miss - perform HTTP request
        url = self._get_url(chapter_num)
        logger.info(f"Cache miss for chapter {chapter_num}. Fetching from {url}")
        
        attempt = 0
        while attempt < self.retries:
            attempt += 1
            
            # Enforce politeness delay
            elapsed = time.time() - self.last_request_time
            if elapsed < self.delay:
                sleep_time = self.delay - elapsed
                logger.debug(f"Sleeping for {sleep_time:.2f}s to respect rate limits")
                time.sleep(sleep_time)

            self.last_request_time = time.time()
            
            try:
                logger.info(f"HTTP GET {url} (Attempt {attempt}/{self.retries})")
                response = requests.get(url, headers=self.headers, timeout=self.timeout)
                logger.info(f"HTTP Status {response.status_code} for {url}")
                
                # Check for bad status code
                response.raise_for_status()
                
                # Save to cache
                self.cache_manager.save_chapter(chapter_num, response.text)
                return response.text
                
            except requests.RequestException as e:
                logger.warning(f"Error fetching chapter {chapter_num} (attempt {attempt}): {str(e)}")
                if attempt == self.retries:
                    logger.error(f"Failed to fetch chapter {chapter_num} after {self.retries} attempts.")
                    raise
                # Short delay before retrying
                time.sleep(1.0)
                
        raise requests.RequestException(f"Failed to fetch chapter {chapter_num}")
