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

def test_cli_cover_default():
    args = parse_args([])
    assert args.cover is None

def test_cli_cover_custom():
    args = parse_args(["--cover", "https://example.com/cover.jpg"])
    assert args.cover == "https://example.com/cover.jpg"
    args2 = parse_args(["--cover", "./local_cover.png"])
    assert args2.cover == "./local_cover.png"

def test_cli_update_default():
    args = parse_args([])
    assert args.update is None

def test_cli_update_custom():
    args = parse_args(["--update", "existing.epub"])
    assert args.update == "existing.epub"



def test_cli_threads_default():
    args = parse_args([])
    assert args.threads == 4


def test_cli_threads_custom():
    args = parse_args(["--threads", "8"])
    assert args.threads == 8
    args_short = parse_args(["-t", "2"])
    assert args_short.threads == 2


def test_cli_threads_invalid():
    with pytest.raises(SystemExit):
        parse_args(["--threads", "not-an-int"])


def test_cli_ad_pattern_single():
    args = parse_args(["--ad-pattern", "pattern1"])
    assert args.ad_pattern == ["pattern1"]


def test_cli_ad_pattern_multiple():
    args = parse_args(["--ad-pattern", "pattern1", "--ad-pattern", "pattern2"])
    assert args.ad_pattern == ["pattern1", "pattern2"]


def test_cli_ad_pattern_comma_separated():
    args = parse_args(["--ad-pattern", "pattern1,pattern2, pattern3"])
    assert args.ad_pattern == ["pattern1", "pattern2", "pattern3"]


def test_cli_ad_pattern_default():
    args = parse_args([])
    assert args.ad_pattern is None



