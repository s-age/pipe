"""Unit tests for SessionStartAction."""

from unittest.mock import MagicMock

import pytest
from pipe.web.action_responses import SessionStartResponse
from pipe.web.actions.session.session_start_action import SessionStartAction
from pipe.web.requests.sessions.start_session import StartSessionRequest


class TestSessionStartAction:
    """Tests for SessionStartAction."""

    @pytest.fixture
    def mock_session_service(self) -> MagicMock:
        """Create a mock SessionService."""
        return MagicMock()

    @pytest.fixture
    def mock_takt_agent(self) -> MagicMock:
        """Create a mock TaktAgent."""
        return MagicMock()

    @pytest.fixture
    def mock_request(self) -> MagicMock:
        """Create a mock StartSessionRequest."""
        request = MagicMock(spec=StartSessionRequest)
        request.purpose = "test purpose"
        request.background = "test background"
        request.instruction = "test instruction"
        request.roles = ["role1"]
        request.multi_step_reasoning_enabled = True
        request.hyperparameters = None
        request.parent = "parent_id"
        request.artifacts = ["art1"]
        request.procedure = "proc1"
        request.references = None
        return request

    def test_init(
        self, mock_session_service: MagicMock, mock_takt_agent: MagicMock
    ) -> None:
        """Test initialization of SessionStartAction."""
        action = SessionStartAction(
            session_service=mock_session_service,
            takt_agent=mock_takt_agent,
        )
        assert action.session_service == mock_session_service
        assert action.takt_agent == mock_takt_agent

    def test_execute_success(
        self,
        mock_session_service: MagicMock,
        mock_takt_agent: MagicMock,
        mock_request: MagicMock,
    ) -> None:
        """Test successful execution of SessionStartAction."""
        # Setup
        mock_session = MagicMock()
        mock_session.session_id = "new_session_id"
        mock_session_service.create_new_session.return_value = mock_session

        action = SessionStartAction(
            session_service=mock_session_service,
            takt_agent=mock_takt_agent,
            validated_request=mock_request,
        )

        # Execute
        response = action.execute()

        # Verify
        assert isinstance(response, SessionStartResponse)
        assert response.session_id == "new_session_id"

        mock_session_service.create_new_session.assert_called_once_with(
            purpose=mock_request.purpose,
            background=mock_request.background,
            roles=mock_request.roles,
            multi_step_reasoning_enabled=mock_request.multi_step_reasoning_enabled,
            hyperparameters=mock_request.hyperparameters,
            parent_id=mock_request.parent,
            artifacts=mock_request.artifacts,
            procedure=mock_request.procedure,
        )

        mock_takt_agent.run_existing_session.assert_called_once_with(
            session_id="new_session_id",
            instruction=mock_request.instruction,
            output_format="stream-json",
            multi_step_reasoning=mock_request.multi_step_reasoning_enabled,
            references=None,
            artifacts=mock_request.artifacts,
            procedure=mock_request.procedure,
        )

    def test_execute_with_references(
        self,
        mock_session_service: MagicMock,
        mock_takt_agent: MagicMock,
        mock_request: MagicMock,
    ) -> None:
        """Test execution with references."""
        # Setup
        mock_session = MagicMock()
        mock_session.session_id = "new_session_id"
        mock_session_service.create_new_session.return_value = mock_session

        mock_ref = MagicMock()
        mock_ref.path = "path/to/ref"
        mock_request.references = [mock_ref]

        action = SessionStartAction(
            session_service=mock_session_service,
            takt_agent=mock_takt_agent,
            validated_request=mock_request,
        )

        # Execute
        action.execute()

        # Verify
        mock_takt_agent.run_existing_session.assert_called_once()
        call_args = mock_takt_agent.run_existing_session.call_args[1]
        assert call_args["references"] == ["path/to/ref"]

    def test_execute_no_request(
        self, mock_session_service: MagicMock, mock_takt_agent: MagicMock
    ) -> None:
        """Test execute raises ValueError when validated_request is missing."""
        action = SessionStartAction(
            session_service=mock_session_service,
            takt_agent=mock_takt_agent,
            validated_request=None,
        )

        with pytest.raises(ValueError, match="Request is required"):
            action.execute()
