"""Tests for DeleteSessionTurnsResult model."""

import json

from pipe.core.models.results.delete_session_turns_result import (
    DeleteSessionTurnsResult,
)

from tests.helpers.results_factory import ResultFactory


class TestDeleteSessionTurnsResult:
    """DeleteSessionTurnsResult model validation and serialization tests."""

    def test_default_values(self):
        """Test creating a DeleteSessionTurnsResult with default values."""
        result = DeleteSessionTurnsResult()
        assert result.message is None
        assert result.error is None

    def test_valid_creation(self):
        """Test creating a DeleteSessionTurnsResult with explicit values
        using factory.
        """
        message = "3 turns deleted"
        result = ResultFactory.create_delete_session_turns_result(message=message)
        assert result.message == message
        assert result.error is None

    def test_error_creation(self):
        """Test creating a DeleteSessionTurnsResult with an error message."""
        error_msg = "Failed to delete turns: session not found"
        result = ResultFactory.create_delete_session_turns_result(
            message=None, error=error_msg
        )
        assert result.message is None
        assert result.error == error_msg

    def test_serialization_with_aliases(self):
        """Test serialization with by_alias=True for camelCase conversion.

        Note: message and error fields are the same in snake_case and camelCase,
        but we verify the behavior as it inherits from CamelCaseModel.
        """
        result = ResultFactory.create_delete_session_turns_result(
            message="Success", error="None"
        )
        dumped = result.model_dump(by_alias=True)
        assert dumped["message"] == "Success"
        assert dumped["error"] == "None"

    def test_deserialization(self):
        """Test that model_validate works correctly from a dictionary."""
        data = {"message": "Deleted", "error": None}
        result = DeleteSessionTurnsResult.model_validate(data)
        assert result.message == "Deleted"
        assert result.error is None

    def test_roundtrip_serialization(self):
        """Test that serialization and deserialization preserve data."""
        original = ResultFactory.create_delete_session_turns_result(
            message="Batch delete completed", error=None
        )

        # Serialize to JSON string (by_alias=True for consistency with API)
        json_str = original.model_dump_json(by_alias=True)

        # Deserialize back
        data = json.loads(json_str)
        restored = DeleteSessionTurnsResult.model_validate(data)

        # Verify all fields are preserved
        assert restored.message == original.message
        assert restored.error == original.error
        assert restored == original
