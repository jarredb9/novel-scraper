"""Main entry point for the web novel scraper and PDF compiler.

This module parses command-line arguments and runs the main orchestrator flow.
"""

import sys
import logging
from src.cli import parse_args
from src.orchestrator import run_orchestrator


def main():
    """Main execution function to parse args and run the orchestrator."""
    # Configure root logger with minimal level for stdout, so verbose logs are
    # written to scraper.log only.
    logging.basicConfig(level=logging.WARNING)

    args = parse_args(sys.argv[1:])
    if getattr(args, "tui", False):
        try:
            from src.tui import run_tui
            run_tui()
            return
        except Exception as e:
            print(f"Error launching TUI: {str(e)}", file=sys.stderr)
            sys.exit(1)

    try:
        run_orchestrator(
            start=args.start,
            end=args.end,
            delay=args.delay,
            cache_dir=args.cache_dir,
            output=args.output,
            update=args.update,
            cover=args.cover,
            format=args.format,
            threads=args.threads,
            url=args.url,
            ad_patterns=args.ad_pattern,
        )
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
