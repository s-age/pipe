from pipe.core.models.results.get_session_result import GetSessionResult


class TestGetSessionResult:
    """Tests for GetSessionResult model."""

    def test_valid_get_session_result_creation(self):
        """Test creating a valid GetSessionResult with all fields."""
        result = GetSessionResult(
            session_id="test-session-123",
            turns=["Turn 1 content", "Turn 2 content"],
            turns_count=2,
            error=None,
        )
        assert result.session_id == "test-session-123"
        assert len(result.turns) == 2
        assert result.turns_count == 2
        assert result.error is None

    def test_default_values(self):
        """Test default values of GetSessionResult."""
        result = GetSessionResult()
        assert result.session_id is None
        assert result.turns == []
        assert result.turns_count is None
        assert result.error is None

    def test_type_conversion(self):
        """Test that types are converted correctly."""
        # turns_count should be int
        result = GetSessionResult(turns_count="5")
        assert result.turns_count == 5

    def test_serialization_camel_case(self):
        """Test that serialization uses camelCase aliases."""
        result = GetSessionResult(session_id="test-123", turns_count=10)
        dumped = result.model_dump(by_alias=True)

        # Check for camelCase keys
        assert "sessionId" in dumped
        assert dumped["sessionId"] == "test-123"
        assert "turnsCount" in dumped
        assert dumped["turnsCount"] == 10
        assert "turns" in dumped

        # Without by_alias, it should be snake_case
        dumped_snake = result.model_dump()
        assert "session_id" in dumped_snake
        assert "turns_count" in dumped_snake

    def test_deserialization_from_camel_case(self):
        """Test deserialization from a dictionary with camelCase keys."""
        data = {
            "sessionId": "test-456",
            "turns": ["Hello"],
            "turnsCount": 1,
            "error": "Some error",
        }
        result = GetSessionResult.model_validate(data)

        assert result.session_id == "test-456"
        assert result.turns == ["Hello"]
        assert result.turns_count == 1
        assert result.error == "Some error"

    def test_roundtrip_serialization(self):
        """Test that serialization and deserialization preserve data."""
        import json

        original = GetSessionResult(
            session_id="roundtrip-789",
            turns=["First", "Second"],
            turns_count=2,
            error=None,
        )

        # Serialize to JSON string with camelCase
        json_str = original.model_dump_json(by_alias=True)

        # Deserialize back
        data = json.loads(json_str)
        restored = GetSessionResult.model_validate(data)

        assert restored.session_id == original.session_id
        assert restored.turns == original.turns
        assert restored.turns_count == original.turns_count
        assert restored.error == original.error
