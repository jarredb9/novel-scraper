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
        assert args[0] == f"https://freewebnovel.com/the-first-legendary-beast-master/chapter-{chapter_num}.html"
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
    scraper = NovelScraper(cache_manager=mock_cache, base_url="https://freewebnovel.com/the-first-legendary-beast-master/", delay=0.0)
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "content"
        mock_get.return_value = mock_response
        
        scraper.fetch_chapter_html(776)
        
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert args[0] == "https://freewebnovel.com/the-first-legendary-beast-master/chapter-776.html"


def test_scraper_exponential_backoff_on_429(mock_cache):
    chapter_num = 777
    scraper = NovelScraper(cache_manager=mock_cache, delay=0.0, retries=2)
    
    with patch("requests.get") as mock_get, patch("time.sleep") as mock_sleep:
        # Mock a response that triggers raise_for_status to throw an HTTPError
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            "Too Many Requests", response=mock_response
        )
        mock_get.return_value = mock_response
        
        with pytest.raises(requests.RequestException):
            scraper.fetch_chapter_html(chapter_num)
            
        assert mock_get.call_count == 2
        # Ensure sleep was called with backoff delays (e.g. 5.0s on first attempt)
        assert mock_sleep.call_count == 1
        # Verify the backoff sleep values: attempt 1 -> 5.0
        sleep_args = [call[0][0] for call in mock_sleep.call_args_list]
        assert 5.0 in sleep_args


def test_scraper_thread_safety(mock_cache):
    import threading
    scraper = NovelScraper(cache_manager=mock_cache, delay=0.2)
    
    call_times = []
    
    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "content"
        mock_get.return_value = mock_resp
        
        def worker(ch):
            scraper.fetch_chapter_html(ch)
            call_times.append(time.time())

        # Use non-cached chapters to force requests.get
        threads = [threading.Thread(target=worker, args=(ch,)) for ch in [900, 901, 902]]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            
    call_times.sort()
    # There are 3 calls, each should be separated by at least 0.2 seconds delay
    diffs = [call_times[i+1] - call_times[i] for i in range(len(call_times)-1)]
    for diff in diffs:
        assert diff >= 0.18  # Allow tiny floating-point/thread scheduling tolerance




