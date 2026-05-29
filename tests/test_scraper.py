import pytest
from unittest.mock import MagicMock, patch
import requests
import time
from src.cache import CachingManager
from src.scraper import NovelScraper

@pytest.fixture
def mock_cache(tmp_path):
    return CachingManager(cache_dir=str(tmp_path))

def test_scraper_cache_hit(mock_cache):
    # Setup cache hit
    chapter_num = 776
    expected_content = "<html>Cached Content</html>"
    mock_cache.save_chapter(chapter_num, expected_content)
    
    scraper = NovelScraper(cache_manager=mock_cache)
    
    with patch("requests.get") as mock_get:
        content = scraper.fetch_chapter_html(chapter_num)
        assert content == expected_content
        # Ensure requests.get was NOT called
        mock_get.assert_not_called()

def test_scraper_cache_miss_success(mock_cache):
    chapter_num = 776
    expected_content = "<html>Network Content</html>"
    
    scraper = NovelScraper(cache_manager=mock_cache, delay=0.0)
    
    with patch("requests.get") as mock_get, patch("time.sleep") as mock_sleep:
        # Mock requests.get response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = expected_content
        mock_get.return_value = mock_response
        
        content = scraper.fetch_chapter_html(chapter_num)
        
        assert content == expected_content
        assert mock_cache.read_chapter(chapter_num) == expected_content
        
        # Verify requests.get was called with headers and timeout
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert args[0] == f"https://freewebnovel.com/novel/the-first-legendary-beast-{chapter_num}.html" # Let's check format. Wait, is it beast-X or beast-X.html? The requirement says: https://freewebnovel.com/novel/the-first-legendary-beast-X or similar. Let's make base URL configurable or just match what's requested. Let's make it match: base_url + str(chapter_num) + ".html" or similar. Wait! Spec says: "Scraping URLs in the format `https://freewebnovel.com/novel/the-first-legendary-beast-X` (where X is 776 to 1780)". But wait, the actual URL on freewebnovel could have .html or not. Let's look at the spec: https://freewebnovel.com/novel/the-first-legendary-beast-X. So we will default to `https://freewebnovel.com/novel/the-first-legendary-beast-{chapter_num}.html`. Let's support both or just append .html. Let's check the spec: "https://freewebnovel.com/novel/the-first-legendary-beast-X". Let's support base url as `https://freewebnovel.com/novel/the-first-legendary-beast-{chapter_num}.html`.
        assert "User-Agent" in kwargs["headers"]
        assert kwargs["timeout"] == 10

def test_scraper_retry_on_failure(mock_cache):
    chapter_num = 777
    scraper = NovelScraper(cache_manager=mock_cache, delay=0.0, retries=2)
    
    with patch("requests.get") as mock_get, patch("time.sleep") as mock_sleep:
        mock_get.side_effect = requests.RequestException("Connection error")
        
        with pytest.raises(requests.RequestException):
            scraper.fetch_chapter_html(chapter_num)
            
        assert mock_get.call_count == 2
        # Ensure sleep was called between retries
        assert mock_sleep.call_count >= 1

def test_scraper_politeness_delay(mock_cache):
    scraper = NovelScraper(cache_manager=mock_cache, delay=1.5)
    chapter_num = 778
    
    with patch("requests.get") as mock_get, patch("time.sleep") as mock_sleep:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "content"
        mock_get.return_value = mock_response
        
        # First request should NOT delay if it's the first time
        scraper.fetch_chapter_html(chapter_num)
        
        # Second request should trigger a sleep of 1.5 seconds
        scraper.fetch_chapter_html(chapter_num + 1)
        
        assert mock_sleep.call_count == 1
        sleep_args = mock_sleep.call_args[0][0]
        assert pytest.approx(sleep_args, abs=0.05) == 1.5

def test_scraper_base_url_format(mock_cache):
    scraper = NovelScraper(cache_manager=mock_cache, base_url="https://freewebnovel.com/novel/", delay=0.0)
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "content"
        mock_get.return_value = mock_response
        
        scraper.fetch_chapter_html(776)
        
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert args[0] == "https://freewebnovel.com/novel/the-first-legendary-beast-776.html"

