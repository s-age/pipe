import json
import unittest
from unittest.mock import MagicMock, patch

import pytest
from pipe.core.models.hyperparameters import Hyperparameters
from pipe.core.models.reference import Reference
from pipe.core.models.role import RoleOption
from pipe.core.models.session import Session

# The Flask app factory needs to be imported for testing
from pipe.web.app import create_app


class TestAppApi(unittest.TestCase):
    def setUp(self):
        # Create the app using the factory
        self.app = create_app(init_index=False)
        self.app.config["TESTING"] = True
        with self.app.app_context():
            self.client = self.app.test_client()

        # We patch the session_service used by the app to isolate the web layer
        # and avoid actual file system operations.
        self.mock_session_service = MagicMock()
        self.mock_session_reference_service = MagicMock()
        self.mock_session_turn_service = MagicMock()
        self.mock_session_meta_service = MagicMock()
        self.mock_session_todo_service = MagicMock()
        self.mock_session_tree_service = MagicMock()
        self.mock_session_workflow_service = MagicMock()
        self.mock_session_optimization_service = MagicMock()
        self.mock_session_management_service = MagicMock()

        # The patch needs to target the service container getter
        self.patcher = patch(
            "pipe.web.service_container.get_session_service",
            return_value=self.mock_session_service,
        )
        self.management_patcher = patch(
            "pipe.web.service_container.get_session_management_service",
            return_value=self.mock_session_management_service,
        )
        self.reference_patcher = patch(
            "pipe.web.service_container.get_session_reference_service",
            return_value=self.mock_session_reference_service,
        )
        self.turn_patcher = patch(
            "pipe.web.service_container.get_session_turn_service",
            return_value=self.mock_session_turn_service,
        )
        self.meta_patcher = patch(
            "pipe.web.service_container.get_session_meta_service",
            return_value=self.mock_session_meta_service,
        )
        self.todo_patcher = patch(
            "pipe.web.service_container.get_session_todo_service",
            return_value=self.mock_session_todo_service,
        )
        self.tree_patcher = patch(
            "pipe.web.service_container.get_session_tree_service",
            return_value=self.mock_session_tree_service,
        )
        self.workflow_patcher = patch(
            "pipe.web.service_container.get_session_workflow_service",
            return_value=self.mock_session_workflow_service,
        )
        self.optimization_patcher = patch(
            "pipe.web.service_container.get_session_optimization_service",
            return_value=self.mock_session_optimization_service,
        )
        self.patcher.start()
        self.management_patcher.start()
        self.reference_patcher.start()
        self.turn_patcher.start()
        self.meta_patcher.start()
        self.todo_patcher.start()
        self.tree_patcher.start()
        self.workflow_patcher.start()
        self.optimization_patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.management_patcher.stop()
        self.reference_patcher.stop()
        self.turn_patcher.stop()
        self.meta_patcher.stop()
        self.todo_patcher.stop()
        self.tree_patcher.stop()
        self.workflow_patcher.stop()
        self.optimization_patcher.stop()

    def test_edit_reference_ttl_api_success(self):
        """Tests the TTL update API endpoint with a valid request."""
        session_id = "test_session"
        reference_index = 0
        file_path = "test.py"
        new_ttl = 5

        # Mock the session that the service will return
        mock_session = MagicMock(spec=Session)
        mock_session.references = [Reference(path=file_path, disabled=False, ttl=3)]
        self.mock_session_service.get_session.return_value = mock_session

        response = self.client.open(
            f"/api/v1/session/{session_id}/references/{reference_index}/ttl",
            method="PATCH",
            json={"ttl": new_ttl},
        )

        self.assertEqual(response.status_code, 200)
        self.mock_session_service.get_session.assert_called_once_with(session_id)
        self.mock_session_reference_service.update_reference_ttl_by_index.assert_called_once_with(
            session_id, reference_index, new_ttl
        )

    def test_edit_reference_ttl_api_session_not_found(self):
        """Tests the API response when the session ID does not exist."""
        self.mock_session_service.get_session.return_value = None

        response = self.client.open(
            "/api/session/nonexistent/references/0/ttl",
            method="PATCH",
            json={"ttl": 5},
        )

        self.assertEqual(response.status_code, 404)

    def test_edit_reference_ttl_api_index_out_of_range(self):
        """Tests the API response for an out-of-range reference index."""
        session_id = "test_session"
        mock_session = MagicMock(spec=Session)
        mock_session.references = [Reference(path="test.py")]
        self.mock_session_service.get_session.return_value = mock_session

        response = self.client.open(
            f"/api/v1/session/{session_id}/references/99/ttl",
            # Index 99 is out of range
            method="PATCH",
            json={"ttl": 5},
        )

        self.assertEqual(response.status_code, 400)

    def test_edit_reference_ttl_api_invalid_ttl_value(self):
        """Tests the API response for various invalid TTL values."""
        session_id = "test_session"
        mock_session = MagicMock(spec=Session)
        mock_session.references = [Reference(path="test.py")]
        self.mock_session_service.get_session.return_value = mock_session

        invalid_payloads = [
            {"ttl": -1},
            {"ttl": "not-a-number"},
            {"ttl": 1.5},
            {},  # Missing ttl
        ]

        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                response = self.client.open(
                    f"/api/v1/session/{session_id}/references/0/ttl",
                    method="PATCH",
                    json=payload,
                )
                self.assertEqual(response.status_code, 422)

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

    def test_get_session_api_success(self):
        """Tests successfully getting a single session via API."""
        session_id = "test_id"
        # Use real Session object to support Pydantic serialization
        session = Session(
            session_id=session_id, created_at="2025-01-01T00:00:00Z", purpose="Details"
        )
        self.mock_session_service.get_session.return_value = session

        response = self.client.get(f"/api/v1/session/{session_id}")
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertIn("data", response_json)
        data = response_json["data"]
        self.assertEqual(data["sessionId"], session_id)
        self.assertEqual(data["purpose"], "Details")

    def test_get_session_api_not_found(self):
        """Tests the 404 response when getting a non-existent session."""
        self.mock_session_service.get_session.return_value = None
        response = self.client.get("/api/v1/session/non_existent")
        self.assertEqual(response.status_code, 404)

    def test_delete_session_api(self):
        """Tests successfully deleting a session via API."""
        session_id = "test_id_to_delete"
        response = self.client.delete(f"/api/v1/session/{session_id}")
        self.assertEqual(response.status_code, 200)
        self.mock_session_management_service.delete_sessions.assert_called_once_with(
            [session_id]
        )

    @patch("pipe.core.agents.takt_agent.TaktAgent.run_existing_session")
    def test_create_new_session_api_success(self, mock_run_existing_session):
        # Configure the mock to return a proper session object
        mock_session = MagicMock()
        mock_session.session_id = "new_session_123"
        self.mock_session_service.create_new_session.return_value = mock_session

        payload = {
            "purpose": "Test",
            "background": "BG",
            "instruction": "Do thing",
            "roles": [],
            "parent": None,
            "references": [],
            "multi_step_reasoning_enabled": False,
            "hyperparameters": Hyperparameters().model_dump(),
        }
        response = self.client.post(
            "/api/v1/session/start",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertIn("data", response_json)
        data = response_json["data"]
        self.assertEqual(data["sessionId"], "new_session_123")
        mock_run_existing_session.assert_called_once()

    @pytest.mark.skip(reason="Validation behavior needs review after refactoring")
    def test_create_new_session_api_validation_error(self):
        """Tests the validation error for the new session API."""
        response = self.client.post(
            "/api/v1/session/start",
            data=json.dumps({}),  # Empty payload
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 422)

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
            session_id, turn_index, payload
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

    def test_edit_session_meta_api_success(self):
        """Tests successfully editing session metadata via API."""
        session_id = "sid"
        payload = {"purpose": "New Purpose"}

        response = self.client.patch(
            f"/api/v1/session/{session_id}/meta",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.mock_session_meta_service.edit_session_meta.assert_called_once_with(
            session_id, payload
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

    def test_edit_todos_api_success(self):
        """Tests successfully editing todos."""
        payload = {"todos": [{"title": "Test Todo", "checked": False}]}
        response = self.client.patch(
            "/api/v1/session/sid/todos",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        # Pydantic models are not directly comparable with dicts, so we check
        # the call args manually
        self.mock_session_todo_service.update_todos.assert_called_once()
        args, _ = self.mock_session_todo_service.update_todos.call_args
        self.assertEqual(args[0], "sid")
        self.assertEqual(args[1][0].title, "Test Todo")

    def test_delete_todos_api_success(self):
        """Tests successfully deleting all todos from a session."""
        response = self.client.delete("/api/v1/session/sid/todos")
        self.assertEqual(response.status_code, 200)
        self.mock_session_todo_service.delete_todos.assert_called_once_with("sid")

    def test_edit_references_api_success(self):
        """Tests successfully editing references."""
        payload = {"references": [{"path": "/test.py", "disabled": False, "ttl": -1}]}
        response = self.client.patch(
            "/api/v1/session/sid/references",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.mock_session_reference_service.update_references.assert_called_once()

    def test_fork_session_api_success(self):
        """Tests successfully forking a session."""
        # Mock session with turns for validation
        mock_session = MagicMock(spec=Session)
        mock_session.turns = ["turn0", "turn1", "turn2"]
        self.mock_session_service.get_session.return_value = mock_session
        self.mock_session_workflow_service.fork_session.return_value = "new_forked_id"
        payload = {"session_id": "original_id"}
        response = self.client.post(
            "/api/v1/session/original_id/fork/1",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertIn("data", response_json)
        data = response_json["data"]
        self.assertEqual(data["newSessionId"], "new_forked_id")
        self.mock_session_workflow_service.fork_session.assert_called_once_with(
            "original_id", 1
        )

    def test_fork_session_api_not_found(self):
        """Tests 404 on fork if session is not found."""
        # Return None for non-existent session in validation
        self.mock_session_service.get_session.return_value = None
        payload = {"session_id": "original_id"}
        response = self.client.post(
            "/api/v1/session/original_id/fork/1",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_get_session_turns_api(self):
        """Tests getting session turns via API."""
        from pipe.core.models.turn import UserTaskTurn

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

    @pytest.mark.skip(reason="Complex mocking required for streaming test")
    def test_send_instruction_api_success(self):
        """Tests the streaming instruction endpoint."""
        from unittest.mock import patch

        mock_session = MagicMock()
        mock_session.pools = []
        mock_session.session_id = "sid"

        with (
            patch("pipe.web.app.session_service") as mock_session_service_patch,
            patch(
                "pipe.core.factories.service_factory.ServiceFactory"
            ) as mock_service_factory,
            patch(
                "pipe.core.delegates.gemini_api_delegate.run_stream"
            ) as mock_run_stream,
        ):
            mock_session_service_patch.repository.find.return_value = mock_session
            mock_session_service_patch.get_session.return_value = mock_session

            mock_prompt_service = MagicMock()
            mock_prompt_model = MagicMock()
            mock_prompt_model.model_dump.return_value = {"test": "data"}
            mock_prompt_service.build_prompt.return_value = mock_prompt_model
            mock_service_factory.return_value.create_prompt_service.return_value = (
                mock_prompt_service
            )

            mock_run_stream.return_value = iter(
                ["line 1\n", "line 2\n", ("end", "model response", 100, [MagicMock()])]
            )

            # Stop the setUp patch to avoid conflict
            self.patcher.stop()

            try:
                response = self.client.post(
                    "/api/v1/session/sid/instruction",
                    data=json.dumps({"instruction": "stream test"}),
                    content_type="application/json",
                )

                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.is_streamed)

                stream_content = [line for line in response.iter_encoded()]
                self.assertIn(b'data: {"content": "line 1\\n"}\n\n', stream_content)
                self.assertIn(b'data: {"content": "line 2\\n"}\n\n', stream_content)
                mock_run_stream.assert_called_once()
            finally:
                self.patcher.start()

    def test_send_instruction_api_pool_limit(self):
        """Tests that the instruction endpoint rejects when the pool is full."""
        mock_session = MagicMock()
        mock_session.pools = list(range(25))  # Pool is full (limit is 25)
        self.mock_session_service.get_session.return_value = mock_session

        response = self.client.post(
            "/api/v1/session/sid/instruction",
            data=json.dumps({"instruction": "stream test"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    @pytest.mark.skip(
        reason="BFF endpoint needs refactoring: Actions called from "
        "controllers don't have validated_request initialized"
    )
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
                "session1": {"purpose": "Test 1"},
                "session2": {"purpose": "Test 2"},
            },
            "session_tree": {},
        }
        self.mock_session_service.get_session_tree.return_value = mock_tree_data

        # Mock SessionGetAction dependencies - need session for validation too
        mock_session = MagicMock(spec=Session)
        mock_session.to_dict.return_value = {"id": session_id, "purpose": "Details"}
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

        self.assertEqual(len(data["sessionTree"]["sessions"]), 2)
        self.assertEqual(data["currentSession"]["purpose"], "Details")
        self.assertIsInstance(data["settings"], dict)


class TestAppViews(unittest.TestCase):
    def setUp(self):
        self.app = create_app(init_index=False)
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.mock_session_service = MagicMock()
        # Patch in the service container
        self.patcher = patch(
            "pipe.web.service_container.get_container",
            return_value=MagicMock(session_service=self.mock_session_service),
        )
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_view_session_not_found(self):
        """Tests that a 404 is returned for a non-existent session."""
        self.mock_session_service.list_sessions().__contains__.return_value = False
        response = self.client.get("/session/non_existent_id")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
