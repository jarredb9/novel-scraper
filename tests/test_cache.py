import pytest
from pathlib import Path
from src.cache import CachingManager

def test_cache_dir_creation(tmp_path):
    cache_dir = tmp_path / "cache"
    assert not cache_dir.exists()
    
    manager = CachingManager(cache_dir=str(cache_dir))
    assert cache_dir.exists()
    assert cache_dir.is_dir()

def test_cache_miss(tmp_path):
    manager = CachingManager(cache_dir=str(tmp_path))
    assert not manager.is_cached(776)
    assert manager.read_chapter(776) is None

def test_cache_save_and_hit(tmp_path):
    manager = CachingManager(cache_dir=str(tmp_path))
    chapter_num = 776
    content = "<html><body>Chapter Content</body></html>"
    
    manager.save_chapter(chapter_num, content)
    
    assert manager.is_cached(chapter_num)
    assert manager.read_chapter(chapter_num) == content
    
    # Check physical file
    expected_file = tmp_path / f"chapter_{chapter_num}.html"
    assert expected_file.exists()
    assert expected_file.read_text(encoding="utf-8") == content
