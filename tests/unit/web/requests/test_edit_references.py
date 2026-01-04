"""Unit tests for EditReferencesRequest."""

import pytest
from pipe.core.models.reference import Reference
from pipe.web.requests.sessions.edit_references import EditReferencesRequest
from pydantic import ValidationError


class TestEditReferencesRequest:
    """Tests for the EditReferencesRequest model."""

    def test_valid_initialization(self):
        """Test initialization with valid snake_case data."""
        references = [
            Reference(path="src/main.py", disabled=False, ttl=3600, persist=True),
            Reference(path="README.md"),
        ]
        request = EditReferencesRequest(
            session_id="test-session-123",
            references=references,
        )
        assert request.session_id == "test-session-123"
        assert len(request.references) == 2
        assert request.references[0].path == "src/main.py"
        assert request.references[1].disabled is False

    def test_camel_case_normalization(self):
        """Test that camelCase keys are normalized to snake_case."""
        data = {
            "sessionId": "test-session-456",
            "references": [
                {
                    "path": "config.json",
                    "disabled": True,
                    "ttl": 60,
                    "persist": False,
                }
            ],
        }
        # EditReferencesRequest.model_validate will trigger normalize_keys
        request = EditReferencesRequest.model_validate(data)
        assert request.session_id == "test-session-456"
        assert request.references[0].path == "config.json"
        assert request.references[0].disabled is True

    def test_missing_session_id(self):
        """Test that missing session_id raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            EditReferencesRequest(references=[])

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("session_id",) and error["type"] == "missing"
            for error in errors
        )

    def test_missing_references(self):
        """Test that missing references raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            EditReferencesRequest(session_id="test-session")

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("references",) and error["type"] == "missing"
            for error in errors
        )

    def test_invalid_references_type(self):
        """Test that invalid references type raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            EditReferencesRequest(session_id="test-session", references="not-a-list")

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("references",) for error in errors)

    def test_invalid_reference_item(self):
        """Test that invalid reference item raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            EditReferencesRequest(
                session_id="test-session",
                references=[{"not_path": "oops"}],
            )

        errors = exc_info.value.errors()
        # Error should be in references[0].path
        assert any(error["loc"] == ("references", 0, "path") for error in errors)

    def test_create_with_path_params(self):
        """Test create_with_path_params merges path and body data."""
        path_params = {"session_id": "path-session-id"}
        body_data = {"references": [{"path": "file.txt"}]}
        request = EditReferencesRequest.create_with_path_params(
            path_params=path_params, body_data=body_data
        )
        assert request.session_id == "path-session-id"
        assert request.references[0].path == "file.txt"

    def test_extra_fields_forbidden(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValidationError) as exc_info:
            EditReferencesRequest(
                session_id="test", references=[], extra_field="not allowed"
            )

        errors = exc_info.value.errors()
        assert any(error["type"] == "extra_forbidden" for error in errors)

    def test_serialization(self):
        """Test serialization to dict."""
        references = [Reference(path="test.py")]
        request = EditReferencesRequest(
            session_id="test-session",
            references=references,
        )
        dumped = request.model_dump()
        assert dumped["session_id"] == "test-session"
        assert dumped["references"][0]["path"] == "test.py"
