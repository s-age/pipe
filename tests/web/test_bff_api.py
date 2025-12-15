import unittest
from unittest.mock import MagicMock, patch

from pipe.core.models.role import RoleOption
from pipe.core.models.session import Session
from pipe.web.app import create_app


class TestBffApi(unittest.TestCase):
    def setUp(self):
        self.app = create_app(init_index=False)
        self.app.config["TESTING"] = True
        with self.app.app_context():
            self.client = self.app.test_client()

        self.mock_session_service = MagicMock()
        self.mock_session_tree_service = MagicMock()

        self.patcher = patch(
            "pipe.web.service_container.get_session_service",
            return_value=self.mock_session_service,
        )
        self.tree_patcher = patch(
            "pipe.web.service_container.get_session_tree_service",
            return_value=self.mock_session_tree_service,
        )
        self.patcher.start()
        self.tree_patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.tree_patcher.stop()

    @patch("pipe.web.service_container.get_role_service")
    @patch("pipe.web.service_container.get_settings")
    def test_get_session_dashboard_api_success(
        self, mock_get_settings, mock_get_role_service
    ):
        """Tests the /api/v1/bff/session-dashboard/{session_id}."""
        session_id = "test_session_id"

        # Mock SettingsGetAction dependency
        mock_settings = MagicMock()
        mock_settings.to_api_dict.return_value = {
            "mode": "gemini-cli",
            "model": "gemini-2.0-flash-exp",
        }
        mock_get_settings.return_value = mock_settings

        # Mock SessionTreeAction dependencies
        mock_tree_data = {
            "sessions": {
                "session1": {"session_id": "session1", "purpose": "Test 1"},
                "session2": {"session_id": "session2", "purpose": "Test 2"},
            },
            "session_tree": [],
        }
        self.mock_session_tree_service.get_session_tree.return_value = mock_tree_data

        # Mock SessionGetAction dependencies - need session for validation too
        mock_session = Session(
            session_id=session_id,
            created_at="2025-01-01T00:00:00+00:00",
            purpose="Details",
        )
        self.mock_session_service.get_session.return_value = mock_session

        # Mock GetRolesAction dependencies
        mock_role_service = MagicMock()
        mock_role_service.get_all_role_options.return_value = [
            RoleOption(label="python/developer", value="roles/python/developer.md"),
            RoleOption(label="engineer", value="roles/engineer.md"),
        ]
        mock_get_role_service.return_value = mock_role_service

        response = self.client.get(f"/api/v1/bff/chat_history?session_id={session_id}")
        if response.status_code != 200:
            print(f"Response data: {response.get_data(as_text=True)}")
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertIn("data", response_json)
        data = response_json["data"]

        self.assertIn("sessionTree", data)
        self.assertIn("currentSession", data)
        self.assertIn("settings", data)

        self.assertEqual(len(data["sessions"]), 2)
        self.assertEqual(data["currentSession"]["purpose"], "Details")
        self.assertIsInstance(data["settings"], dict)
