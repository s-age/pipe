"""Unit tests for DeleteTurnRequest."""

from unittest.mock import patch

import pytest
from pipe.web.exceptions import BadRequestError, NotFoundError
from pipe.web.requests.sessions.delete_turn import DeleteTurnRequest

from tests.factories.models import SessionFactory


class TestDeleteTurnRequest:
    """Tests for DeleteTurnRequest model."""

    def test_validate_turn_index_valid(self):
        """Test that valid turn_index is accepted."""
        with patch(
            "pipe.web.service_container.get_session_service"
        ) as mock_get_service:
            mock_session = SessionFactory.create_with_turns(turn_count=3)
            mock_get_service.return_value.get_session.return_value = mock_session

            request = DeleteTurnRequest.create_with_path_params(
                path_params={"session_id": "test-session", "turn_index": "1"}
            )
            assert request.turn_index == 1
            assert request.session_id == "test-session"

    def test_validate_turn_index_invalid(self):
        """Test that invalid turn_index raises BadRequestError."""
        with pytest.raises(BadRequestError, match="turn_index must be an integer"):
            DeleteTurnRequest.create_with_path_params(
                path_params={"session_id": "test-session", "turn_index": "invalid"}
            )

    def test_validate_turn_exists_session_not_found(self):
        """Test that NotFoundError is raised when session does not exist."""
        with patch(
            "pipe.web.service_container.get_session_service"
        ) as mock_get_service:
            mock_get_service.return_value.get_session.return_value = None

            with pytest.raises(NotFoundError, match="Session not found."):
                DeleteTurnRequest.create_with_path_params(
                    path_params={"session_id": "non-existent", "turn_index": 0}
                )

    def test_validate_turn_exists_index_out_of_range_negative(self):
        """Test that BadRequestError is raised when turn_index is negative."""
        with patch(
            "pipe.web.service_container.get_session_service"
        ) as mock_get_service:
            mock_session = SessionFactory.create_with_turns(turn_count=3)
            mock_get_service.return_value.get_session.return_value = mock_session

            with pytest.raises(BadRequestError, match="Turn index out of range."):
                DeleteTurnRequest.create_with_path_params(
                    path_params={"session_id": "test-session", "turn_index": -1}
                )

    def test_validate_turn_exists_index_out_of_range_too_high(self):
        """Test that BadRequestError is raised when turn_index is out of range."""
        with patch(
            "pipe.web.service_container.get_session_service"
        ) as mock_get_service:
            mock_session = SessionFactory.create_with_turns(turn_count=3)
            mock_get_service.return_value.get_session.return_value = mock_session

            with pytest.raises(BadRequestError, match="Turn index out of range."):
                DeleteTurnRequest.create_with_path_params(
                    path_params={"session_id": "test-session", "turn_index": 3}
                )

    def test_create_with_path_params_success(self):
        """Test successful creation with path parameters."""
        with patch(
            "pipe.web.service_container.get_session_service"
        ) as mock_get_service:
            mock_session = SessionFactory.create_with_turns(turn_count=3)
            mock_get_service.return_value.get_session.return_value = mock_session

            request = DeleteTurnRequest.create_with_path_params(
                path_params={"session_id": "test-session", "turn_index": 2}
            )
            assert request.session_id == "test-session"
            assert request.turn_index == 2
