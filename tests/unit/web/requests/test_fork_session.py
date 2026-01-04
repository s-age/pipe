"""
Unit tests for ForkSessionRequest.
"""

from unittest.mock import MagicMock, patch

import pytest
from pipe.web.exceptions import BadRequestError, NotFoundError
from pipe.web.requests.sessions.fork_session import ForkSessionRequest

from tests.factories.models.session_factory import SessionFactory


class TestForkSessionRequest:
    """Tests for ForkSessionRequest model."""

    @patch("pipe.web.requests.sessions.fork_session.normalize_camel_case_keys")
    def test_normalize_keys(self, mock_normalize: MagicMock) -> None:
        """Test that normalize_keys calls normalize_camel_case_keys."""
        data = {"sessionId": "test-123", "forkIndex": 5}
        mock_normalize.return_value = {"session_id": "test-123", "fork_index": 5}

        # We need to mock get_session_service to avoid validation error in model_validator(mode="after")
        with patch(
            "pipe.web.service_container.get_session_service"
        ) as mock_get_service:
            mock_session = MagicMock()
            mock_session.turns = [MagicMock()] * 10
            mock_get_service.return_value.get_session.return_value = mock_session

            request = ForkSessionRequest.model_validate(data)

            assert request.session_id == "test-123"
            assert request.fork_index == 5
            mock_normalize.assert_called_with(data)

    def test_validate_fork_index_valid_string(self) -> None:
        """Test that fork_index as a string integer is converted."""
        with patch(
            "pipe.web.service_container.get_session_service"
        ) as mock_get_service:
            mock_session = MagicMock()
            mock_session.turns = [MagicMock()] * 5
            mock_get_service.return_value.get_session.return_value = mock_session

            # Use type: ignore because we are intentionally passing a string to an int field for testing the validator
            request = ForkSessionRequest(session_id="test", fork_index="2")  # type: ignore
            assert request.fork_index == 2

    def test_validate_fork_index_invalid(self) -> None:
        """Test that invalid fork_index raises BadRequestError."""
        with pytest.raises(BadRequestError, match="fork_index must be an integer"):
            ForkSessionRequest(session_id="test", fork_index="abc")  # type: ignore

    def test_validate_fork_possible_success(self) -> None:
        """Test successful validation when session exists and index is valid."""
        with patch(
            "pipe.web.service_container.get_session_service"
        ) as mock_get_service:
            mock_session = SessionFactory.create_with_turns(turn_count=5)
            mock_get_service.return_value.get_session.return_value = mock_session

            request = ForkSessionRequest(session_id="test-session", fork_index=2)
            assert request.session_id == "test-session"
            assert request.fork_index == 2
            mock_get_service.return_value.get_session.assert_called_once_with(
                "test-session"
            )

    def test_validate_fork_possible_session_not_found(self) -> None:
        """Test that NotFoundError is raised if session does not exist."""
        with patch(
            "pipe.web.service_container.get_session_service"
        ) as mock_get_service:
            mock_get_service.return_value.get_session.return_value = None

            with pytest.raises(NotFoundError, match="Session not found."):
                ForkSessionRequest(session_id="non-existent", fork_index=0)

    def test_validate_fork_possible_index_out_of_range_low(self) -> None:
        """Test that BadRequestError is raised if fork_index < 0."""
        with patch(
            "pipe.web.service_container.get_session_service"
        ) as mock_get_service:
            mock_session = SessionFactory.create_with_turns(turn_count=5)
            mock_get_service.return_value.get_session.return_value = mock_session

            with pytest.raises(BadRequestError, match="Fork index out of range."):
                ForkSessionRequest(session_id="test", fork_index=-1)

    def test_validate_fork_possible_index_out_of_range_high(self) -> None:
        """Test that BadRequestError is raised if fork_index >= len(turns)."""
        with patch(
            "pipe.web.service_container.get_session_service"
        ) as mock_get_service:
            mock_session = SessionFactory.create_with_turns(turn_count=3)
            mock_get_service.return_value.get_session.return_value = mock_session

            with pytest.raises(BadRequestError, match="Fork index out of range."):
                ForkSessionRequest(session_id="test", fork_index=3)

    def test_create_with_path_params(self) -> None:
        """Test create_with_path_params merges data correctly."""
        path_params = {"session_id": "path-session", "fork_index": "1"}

        with patch(
            "pipe.web.service_container.get_session_service"
        ) as mock_get_service:
            mock_session = SessionFactory.create_with_turns(turn_count=5)
            mock_get_service.return_value.get_session.return_value = mock_session

            request = ForkSessionRequest.create_with_path_params(
                path_params=path_params
            )

            assert request.session_id == "path-session"
            assert request.fork_index == 1
