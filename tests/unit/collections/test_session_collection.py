import json
import os
import tempfile
import unittest
from io import StringIO
from unittest.mock import Mock, patch

from pipe.core.collections.sessions import SessionCollection
from pipe.core.collections.turns import TurnCollection
from pipe.core.models.turn import ToolResponseTurn, UserTaskTurn


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
        collection = SessionCollection(self.index_path, self.timezone_name)
        session_meta = collection.find("session1")
        self.assertIsNotNone(session_meta)
        self.assertEqual(session_meta["purpose"], "Test session 1")
        self.assertEqual(len(collection), 2)

    def test_add_session_and_save(self):
        """Tests that a new session can be added and saved to the index file."""
        collection = SessionCollection(self.index_path, self.timezone_name)

        # Mock a Session object, as SessionCollection only needs metadata from it
        mock_session = Mock()
        mock_session.session_id = "session2"
        mock_session.purpose = "A new session"
        mock_session.created_at = "2025-01-03T00:00:00Z"

        collection.add(mock_session)
        collection.save()

        # Read the file back and verify the new session was added
        with open(self.index_path) as f:
            data = json.load(f)

        self.assertEqual(len(data["sessions"]), 3)
        self.assertIn("session2", data["sessions"])
        self.assertEqual(data["sessions"]["session2"]["purpose"], "A new session")
        self.assertIn("last_updated", data["sessions"]["session2"])

    def test_update_session_and_save(self):
        """Tests that an existing session's metadata can be updated and saved."""
        collection = SessionCollection(self.index_path, self.timezone_name)

        collection.update("session1", purpose="Updated purpose")
        collection.save()

        with open(self.index_path) as f:
            data = json.load(f)

        self.assertEqual(data["sessions"]["session1"]["purpose"], "Updated purpose")
        # Check that last_updated timestamp has changed from the initial one
        self.assertNotEqual(
            data["sessions"]["session1"]["last_updated"],
            self.initial_data["sessions"]["session1"]["last_updated"],
        )

    def test_delete_session_and_children_and_save(self):
        """Tests that deleting a session also removes its children and saves the
        result."""
        collection = SessionCollection(self.index_path, self.timezone_name)

        result = collection.delete("session1")
        self.assertTrue(result)
        collection.save()

        with open(self.index_path) as f:
            data = json.load(f)

        self.assertEqual(len(data["sessions"]), 0)
        self.assertNotIn("session1", data["sessions"])
        self.assertNotIn("session1/child1", data["sessions"])

    def test_delete_nonexistent_session(self):
        """Tests that attempting to delete a non-existent session fails gracefully."""
        collection = SessionCollection(self.index_path, self.timezone_name)
        result = collection.delete("nonexistent")
        self.assertFalse(result)

        # Ensure data is not changed by the failed operation
        with open(self.index_path) as f:
            data = json.load(f)
        self.assertEqual(data, self.initial_data)

    def test_add_duplicate_session_raises_error(self):
        """Tests that adding a session with an existing ID raises a ValueError."""
        collection = SessionCollection(self.index_path, self.timezone_name)
        mock_session = Mock()
        mock_session.session_id = "session1"  # This ID already exists
        with self.assertRaises(ValueError):
            collection.add(mock_session)

    def test_invalid_timezone_falls_back_to_utc(self):
        """Tests that an invalid timezone name results in a fallback to UTC and a
        warning."""
        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            collection = SessionCollection(self.index_path, "Invalid/Timezone")
            self.assertEqual(collection.timezone_obj.key, "UTC")
            self.assertEqual(
                mock_stderr.getvalue(),
                "Warning: Timezone 'Invalid/Timezone' not found. Using UTC.\n",
            )

    def test_edit_turn_success(self):
        """Tests that a turn can be successfully edited."""
        collection = SessionCollection(self.index_path, self.timezone_name)
        mock_session = Mock()
        mock_session.session_id = "session1"
        mock_session.turns = TurnCollection(
            [UserTaskTurn(type="user_task", instruction="Original", timestamp="1")]
        )

        collection.edit_turn(mock_session, 0, {"instruction": "Updated"})

        self.assertEqual(mock_session.turns[0].instruction, "Updated")
        mock_session.save.assert_called_once()

    def test_edit_turn_index_error(self):
        """Tests that editing a turn with an out-of-bounds index raises IndexError."""
        collection = SessionCollection(self.index_path, self.timezone_name)
        mock_session = Mock()
        mock_session.session_id = "session1"
        mock_session.turns = TurnCollection()

        with self.assertRaises(IndexError):
            collection.edit_turn(mock_session, 0, {"instruction": "Updated"})

    def test_edit_turn_value_error(self):
        """Tests that editing a non-editable turn type raises ValueError."""
        collection = SessionCollection(self.index_path, self.timezone_name)
        mock_session = Mock()
        mock_session.session_id = "session1"
        mock_session.turns = TurnCollection(
            [
                ToolResponseTurn(
                    type="tool_response",
                    name="t",
                    response={},
                    timestamp="1",
                )
            ]
        )

        with self.assertRaises(ValueError):
            collection.edit_turn(mock_session, 0, {"response": {}})

    def test_delete_turn_success(self):
        """Tests that a turn can be successfully deleted."""
        collection = SessionCollection(self.index_path, self.timezone_name)
        mock_session = Mock()
        mock_session.session_id = "session1"
        mock_session.turns = TurnCollection(
            [UserTaskTurn(type="user_task", instruction="To be deleted", timestamp="1")]
        )

        collection.delete_turn(mock_session, 0)

        self.assertEqual(len(mock_session.turns), 0)
        mock_session.save.assert_called_once()

    def test_delete_turn_index_error(self):
        """Tests that deleting a turn with an out-of-bounds index raises IndexError."""
        collection = SessionCollection(self.index_path, self.timezone_name)
        mock_session = Mock()
        mock_session.session_id = "session1"
        mock_session.turns = TurnCollection()

        with self.assertRaises(IndexError):
            collection.delete_turn(mock_session, 0)

    def test_merge_pool_with_items(self):
        """Tests that merge_pool moves turns from the pool to the main turn list."""
        collection = SessionCollection(self.index_path, self.timezone_name)
        mock_session = Mock()
        mock_session.session_id = "session1"
        mock_session.turns = TurnCollection(
            [UserTaskTurn(type="user_task", instruction="1", timestamp="1")]
        )
        mock_session.pools = TurnCollection(
            [UserTaskTurn(type="user_task", instruction="2", timestamp="2")]
        )

        collection.merge_pool(mock_session)

        self.assertEqual(len(mock_session.turns), 2)
        self.assertEqual(len(mock_session.pools), 0)
        self.assertEqual(mock_session.turns[1].instruction, "2")
        mock_session.save.assert_called_once()

    def test_merge_pool_empty(self):
        """Tests that merge_pool does nothing if the pool is empty."""
        collection = SessionCollection(self.index_path, self.timezone_name)
        mock_session = Mock()
        mock_session.session_id = "session1"
        mock_session.turns = TurnCollection(
            [UserTaskTurn(type="user_task", instruction="1", timestamp="1")]
        )
        mock_session.pools = TurnCollection()

        collection.merge_pool(mock_session)

        self.assertEqual(len(mock_session.turns), 1)
        mock_session.save.assert_not_called()

    def test_get_sorted_by_last_updated_empty(self):
        """Tests that get_sorted_by_last_updated returns an empty list when there are
        no sessions."""
        # Create an empty index file
        with open(self.index_path, "w") as f:
            json.dump({"sessions": {}}, f)

        collection = SessionCollection(self.index_path, self.timezone_name)
        sorted_sessions = collection.get_sorted_by_last_updated()
        self.assertEqual(sorted_sessions, [])


if __name__ == "__main__":
    unittest.main()
