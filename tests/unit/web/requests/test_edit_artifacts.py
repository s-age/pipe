"""Unit tests for EditArtifactsRequest model."""

import pytest
from pipe.core.models.artifact import Artifact
from pipe.web.requests.sessions.edit_artifacts import EditArtifactsRequest
from pydantic import ValidationError


class TestEditArtifactsRequest:
    """Tests for the EditArtifactsRequest model."""

    def test_valid_initialization(self) -> None:
        """Test valid initialization with snake_case."""
        artifacts = [
            Artifact(path="src/main.py", contents="print('hello')"),
            Artifact(path="README.md", contents=None),
        ]
        request = EditArtifactsRequest(
            session_id="test-session-123", artifacts=artifacts
        )
        assert request.session_id == "test-session-123"
        assert len(request.artifacts) == 2
        assert request.artifacts[0].path == "src/main.py"
        assert request.artifacts[1].contents is None

    def test_initialization_with_camel_case(self) -> None:
        """Test initialization with camelCase keys (normalization)."""
        data = {
            "sessionId": "test-session-456",
            "artifacts": [{"path": "test.txt", "contents": "test content"}],
        }
        request = EditArtifactsRequest.model_validate(data)
        assert request.session_id == "test-session-456"
        assert len(request.artifacts) == 1
        assert request.artifacts[0].path == "test.txt"

    def test_missing_required_fields(self) -> None:
        """Test that missing required fields raise ValidationError."""
        # Missing artifacts
        with pytest.raises(ValidationError) as exc_info:
            EditArtifactsRequest(session_id="test-session")
        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("artifacts",) and error["type"] == "missing"
            for error in errors
        )

        # Missing session_id
        with pytest.raises(ValidationError) as exc_info:
            EditArtifactsRequest(artifacts=[])
        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("session_id",) and error["type"] == "missing"
            for error in errors
        )

    def test_invalid_artifact_data(self) -> None:
        """Test that invalid artifact data raises ValidationError."""
        # Artifact missing path
        data = {"session_id": "test-session", "artifacts": [{"contents": "no path"}]}
        with pytest.raises(ValidationError) as exc_info:
            EditArtifactsRequest.model_validate(data)
        errors = exc_info.value.errors()
        # loc will be ('artifacts', 0, 'path')
        assert any(
            error["loc"] == ("artifacts", 0, "path") and error["type"] == "missing"
            for error in errors
        )

    def test_extra_fields_forbidden(self) -> None:
        """Test that extra fields are forbidden."""
        with pytest.raises(ValidationError) as exc_info:
            EditArtifactsRequest(
                session_id="test-session", artifacts=[], extra_field="not allowed"
            )
        errors = exc_info.value.errors()
        assert any(error["type"] == "extra_forbidden" for error in errors)

    def test_create_with_path_params(self) -> None:
        """Test create_with_path_params method."""
        path_params = {"session_id": "path-session-789"}
        body_data = {"artifacts": [{"path": "app.py", "contents": "import os"}]}
        request = EditArtifactsRequest.create_with_path_params(
            path_params=path_params, body_data=body_data
        )
        assert request.session_id == "path-session-789"
        assert len(request.artifacts) == 1
        assert request.artifacts[0].path == "app.py"

    def test_serialization(self) -> None:
        """Test model_dump serialization."""
        request = EditArtifactsRequest(
            session_id="test-session", artifacts=[Artifact(path="test.py")]
        )
        dumped = request.model_dump()
        assert dumped["session_id"] == "test-session"
        assert dumped["artifacts"][0]["path"] == "test.py"
