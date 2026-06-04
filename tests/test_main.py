import sys
from unittest.mock import patch, MagicMock
import pytest
from main import main

def test_main_execution():
    with patch('main.parse_args') as mock_parse_args, \
         patch('main.run_orchestrator') as mock_run_orchestrator:
        
        mock_args = MagicMock()
        mock_args.start = 776
        mock_args.end = 778
        mock_args.delay = 1.0
        mock_args.cache_dir = "./cache"
        mock_args.output = "novel.pdf"
        mock_args.cover = None
        mock_args.format = "both"
        mock_args.threads = 4
        mock_args.url = None
        mock_args.update = None
        mock_args.ad_pattern = None
        mock_args.tui = False
        mock_parse_args.return_value = mock_args

        # Mock sys.argv
        with patch.object(sys, 'argv', ['main.py']):
            main()

        mock_parse_args.assert_called_once_with([])
        mock_run_orchestrator.assert_called_once_with(
            start=776,
            end=778,
            delay=1.0,
            cache_dir="./cache",
            output="novel.pdf",
            update=None,
            cover=None,
            format="both",
            threads=4,
            url=None,
            ad_patterns=None,
        )

def test_main_execution_error():
    with patch('main.parse_args') as mock_parse_args, \
         patch('main.run_orchestrator') as mock_run_orchestrator:
        
        mock_args = MagicMock()
        mock_args.cover = None
        mock_args.update = None
        mock_args.tui = False
        mock_parse_args.return_value = mock_args
        mock_run_orchestrator.side_effect = Exception("Orchestrator failed")

        with patch.object(sys, 'argv', ['main.py']), \
             pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1


def test_main_tui_routing():
    with patch('main.parse_args') as mock_parse_args, \
         patch('src.tui.run_tui') as mock_run_tui, \
         patch('main.run_orchestrator') as mock_run_orchestrator:
        
        mock_args = MagicMock()
        mock_args.tui = True
        mock_parse_args.return_value = mock_args

        with patch.object(sys, 'argv', ['main.py']):
            main()

        mock_run_tui.assert_called_once()
        mock_run_orchestrator.assert_not_called()

