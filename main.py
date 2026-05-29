import sys
import logging
from src.cli import parse_args
from src.orchestrator import run_orchestrator

def main():
    # Configure root logger with minimal level for stdout, so verbose logs are written to scraper.log only
    logging.basicConfig(level=logging.WARNING)
    
    args = parse_args(sys.argv[1:])
    try:
        run_orchestrator(
            start=args.start,
            end=args.end,
            delay=args.delay,
            cache_dir=args.cache_dir,
            output=args.output
        )
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
