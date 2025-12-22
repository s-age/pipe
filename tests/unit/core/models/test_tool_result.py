import pytest
from pipe.core.models.tool_result import ToolResult
from pydantic import ValidationError


class TestToolResultModel:
    """ToolResult model validation and serialization tests."""

    def test_tool_result_success(self):
        """Test ToolResult with successful data."""
        result = ToolResult[str](data="success data")
        assert result.data == "success data"
        assert result.error is None
        assert result.is_success is True

    def test_tool_result_error(self):
        """Test ToolResult with an error message."""
        result = ToolResult[str](error="something went wrong")
        assert result.data is None
        assert result.error == "something went wrong"
        assert result.is_success is False

    def test_tool_result_default_values(self):
        """Test ToolResult default values."""
        result = ToolResult[int]()
        assert result.data is None
        assert result.error is None
        assert result.is_success is True  # error is None means success

    def test_tool_result_with_dict_data(self):
        """Test ToolResult with dictionary data and type validation."""
        data = {"key": "value"}
        result = ToolResult[dict](data=data)
        assert result.data == data
        assert result.is_success is True

    def test_tool_result_type_validation(self):
        """Test that ToolResult enforces type constraints on data."""
        # Pydantic will try to coerce if possible, but let's test a clear mismatch if
        # any
        # For str, most things can be coerced. For int, a string "abc" should fail.
        with pytest.raises(ValidationError):
            ToolResult[int](data="not an int")

    def test_tool_result_serialization(self):
        """Test serialization and deserialization of ToolResult."""
        original = ToolResult[dict](data={"status": "ok"}, error=None)

        # Serialize
        dumped = original.model_dump()
        assert dumped["data"] == {"status": "ok"}
        assert dumped["error"] is None

        # Deserialize
        restored = ToolResult[dict].model_validate(dumped)
        assert restored.data == {"status": "ok"}
        assert restored.error is None
        assert restored.is_success is True

    def test_tool_result_json_roundtrip(self):
        """Test JSON serialization roundtrip."""
        original = ToolResult[str](data="json test")
        json_str = original.model_dump_json()

        restored = ToolResult[str].model_validate_json(json_str)
        assert restored.data == "json test"
        assert restored.is_success is True
