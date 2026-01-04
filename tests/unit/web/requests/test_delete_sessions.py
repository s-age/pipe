"""
Unit tests for delete sessions request models.
"""

import pytest
from pipe.web.requests.sessions.delete_sessions import (
    DeleteBackupRequest,
    DeleteSessionsRequest,
)
from pydantic import ValidationError


class TestDeleteSessionsRequest:
    """Tests for DeleteSessionsRequest model."""

    def test_valid_initialization(self):
        """Test valid initialization with session_ids."""
        session_ids = ["session-1", "session-2"]
        request = DeleteSessionsRequest(session_ids=session_ids)
        assert request.session_ids == session_ids

    def test_missing_session_ids(self):
        """Test that missing session_ids raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            DeleteSessionsRequest()  # type: ignore[call-arg]

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("session_ids",) for error in errors)
        assert any(error["type"] == "missing" for error in errors)

    def test_extra_fields_forbidden(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValidationError) as exc_info:
            DeleteSessionsRequest(session_ids=["s1"], extra_field="not_allowed")  # type: ignore[call-arg]

        errors = exc_info.value.errors()
        assert any(error["type"] == "extra_forbidden" for error in errors)


class TestDeleteBackupRequest:
    """Tests for DeleteBackupRequest model."""

    def test_valid_with_session_ids(self):
        """Test valid initialization with session_ids only."""
        session_ids = ["session-1"]
        request = DeleteBackupRequest(session_ids=session_ids)
        assert request.session_ids == session_ids
        assert request.file_paths is None

    def test_valid_with_file_paths(self):
        """Test valid initialization with file_paths only."""
        file_paths = ["/path/to/backup1"]
        request = DeleteBackupRequest(file_paths=file_paths)
        assert request.file_paths == file_paths
        assert request.session_ids is None

    def test_neither_provided_raises_error(self):
        """Test that providing neither session_ids nor file_paths raises ValueError."""
        with pytest.raises(ValidationError) as exc_info:
            DeleteBackupRequest()

        errors = exc_info.value.errors()
        # model_post_init raises ValueError which Pydantic wraps in ValidationError
        assert any(
            "Either session_ids or file_paths must be provided" in str(error["msg"])
            for error in errors
        )

    def test_both_provided_raises_error(self):
        """Test that providing both session_ids and file_paths raises ValueError."""
        with pytest.raises(ValidationError) as exc_info:
            DeleteBackupRequest(session_ids=["s1"], file_paths=["p1"])

        errors = exc_info.value.errors()
        assert any(
            "Cannot provide both session_ids and file_paths" in str(error["msg"])
            for error in errors
        )

    def test_extra_fields_forbidden(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValidationError) as exc_info:
            DeleteBackupRequest(session_ids=["s1"], extra_field="not_allowed")  # type: ignore[call-arg]

        errors = exc_info.value.errors()
        assert any(error["type"] == "extra_forbidden" for error in errors)
