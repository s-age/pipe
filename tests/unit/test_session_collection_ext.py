import json
import os
import tempfile
import unittest
import zoneinfo
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
        self.timezone_obj = zoneinfo.ZoneInfo(self.timezone_name)

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
        # self.session.save() is removed

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

        self.collection = SessionCollection(self.initial_data, self.timezone_name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_turn(self):
        new_turn = UserTaskTurn(
            type="user_task",
            instruction="A new task",
            timestamp="2025-01-01T00:03:00Z",
        )
        self.session.add_turn(new_turn)
        self.assertEqual(len(self.session.turns), 3)
        self.assertEqual(self.session.turns[-1].instruction, "A new task")

    def test_edit_turn(self):
        new_data = {"instruction": "Updated instruction"}
        self.session.edit_turn(0, new_data)
        self.assertEqual(self.session.turns[0].instruction, "Updated instruction")

    def test_delete_turn(self):
        self.session.delete_turn(0)
        self.assertEqual(len(self.session.turns), 1)
        self.assertEqual(self.session.turns[0].type, "model_response")

    def test_merge_pool(self):
        self.session.merge_pool()
        self.assertEqual(len(self.session.turns), 3)
        self.assertEqual(len(self.session.pools), 0)
        self.assertEqual(self.session.turns[-1].instruction, "Pool task")

    @patch("pipe.core.models.session.get_current_timestamp")
    def test_fork(self, mock_get_current_timestamp):
        mock_get_current_timestamp.return_value = "2025-01-02T00:00:00Z"
        new_session = self.session.fork(1, self.timezone_obj)

        self.assertIsNotNone(new_session)
        self.assertEqual(len(new_session.turns), 2)
        self.assertTrue(new_session.purpose.startswith("Fork of:"))


if __name__ == "__main__":
    unittest.main()
