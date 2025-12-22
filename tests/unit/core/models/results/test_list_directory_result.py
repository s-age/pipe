from pipe.core.models.results.list_directory_result import ListDirectoryResult


class TestListDirectoryResult:
    """Tests for ListDirectoryResult model."""

    def test_default_values(self):
        """Test default values for fields."""
        result = ListDirectoryResult()
        assert result.files == []
        assert result.directories == []
        assert result.error is None

    def test_valid_creation(self):
        """Test creating a valid result with all fields."""
        result = ListDirectoryResult(
            files=["file1.txt", "file2.py"],
            directories=["src", "tests"],
            error="Something went wrong",
        )
        assert result.files == ["file1.txt", "file2.py"]
        assert result.directories == ["src", "tests"]
        assert result.error == "Something went wrong"

    def test_model_dump_with_aliases(self):
        """Test serialization with by_alias=True for camelCase conversion."""
        result = ListDirectoryResult(
            files=["test.py"],
            directories=["dir"],
            error=None,
        )
        # CamelCaseModel should convert fields to camelCase when using by_alias=True
        dumped = result.model_dump(by_alias=True)
        assert "files" in dumped
        assert "directories" in dumped
        assert "error" in dumped

        # Test serialization of a more complex case if needed,
        # but ListDirectoryResult fields don't have underscores.
        # However, verifying by_alias=True is standard practice.
        assert dumped["files"] == ["test.py"]

    def test_model_validate_with_aliases(self):
        """Test deserialization from camelCase data."""
        data = {
            "files": ["file.txt"],
            "directories": ["subdir"],
            "error": "error message",
        }
        # Pydantic models with populate_by_name=True (standard in CamelCaseModel)
        # can be validated from dicts with or without aliases
        result = ListDirectoryResult.model_validate(data)
        assert result.files == ["file.txt"]
        assert result.directories == ["subdir"]
        assert result.error == "error message"

    def test_roundtrip_serialization(self):
        """Test that serialization and deserialization preserve data."""
        original = ListDirectoryResult(
            files=["a.py", "b.py"], directories=["docs"], error=None
        )

        # Serialize to JSON string
        json_str = original.model_dump_json(by_alias=True)

        # Deserialize back
        restored = ListDirectoryResult.model_validate_json(json_str)

        # Verify all fields are preserved
        assert restored.files == original.files
        assert restored.directories == original.directories
        assert restored.error == original.error
