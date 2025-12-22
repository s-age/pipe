"""Unit tests for EditSessionTurnResult model."""

import json

from pipe.core.models.results.edit_session_turn_result import EditSessionTurnResult


class TestEditSessionTurnResult:
    """Tests for EditSessionTurnResult model validation and serialization."""

    def test_default_values(self):
        """Test that default values are None."""
        result = EditSessionTurnResult()
        assert result.message is None
        assert result.error is None

    def test_valid_creation_with_message(self):
        """Test creating with a success message."""
        result = EditSessionTurnResult(message="Turn updated successfully")
        assert result.message == "Turn updated successfully"
        assert result.error is None

    def test_valid_creation_with_error(self):
        """Test creating with an error message."""
        result = EditSessionTurnResult(error="Session not found")
        assert result.message is None
        assert result.error == "Session not found"

    def test_model_dump_with_aliases(self):
        """Test serialization with by_alias=True.

        Note: Since field names are single words, the camelCase alias
        is identical to the snake_case name.
        """
        result = EditSessionTurnResult(message="Success", error="None")
        dumped = result.model_dump(by_alias=True)

        assert dumped["message"] == "Success"
        assert dumped["error"] == "None"

    def test_model_validate_from_dict(self):
        """Test deserialization from a dictionary."""
        data = {"message": "Update ok", "error": None}
        result = EditSessionTurnResult.model_validate(data)
        assert result.message == "Update ok"
        assert result.error is None

    def test_roundtrip_serialization(self):
        """Test that serialization and deserialization preserve data."""
        original = EditSessionTurnResult(message="Modified turn 5", error=None)

        # Serialize to JSON string (by_alias=True for consistency)
        json_str = original.model_dump_json(by_alias=True)

        # Deserialize back
        data = json.loads(json_str)
        restored = EditSessionTurnResult.model_validate(data)

        # Verify fields are preserved
        assert restored.message == original.message
        assert restored.error == original.error
        assert restored == original
