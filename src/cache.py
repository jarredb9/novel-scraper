import os
from pathlib import Path
from typing import Optional

class CachingManager:
    """Manages local HTML caching for the novel scraper to support resume-friendly behavior."""
    
    def __init__(self, cache_dir: str = "./cache"):
        """Initializes the caching manager and ensures the cache directory exists.
        
        Args:
            cache_dir (str): Path to the cache directory.
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_chapter_path(self, chapter_num: int) -> Path:
        """Returns the file path for a cached chapter.
        
        Args:
            chapter_num (int): The chapter number.
            
        Returns:
            Path: The path to the cached HTML file.
        """
        return self.cache_dir / f"chapter_{chapter_num}.html"
        
    def is_cached(self, chapter_num: int) -> bool:
        """Checks if a chapter is cached locally.
        
        Args:
            chapter_num (int): The chapter number.
            
        Returns:
            bool: True if the chapter HTML is cached, False otherwise.
        """
        return self._get_chapter_path(chapter_num).exists()
        
    def read_chapter(self, chapter_num: int) -> Optional[str]:
        """Reads a cached chapter's HTML content.
        
        Args:
            chapter_num (int): The chapter number.
            
        Returns:
            Optional[str]: The HTML content if cached, or None if not.
        """
        path = self._get_chapter_path(chapter_num)
        if path.exists():
            return path.read_text(encoding="utf-8")
        return None
        
    def save_chapter(self, chapter_num: int, content: str) -> None:
        """Saves a chapter's HTML content to the local cache.
        
        Args:
            chapter_num (int): The chapter number.
            content (str): The HTML content of the chapter.
        """
        path = self._get_chapter_path(chapter_num)
        path.write_text(content, encoding="utf-8")
