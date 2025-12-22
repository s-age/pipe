import pytest
from pipe.core.models.procedure import ProcedureOption
from pydantic import ValidationError


class TestProcedureOption:
    """Tests for ProcedureOption model."""

    def test_valid_creation(self):
        """Test creating a valid ProcedureOption."""
        option = ProcedureOption(label="Test Label", value="test_value")
        assert option.label == "Test Label"
        assert option.value == "test_value"

    def test_validation_missing_required_fields(self):
        """Test validation fails when required fields are missing."""
        with pytest.raises(ValidationError) as exc_info:
            ProcedureOption(label="Test Label")
        assert "value" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            ProcedureOption(value="test_value")
        assert "label" in str(exc_info.value)

    def test_serialization_camel_case(self):
        """Test serialization with by_alias=True."""
        option = ProcedureOption(label="Test Label", value="test_value")
        dumped = option.model_dump(by_alias=True)
        assert dumped["label"] == "Test Label"
        assert dumped["value"] == "test_value"

    def test_roundtrip_serialization(self):
        """Test serialization and deserialization roundtrip."""
        original = ProcedureOption(label="Test Label", value="test_value")
        json_str = original.model_dump_json(by_alias=True)

        restored = ProcedureOption.model_validate_json(json_str)
        assert restored.label == original.label
        assert restored.value == original.value
        assert restored == original
