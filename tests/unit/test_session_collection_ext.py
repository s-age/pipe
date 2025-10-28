import json
import os
import tempfile
import unittest
from unittest.mock import patch

from pipe.core.collections.sessions import SessionCollection
from pipe.core.collections.turns import TurnCollection
from pipe.core.models.hyperparameters import Hyperparameters
from pipe.core.models.session import Session
from pipe.core.models.turn import ModelResponseTurn, UserTaskTurn


class TestSessionCollectionExtensions(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.sessions_dir = self.temp_dir.name
        self.index_path = os.path.join(self.sessions_dir, "index.json")
        self.timezone_name = "UTC"

        # Mock Session static variables
        Session.sessions_dir = self.sessions_dir
        Session.backups_dir = os.path.join(self.sessions_dir, "backups")
        Session.timezone_name = self.timezone_name
        Session.default_hyperparameters = Hyperparameters()

        # Create a dummy session file for testing
        self.session_id = "test_session"
        self.session_path = os.path.join(self.sessions_dir, f"{self.session_id}.json")
        self.session = Session(
            session_id=self.session_id,
            purpose="Test Session",
            created_at="2025-01-01T00:00:00Z",
            turns=TurnCollection(
                [
                    UserTaskTurn(
                        type="user_task",
                        instruction="Do something",
                        timestamp="2025-01-01T00:00:00Z",
                    ),
                    ModelResponseTurn(
                        type="model_response",
                        content=json.dumps({"message": "Done"}),
                        timestamp="2025-01-01T00:01:00Z",
                    ),
                ]
            ),
            pools=TurnCollection(
                [
                    UserTaskTurn(
                        type="user_task",
                        instruction="Pool task",
                        timestamp="2025-01-01T00:02:00Z",
                    )
                ]
            ),
        )
        self.session.save()

        # Create an initial index
        self.initial_data = {
            "sessions": {
                self.session_id: {
                    "purpose": "Test Session",
                    "created_at": "2025-01-01T00:00:00Z",
                    "last_updated": "2025-01-01T01:00:00Z",
                }
            }
        }
        with open(self.index_path, "w") as f:
            json.dump(self.initial_data, f)

        self.collection = SessionCollection(self.index_path, self.timezone_name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_turn(self):
        new_turn = UserTaskTurn(
            type="user_task",
            instruction="A new task",
            timestamp="2025-01-01T00:03:00Z",
        )
        self.collection.add_turn(self.session, new_turn)

        reloaded_session = Session.find(self.session_id)
        self.assertEqual(len(reloaded_session.turns), 3)
        self.assertEqual(reloaded_session.turns[-1].instruction, "A new task")

        # Check if index is updated
        with open(self.index_path) as f:
            index_data = json.load(f)
        self.assertNotEqual(
            index_data["sessions"][self.session_id]["last_updated"],
            self.initial_data["sessions"][self.session_id]["last_updated"],
        )

    def test_edit_turn(self):
        new_data = {"instruction": "Updated instruction"}
        self.collection.edit_turn(self.session, 0, new_data)

        reloaded_session = Session.find(self.session_id)
        self.assertEqual(reloaded_session.turns[0].instruction, "Updated instruction")

    def test_delete_turn(self):
        self.collection.delete_turn(self.session, 0)

        reloaded_session = Session.find(self.session_id)
        self.assertEqual(len(reloaded_session.turns), 1)
        self.assertEqual(reloaded_session.turns[0].type, "model_response")

    def test_merge_pool(self):
        self.collection.merge_pool(self.session)

        reloaded_session = Session.find(self.session_id)
        self.assertEqual(len(reloaded_session.turns), 3)
        self.assertEqual(len(reloaded_session.pools), 0)
        self.assertEqual(reloaded_session.turns[-1].instruction, "Pool task")

    @patch("pipe.core.collections.sessions.get_current_timestamp")
    def test_fork(self, mock_get_current_timestamp):
        mock_get_current_timestamp.return_value = "2025-01-02T00:00:00Z"
        new_session = self.collection.fork(self.session, 1)

        self.assertIsNotNone(new_session)
        self.assertTrue(os.path.exists(new_session.file_path))
        self.assertEqual(len(new_session.turns), 2)
        self.assertTrue(new_session.purpose.startswith("Fork of:"))

        # Check if the new session is in the index
        with open(self.index_path) as f:
            index_data = json.load(f)
        self.assertIn(new_session.session_id, index_data["sessions"])


if __name__ == "__main__":
    unittest.main()
