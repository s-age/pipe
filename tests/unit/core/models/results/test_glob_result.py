import json

from pipe.core.models.results.glob_result import GlobResult

from tests.factories.models.results.results_factory import ResultFactory


class TestGlobResultModel:
    """GlobResult model validation and serialization tests."""

    def test_valid_glob_result_creation(self):
        """Test creating a valid GlobResult with all fields."""
        result = ResultFactory.create_glob_result(
            content="file1.txt\nfile2.txt", error=None
        )
        assert result.content == "file1.txt\nfile2.txt"
        assert result.error is None

    def test_glob_result_default_values(self):
        """Test GlobResult default values."""
        # When creating via Pydantic directly to test defaults
        result = GlobResult()
        assert result.content is None
        assert result.error is None

    def test_glob_result_with_error(self):
        """Test GlobResult with an error message."""
        result = ResultFactory.create_glob_result(content=None, error="No files found")
        assert result.content is None
        assert result.error == "No files found"

    def test_glob_result_serialization_with_aliases(self):
        """Test serialization with by_alias=True for camelCase conversion."""
        result = ResultFactory.create_glob_result(content="test.py", error="None")
        # Fields in GlobResult don't actually change between snake_case and camelCase
        # because they are single words ("content", "error").
        # But we still test the principle.
        dumped = result.model_dump(by_alias=True)
        assert "content" in dumped
        assert "error" in dumped
        assert dumped["content"] == "test.py"

    def test_glob_result_deserialization(self):
        """Test deserialization with model_validate()."""
        data = {"content": "matched_path.ts", "error": None}
        result = GlobResult.model_validate(data)
        assert result.content == "matched_path.ts"
        assert result.error is None

    def test_glob_result_roundtrip_serialization(self):
        """Test that serialization and deserialization preserve data."""
        original = ResultFactory.create_glob_result(
            content="path/to/file.py", error="some error"
        )

        # Serialize
        json_str = original.model_dump_json(by_alias=True)

        # Deserialize
        data = json.loads(json_str)
        restored = GlobResult.model_validate(data)

        # Verify
        assert restored.content == original.content
        assert restored.error == original.error
        assert restored == original
