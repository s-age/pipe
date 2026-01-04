"""Unit tests for EditReferenceTtlRequest."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.web.exceptions import BadRequestError, NotFoundError
from pipe.web.requests.sessions.edit_reference_ttl import EditReferenceTtlRequest
from pydantic import ValidationError


class TestEditReferenceTtlRequest:
    """Tests for the EditReferenceTtlRequest model."""

    @pytest.fixture
    def mock_session_service(self):
        """Fixture to mock the session service."""
        with patch("pipe.web.service_container.get_session_service") as mock_get:
            mock_service = MagicMock()
            mock_get.return_value = mock_service
            yield mock_service

    def test_valid_request(self, mock_session_service):
        """Test initialization with valid data."""
        # Setup mock session with references
        mock_session = MagicMock()
        mock_session.references = [MagicMock(), MagicMock()]
        mock_session_service.get_session.return_value = mock_session

        data = {"session_id": "test-session", "reference_index": 1, "ttl": 3600}
        request = EditReferenceTtlRequest(**data)

        assert request.session_id == "test-session"
        assert request.reference_index == 1
        assert request.ttl == 3600
        mock_session_service.get_session.assert_called_once_with("test-session")

    def test_camel_case_normalization(self, mock_session_service):
        """Test that camelCase keys are normalized to snake_case."""
        mock_session = MagicMock()
        mock_session.references = [MagicMock()]
        mock_session_service.get_session.return_value = mock_session

        data = {"sessionId": "test-session", "referenceIndex": 0, "ttl": 100}
        request = EditReferenceTtlRequest(**data)

        assert request.session_id == "test-session"
        assert request.reference_index == 0
        assert request.ttl == 100

    def test_negative_ttl_raises_error(self, mock_session_service):
        """Test that negative TTL raises a ValidationError."""
        data = {"session_id": "test-session", "reference_index": 0, "ttl": -1}
        with pytest.raises(ValidationError) as exc_info:
            EditReferenceTtlRequest(**data)

        assert "ttl" in str(exc_info.value)

    def test_invalid_reference_index_type(self, mock_session_service):
        """Test that non-integer reference_index raises BadRequestError."""
        data = {
            "session_id": "test-session",
            "reference_index": "not-an-int",
            "ttl": 100,
        }
        with pytest.raises(BadRequestError, match="reference_index must be an integer"):
            EditReferenceTtlRequest(**data)

    def test_session_not_found(self, mock_session_service):
        """Test that NotFoundError is raised if session does not exist."""
        mock_session_service.get_session.return_value = None

        data = {"session_id": "non-existent", "reference_index": 0, "ttl": 100}
        with pytest.raises(NotFoundError, match="Session not found."):
            EditReferenceTtlRequest(**data)

    def test_reference_index_out_of_range_low(self, mock_session_service):
        """Test that BadRequestError is raised if reference_index is negative."""
        mock_session = MagicMock()
        mock_session.references = [MagicMock()]
        mock_session_service.get_session.return_value = mock_session

        data = {"session_id": "test-session", "reference_index": -1, "ttl": 100}
        with pytest.raises(BadRequestError, match="Reference index out of range."):
            EditReferenceTtlRequest(**data)

    def test_reference_index_out_of_range_high(self, mock_session_service):
        """Test that BadRequestError is raised if reference_index is too high."""
        mock_session = MagicMock()
        mock_session.references = [MagicMock()]  # Only 1 reference (index 0)
        mock_session_service.get_session.return_value = mock_session

        data = {"session_id": "test-session", "reference_index": 1, "ttl": 100}
        with pytest.raises(BadRequestError, match="Reference index out of range."):
            EditReferenceTtlRequest(**data)

    def test_create_with_path_params(self, mock_session_service):
        """Test create_with_path_params method."""
        mock_session = MagicMock()
        mock_session.references = [MagicMock()]
        mock_session_service.get_session.return_value = mock_session

        path_params = {"session_id": "test-session", "reference_index": 0}
        body_data = {"ttl": 500}

        request = EditReferenceTtlRequest.create_with_path_params(
            path_params, body_data
        )

        assert request.session_id == "test-session"
        assert request.reference_index == 0
        assert request.ttl == 500
