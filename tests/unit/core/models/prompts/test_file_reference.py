import json

import pytest
from pipe.core.models.prompts.file_reference import PromptFileReference
from pydantic import ValidationError


class TestPromptFileReference:
    """PromptFileReference model validation and serialization tests."""

    def test_valid_creation(self):
        """Test creating a valid PromptFileReference with all required fields."""
        ref = PromptFileReference(path="src/main.py", content="print('hello')")
        assert ref.path == "src/main.py"
        assert ref.content == "print('hello')"

    def test_validation_missing_required_field(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            PromptFileReference(path="src/main.py")
        assert "content" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            PromptFileReference(content="some content")
        assert "path" in str(exc_info.value)

    def test_model_dump_with_aliases(self):
        """Test serialization with by_alias=True."""
        ref = PromptFileReference(path="src/main.py", content="print('hello')")
        # In this specific model, "path" and "content" are the same in camelCase and
        # snake_case
        dumped = ref.model_dump(by_alias=True)
        assert dumped["path"] == "src/main.py"
        assert dumped["content"] == "print('hello')"

    def test_model_validate_from_dict(self):
        """Test creating a model from a dictionary using model_validate."""
        data = {"path": "docs/README.md", "content": "# Hello"}
        ref = PromptFileReference.model_validate(data)
        assert ref.path == "docs/README.md"
        assert ref.content == "# Hello"

    def test_roundtrip_serialization(self):
        """Test that serialization and deserialization preserve data."""
        original = PromptFileReference(
            path="tests/test_file.py", content="def test_pass(): pass"
        )

        # Serialize to JSON string
        json_str = original.model_dump_json(by_alias=True)

        # Deserialize back
        data = json.loads(json_str)
        restored = PromptFileReference.model_validate(data)

        # Verify all fields are preserved
        assert restored.path == original.path
        assert restored.content == original.content
        assert restored == original
