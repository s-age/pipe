import pytest
from pipe.core.models.role import RoleOption
from pydantic import ValidationError


class TestRoleOptionModel:
    """RoleOption model validation and serialization tests."""

    def test_valid_role_option_creation(self):
        """Test creating a valid RoleOption with all required fields."""
        role = RoleOption(label="Developer", value="developer")
        assert role.label == "Developer"
        assert role.value == "developer"

    def test_role_option_validation_missing_required_field(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            RoleOption(label="Developer")  # type: ignore
        assert "value" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            RoleOption(value="developer")  # type: ignore
        assert "label" in str(exc_info.value)

    def test_role_option_model_dump_with_aliases(self):
        """Test serialization with by_alias=True for camelCase conversion.
        Note: label and value don't have underscores, so they remain same,
        but we verify the mechanism.
        """
        role = RoleOption(label="Developer", value="developer")
        dumped = role.model_dump(by_alias=True)
        assert dumped["label"] == "Developer"
        assert dumped["value"] == "developer"

    def test_role_option_deserialization_from_camel_case(self):
        """Test that RoleOption can be validated from camelCase data."""
        # RoleOption fields don't have snake_case to camelCase conversion
        # but populate_by_name=True should work.
        data = {"label": "Reviewer", "value": "reviewer"}
        role = RoleOption.model_validate(data)
        assert role.label == "Reviewer"
        assert role.value == "reviewer"

    def test_role_option_roundtrip_serialization(self):
        """Test that serialization and deserialization preserve data."""
        original = RoleOption(label="Architect", value="architect")

        # Serialize to JSON string
        json_str = original.model_dump_json(by_alias=True)

        # Deserialize back
        restored = RoleOption.model_validate_json(json_str)

        # Verify all fields are preserved
        assert restored.label == original.label
        assert restored.value == original.value
        assert restored == original
