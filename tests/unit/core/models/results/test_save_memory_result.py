"""Unit tests for SaveMemoryResult model."""

import pytest
from pipe.core.models.results.save_memory_result import SaveMemoryResult
from pydantic import ValidationError

from tests.factories.models.results.results_factory import ResultFactory


class TestSaveMemoryResult:
    """SaveMemoryResult model validation and serialization tests."""

    def test_valid_success_result_creation(self):
        """Test creating a valid success result."""
        result = ResultFactory.create_save_memory_result(
            status="success", message="Memory saved successfully"
        )
        assert result.status == "success"
        assert result.message == "Memory saved successfully"

    def test_valid_error_result_creation(self):
        """Test creating a valid error result."""
        result = ResultFactory.create_save_memory_result(
            status="error", message="Failed to save memory"
        )
        assert result.status == "error"
        assert result.message == "Failed to save memory"

    def test_default_values(self):
        """Test that message defaults to None."""
        result = SaveMemoryResult(status="success")
        assert result.status == "success"
        assert result.message is None

    def test_invalid_status_raises_validation_error(self):
        """Test that invalid status raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SaveMemoryResult(status="invalid_status")
        assert "status" in str(exc_info.value)
        assert "Input should be 'success' or 'error'" in str(exc_info.value)

    def test_missing_required_field_raises_validation_error(self):
        """Test that missing required 'status' raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SaveMemoryResult()
        assert "status" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)

    def test_model_dump_with_aliases(self):
        """Test serialization with by_alias=True for camelCase conversion.

        Even though SaveMemoryResult fields (status, message) don't change
        between snake_case and camelCase, we verify the inheritance from
        CamelCaseModel.
        """
        result = ResultFactory.create_save_memory_result(
            status="success", message="Saved"
        )
        dumped = result.model_dump(by_alias=True)
        assert dumped["status"] == "success"
        assert dumped["message"] == "Saved"

    def test_model_validate(self):
        """Test that model_validate works correctly."""
        data = {"status": "success", "message": "Validated"}
        result = SaveMemoryResult.model_validate(data)
        assert result.status == "success"
        assert result.message == "Validated"

    def test_roundtrip_serialization(self):
        """Test that serialization and deserialization preserve data."""
        original = ResultFactory.create_save_memory_result(
            status="error", message="Roundtrip error message"
        )

        # Serialize
        json_str = original.model_dump_json(by_alias=True)

        # Deserialize
        restored = SaveMemoryResult.model_validate_json(json_str)

        # Verify
        assert restored.status == original.status
        assert restored.message == original.message
        assert restored == original
