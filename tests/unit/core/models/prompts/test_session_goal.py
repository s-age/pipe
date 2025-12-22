import pytest
from pipe.core.models.prompts.session_goal import PromptSessionGoal
from pydantic import ValidationError


class TestPromptSessionGoal:
    """Tests for the PromptSessionGoal model."""

    def test_valid_creation(self):
        """Test creating a valid PromptSessionGoal with all fields."""
        goal = PromptSessionGoal(
            description="Test description",
            purpose="Test purpose",
            background="Test background",
        )
        assert goal.description == "Test description"
        assert goal.purpose == "Test purpose"
        assert goal.background == "Test background"

    def test_build_method(self):
        """Test the build class method."""
        purpose = "Implement a new feature"
        background = "The user wants to add a login page"

        goal = PromptSessionGoal.build(purpose=purpose, background=background)

        assert goal.purpose == purpose
        assert goal.background == background
        assert (
            goal.description == "This section outlines the goal of the current session."
        )

    def test_validation_error_missing_fields(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            # Missing purpose and background
            PromptSessionGoal(description="Test")

    def test_serialization_camel_case(self):
        """Test that model_dump(by_alias=True) produces camelCase keys if applicable.

        Note: Since fields in PromptSessionGoal don't have underscores
        (description, purpose, background), camelCase conversion might not change
        the keys, but we verify the mechanism.
        """
        goal = PromptSessionGoal(
            description="desc",
            purpose="purp",
            background="back",
        )

        dumped = goal.model_dump(by_alias=True)
        assert dumped["description"] == "desc"
        assert dumped["purpose"] == "purp"
        assert dumped["background"] == "back"

    def test_deserialization(self):
        """Test model_validate with a dictionary."""
        data = {
            "description": "desc",
            "purpose": "purp",
            "background": "back",
        }
        goal = PromptSessionGoal.model_validate(data)
        assert goal.description == "desc"
        assert goal.purpose == "purp"
        assert goal.background == "back"

    def test_roundtrip_serialization(self):
        """Test that serialization and deserialization preserve data."""
        original = PromptSessionGoal.build(
            purpose="Roundtrip test", background="Verifying data integrity"
        )

        json_str = original.model_dump_json(by_alias=True)
        restored = PromptSessionGoal.model_validate_json(json_str)

        assert restored.description == original.description
        assert restored.purpose == original.purpose
        assert restored.background == original.background
        assert restored == original
