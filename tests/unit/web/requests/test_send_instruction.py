"""
Unit tests for SendInstructionRequest model.
"""

from unittest.mock import MagicMock, patch

import pytest
from pipe.web.exceptions import NotFoundError
from pipe.web.requests.sessions.send_instruction import SendInstructionRequest
from pydantic import ValidationError


class TestSendInstructionRequest:
    """Tests for SendInstructionRequest model."""

    @patch("pipe.web.service_container.get_session_service")
    def test_valid_request(self, mock_get_service: MagicMock) -> None:
        """Test valid request initialization."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.get_session.return_value = {"session_id": "test-123"}

        data = {"session_id": "test-123", "instruction": "Hello world"}
        request = SendInstructionRequest(**data)
        assert request.session_id == "test-123"
        assert request.instruction == "Hello world"
        mock_service.get_session.assert_called_once_with("test-123")

    @patch("pipe.web.service_container.get_session_service")
    def test_normalization(self, mock_get_service: MagicMock) -> None:
        """Test camelCase keys are normalized to snake_case."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.get_session.return_value = {"session_id": "test-123"}

        # sessionId (camelCase) should be normalized to session_id (snake_case)
        data = {"sessionId": "test-123", "instruction": "Test"}
        request = SendInstructionRequest(**data)
        assert request.session_id == "test-123"

    @pytest.mark.parametrize("invalid_instruction", ["", " ", "\n\t"])
    @patch("pipe.web.service_container.get_session_service")
    def test_empty_instruction(
        self, mock_get_service: MagicMock, invalid_instruction: str
    ) -> None:
        """Test that empty or whitespace instruction raises ValidationError."""
        data = {"session_id": "test-123", "instruction": invalid_instruction}
        with pytest.raises(ValidationError) as exc_info:
            SendInstructionRequest(**data)

        assert "instruction must not be empty" in str(exc_info.value)

    @patch("pipe.web.service_container.get_session_service")
    def test_session_not_found(self, mock_get_service: MagicMock) -> None:
        """Test that NotFoundError is raised when session does not exist."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.get_session.return_value = None

        data = {"session_id": "non-existent", "instruction": "Test"}
        with pytest.raises(NotFoundError, match="Session not found."):
            SendInstructionRequest(**data)

    @patch("pipe.web.service_container.get_session_service")
    def test_create_with_path_params(self, mock_get_service: MagicMock) -> None:
        """Test create_with_path_params merges data correctly."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.get_session.return_value = {"session_id": "path-123"}

        path_params = {"session_id": "path-123"}
        body_data = {"instruction": "Instruction from body"}

        request = SendInstructionRequest.create_with_path_params(
            path_params=path_params, body_data=body_data
        )

        assert request.session_id == "path-123"
        assert request.instruction == "Instruction from body"

    def test_missing_fields(self) -> None:
        """Test Pydantic validation for missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            # session_id is required, instruction is required
            SendInstructionRequest(session_id="test-123")  # type: ignore

        errors = exc_info.value.errors()
        assert any(
            err["loc"] == ("instruction",) and err["type"] == "missing"
            for err in errors
        )
