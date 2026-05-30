import pytest
from src.cli import parse_args

def test_cli_default_args():
    # If no arguments are passed, we should get default values
    args = parse_args([])
    assert args.start == 776
    assert args.end == 1780
    assert args.delay == 1.0
    assert args.cache_dir == "./cache"
    assert args.output == "novel.pdf"

def test_cli_custom_args():
    # Test passing custom arguments for all options
    args = parse_args([
        "--start", "800",
        "--end", "900",
        "--delay", "2.5",
        "--cache-dir", "./test_cache_dir",
        "--output", "test_novel.pdf"
    ])
    assert args.start == 800
    assert args.end == 900
    assert args.delay == 2.5
    assert args.cache_dir == "./test_cache_dir"
    assert args.output == "test_novel.pdf"

def test_cli_invalid_start_type():
    # start should be an integer
    with pytest.raises(SystemExit):
        parse_args(["--start", "not-an-int"])

def test_cli_invalid_end_type():
    # end should be an integer
    with pytest.raises(SystemExit):
        parse_args(["--end", "not-an-int"])

def test_cli_invalid_delay_type():
    # delay should be a float
    with pytest.raises(SystemExit):
        parse_args(["--delay", "not-a-float"])

def test_cli_format_default():
    args = parse_args([])
    assert args.format == "both"

def test_cli_format_choices():
    for fmt in ["pdf", "epub", "both"]:
        args = parse_args(["--format", fmt])
        assert args.format == fmt

def test_cli_format_invalid():
    with pytest.raises(SystemExit):
        parse_args(["--format", "mobi"])

