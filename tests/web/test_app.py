import json
import unittest
from unittest.mock import MagicMock, patch

from pipe.core.models.hyperparameters import Hyperparameters
from pipe.core.models.reference import Reference
from pipe.core.models.session import Session

# The Flask app object needs to be imported for testing
from pipe.web.app import app


class TestAppApi(unittest.TestCase):
    def setUp(self):
        # Configure the app for testing
        app.config["TESTING"] = True
        with app.app_context():
            self.client = app.test_client()

        # We patch the session_service used by the app to isolate the web layer
        # and avoid actual file system operations.
        self.mock_session_service = MagicMock()

        # The patch needs to target where the object is *used*
        self.patcher = patch("pipe.web.app.session_service", self.mock_session_service)
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
            f"/api/session/{session_id}/references/{reference_index}/ttl",
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
            f"/api/session/{session_id}/references/99/ttl",  # Index 99 is out of range
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
                    f"/api/session/{session_id}/references/0/ttl",
                    method="PATCH",
                    json=payload,
                )
                self.assertEqual(response.status_code, 422)

    def test_get_sessions_api(self):
        """Tests the API endpoint for getting all sessions."""
        mock_sessions = [["session1", {"purpose": "Test 1"}]]
        (
            self.mock_session_service.list_sessions().get_sorted_by_last_updated.return_value
        ) = mock_sessions
        response = self.client.get("/api/sessions")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("sessions", data)
        self.assertEqual(data["sessions"], mock_sessions)

    def test_get_session_tree_api_v1(self):
        """Tests the v1 API endpoint for getting session tree."""
        mock_sessions = [["session1", {"purpose": "Test 1"}]]
        (
            self.mock_session_service.list_sessions().get_sorted_by_last_updated.return_value
        ) = mock_sessions
        response = self.client.get("/api/v1/session_tree")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("sessions", data)
        self.assertEqual(data["sessions"], mock_sessions)

    def test_get_session_api_success(self):
        """Tests successfully getting a single session via API."""
        session_id = "test_id"
        mock_session = MagicMock(spec=Session)
        mock_session.to_dict.return_value = {"id": session_id, "purpose": "Details"}
        self.mock_session_service.get_session.return_value = mock_session

        response = self.client.get(f"/api/session/{session_id}")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("session", data)
        self.assertEqual(data["session"]["purpose"], "Details")

    def test_get_session_api_not_found(self):
        """Tests the 404 response when getting a non-existent session."""
        self.mock_session_service.get_session.return_value = None
        response = self.client.get("/api/session/non_existent")
        self.assertEqual(response.status_code, 404)

    def test_delete_session_api(self):
        """Tests successfully deleting a session via API."""
        session_id = "test_id_to_delete"
        response = self.client.delete(f"/api/session/{session_id}")
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
            "/api/session/start",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["session_id"], "new_session_123")
        mock_subprocess_run.assert_called_once()

    def test_create_new_session_api_validation_error(self):
        """Tests the validation error for the new session API."""
        response = self.client.post(
            "/api/session/start",
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
            f"/api/session/{session_id}/turns/{turn_index}",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.mock_session_service.edit_turn.assert_called_once_with(
            session_id, turn_index, payload
        )

    def test_edit_session_meta_api_success(self):
        """Tests successfully editing session metadata via API."""
        session_id = "sid"
        payload = {"purpose": "New Purpose"}

        response = self.client.patch(
            f"/api/session/{session_id}/meta",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.mock_session_service.edit_session_meta.assert_called_once_with(
            session_id, payload
        )

    def test_delete_turn_api_success(self):
        """Tests successfully deleting a turn."""
        response = self.client.delete("/api/session/sid/turn/0")
        self.assertEqual(response.status_code, 200)
        self.mock_session_service.delete_turn.assert_called_once_with("sid", 0)

    def test_delete_turn_api_not_found(self):
        """Tests 404 error when deleting a turn from a non-existent session."""
        self.mock_session_service.delete_turn.side_effect = FileNotFoundError
        response = self.client.delete("/api/session/sid/turn/0")
        self.assertEqual(response.status_code, 404)

    def test_delete_turn_api_index_error(self):
        """Tests 400 error when deleting a turn with an invalid index."""
        self.mock_session_service.delete_turn.side_effect = IndexError
        response = self.client.delete("/api/session/sid/turn/99")
        self.assertEqual(response.status_code, 400)

    def test_edit_todos_api_success(self):
        """Tests successfully editing todos."""
        payload = {"todos": [{"title": "Test Todo", "checked": False}]}
        response = self.client.patch(
            "/api/session/sid/todos",
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
        response = self.client.delete("/api/session/sid/todos")
        self.assertEqual(response.status_code, 200)
        self.mock_session_service.delete_todos.assert_called_once_with("sid")

    def test_edit_references_api_success(self):
        """Tests successfully editing references."""
        payload = {"references": [{"path": "/test.py", "disabled": False, "ttl": -1}]}
        response = self.client.patch(
            "/api/session/sid/references",
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
            "/api/session/original_id/fork/1",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["new_session_id"], "new_forked_id")
        self.mock_session_service.fork_session.assert_called_once_with("original_id", 1)

    def test_fork_session_api_not_found(self):
        """Tests 404 on fork if session is not found."""
        self.mock_session_service.fork_session.side_effect = FileNotFoundError
        payload = {"session_id": "original_id"}
        response = self.client.post(
            "/api/session/original_id/fork/1",
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

        response = self.client.get("/api/session/sid/turns?since=0")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("turns", data)
        self.assertEqual(len(data["turns"]), 1)
        self.assertEqual(data["turns"][0]["instruction"], "test")

    @patch("subprocess.Popen")
    def test_send_instruction_api_success(self, mock_popen):
        """Tests the streaming instruction endpoint."""
        mock_session = MagicMock()
        mock_session.pools = []
        self.mock_session_service.get_session.return_value = mock_session

        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = ["line 1\n", "line 2\n", ""]
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        payload = {"instruction": "stream test"}
        response = self.client.post(
            "/api/session/sid/instruction",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_streamed)

        # Consume the stream and check content
        stream_content = [line for line in response.iter_encoded()]
        self.assertIn(b'data: {"content": "line 1\\n"}\n\n', stream_content)
        self.assertIn(b'data: {"content": "line 2\\n"}\n\n', stream_content)

    def test_send_instruction_api_pool_limit(self):
        """Tests that the instruction endpoint rejects when the pool is full."""
        mock_session = MagicMock()
        mock_session.pools = [1, 2, 3, 4, 5, 6, 7]  # Pool is full
        self.mock_session_service.get_session.return_value = mock_session

        payload = {"instruction": "stream test"}
        response = self.client.post(
            "/api/session/sid/instruction",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)


class TestAppViews(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()
        self.mock_session_service = MagicMock()
        self.patcher = patch("pipe.web.app.session_service", self.mock_session_service)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_index_page(self):
        """Tests the index page rendering."""
        (
            self.mock_session_service.list_sessions().get_sorted_by_last_updated.return_value
        ) = [("session1", {"purpose": "Test Session 1"})]
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Test Session 1", response.data)

    def test_new_session_page(self):
        """Tests the new session page rendering."""
        (
            self.mock_session_service.list_sessions().get_sorted_by_last_updated.return_value
        ) = []
        response = self.client.get("/start_session")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Create New Session", response.data)

    def test_view_session_page(self):
        """Tests viewing a specific session."""
        session_id = "test_session_id"
        mock_session = MagicMock(spec=Session)
        mock_session.to_dict.return_value = {"turns": [], "purpose": "My Test Session"}
        mock_session.purpose = "My Test Session"
        mock_session.hyperparameters = None
        mock_session.references = []
        mock_session.artifacts = []  # Added to fix AttributeError
        mock_session.multi_step_reasoning_enabled = False
        mock_session.token_count = 123

        self.mock_session_service.list_sessions().__contains__.return_value = True
        (
            self.mock_session_service.list_sessions().get_sorted_by_last_updated.return_value
        ) = []
        self.mock_session_service.get_session.return_value = mock_session

        response = self.client.get(f"/session/{session_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"My Test Session", response.data)
        self.mock_session_service.get_session.assert_called_once_with(session_id)

    def test_view_session_not_found(self):
        """Tests that a 404 is returned for a non-existent session."""
        self.mock_session_service.list_sessions().__contains__.return_value = False
        response = self.client.get("/session/non_existent_id")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
