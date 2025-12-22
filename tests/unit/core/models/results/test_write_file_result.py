"""Unit tests for WriteFileResult model."""

import json

import pytest
from pipe.core.models.results.write_file_result import WriteFileResult
from pydantic import ValidationError

from tests.helpers.results_factory import ResultFactory


class TestWriteFileResult:
    """Tests for WriteFileResult model."""

    def test_valid_write_file_result_creation(self):
        """Test creating a valid WriteFileResult with all fields."""
        diff_content = "--- a.txt\n+++ b.txt\n-old\n+new"
        result = ResultFactory.create_write_file_result(
            status="success",
            message="File updated",
            diff=diff_content,
            error=None,
        )
        assert result.status == "success"
        assert result.message == "File updated"
        assert result.diff == diff_content
        assert result.error is None

    def test_write_file_result_default_values(self):
        """Test default values of WriteFileResult."""
        # status is required, others have defaults
        result = WriteFileResult(status="success")
        assert result.status == "success"
        assert result.message is None
        assert result.diff is None
        assert result.error is None

    def test_write_file_result_validation_invalid_status(self):
        """Test validation for invalid status value."""
        with pytest.raises(ValidationError) as exc_info:
            WriteFileResult(status="invalid_status")  # type: ignore
        assert "status" in str(exc_info.value)
        assert "Input should be 'success' or 'error'" in str(exc_info.value)

    def test_write_file_result_validation_missing_status(self):
        """Test validation for missing required status field."""
        with pytest.raises(ValidationError) as exc_info:
            WriteFileResult(status=None)  # type: ignore
        assert "status" in str(exc_info.value)

    def test_write_file_result_serialization_camel_case(self):
        """Test serialization with by_alias=True for camelCase output."""
        result = ResultFactory.create_write_file_result(
            status="success", message="Success message"
        )
        dumped = result.model_dump(by_alias=True)
        # Fields that don't have underscores don't change
        assert dumped["status"] == "success"
        assert dumped["message"] == "Success message"
        # CamelCaseModel should ensure all fields follow camelCase
        # if they had underscores, but here the fields are single words
        # or already follow the pattern.
        # Let's verify with model_dump() too.
        assert result.model_dump() == {
            "status": "success",
            "message": "Success message",
            "diff": result.diff,
            "error": None,
        }

    def test_write_file_result_roundtrip_serialization(self):
        """Test serialization and deserialization preserve data."""
        original = ResultFactory.create_write_file_result(
            status="error",
            message="Failed to write",
            error="Permission denied",
            diff=None,
        )

        # Serialize to JSON string
        json_str = original.model_dump_json(by_alias=True)

        # Deserialize back
        data = json.loads(json_str)
        restored = WriteFileResult.model_validate(data)

        # Verify all fields are preserved
        assert restored.status == original.status
        assert restored.message == original.message
        assert restored.error == original.error
        assert restored.diff == original.diff
        assert restored == original
