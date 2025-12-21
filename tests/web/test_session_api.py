import json
import unittest
from unittest.mock import MagicMock, patch

from pipe.core.models.hyperparameters import Hyperparameters
from pipe.core.models.session import Session
from pipe.web.app import create_app


class TestSessionApi(unittest.TestCase):
    def setUp(self):
        self.app = create_app(init_index=False)
        self.app.config["TESTING"] = True
        with self.app.app_context():
            self.client = self.app.test_client()

        self.mock_session_service = MagicMock()
        self.mock_session_workflow_service = MagicMock()
        self.mock_session_management_service = MagicMock()
        self.mock_takt_agent = MagicMock()

        # Mock both service_container (for validators) and DI container (for actions)
        self.patcher = patch(
            "pipe.web.service_container.get_session_service",
            return_value=self.mock_session_service,
        )
        self.workflow_patcher = patch(
            "pipe.web.service_container.get_session_workflow_service",
            return_value=self.mock_session_workflow_service,
        )
        self.management_patcher = patch(
            "pipe.web.service_container.get_session_management_service",
            return_value=self.mock_session_management_service,
        )

        # Mock DI container for action dependency injection
        # We need to patch _get_dispatcher to return a dispatcher with mocked container
        from pipe.core.agents.takt_agent import TaktAgent
        from pipe.core.container import DependencyContainer
        from pipe.core.services.session_management_service import (
            SessionManagementService,
        )
        from pipe.core.services.session_service import SessionService
        from pipe.core.services.session_workflow_service import (
            SessionWorkflowService,
        )
        from pipe.web.binder import RequestBinder
        from pipe.web.dispatcher import ActionDispatcher
        from pipe.web.factory import GenericActionFactory

        # Create a mock container
        mock_container = MagicMock(spec=DependencyContainer)

        def mock_get(service_type):
            service_map = {
                SessionService: self.mock_session_service,
                SessionWorkflowService: self.mock_session_workflow_service,
                SessionManagementService: self.mock_session_management_service,
                TaktAgent: self.mock_takt_agent,
            }
            return service_map.get(service_type)

        mock_container.get = mock_get

        # Create dispatcher with mocked container
        binder = RequestBinder()
        factory = GenericActionFactory(mock_container)
        mock_dispatcher = ActionDispatcher(binder, factory)

        # Patch get_dispatcher to return our mock dispatcher
        self.dispatcher_patcher = patch(
            "pipe.web.dispatcher.get_dispatcher", return_value=mock_dispatcher
        )

        self.patcher.start()
        self.workflow_patcher.start()
        self.management_patcher.start()
        self.dispatcher_patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.workflow_patcher.stop()
        self.management_patcher.stop()
        self.dispatcher_patcher.stop()

    def test_get_session_api_success(self):
        """Tests successfully getting a single session via API."""
        session_id = "test_id"
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

    def test_create_new_session_api_success(self):
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
        self.mock_takt_agent.run_existing_session.assert_called_once()

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
