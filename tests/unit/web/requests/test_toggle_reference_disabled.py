"""Unit tests for ToggleReferenceDisabledRequest."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.web.exceptions import BadRequestError, NotFoundError
from pipe.web.requests.sessions.toggle_reference_disabled import (
    ToggleReferenceDisabledRequest,
)


class TestToggleReferenceDisabledRequest:
    """Tests for ToggleReferenceDisabledRequest."""

    @patch("pipe.web.service_container.get_session_service")
    def test_valid_request(self, mock_get_service: MagicMock) -> None:
        """Test valid request with existing session and reference."""
        mock_session = MagicMock()
        mock_session.references = [MagicMock(), MagicMock()]
        mock_get_service.return_value.get_session.return_value = mock_session

        request = ToggleReferenceDisabledRequest(
            session_id="test-session", reference_index=1
        )
        assert request.session_id == "test-session"
        assert request.reference_index == 1

    def test_invalid_reference_index_type(self) -> None:
        """Test that non-integer reference_index raises BadRequestError."""
        with pytest.raises(BadRequestError, match="reference_index must be an integer"):
            ToggleReferenceDisabledRequest(
                session_id="test-session", reference_index="not-an-int"
            )

    @patch("pipe.web.service_container.get_session_service")
    def test_session_not_found(self, mock_get_service: MagicMock) -> None:
        """Test that NotFoundError is raised when session does not exist."""
        mock_get_service.return_value.get_session.return_value = None

        with pytest.raises(NotFoundError, match="Session not found."):
            ToggleReferenceDisabledRequest(session_id="non-existent", reference_index=0)

    @patch("pipe.web.service_container.get_session_service")
    def test_reference_index_out_of_range_negative(
        self, mock_get_service: MagicMock
    ) -> None:
        """Test that BadRequestError is raised when reference_index is negative."""
        mock_session = MagicMock()
        mock_session.references = [MagicMock()]
        mock_get_service.return_value.get_session.return_value = mock_session

        with pytest.raises(BadRequestError, match="Reference index out of range."):
            ToggleReferenceDisabledRequest(
                session_id="test-session", reference_index=-1
            )

    @patch("pipe.web.service_container.get_session_service")
    def test_reference_index_out_of_range_positive(
        self, mock_get_service: MagicMock
    ) -> None:
        """Test that BadRequestError is raised when reference_index is out of range."""
        mock_session = MagicMock()
        mock_session.references = [MagicMock()]
        mock_get_service.return_value.get_session.return_value = mock_session

        with pytest.raises(BadRequestError, match="Reference index out of range."):
            ToggleReferenceDisabledRequest(session_id="test-session", reference_index=1)

    @patch("pipe.web.service_container.get_session_service")
    def test_create_with_path_params(self, mock_get_service: MagicMock) -> None:
        """Test creating request with path parameters."""
        mock_session = MagicMock()
        mock_session.references = [MagicMock()]
        mock_get_service.return_value.get_session.return_value = mock_session

        path_params = {"session_id": "test-session", "reference_index": "0"}
        request = ToggleReferenceDisabledRequest.create_with_path_params(path_params)

        assert request.session_id == "test-session"
        assert request.reference_index == 0
