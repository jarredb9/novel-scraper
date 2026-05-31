"""Command-line interface argument parser for the novel scraper.

This module parses command-line arguments to customize the scraper's range,
delay, cache directory, and output filename.
"""

import argparse
from typing import List, Optional


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments for the novel scraper.

    Args:
        args: List of command line arguments to parse. If None, sys.argv is
          used.

    Returns:
        argparse.Namespace: The parsed arguments with properties start, end,
          delay, cache_dir, output.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Scrape chapters of a web novel and compile them into a PDF."
        )
    )
    parser.add_argument(
        "--start",
        type=int,
        default=776,
        help="Chapter number to start scraping from (default: 776)",
    )
    parser.add_argument(
        "--end",
        type=int,
        default=1780,
        help="Chapter number to end scraping at (default: 1780)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help=(
            "Delay in seconds between successive network requests "
            "(default: 1.0)"
        ),
    )
    parser.add_argument(
        "--cache-dir",
        type=str,
        default="./cache",
        help=(
            "Directory to cache the downloaded chapter HTML files "
            "(default: ./cache)"
        ),
    )
    parser.add_argument(
        "--output",
        type=str,
        default="novel.pdf",
        help="Filename of the compiled output PDF (default: novel.pdf)",
    )
    parser.add_argument(
        "--update-pdf",
        "--merge-pdf",
        type=str,
        default=None,
        help="Path to an existing compiled PDF to update with new chapters",
    )
    parser.add_argument(
        "--update-epub",
        "--merge-epub",
        dest="update_epub",
        type=str,
        default=None,
        help="Path to an existing compiled EPUB to update with new chapters",
    )
    parser.add_argument(
        "--cover",
        type=str,
        default=None,
        help="Optional path or URL to the cover image (default: None)",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["pdf", "epub", "both"],
        default="both",
        help="Output compilation format: pdf, epub, or both (default: both)",
    )
    return parser.parse_args(args)
