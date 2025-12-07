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

        # The patch needs to target the service container getter
        self.patcher = patch(
            "pipe.web.service_container.get_session_service",
            return_value=self.mock_session_service,
        )
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

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
        self.mock_session_service.update_reference_ttl_in_session.assert_called_once_with(
            session_id, file_path, new_ttl
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

        (
            self.mock_session_service.list_sessions().get_sorted_by_last_updated.return_value
        ) = [["session1", {"purpose": "Test 1"}]]
        response = self.client.get("/api/v1/session_tree")
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertIn("data", response_json)
        data = response_json["data"]
        self.assertIn("sessions", data)

    def test_get_session_tree_api_v1(self):
        """Tests the v1 API endpoint for getting session tree."""
        mock_sessions = {"session1": {"purpose": "Test 1"}}
        (
            self.mock_session_service.list_sessions().get_sorted_by_last_updated.return_value
        ) = [["session1", {"purpose": "Test 1"}]]
        response = self.client.get("/api/v1/session_tree")
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertIn("data", response_json)
        data = response_json["data"]
        self.assertIn("sessions", data)
        self.assertEqual(data["sessions"], mock_sessions)

    def test_get_session_api_success(self):
        """Tests successfully getting a single session via API."""
        session_id = "test_id"
        mock_session = MagicMock(spec=Session)
        mock_session.to_dict.return_value = {"id": session_id, "purpose": "Details"}
        self.mock_session_service.get_session.return_value = mock_session

        response = self.client.get(f"/api/v1/session/{session_id}")
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertIn("data", response_json)
        data = response_json["data"]
        self.assertEqual(data["id"], session_id)
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
        self.mock_session_service.delete_session.assert_called_once_with(session_id)

    @patch("subprocess.run")
    def test_create_new_session_api_success(self, mock_subprocess_run):
        """Tests the successful creation of a new session via API."""
        mock_session = MagicMock()
        mock_session.session_id = "new_session_123"
        self.mock_session_service.create_new_session.return_value = mock_session
        mock_subprocess_run.return_value = MagicMock(check=True)

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
        mock_subprocess_run.assert_called_once()

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

        response = self.client.patch(
            f"/api/v1/session/{session_id}/turn/{turn_index}",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.mock_session_service.edit_turn.assert_called_once_with(
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
        self.mock_session_service.edit_session_meta.assert_called_once_with(
            session_id, payload
        )

    def test_delete_turn_api_success(self):
        response = self.client.delete("/api/v1/session/sid/turn/0")
        self.assertEqual(response.status_code, 200)
        self.mock_session_service.delete_turn.assert_called_once_with("sid", 0)

    def test_delete_turn_api_not_found(self):
        """Tests 404 error when deleting a turn from a non-existent session."""
        self.mock_session_service.delete_turn.side_effect = FileNotFoundError
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
        self.mock_session_service.update_todos.assert_called_once()
        args, _ = self.mock_session_service.update_todos.call_args
        self.assertEqual(args[0], "sid")
        self.assertEqual(args[1][0].title, "Test Todo")

    def test_delete_todos_api_success(self):
        """Tests successfully deleting all todos from a session."""
        response = self.client.delete("/api/v1/session/sid/todos")
        self.assertEqual(response.status_code, 200)
        self.mock_session_service.delete_todos.assert_called_once_with("sid")

    def test_edit_references_api_success(self):
        """Tests successfully editing references."""
        payload = {"references": [{"path": "/test.py", "disabled": False, "ttl": -1}]}
        response = self.client.patch(
            "/api/v1/session/sid/references",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.mock_session_service.update_references.assert_called_once()

    def test_fork_session_api_success(self):
        """Tests successfully forking a session."""
        self.mock_session_service.fork_session.return_value = "new_forked_id"
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
        self.mock_session_service.fork_session.assert_called_once_with("original_id", 1)

    def test_fork_session_api_not_found(self):
        """Tests 404 on fork if session is not found."""
        self.mock_session_service.fork_session.side_effect = FileNotFoundError
        payload = {"session_id": "original_id"}
        response = self.client.post(
            "/api/v1/session/original_id/fork/1",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_get_session_turns_api(self):
        """Tests getting session turns via API."""
        mock_turn = MagicMock()
        mock_turn.model_dump.return_value = {"instruction": "test"}
        mock_session = MagicMock()
        mock_session.turns = [mock_turn]
        self.mock_session_service.get_session.return_value = mock_session

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
        mock_session.pools = [1, 2, 3, 4, 5, 6, 7]  # Pool is full
        self.mock_session_service.get_session.return_value = mock_session

        response = self.client.post(
            "/api/v1/session/sid/instruction",
            data=json.dumps({"instruction": "stream test"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    @patch("pipe.web.actions.fs_actions.RoleService")
    def test_get_session_dashboard_api_success(self, MockRoleServiceForGetRolesAction):
        """Tests the /api/v1/bff/session-dashboard/{session_id} endpoint."""
        session_id = "test_session_id"

        # Mock SessionTreeAction dependencies (uses self.mock_session_service)
        mock_list_sessions = self.mock_session_service.list_sessions
        mock_list_sessions.return_value.get_sorted_by_last_updated.return_value = [
            ["session1", {"purpose": "Test 1"}],
            ["session2", {"purpose": "Test 2"}],
        ]

        # Mock SessionGetAction dependencies (uses self.mock_session_service)
        mock_session = MagicMock(spec=Session)
        mock_session.to_dict.return_value = {"id": session_id, "purpose": "Details"}
        self.mock_session_service.get_session.return_value = mock_session

        # Mock GetRolesAction dependencies
        mock_role_service = MockRoleServiceForGetRolesAction.return_value
        mock_role_service.get_all_role_options.return_value = [
            RoleOption(label="python/developer", value="roles/python/developer.md"),
            RoleOption(label="engineer", value="roles/engineer.md"),
        ]

        response = self.client.get(f"/api/v1/bff/chat_history?session_id={session_id}")
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertIn("data", response_json)
        data = response_json["data"]

        self.assertIn("sessionTree", data)
        self.assertIn("currentSession", data)
        self.assertIn("settings", data)

        self.assertEqual(len(data["sessionTree"]), 2)
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
