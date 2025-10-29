import json
import os
import tempfile
import unittest
from io import StringIO
from unittest.mock import patch

from pipe.core.collections.sessions import SessionCollection


class TestSessionCollection(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.index_path = os.path.join(self.temp_dir.name, "index.json")
        self.timezone_name = "UTC"

        # Initial data for some tests
        self.initial_data = {
            "sessions": {
                "session1": {
                    "purpose": "Test session 1",
                    "created_at": "2025-01-01T00:00:00Z",
                    "last_updated": "2025-01-01T01:00:00Z",
                },
                "session1/child1": {
                    "purpose": "Child session",
                    "created_at": "2025-01-02T00:00:00Z",
                    "last_updated": "2025-01-02T01:00:00Z",
                },
            }
        }
        with open(self.index_path, "w") as f:
            json.dump(self.initial_data, f)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initial_load_and_find(self):
        """Tests that the collection correctly loads data from an existing index
        file."""
        collection = SessionCollection(self.initial_data, self.timezone_name)
        session_meta = collection.find("session1")
        self.assertIsNotNone(session_meta)
        self.assertEqual(session_meta["purpose"], "Test session 1")
        self.assertEqual(len(collection), 2)

    def test_delete_nonexistent_session(self):
        """Tests that attempting to delete a non-existent session fails gracefully."""
        collection = SessionCollection(self.initial_data, self.timezone_name)
        result = collection.delete("nonexistent")
        self.assertFalse(result)

        # Ensure data is not changed by the failed operation
        self.assertEqual(collection._index_data, self.initial_data)

    def test_invalid_timezone_falls_back_to_utc(self):
        """Tests that an invalid timezone name results in a fallback to UTC and a
        warning."""
        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            collection = SessionCollection(self.initial_data, "Invalid/Timezone")
            self.assertEqual(collection.timezone_obj.key, "UTC")
            self.assertEqual(
                mock_stderr.getvalue(),
                "Warning: Timezone 'Invalid/Timezone' not found. Using UTC.\n",
            )

    def test_get_sorted_by_last_updated_empty(self):
        """Tests that get_sorted_by_last_updated returns an empty list when there are
        no sessions."""
        collection = SessionCollection({"sessions": {}}, self.timezone_name)
        sorted_sessions = collection.get_sorted_by_last_updated()
        self.assertEqual(sorted_sessions, [])

    def test_iterator(self):
        """Tests that the iterator yields the correct session IDs."""
        collection = SessionCollection(self.initial_data, self.timezone_name)
        session_ids = list(collection)
        self.assertEqual(len(session_ids), 2)
        self.assertIn("session1", session_ids)
        self.assertIn("session1/child1", session_ids)

    def test_find_nonexistent(self):
        """Tests that find returns None for a non-existent session."""
        collection = SessionCollection(self.initial_data, self.timezone_name)
        self.assertIsNone(collection.find("nonexistent"))

    def test_len_with_no_sessions_key(self):
        """Tests that __len__ returns 0 if 'sessions' key is missing."""
        collection = SessionCollection({}, self.timezone_name)
        self.assertEqual(len(collection), 0)

    def test_find_with_no_sessions_key(self):
        """Tests that find returns None if 'sessions' key is missing."""
        collection = SessionCollection({}, self.timezone_name)
        self.assertIsNone(collection.find("session1"))

    def test_delete_with_no_sessions_key(self):
        """Tests that delete returns False if 'sessions' key is missing."""
        collection = SessionCollection({}, self.timezone_name)
        self.assertFalse(collection.delete("session1"))


if __name__ == "__main__":
    unittest.main()
