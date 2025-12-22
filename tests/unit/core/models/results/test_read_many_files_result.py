"""Unit tests for ReadManyFilesResult model."""

import json

import pytest
from pipe.core.models.results.read_many_files_result import (
    FileContent,
    ReadManyFilesResult,
)
from pydantic import ValidationError

from tests.factories.models.results.results_factory import ResultFactory


class TestReadManyFilesResult:
    """ReadManyFilesResult model validation and serialization tests."""

    def test_valid_file_content_creation(self):
        """Test creating a valid FileContent with required fields."""
        file_content = ResultFactory.create_file_content(
            path="src/main.py", content="print('hello')", error=None
        )
        assert file_content.path == "src/main.py"
        assert file_content.content == "print('hello')"
        assert file_content.error is None

    def test_file_content_validation_missing_path(self):
        """Test that missing path in FileContent raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            FileContent(content="some content")
        assert "path" in str(exc_info.value)

    def test_read_many_files_result_defaults(self):
        """Test ReadManyFilesResult default values."""
        # Create empty result
        result = ReadManyFilesResult()
        assert result.files == []
        assert result.message is None
        assert result.error is None

    def test_read_many_files_result_with_files(self):
        """Test ReadManyFilesResult with multiple files."""
        files = [
            ResultFactory.create_file_content(path="a.py", content="A"),
            ResultFactory.create_file_content(path="b.py", error="Not found"),
        ]
        result = ResultFactory.create_read_many_files_result(
            files=files, message="Partially successful"
        )
        assert len(result.files) == 2
        assert result.files[0].path == "a.py"
        assert result.files[1].error == "Not found"
        assert result.message == "Partially successful"

    def test_serialization_with_aliases(self):
        """Test serialization with by_alias=True for camelCase conversion."""
        file_content = ResultFactory.create_file_content(path="test.py")
        result = ResultFactory.create_read_many_files_result(
            files=[file_content], message="Done"
        )

        # model_dump with by_alias=True
        dumped = result.model_dump(by_alias=True)
        # Note: 'path', 'content', 'error', 'files', 'message' are all single words
        # but CamelCaseModel handles them. Let's verify structure.
        assert "files" in dumped
        assert isinstance(dumped["files"], list)
        assert dumped["files"][0]["path"] == "test.py"
        assert dumped["message"] == "Done"

    def test_deserialization_from_camel_case(self):
        """Test deserialization from camelCase data."""
        data = {
            "files": [{"path": "test.py", "content": "hello"}],
            "message": "success",
            "error": None,
        }
        result = ReadManyFilesResult.model_validate(data)
        assert len(result.files) == 1
        assert result.files[0].path == "test.py"
        assert result.message == "success"

    def test_roundtrip_serialization(self):
        """Test that serialization and deserialization preserve data."""
        original = ResultFactory.create_read_many_files_result(
            files=[
                ResultFactory.create_file_content(path="1.py", content="C1"),
                ResultFactory.create_file_content(path="2.py", error="Err"),
            ],
            message="Multiple",
            error="General error",
        )

        # Serialize to JSON string
        json_str = original.model_dump_json(by_alias=True)

        # Deserialize back
        data = json.loads(json_str)
        restored = ReadManyFilesResult.model_validate(data)

        # Verify all fields are preserved
        assert restored.message == original.message
        assert restored.error == original.error
        assert len(restored.files) == len(original.files)
        assert restored.files[0].path == original.files[0].path
        assert restored.files[0].content == original.files[0].content
        assert restored.files[1].error == original.files[1].error

    def test_file_content_optional_fields(self):
        """Test that content and error are optional in FileContent."""
        # Only path provided
        fc = FileContent(path="only_path.txt")
        assert fc.path == "only_path.txt"
        assert fc.content is None
        assert fc.error is None
