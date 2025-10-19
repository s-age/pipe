import unittest
import tempfile
import shutil
import os
from src.history_manager import HistoryManager

class TestHistoryManager(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory for testing."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.test_dir)

    def test_initialization(self):
        """Test that the history directory and index file are created."""
        hm = HistoryManager(self.test_dir)
        self.assertTrue(os.path.exists(hm.sessions_dir))
        self.assertTrue(os.path.exists(hm.index_path))

if __name__ == '__main__':
    unittest.main()
