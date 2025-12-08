import json
import os
import shutil
import tempfile
import unittest
import zoneinfo
from unittest.mock import patch

from pipe.core.collections.turns import TurnCollection
from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.models.settings import Settings
from pipe.core.models.turn import ModelResponseTurn, UserTaskTurn


class TestSessionCollectionExtensions(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.sessions_dir = os.path.join(self.temp_dir, "sessions")
        os.makedirs(self.sessions_dir, exist_ok=True)
        self.index_path = os.path.join(self.sessions_dir, "index.json")
        self.timezone_name = "UTC"
        self.timezone_obj = zoneinfo.ZoneInfo(self.timezone_name)

        # Setup settings
        settings_data = {
            "api_mode": "gemini-cli",
            "model": "gemini-2.0-flash-exp",
            "expert_mode": False,
            "timezone": "UTC",
            "parameters": {
                "temperature": {"value": 0.5, "description": "t"},
                "top_p": {"value": 0.9, "description": "p"},
                "top_k": {"value": 40, "description": "k"},
            },
        }
        self.settings = Settings(**settings_data)
        self.service_factory = ServiceFactory(self.temp_dir, self.settings)
        self.session_service = self.service_factory.create_session_service()
        self.turn_service = self.service_factory.create_session_turn_service()
        self.workflow_service = self.service_factory.create_session_workflow_service()

        # Create a test session using the service
        test_session = self.session_service.create_new_session(
            purpose="Test Session",
            background="Test Background",
            roles=[],
        )
        self.session_id = test_session.session_id

        # Add initial turns
        session = self.session_service.get_session(self.session_id)
        session.turns.append(
            UserTaskTurn(
                type="user_task",
                instruction="Do something",
                timestamp="2025-01-01T00:00:00Z",
            )
        )
        session.turns.append(
            ModelResponseTurn(
                type="model_response",
                content=json.dumps({"message": "Done"}),
                timestamp="2025-01-01T00:01:00Z",
            )
        )
        session.pools = TurnCollection(
            [
                UserTaskTurn(
                    type="user_task",
                    instruction="Pool task",
                    timestamp="2025-01-01T00:02:00Z",
                )
            ]
        )
        self.session_service._save_session(session)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_add_turn(self):
        new_turn = UserTaskTurn(
            type="user_task",
            instruction="A new task",
            timestamp="2025-01-01T00:03:00Z",
        )
        self.turn_service.add_turn_to_session(self.session_id, new_turn)
        session = self.session_service.get_session(self.session_id)
        self.assertEqual(len(session.turns), 3)
        self.assertEqual(session.turns[-1].instruction, "A new task")

    def test_edit_turn(self):
        new_data = {"instruction": "Updated instruction"}
        self.turn_service.edit_turn(self.session_id, 0, new_data)
        session = self.session_service.get_session(self.session_id)
        self.assertEqual(session.turns[0].instruction, "Updated instruction")

    def test_delete_turn(self):
        self.turn_service.delete_turn(self.session_id, 0)
        session = self.session_service.get_session(self.session_id)
        self.assertEqual(len(session.turns), 1)
        self.assertEqual(session.turns[0].type, "model_response")

    def test_merge_pool(self):
        self.turn_service.merge_pool_into_turns(self.session_id)
        session = self.session_service.get_session(self.session_id)
        self.assertEqual(len(session.turns), 3)
        self.assertEqual(len(session.pools), 0)
        self.assertEqual(session.turns[-1].instruction, "Pool task")

    @patch("pipe.core.utils.datetime.get_current_timestamp")
    def test_fork(self, mock_get_current_timestamp):
        mock_get_current_timestamp.return_value = "2025-01-02T00:00:00Z"
        new_session_id = self.workflow_service.fork_session(self.session_id, 1)
        new_session = self.session_service.get_session(new_session_id)

        self.assertIsNotNone(new_session)
        self.assertEqual(len(new_session.turns), 2)
        self.assertTrue(new_session.purpose.startswith("Fork of:"))


if __name__ == "__main__":
    unittest.main()
