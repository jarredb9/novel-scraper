from unittest.mock import patch
from src.tui import run_tui

def test_run_tui():
    """Verify that run_tui instantiates and runs the ScraperApp."""
    with patch('src.tui.ScraperApp.run') as mock_run:
        run_tui()
        mock_run.assert_called_once()
