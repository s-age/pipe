import pytest
from pipe.core.models.artifact import Artifact
from pydantic import ValidationError

from tests.factories.models import ArtifactFactory


class TestArtifactModel:
    """Artifact model validation and serialization tests."""

    def test_valid_artifact_creation(self):
        """Test creating a valid artifact with required fields."""
        artifact = ArtifactFactory.create(path="src/main.py", contents="print('hello')")
        assert artifact.path == "src/main.py"
        assert artifact.contents == "print('hello')"

    def test_artifact_default_values(self):
        """Test artifact default values."""
        artifact = Artifact(path="README.md")
        assert artifact.path == "README.md"
        assert artifact.contents is None

    def test_artifact_batch_creation(self):
        """Test creating multiple artifacts using factory."""
        artifacts = ArtifactFactory.create_batch(3)
        assert len(artifacts) == 3
        assert artifacts[0].path == "test_0.py"
        assert artifacts[2].path == "test_2.py"

    def test_artifact_validation_missing_required_field(self):
        """Test that missing path raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Artifact(contents="some content")
        assert "path" in str(exc_info.value)

    def test_artifact_model_dump_json_mode(self):
        """Test serialization with model_dump(mode='json')."""
        artifact = Artifact(path="test.txt", contents="content")
        dumped = artifact.model_dump(mode="json")
        # Artifact has no snake_case fields that need camelCase conversion,
        # but we should still verify the basic dump.
        assert dumped["path"] == "test.txt"
        assert dumped["contents"] == "content"

    def test_artifact_model_validate_snake_case(self):
        """Test validation from snake_case dictionary."""
        data = {"path": "test.py", "contents": "print(1)"}
        artifact = Artifact.model_validate(data)
        assert artifact.path == "test.py"
        assert artifact.contents == "print(1)"

    def test_artifact_model_validate_camel_case(self):
        """Test validation from camelCase dictionary (if applicable)."""
        # path and contents are the same in camelCase and snake_case,
        # but let's test the mechanism.
        data = {"path": "test.py", "contents": "print(1)"}
        artifact = Artifact.model_validate(data)
        assert artifact.path == "test.py"

    def test_artifact_roundtrip_serialization(self):
        """Test that serialization and deserialization preserve data."""
        import json

        original = Artifact(path="path/to/file.py", contents="content here")
        json_str = original.model_dump_json()

        data = json.loads(json_str)
        restored = Artifact.model_validate(data)

        assert restored.path == original.path
        assert restored.contents == original.contents
        assert restored == original
