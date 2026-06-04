from unittest.mock import patch
from src.tui import run_tui

def test_run_tui_stub():
    with patch('builtins.print') as mock_print:
        run_tui()
        mock_print.assert_called_once_with("TUI is not fully implemented yet.")
