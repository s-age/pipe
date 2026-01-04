"""Unit tests for EditReferencePersistRequest."""

from unittest.mock import patch

import pytest
from pipe.web.exceptions import BadRequestError, NotFoundError
from pipe.web.requests.sessions.edit_reference_persist import (
    EditReferencePersistRequest,
)

from tests.factories.models.reference_factory import ReferenceFactory
from tests.factories.models.session_factory import SessionFactory


class TestEditReferencePersistRequest:
    """Tests for the EditReferencePersistRequest model."""

    @pytest.fixture
    def mock_session_service(self):
        """Mock session service."""
        with patch("pipe.web.service_container.get_session_service") as mock:
            yield mock

    def test_valid_initialization(self, mock_session_service):
        """Test valid initialization with all required fields."""
        session = SessionFactory.create(
            session_id="test-session",
            references=ReferenceFactory.create_batch(2),
        )
        mock_session_service.return_value.get_session.return_value = session

        request = EditReferencePersistRequest(
            session_id="test-session", reference_index=1, persist=True
        )

        assert request.session_id == "test-session"
        assert request.reference_index == 1
        assert request.persist is True

    def test_camel_case_normalization(self, mock_session_service):
        """Test that camelCase keys are normalized to snake_case."""
        session = SessionFactory.create(
            session_id="test-session",
            references=ReferenceFactory.create_batch(1),
        )
        mock_session_service.return_value.get_session.return_value = session

        data = {"sessionId": "test-session", "referenceIndex": 0, "persist": True}

        # Note: EditReferencePersistRequest.normalize_keys is called before field validation
        request = EditReferencePersistRequest.model_validate(data)

        assert request.session_id == "test-session"
        assert request.reference_index == 0
        assert request.persist is True

    def test_reference_index_conversion(self, mock_session_service):
        """Test that reference_index is converted from string to integer."""
        session = SessionFactory.create(
            session_id="test-session",
            references=ReferenceFactory.create_batch(2),
        )
        mock_session_service.return_value.get_session.return_value = session

        request = EditReferencePersistRequest(
            session_id="test-session",
            reference_index="1",  # String input
            persist=True,
        )

        assert request.reference_index == 1
        assert isinstance(request.reference_index, int)

    def test_invalid_reference_index_type(self):
        """Test that invalid reference_index type raises BadRequestError."""
        with pytest.raises(BadRequestError, match="reference_index must be an integer"):
            EditReferencePersistRequest(
                session_id="test-session", reference_index="abc", persist=True
            )

    def test_session_not_found(self, mock_session_service):
        """Test that NotFoundError is raised when session does not exist."""
        mock_session_service.return_value.get_session.return_value = None

        with pytest.raises(NotFoundError, match="Session not found."):
            EditReferencePersistRequest(
                session_id="non-existent", reference_index=0, persist=True
            )

    def test_reference_index_out_of_range_negative(self, mock_session_service):
        """Test that negative reference_index raises BadRequestError."""
        session = SessionFactory.create(
            session_id="test-session",
            references=ReferenceFactory.create_batch(1),
        )
        mock_session_service.return_value.get_session.return_value = session

        with pytest.raises(BadRequestError, match="Reference index out of range."):
            EditReferencePersistRequest(
                session_id="test-session", reference_index=-1, persist=True
            )

    def test_reference_index_out_of_range_too_large(self, mock_session_service):
        """Test that too large reference_index raises BadRequestError."""
        session = SessionFactory.create(
            session_id="test-session",
            references=ReferenceFactory.create_batch(1),
        )
        mock_session_service.return_value.get_session.return_value = session

        with pytest.raises(BadRequestError, match="Reference index out of range."):
            EditReferencePersistRequest(
                session_id="test-session",
                reference_index=1,  # Only 1 reference (index 0)
                persist=True,
            )

    def test_create_with_path_params(self, mock_session_service):
        """Test creation using path parameters and body data."""
        session = SessionFactory.create(
            session_id="test-session",
            references=ReferenceFactory.create_batch(1),
        )
        mock_session_service.return_value.get_session.return_value = session

        path_params = {"session_id": "test-session", "reference_index": 0}
        body_data = {"persist": False}

        request = EditReferencePersistRequest.create_with_path_params(
            path_params=path_params, body_data=body_data
        )

        assert request.session_id == "test-session"
        assert request.reference_index == 0
        assert request.persist is False
