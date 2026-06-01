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
        ),
        allow_abbrev=False,
    )
    parser.add_argument(
        "--start",
        type=int,
        default=None,
        help="Chapter number to start scraping from (default: 776)",
    )
    parser.add_argument(
        "--end",
        type=int,
        default=None,
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
        "--update",
        type=str,
        default=None,
        help=(
            "Path to an existing compiled PDF/EPUB to "
            "update with new chapters automatically"
        ),
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
    parser.add_argument(
        "--threads",
        "-t",
        type=int,
        default=4,
        help="Number of concurrent scraper threads (default: 4)",
    )
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="Landing page URL of the novel for chapter link auto-detection",
    )
    parser.add_argument(
        "--ad-pattern",
        action="append",
        default=None,
        help="Custom ad regex pattern to filter out (can be specified multiple times or comma-separated)",
    )
    parsed_args = parser.parse_args(args)

    # Post-process ad patterns: split comma-separated entries and clean whitespace
    ad_patterns = []
    if getattr(parsed_args, "ad_pattern", None):
        for item in parsed_args.ad_pattern:
            for p in item.split(","):
                p_stripped = p.strip()
                if p_stripped:
                    ad_patterns.append(p_stripped)
    parsed_args.ad_pattern = ad_patterns if ad_patterns else None

    if parsed_args.url is None and parsed_args.update is None:
        if parsed_args.start is None:
            parsed_args.start = 776
        if parsed_args.end is None:
            parsed_args.end = 1780
    return parsed_args
