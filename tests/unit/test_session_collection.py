import unittest
import os
import tempfile
import json
from datetime import timezone
import zoneinfo
from unittest.mock import Mock

from pipe.core.collections.sessions import SessionCollection

class TestSessionCollection(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.index_path = os.path.join(self.temp_dir.name, "index.json")
        self.timezone_obj = zoneinfo.ZoneInfo("UTC")

        # Initial data for some tests
        self.initial_data = {
            "sessions": {
                "session1": {
                    "purpose": "Test session 1",
                    "created_at": "2025-01-01T00:00:00Z",
                    "last_updated": "2025-01-01T01:00:00Z"
                },
                "session1/child1": {
                    "purpose": "Child session",
                    "created_at": "2025-01-02T00:00:00Z",
                    "last_updated": "2025-01-02T01:00:00Z"
                }
            }
        }
        with open(self.index_path, 'w') as f:
            json.dump(self.initial_data, f)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initial_load_and_find(self):
        """Tests that the collection correctly loads data from an existing index file."""
        collection = SessionCollection(self.index_path, self.timezone_obj)
        session_meta = collection.find("session1")
        self.assertIsNotNone(session_meta)
        self.assertEqual(session_meta['purpose'], "Test session 1")
        self.assertEqual(len(collection), 2)

    def test_add_session_and_save(self):
        """Tests that a new session can be added and saved to the index file."""
        collection = SessionCollection(self.index_path, self.timezone_obj)
        
        # Mock a Session object, as SessionCollection only needs metadata from it
        mock_session = Mock()
        mock_session.session_id = "session2"
        mock_session.purpose = "A new session"
        mock_session.created_at = "2025-01-03T00:00:00Z"
        
        collection.add(mock_session)
        collection.save()
        
        # Read the file back and verify the new session was added
        with open(self.index_path, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(len(data['sessions']), 3)
        self.assertIn("session2", data['sessions'])
        self.assertEqual(data['sessions']['session2']['purpose'], "A new session")
        self.assertIn('last_updated', data['sessions']['session2'])

    def test_update_session_and_save(self):
        """Tests that an existing session's metadata can be updated and saved."""
        collection = SessionCollection(self.index_path, self.timezone_obj)
        
        collection.update("session1", purpose="Updated purpose")
        collection.save()
        
        with open(self.index_path, 'r') as f:
            data = json.load(f)
            
        self.assertEqual(data['sessions']['session1']['purpose'], "Updated purpose")
        # Check that last_updated timestamp has changed from the initial one
        self.assertNotEqual(data['sessions']['session1']['last_updated'], self.initial_data['sessions']['session1']['last_updated'])

    def test_delete_session_and_children_and_save(self):
        """Tests that deleting a session also removes its children and saves the result."""
        collection = SessionCollection(self.index_path, self.timezone_obj)
        
        result = collection.delete("session1")
        self.assertTrue(result)
        collection.save()
        
        with open(self.index_path, 'r') as f:
            data = json.load(f)
            
        self.assertEqual(len(data['sessions']), 0)
        self.assertNotIn("session1", data['sessions'])
        self.assertNotIn("session1/child1", data['sessions'])

    def test_delete_nonexistent_session(self):
        """Tests that attempting to delete a non-existent session fails gracefully."""
        collection = SessionCollection(self.index_path, self.timezone_obj)
        result = collection.delete("nonexistent")
        self.assertFalse(result)
        
        # Ensure data is not changed by the failed operation
        with open(self.index_path, 'r') as f:
            data = json.load(f)
        self.assertEqual(data, self.initial_data)

if __name__ == '__main__':
    unittest.main()
