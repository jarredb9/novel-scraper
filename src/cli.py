import argparse
from typing import List, Optional

def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments for the novel scraper.

    Args:
        args: List of command line arguments to parse. If None, sys.argv is used.

    Returns:
        argparse.Namespace: The parsed arguments with properties start, end, delay, cache_dir, output.
    """
    parser = argparse.ArgumentParser(
        description="Scrape chapters of a web novel and compile them into a PDF."
    )
    parser.add_argument(
        "--start",
        type=int,
        default=776,
        help="Chapter number to start scraping from (default: 776)"
    )
    parser.add_argument(
        "--end",
        type=int,
        default=1780,
        help="Chapter number to end scraping at (default: 1780)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay in seconds between successive network requests (default: 1.0)"
    )
    parser.add_argument(
        "--cache-dir",
        type=str,
        default="./cache",
        help="Directory to cache the downloaded chapter HTML files (default: ./cache)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="novel.pdf",
        help="Filename of the compiled output PDF (default: novel.pdf)"
    )
    return parser.parse_args(args)
