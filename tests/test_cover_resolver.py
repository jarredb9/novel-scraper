import os
import pytest
import requests
from unittest.mock import patch, MagicMock
from src.cover_resolver import resolve_cover, derive_landing_page_url

def test_derive_landing_page_url():
    assert derive_landing_page_url("https://freewebnovel.com/the-first-legendary-beast-master/chapter-") == "https://freewebnovel.com/the-first-legendary-beast-master.html"
    assert derive_landing_page_url("https://freewebnovel.com/novel/") == "https://freewebnovel.com/novel.html"
    assert derive_landing_page_url("https://freewebnovel.com/novel") == "https://freewebnovel.com/novel"

def test_resolve_cover_from_local_file(tmp_path):
    # Setup local file
    local_file = tmp_path / "my_cover.png"
    local_file.write_bytes(b"dummy image data")
    cache_dir = tmp_path / "cache"
    
    # Resolve
    resolved = resolve_cover(str(local_file), "https://freewebnovel.com/novel/chapter-", str(cache_dir))
    
    # Assert
    expected_cache = os.path.join(str(cache_dir), "cover.jpg")
    assert resolved == expected_cache
    assert os.path.exists(expected_cache)
    with open(expected_cache, "rb") as f:
        assert f.read() == b"dummy image data"

@patch("requests.get")
def test_resolve_cover_from_url(mock_get, tmp_path):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"downloaded image data"
    mock_get.return_value = mock_response
    
    cache_dir = tmp_path / "cache"
    
    resolved = resolve_cover("https://example.com/cover.jpg", "https://freewebnovel.com/novel/chapter-", str(cache_dir))
    
    expected_cache = os.path.join(str(cache_dir), "cover.jpg")
    assert resolved == expected_cache
    assert os.path.exists(expected_cache)
    with open(expected_cache, "rb") as f:
        assert f.read() == b"downloaded image data"
    
    mock_get.assert_called_once_with("https://example.com/cover.jpg", timeout=10)

@patch("requests.get")
def test_resolve_cover_auto_scraping(mock_get, tmp_path):
    # Mock landing page response and image response
    landing_page_html = """
    <html>
      <body>
        <div class="m-imgtxt">
          <div class="pic">
            <img src="https://img.freewebnovel.com/novel/cover.jpg" alt="Novel Cover" />
          </div>
        </div>
      </body>
    </html>
    """
    mock_landing_res = MagicMock()
    mock_landing_res.status_code = 200
    mock_landing_res.text = landing_page_html
    
    mock_img_res = MagicMock()
    mock_img_res.status_code = 200
    mock_img_res.content = b"scraped image data"
    
    mock_get.side_effect = [mock_landing_res, mock_img_res]
    
    cache_dir = tmp_path / "cache"
    
    resolved = resolve_cover(None, "https://freewebnovel.com/novel/chapter-", str(cache_dir))
    
    expected_cache = os.path.join(str(cache_dir), "cover.jpg")
    assert resolved == expected_cache
    assert os.path.exists(expected_cache)
    with open(expected_cache, "rb") as f:
        assert f.read() == b"scraped image data"
    
    assert mock_get.call_count == 2
    mock_get.assert_any_call("https://freewebnovel.com/novel.html", timeout=10)
    mock_get.assert_any_call("https://img.freewebnovel.com/novel/cover.jpg", timeout=10)

@patch("requests.get")
def test_resolve_cover_soft_fallback(mock_get, tmp_path):
    # Setup mock to raise exception
    mock_get.side_effect = requests.RequestException("Network error")
    
    cache_dir = tmp_path / "cache"
    
    resolved = resolve_cover(None, "https://freewebnovel.com/novel/chapter-", str(cache_dir))
    
    assert resolved is None
    assert not os.path.exists(os.path.join(str(cache_dir), "cover.jpg"))

def test_resolve_cover_cache_hit(tmp_path):
    cache_dir = tmp_path / "cache"
    os.makedirs(cache_dir, exist_ok=True)
    cached_file = cache_dir / "cover.jpg"
    cached_file.write_bytes(b"existing cache data")
    
    # We pass a URL but it should hit cache and NOT call requests.get
    with patch("requests.get") as mock_get:
        resolved = resolve_cover("https://example.com/cover.jpg", "https://freewebnovel.com/novel/chapter-", str(cache_dir))
        assert resolved == str(cached_file)
        mock_get.assert_not_called()
