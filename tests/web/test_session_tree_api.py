import unittest
from unittest.mock import MagicMock, patch

from pipe.web.app import create_app


class TestSessionTreeApi(unittest.TestCase):
    def setUp(self):
        self.app = create_app(init_index=False)
        self.app.config["TESTING"] = True
        with self.app.app_context():
            self.client = self.app.test_client()

        self.mock_session_tree_service = MagicMock()

        self.tree_patcher = patch(
            "pipe.web.service_container.get_session_tree_service",
            return_value=self.mock_session_tree_service,
        )
        self.tree_patcher.start()

    def tearDown(self):
        self.tree_patcher.stop()

    def test_get_session_tree_api_v1(self):
        """Tests the v1 API endpoint for getting session tree."""
        mock_tree_data = {
            "sessions": {"session1": {"purpose": "Test 1", "session_id": "session1"}},
            "session_tree": [],
        }
        self.mock_session_tree_service.get_session_tree.return_value = mock_tree_data

        response = self.client.get("/api/v1/session_tree")
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertIn("data", response_json)
        data = response_json["data"]
        self.assertIn("sessions", data)
        # Expected response is camelCase
        expected_data = {
            "sessions": {
                "session1": {
                    "purpose": "Test 1",
                    "sessionId": "session1",
                    "createdAt": None,
                    "lastUpdatedAt": None,
                }
            },
            "sessionTree": [],
        }
        self.assertEqual(data, expected_data)
