"""Pytest configuration and fixtures."""

import sys
from pathlib import Path

# Add tests directory to Python path
tests_dir = Path(__file__).parent
sys.path.insert(0, str(tests_dir))
