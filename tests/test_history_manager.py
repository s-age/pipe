import unittest
import tempfile
import shutil
from pathlib import Path
from src.history_manager import HistoryManager

class TestHistoryManager(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory for testing."""
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.test_dir)

    def test_initialization(self):
        """Test that the history directory and index file are created."""
        hm = HistoryManager(self.test_dir)
        self.assertTrue(hm.history_dir.exists())
        self.assertTrue(hm.objects_dir.exists())
        self.assertTrue(hm.index_path.exists())

if __name__ == '__main__':
    unittest.main()
