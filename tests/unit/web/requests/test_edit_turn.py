"""
Unit tests for the EditTurnRequest model.
"""

from unittest.mock import patch

import pytest
from pipe.web.exceptions import BadRequestError, NotFoundError
from pipe.web.requests.sessions.edit_turn import EditTurnRequest
from pydantic import ValidationError

from tests.factories.models import SessionFactory, TurnFactory


class TestEditTurnRequest:
    """Tests for the EditTurnRequest model."""

    def test_initialization_success(self):
        """Test successful initialization with all fields."""
        # We need to mock get_session_service for the model_validator(mode="after")
        # Since it's a function-level import, we patch the source module.
        with patch(
            "pipe.web.service_container.get_session_service"
        ) as mock_get_service:
            mock_session = SessionFactory.create(turns=TurnFactory.create_batch(2))
            mock_get_service.return_value.get_session.return_value = mock_session

            request = EditTurnRequest(
                session_id="test-session",
                turn_index=0,
                content="New content",
                instruction="New instruction",
            )

            assert request.session_id == "test-session"
            assert request.turn_index == 0
            assert request.content == "New content"
            assert request.instruction == "New instruction"

    def test_normalize_keys(self):
        """Test that camelCase keys are normalized to snake_case."""
        with patch(
            "pipe.web.service_container.get_session_service"
        ) as mock_get_service:
            mock_session = SessionFactory.create(turns=TurnFactory.create_batch(1))
            mock_get_service.return_value.get_session.return_value = mock_session

            # Pydantic V2 model_validate handles the before validator
            data = {
                "sessionId": "test-session",
                "turnIndex": 0,
                "content": "New content",
            }
            request = EditTurnRequest.model_validate(data)

            assert request.session_id == "test-session"
            assert request.turn_index == 0
            assert request.content == "New content"

    def test_validate_turn_index_type_success(self):
        """Test that turn_index is correctly validated as an integer."""
        with patch(
            "pipe.web.service_container.get_session_service"
        ) as mock_get_service:
            mock_session = SessionFactory.create(turns=TurnFactory.create_batch(1))
            mock_get_service.return_value.get_session.return_value = mock_session

            request = EditTurnRequest(session_id="test-session", turn_index="0")
            assert request.turn_index == 0

    def test_validate_turn_index_type_failure(self):
        """Test that invalid turn_index type raises BadRequestError."""
        with pytest.raises(BadRequestError, match="turn_index must be an integer"):
            EditTurnRequest(session_id="test-session", turn_index="not-an-int")

    def test_validate_content_empty(self):
        """Test that empty content raises ValueError."""
        with pytest.raises(ValidationError) as exc_info:
            EditTurnRequest(session_id="test-session", turn_index=0, content="")

        assert "Content cannot be empty or only whitespace" in str(exc_info.value)

    def test_validate_content_whitespace(self):
        """Test that whitespace-only content raises ValueError."""
        with pytest.raises(ValidationError) as exc_info:
            EditTurnRequest(session_id="test-session", turn_index=0, content="   ")

        assert "Content cannot be empty or only whitespace" in str(exc_info.value)

    def test_validate_content_invalid_type(self):
        """Test that non-string content raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            EditTurnRequest(session_id="test-session", turn_index=0, content=123)  # type: ignore

        # Pydantic V2 built-in validation catches this before our custom validator
        assert "Input should be a valid string" in str(exc_info.value)

    def test_validate_instruction_empty(self):
        """Test that empty instruction raises ValueError."""
        with pytest.raises(ValidationError) as exc_info:
            EditTurnRequest(session_id="test-session", turn_index=0, instruction="")

        assert "Instruction cannot be empty or only whitespace" in str(exc_info.value)

    def test_validate_instruction_whitespace(self):
        """Test that whitespace-only instruction raises ValueError."""
        with pytest.raises(ValidationError) as exc_info:
            EditTurnRequest(session_id="test-session", turn_index=0, instruction="   ")

        assert "Instruction cannot be empty or only whitespace" in str(exc_info.value)

    def test_validate_instruction_invalid_type(self):
        """Test that non-string instruction raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            EditTurnRequest(session_id="test-session", turn_index=0, instruction=123)  # type: ignore

        # Pydantic V2 built-in validation catches this before our custom validator
        assert "Input should be a valid string" in str(exc_info.value)

    def test_validate_turn_exists_session_not_found(self):
        """Test that NotFoundError is raised if session does not exist."""
        with patch(
            "pipe.web.service_container.get_session_service"
        ) as mock_get_service:
            mock_get_service.return_value.get_session.return_value = None

            with pytest.raises(NotFoundError, match="Session not found."):
                EditTurnRequest(session_id="non-existent", turn_index=0)

    def test_validate_turn_exists_index_out_of_range_low(self):
        """Test that BadRequestError is raised if turn_index is negative."""
        with patch(
            "pipe.web.service_container.get_session_service"
        ) as mock_get_service:
            mock_session = SessionFactory.create(turns=TurnFactory.create_batch(1))
            mock_get_service.return_value.get_session.return_value = mock_session

            with pytest.raises(BadRequestError, match="Turn index out of range."):
                EditTurnRequest(session_id="test-session", turn_index=-1)

    def test_validate_turn_exists_index_out_of_range_high(self):
        """Test that BadRequestError is raised if turn_index is too large."""
        with patch(
            "pipe.web.service_container.get_session_service"
        ) as mock_get_service:
            mock_session = SessionFactory.create(turns=TurnFactory.create_batch(1))
            mock_get_service.return_value.get_session.return_value = mock_session

            with pytest.raises(BadRequestError, match="Turn index out of range."):
                EditTurnRequest(session_id="test-session", turn_index=1)

    def test_model_dump_excludes_none(self):
        """Test that model_dump excludes None values."""
        with patch(
            "pipe.web.service_container.get_session_service"
        ) as mock_get_service:
            mock_session = SessionFactory.create(turns=TurnFactory.create_batch(1))
            mock_get_service.return_value.get_session.return_value = mock_session

            request = EditTurnRequest(
                session_id="test-session", turn_index=0, content="New content"
            )
            dumped = request.model_dump()

            assert "content" in dumped
            assert "instruction" not in dumped
            assert dumped["content"] == "New content"

    def test_create_with_path_params(self):
        """Test creating request with path parameters and body data."""
        with patch(
            "pipe.web.service_container.get_session_service"
        ) as mock_get_service:
            mock_session = SessionFactory.create(turns=TurnFactory.create_batch(1))
            mock_get_service.return_value.get_session.return_value = mock_session

            path_params = {"session_id": "test-session", "turn_index": 0}
            body_data = {"content": "New content"}

            request = EditTurnRequest.create_with_path_params(path_params, body_data)

            assert isinstance(request, EditTurnRequest)
            assert request.session_id == "test-session"
            assert request.turn_index == 0
            assert request.content == "New content"
