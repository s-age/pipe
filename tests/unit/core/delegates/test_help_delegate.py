"""Unit tests for help_delegate."""

import argparse
from unittest.mock import MagicMock

from pipe.core.delegates import help_delegate


class TestHelpDelegate:
    """Tests for help_delegate.run function."""

    def test_run_calls_print_help(self):
        """Test that run() calls print_help() on the provided parser."""
        # Setup
        mock_parser = MagicMock(spec=argparse.ArgumentParser)

        # Execute
        help_delegate.run(mock_parser)

        # Verify
        mock_parser.print_help.assert_called_once()
