import pytest
from pipe.core.models.results.replace_result import ReplaceResult
from pydantic import ValidationError

from tests.factories.models.results.results_factory import ResultFactory


class TestReplaceResult:
    """Tests for ReplaceResult model."""

    def test_valid_replace_result_creation(self):
        """Test creating a valid ReplaceResult with all fields."""
        result = ResultFactory.create_replace_result(
            status="success",
            message="Successfully replaced",
            diff="test diff",
            error=None,
        )
        assert result.status == "success"
        assert result.message == "Successfully replaced"
        assert result.diff == "test diff"
        assert result.error is None

    def test_replace_result_default_values(self):
        """Test ReplaceResult default values."""
        # status is required, others have defaults
        result = ReplaceResult(status="failed")
        assert result.status == "failed"
        assert result.message is None
        assert result.diff is None
        assert result.error is None

    def test_replace_result_invalid_status(self):
        """Test that invalid status raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ReplaceResult(status="invalid_status")
        assert "status" in str(exc_info.value)
        # Check allowed values in error message if possible,
        # but at least ensure it fails.

    def test_replace_result_serialization_camel_case(self):
        """Test serialization to camelCase (by_alias=True)."""
        result = ResultFactory.create_replace_result(
            status="error",
            message="An error occurred",
            diff="diff content",
            error="traceback",
        )

        # CamelCaseModel should use aliases for camelCase
        dumped = result.model_dump(by_alias=True)

        # These fields are single words, so they don't change,
        # but we should check they exist.
        assert dumped["status"] == "error"
        assert dumped["message"] == "An error occurred"
        assert dumped["diff"] == "diff content"
        assert dumped["error"] == "traceback"

    def test_replace_result_deserialization_camel_case(self):
        """Test deserialization from camelCase data."""
        data = {"status": "success", "message": "Done", "diff": "+++", "error": None}
        # In this specific model, all fields are single words,
        # so camelCase and snake_case are identical.
        # But we verify model_validate works.
        result = ReplaceResult.model_validate(data)
        assert result.status == "success"
        assert result.message == "Done"

    def test_replace_result_roundtrip(self):
        """Test that serialization and deserialization preserve data."""
        original = ResultFactory.create_replace_result(
            status="success", message="Roundtrip test", diff="some diff", error=None
        )

        # Serialize
        json_str = original.model_dump_json(by_alias=True)

        # Deserialize
        restored = ReplaceResult.model_validate_json(json_str)

        # Verify
        assert restored.status == original.status
        assert restored.message == original.message
        assert restored.diff == original.diff
        assert restored.error == original.error
        assert restored == original
