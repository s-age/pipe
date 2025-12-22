import pytest
from pipe.core.models.search_result import SessionSearchResult
from pydantic import ValidationError

from tests.helpers.search_result_factory import SearchResultFactory


class TestSessionSearchResult:
    """SessionSearchResult model validation and serialization tests."""

    def test_valid_creation(self):
        """Test creating a valid SessionSearchResult with all fields."""
        result = SearchResultFactory.create_session_search_result(
            session_id="session-1",
            title="Project Alpha",
            path="/tmp/sessions/session-1.json",
        )
        assert result.session_id == "session-1"
        assert result.title == "Project Alpha"
        assert result.path == "/tmp/sessions/session-1.json"

    def test_default_values(self):
        """Test default values for SessionSearchResult."""
        # path is optional and defaults to None
        result = SessionSearchResult(
            session_id="session-2",
            title="Minimal Session",
        )
        assert result.path is None

    def test_validation_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        # Missing session_id (alias: sessionId)
        with pytest.raises(ValidationError) as exc_info:
            SessionSearchResult(title="Missing ID")
        assert "sessionId" in str(exc_info.value)

        # Missing title
        with pytest.raises(ValidationError) as exc_info:
            SessionSearchResult(session_id="missing-title")
        assert "title" in str(exc_info.value)

    def test_model_dump_with_aliases(self):
        """Test serialization with by_alias=True for camelCase conversion."""
        result = SearchResultFactory.create_session_search_result(
            session_id="test-id",
            title="Test Title",
        )

        # Use by_alias=True to get camelCase field names
        dumped = result.model_dump(by_alias=True)
        assert dumped["sessionId"] == "test-id"  # snake_case -> camelCase
        assert dumped["title"] == "Test Title"
        assert "path" in dumped

        # Without by_alias=True, field names remain snake_case
        dumped_no_alias = result.model_dump()
        assert dumped_no_alias["session_id"] == "test-id"

    def test_model_validate_from_camel_case(self):
        """Test deserialization from camelCase data (populate_by_name=True)."""
        data = {
            "sessionId": "camel-id",
            "title": "Camel Case Input",
            "path": "/path/to/camel.json",
        }
        result = SessionSearchResult.model_validate(data)
        assert result.session_id == "camel-id"
        assert result.title == "Camel Case Input"
        assert result.path == "/path/to/camel.json"

    def test_roundtrip_serialization(self):
        """Test that serialization and deserialization preserve data."""
        original = SearchResultFactory.create_session_search_result(
            session_id="roundtrip-id",
            title="Roundtrip Test",
            path="/tmp/roundtrip.json",
        )

        # Serialize to JSON string (by_alias=True for camelCase)
        json_str = original.model_dump_json(by_alias=True)

        # Deserialize back
        restored = SessionSearchResult.model_validate_json(json_str)

        # Verify all fields are preserved
        assert restored.session_id == original.session_id
        assert restored.title == original.title
        assert restored.path == original.path
        assert restored == original
