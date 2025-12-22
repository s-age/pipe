import pytest
from pipe.core.models.reference import Reference
from pydantic import ValidationError

from tests.helpers import ReferenceFactory


class TestReferenceModel:
    """Reference model validation and serialization tests."""

    def test_valid_reference_creation(self):
        """Test creating a valid reference with all fields."""
        reference = ReferenceFactory.create(
            path="src/main.py", disabled=True, ttl=3600, persist=True
        )
        assert reference.path == "src/main.py"
        assert reference.disabled is True
        assert reference.ttl == 3600
        assert reference.persist is True

    def test_reference_default_values(self):
        """Test reference default values."""
        reference = Reference(path="README.md")
        assert reference.path == "README.md"
        assert reference.disabled is False
        assert reference.ttl is None
        assert reference.persist is False

    def test_reference_batch_creation(self):
        """Test creating multiple references using factory."""
        references = ReferenceFactory.create_batch(3)
        assert len(references) == 3
        assert references[0].path == "test_0.py"
        assert references[2].path == "test_2.py"

    def test_reference_validation_missing_required_field(self):
        """Test that missing path raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Reference(disabled=True)
        assert "path" in str(exc_info.value)

    def test_reference_model_dump_json_mode(self):
        """Test serialization with model_dump(mode='json')."""
        reference = Reference(path="test.txt", disabled=True, ttl=60)
        dumped = reference.model_dump(mode="json")
        assert dumped["path"] == "test.txt"
        assert dumped["disabled"] is True
        assert dumped["ttl"] == 60

    def test_reference_model_dump_by_alias(self):
        """Test serialization with by_alias=True for camelCase."""
        # Even though these fields don't have underscores, we should verify
        # by_alias=True works.
        reference = Reference(path="test.txt", disabled=True, ttl=60)
        dumped = reference.model_dump(by_alias=True)
        assert dumped["path"] == "test.txt"
        assert dumped["disabled"] is True
        assert dumped["ttl"] == 60

    def test_reference_model_validate_camel_case(self):
        """Test validation from camelCase dictionary."""
        data = {"path": "test.py", "disabled": True, "ttl": 300, "persist": True}
        reference = Reference.model_validate(data)
        assert reference.path == "test.py"
        assert reference.disabled is True
        assert reference.ttl == 300
        assert reference.persist is True

    def test_reference_roundtrip_serialization(self):
        """Test that serialization and deserialization preserve data."""
        import json

        original = Reference(
            path="path/to/file.py", disabled=False, ttl=120, persist=True
        )
        json_str = original.model_dump_json(by_alias=True)

        data = json.loads(json_str)
        restored = Reference.model_validate(data)

        assert restored.path == original.path
        assert restored.disabled == original.disabled
        assert restored.ttl == original.ttl
        assert restored.persist == original.persist
        assert restored == original
