"""Unit tests for CompressSessionTurnsResult model."""

import json

from pipe.core.models.results.compress_session_turns_result import (
    CompressSessionTurnsResult,
)

from tests.helpers import ResultFactory


class TestCompressSessionTurnsResultModel:
    """Tests for the CompressSessionTurnsResult model."""

    def test_valid_creation(self):
        """Test creating a CompressSessionTurnsResult with valid data."""
        result = ResultFactory.create_compress_session_turns_result(
            message="Success", current_turn_count=10, error=None
        )
        assert result.message == "Success"
        assert result.current_turn_count == 10
        assert result.error is None

    def test_default_values(self):
        """Test that default values are None as expected."""
        result = CompressSessionTurnsResult()
        assert result.message is None
        assert result.current_turn_count is None
        assert result.error is None

    def test_serialization_with_aliases(self):
        """Test that model_dump(by_alias=True) uses camelCase field names."""
        result = ResultFactory.create_compress_session_turns_result(
            message="Done", current_turn_count=5
        )
        dumped = result.model_dump(by_alias=True)

        # CamelCaseModel should convert current_turn_count to currentTurnCount
        assert "message" in dumped
        assert dumped["message"] == "Done"
        assert "currentTurnCount" in dumped
        assert dumped["currentTurnCount"] == 5
        assert "error" in dumped
        assert dumped["error"] is None

        # Without by_alias=True, it should be snake_case
        dumped_snake = result.model_dump()
        assert "current_turn_count" in dumped_snake
        assert dumped_snake["current_turn_count"] == 5

    def test_deserialization_from_camel_case(self):
        """Test that the model can be validated from a camelCase dictionary."""
        data = {"message": "Loaded", "currentTurnCount": 3, "error": "Some error"}
        result = CompressSessionTurnsResult.model_validate(data)
        assert result.message == "Loaded"
        assert result.current_turn_count == 3
        assert result.error == "Some error"

    def test_roundtrip_serialization(self):
        """Test that serialization and deserialization preserve data."""
        original = ResultFactory.create_compress_session_turns_result(
            message="Roundtrip test", current_turn_count=7, error=None
        )

        # Serialize to JSON string with aliases (camelCase)
        json_str = original.model_dump_json(by_alias=True)

        # Verify it contains camelCase
        assert "currentTurnCount" in json_str

        # Deserialize back
        data = json.loads(json_str)
        restored = CompressSessionTurnsResult.model_validate(data)

        # Verify all fields are preserved
        assert restored.message == original.message
        assert restored.current_turn_count == original.current_turn_count
        assert restored.error == original.error
        assert restored == original
