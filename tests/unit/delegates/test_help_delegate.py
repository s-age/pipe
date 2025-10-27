import argparse
import unittest
from unittest.mock import MagicMock

from pipe.core.delegates import help_delegate


class TestHelpDelegate(unittest.TestCase):
    def test_run_calls_print_help(self):
        """Tests that the help_delegate correctly calls parser.print_help."""
        mock_parser = MagicMock(spec=argparse.ArgumentParser)

        help_delegate.run(mock_parser)

        mock_parser.print_help.assert_called_once()


if __name__ == "__main__":
    unittest.main()
