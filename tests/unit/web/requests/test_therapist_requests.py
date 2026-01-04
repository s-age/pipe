"""Tests for therapist request models."""

import pytest
from pipe.core.models.session_optimization import (
    SessionModifications,
    TurnCompression,
    TurnEdit,
)
from pipe.web.requests.therapist_requests import (
    ApplyDoctorRequest,
    CreateTherapistRequest,
)
from pydantic import ValidationError


class TestCreateTherapistRequest:
    """Tests for the CreateTherapistRequest model."""

    def test_initialization_with_snake_case(self):
        """Test that the request can be initialized using snake_case field names."""
        request = CreateTherapistRequest(session_id="test-session-123")
        assert request.session_id == "test-session-123"

    def test_serialization(self):
        """Test that model_dump() returns the correct structure."""
        request = CreateTherapistRequest(session_id="test-session-789")
        dumped = request.model_dump()
        assert "session_id" in dumped
        assert dumped["session_id"] == "test-session-789"

    def test_deserialization_from_snake_case(self):
        """Test that the request can be validated from a dictionary with snake_case keys."""
        data = {"session_id": "test-session-abc"}
        request = CreateTherapistRequest.model_validate(data)
        assert request.session_id == "test-session-abc"

    def test_missing_session_id_raises_validation_error(self):
        """Test that missing session_id raises a ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            CreateTherapistRequest()

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("session_id",)
        assert errors[0]["type"] == "missing"

    def test_empty_string_session_id(self):
        """Test that empty string is accepted for session_id."""
        request = CreateTherapistRequest(session_id="")
        assert request.session_id == ""

    def test_create_with_path_params(self):
        """Test creating request with path parameters."""
        request = CreateTherapistRequest.create_with_path_params(
            path_params={}, body_data={"session_id": "body-session-123"}
        )
        assert request.session_id == "body-session-123"

    def test_create_with_path_params_and_body(self):
        """Test creating request with body data only."""
        request = CreateTherapistRequest.create_with_path_params(
            path_params={},
            body_data={"session_id": "body-session-789"},
        )
        assert request.session_id == "body-session-789"


class TestApplyDoctorRequest:
    """Tests for the ApplyDoctorRequest model."""

    def test_initialization_with_snake_case(self):
        """Test that the request can be initialized using snake_case field names."""
        modifications = SessionModifications(
            deletions=[1, 2],
            edits=[TurnEdit(turn=3, new_content="Updated content")],
            compressions=[TurnCompression(start=5, end=10, reason="Compress test")],
        )
        request = ApplyDoctorRequest(
            session_id="test-session-123", modifications=modifications
        )
        assert request.session_id == "test-session-123"
        assert request.modifications == modifications

    def test_initialization_with_dict_modifications(self):
        """Test that the request can be initialized with dict modifications."""
        request = ApplyDoctorRequest(
            session_id="test-session-456",
            modifications={
                "deletions": [1, 2],
                "edits": [{"turn": 3, "new_content": "Updated"}],
                "compressions": [{"start": 5, "end": 10, "reason": "Test"}],
            },
        )
        assert request.session_id == "test-session-456"
        assert len(request.modifications.deletions) == 2
        assert len(request.modifications.edits) == 1
        assert len(request.modifications.compressions) == 1

    def test_serialization(self):
        """Test that model_dump() returns the correct structure."""
        modifications = SessionModifications(deletions=[1], edits=[], compressions=[])
        request = ApplyDoctorRequest(
            session_id="test-session-789", modifications=modifications
        )
        dumped = request.model_dump()
        assert "session_id" in dumped
        assert dumped["session_id"] == "test-session-789"
        assert "modifications" in dumped
        assert "deletions" in dumped["modifications"]

    def test_deserialization_from_snake_case(self):
        """Test that the request can be validated from a dictionary with snake_case keys."""
        data = {
            "session_id": "test-session-abc",
            "modifications": {
                "deletions": [1, 2, 3],
                "edits": [{"turn": 1, "new_content": "New"}],
                "compressions": [],
            },
        }
        request = ApplyDoctorRequest.model_validate(data)
        assert request.session_id == "test-session-abc"
        assert request.modifications.deletions == [1, 2, 3]
        assert len(request.modifications.edits) == 1
        assert request.modifications.edits[0].turn == 1
        assert request.modifications.edits[0].new_content == "New"

    def test_missing_session_id_raises_validation_error(self):
        """Test that missing session_id raises a ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ApplyDoctorRequest(
                modifications={"deletions": [], "edits": [], "compressions": []}
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("session_id",) for error in errors)

    def test_missing_modifications_raises_validation_error(self):
        """Test that missing modifications raises a ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ApplyDoctorRequest(session_id="test-session-123")

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("modifications",) for error in errors)

    def test_empty_modifications(self):
        """Test that empty modifications are accepted."""
        request = ApplyDoctorRequest(
            session_id="test-session-123",
            modifications={"deletions": [], "edits": [], "compressions": []},
        )
        assert request.modifications.deletions == []
        assert request.modifications.edits == []
        assert request.modifications.compressions == []

    def test_complex_modifications(self):
        """Test with complex modifications containing multiple items."""
        data = {
            "session_id": "test-session-complex",
            "modifications": {
                "deletions": [1, 3, 5, 7],
                "edits": [
                    {"turn": 2, "new_content": "First edit"},
                    {"turn": 4, "new_content": "Second edit"},
                    {"turn": 6, "new_content": "Third edit"},
                ],
                "compressions": [
                    {"start": 10, "end": 15, "reason": "First compression"},
                    {"start": 20, "end": 25, "reason": "Second compression"},
                ],
            },
        }
        request = ApplyDoctorRequest.model_validate(data)
        assert request.session_id == "test-session-complex"
        assert len(request.modifications.deletions) == 4
        assert len(request.modifications.edits) == 3
        assert len(request.modifications.compressions) == 2
        assert request.modifications.edits[1].new_content == "Second edit"
        assert request.modifications.compressions[0].start == 10

    def test_create_with_path_params(self):
        """Test creating request with path parameters and body data."""
        request = ApplyDoctorRequest.create_with_path_params(
            path_params={},
            body_data={
                "session_id": "body-session-123",
                "modifications": {"deletions": [], "edits": [], "compressions": []},
            },
        )
        assert request.session_id == "body-session-123"

    def test_create_with_body_data_only(self):
        """Test creating request with body data only."""
        request = ApplyDoctorRequest.create_with_path_params(
            path_params={},
            body_data={
                "session_id": "body-session",
                "modifications": {"deletions": [1], "edits": [], "compressions": []},
            },
        )
        assert request.session_id == "body-session"

    def test_forbid_extra_fields(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValidationError) as exc_info:
            ApplyDoctorRequest(
                session_id="test-session",
                modifications={"deletions": [], "edits": [], "compressions": []},
                extra_field="not_allowed",
            )

        errors = exc_info.value.errors()
        assert any(error["type"] == "extra_forbidden" for error in errors)
