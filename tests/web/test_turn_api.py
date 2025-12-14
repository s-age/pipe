import json
import unittest
from unittest.mock import MagicMock, patch

from pipe.core.models.session import Session
from pipe.core.models.turn import UserTaskTurn
from pipe.web.app import create_app


class TestTurnApi(unittest.TestCase):
    def setUp(self):
        self.app = create_app(init_index=False)
        self.app.config["TESTING"] = True
        with self.app.app_context():
            self.client = self.app.test_client()

        self.mock_session_service = MagicMock()
        self.mock_session_turn_service = MagicMock()

        self.patcher = patch(
            "pipe.web.service_container.get_session_service",
            return_value=self.mock_session_service,
        )
        self.turn_patcher = patch(
            "pipe.web.service_container.get_session_turn_service",
            return_value=self.mock_session_turn_service,
        )
        self.patcher.start()
        self.turn_patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.turn_patcher.stop()

    def test_edit_turn_api_success(self):
        """Tests successfully editing a turn via API."""
        session_id = "sid"
        turn_index = 0
        payload = {"instruction": "new instruction"}

        # Mock session with turns for validation
        mock_session = MagicMock(spec=Session)
        mock_session.turns = ["turn0"]
        self.mock_session_service.get_session.return_value = mock_session

        response = self.client.patch(
            f"/api/v1/session/{session_id}/turn/{turn_index}",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.mock_session_turn_service.edit_turn.assert_called_once_with(
            session_id, turn_index, {"instruction": "new instruction"}
        )

    def test_edit_turn_api_empty_content(self):
        """Tests that empty content is rejected."""
        session_id = "sid"
        turn_index = 0

        # Test empty content
        payload = {"content": ""}
        response = self.client.patch(
            f"/api/v1/session/{session_id}/turn/{turn_index}",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 422)
        self.assertIn("cannot be empty", response.get_json()["message"].lower())

        # Test whitespace-only content
        payload = {"content": "   "}
        response = self.client.patch(
            f"/api/v1/session/{session_id}/turn/{turn_index}",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 422)
        self.assertIn("cannot be empty", response.get_json()["message"].lower())

    def test_edit_turn_api_empty_instruction(self):
        """Tests that empty instruction is rejected."""
        session_id = "sid"
        turn_index = 0

        # Test empty instruction
        payload = {"instruction": ""}
        response = self.client.patch(
            f"/api/v1/session/{session_id}/turn/{turn_index}",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 422)
        self.assertIn("cannot be empty", response.get_json()["message"].lower())

        # Test whitespace-only instruction
        payload = {"instruction": "   \n\t  "}
        response = self.client.patch(
            f"/api/v1/session/{session_id}/turn/{turn_index}",
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_delete_turn_api_success(self):
        # Mock session with turns for validation
        mock_session = MagicMock(spec=Session)
        mock_session.turns = ["turn0", "turn1"]  # At least 1 turn for index 0
        self.mock_session_service.get_session.return_value = mock_session

        response = self.client.delete("/api/v1/session/sid/turn/0")
        self.assertEqual(response.status_code, 200)
        self.mock_session_turn_service.delete_turn.assert_called_once_with("sid", 0)

    def test_delete_turn_api_not_found(self):
        """Tests 404 error when deleting a turn from a non-existent session."""
        # Return None for non-existent session in validation
        self.mock_session_service.get_session.return_value = None
        response = self.client.delete("/api/v1/session/sid/turn/0")
        self.assertEqual(response.status_code, 404)

    def test_delete_turn_api_index_error(self):
        """Tests 400 error when deleting a turn with an invalid index."""
        self.mock_session_service.delete_turn.side_effect = IndexError
        response = self.client.delete("/api/v1/session/sid/turn/99")
        self.assertEqual(response.status_code, 400)

    def test_get_session_turns_api(self):
        """Tests getting session turns via API."""
        turn = UserTaskTurn(
            type="user_task", instruction="test", timestamp="2025-01-01T00:00:00Z"
        )
        # Configure the turn service mock
        self.mock_session_turn_service.get_turns.return_value = [turn]

        response = self.client.get("/api/v1/session/sid/turns?since=0")
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertIn("data", response_json)
        data = response_json["data"]
        self.assertIn("turns", data)
        self.assertEqual(len(data["turns"]), 1)
        self.assertEqual(data["turns"][0]["instruction"], "test")
