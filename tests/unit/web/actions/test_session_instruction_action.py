"""Unit tests for SessionInstructionAction."""

from unittest.mock import MagicMock, patch

import pytest
from flask import Response
from pipe.web.actions.session.session_instruction_action import SessionInstructionAction
from pipe.web.requests.sessions.send_instruction import SendInstructionRequest


class TestSessionInstructionAction:
    """Unit tests for SessionInstructionAction."""

    @pytest.fixture
    def mock_session_service(self) -> MagicMock:
        """Fixture for mock SessionService."""
        return MagicMock()

    @pytest.fixture
    def mock_instruction_service(self) -> MagicMock:
        """Fixture for mock SessionInstructionService."""
        return MagicMock()

    @pytest.fixture
    def mock_request(self) -> MagicMock:
        """Fixture for mock SendInstructionRequest."""
        request = MagicMock(spec=SendInstructionRequest)
        request.session_id = "test-session"
        request.instruction = "test instruction"
        return request

    @pytest.fixture
    def action(
        self,
        mock_session_service: MagicMock,
        mock_instruction_service: MagicMock,
        mock_request: MagicMock,
    ) -> SessionInstructionAction:
        """Fixture for SessionInstructionAction instance."""
        return SessionInstructionAction(
            session_service=mock_session_service,
            session_instruction_service=mock_instruction_service,
            validated_request=mock_request,
        )

    def test_init(
        self,
        mock_session_service: MagicMock,
        mock_instruction_service: MagicMock,
        mock_request: MagicMock,
    ) -> None:
        """Test initialization of SessionInstructionAction."""
        action = SessionInstructionAction(
            session_service=mock_session_service,
            session_instruction_service=mock_instruction_service,
            validated_request=mock_request,
        )
        assert action.session_service == mock_session_service
        assert action.session_instruction_service == mock_instruction_service
        assert action.validated_request == mock_request

    def test_execute_request_missing(
        self, mock_session_service: MagicMock, mock_instruction_service: MagicMock
    ) -> None:
        """Test execute when validated_request is None."""
        action = SessionInstructionAction(
            session_service=mock_session_service,
            session_instruction_service=mock_instruction_service,
            validated_request=None,
        )

        response = action.execute()

        assert isinstance(response, Response)
        assert response.mimetype == "text/event-stream"

        # Consume the generator to check content
        content = list(response.response)
        assert len(content) == 1
        assert 'data: {"error": "Internal Error (Request Missing)"}\n\n' in content[0]

    def test_execute_session_not_found(
        self, action: SessionInstructionAction, mock_session_service: MagicMock
    ) -> None:
        """Test execute when session is not found."""
        mock_session_service.get_session.return_value = None

        response = action.execute()

        assert isinstance(response, Response)
        assert response.mimetype == "text/event-stream"

        content = list(response.response)
        assert len(content) == 1
        assert 'data: {"error": "Session not found"}\n\n' in content[0]
        mock_session_service.get_session.assert_called_once_with("test-session")

    @patch("pipe.web.actions.session.session_instruction_action.stream_with_context")
    def test_execute_success(
        self,
        mock_stream: MagicMock,
        action: SessionInstructionAction,
        mock_session_service: MagicMock,
        mock_instruction_service: MagicMock,
    ) -> None:
        """Test successful execution with streaming."""
        mock_session = MagicMock()
        mock_session_service.get_session.return_value = mock_session

        # Mock the stream service to return a generator
        def mock_stream_gen(session, instruction):
            yield {"type": "start"}
            yield {"content": "hello"}

        mock_instruction_service.execute_instruction_stream.side_effect = (
            mock_stream_gen
        )

        # Mock stream_with_context to just return the generator it receives
        mock_stream.side_effect = lambda x: x

        response = action.execute()

        assert isinstance(response, Response)
        assert response.mimetype == "text/event-stream"

        # Consume the generator
        content = list(response.response)
        assert len(content) == 2
        assert 'data: {"type": "start"}\n\n' in content[0]
        assert 'data: {"content": "hello"}\n\n' in content[1]

        mock_session_service.get_session.assert_called_once_with("test-session")
        mock_instruction_service.execute_instruction_stream.assert_called_once_with(
            mock_session, "test instruction"
        )
        mock_stream.assert_called_once()
