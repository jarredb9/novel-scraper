"""Module for resolving, downloading, and caching the novel's cover image.

Supports local file paths, explicit URLs, and automatic scraping from the novel's landing page.
"""

import os
import shutil
import logging
import requests
from urllib.parse import urljoin
from typing import Optional
from lxml import html

logger = logging.getLogger("novel_scraper")


def derive_landing_page_url(base_url: str) -> str:
    """Derive the landing page URL from the scraper's base_url.

    Args:
        base_url (str): The base chapter URL prefix.

    Returns:
        str: Derived landing page URL.
    """
    if "/chapter-" in base_url:
        return base_url.replace("/chapter-", ".html")
    if base_url.endswith("/"):
        return base_url[:-1] + ".html"
    return base_url


def resolve_cover(
    cover_input: Optional[str],
    base_url: str,
    cache_dir: str,
    timeout: int = 10,
) -> Optional[str]:
    """Resolve, download, and cache the novel's cover image.

    Args:
        cover_input (Optional[str]): Path or URL to the cover image.
        base_url (str): Base URL of the novel chapters.
        cache_dir (str): Directory where cached files are stored.
        timeout (int): Network request timeout in seconds.

    Returns:
        Optional[str]: Path to the cached cover image, or None on failure/soft
        fallback.
    """
    os.makedirs(cache_dir, exist_ok=True)
    cached_path = os.path.join(cache_dir, "cover.jpg")

    # If already cached, return it (avoids redownloading)
    if os.path.exists(cached_path):
        logger.info(f"Cover image found in cache: {cached_path}")
        return cached_path

    try:
        # 1. URL cover_input
        if cover_input and (
            cover_input.startswith("http://")
            or cover_input.startswith("https://")
        ):
            logger.info(f"Downloading cover image from URL: {cover_input}")
            response = requests.get(cover_input, timeout=timeout)
            response.raise_for_status()
            with open(cached_path, "wb") as f:
                f.write(response.content)
            return cached_path

        # 2. Local file cover_input
        elif cover_input:
            if os.path.exists(cover_input):
                logger.info(f"Using local cover file: {cover_input}")
                shutil.copy(cover_input, cached_path)
                return cached_path
            else:
                raise FileNotFoundError(
                    f"Local cover file not found: {cover_input}"
                )

        # 3. Scrape cover automatically
        else:
            landing_url = derive_landing_page_url(base_url)
            logger.info(
                f"Scraping cover image from landing page: {landing_url}"
            )
            response = requests.get(landing_url, timeout=timeout)
            response.raise_for_status()

            tree = html.fromstring(response.text)
            xpath_query = '//div[@class="m-imgtxt"]/div[@class="pic"]/img/@src'
            img_srcs = tree.xpath(xpath_query)

            if not img_srcs:
                raise ValueError(
                    f"No cover image found using XPath: {xpath_query}"
                )

            img_url = urljoin(landing_url, img_srcs[0])
            logger.info(
                f"Downloading scraped cover image from: {img_url}"
            )

            img_res = requests.get(img_url, timeout=timeout)
            img_res.raise_for_status()
            with open(cached_path, "wb") as f:
                f.write(img_res.content)
            return cached_path

    except Exception as e:
        logger.warning(f"Failed to resolve cover image: {str(e)}")
        # Soft fallback: log and return None (do not fail compilation)
        if os.path.exists(cached_path):
            try:
                os.remove(cached_path)
            except Exception:
                pass
        return None
