import json

from pipe.core.models.results.read_file_result import ReadFileResult

from tests.factories.models.results.results_factory import ResultFactory


class TestReadFileResultModel:
    """Tests for ReadFileResult model validation and serialization."""

    def test_default_values(self):
        """Test that default values are correctly set to None."""
        result = ReadFileResult()
        assert result.content is None
        assert result.message is None
        assert result.error is None

    def test_valid_creation(self):
        """Test creating a ReadFileResult with all fields."""
        result = ResultFactory.create_read_file_result(
            content="hello world", message="Success", error=None
        )
        assert result.content == "hello world"
        assert result.message == "Success"
        assert result.error is None

    def test_creation_with_error(self):
        """Test creating a ReadFileResult representing an error."""
        result = ResultFactory.create_read_file_result(
            content=None, message=None, error="File not found"
        )
        assert result.content is None
        assert result.message is None
        assert result.error == "File not found"

    def test_model_dump_with_aliases(self):
        """Test serialization with by_alias=True for camelCase conversion."""
        result = ResultFactory.create_read_file_result(
            content="content", message="msg", error="err"
        )
        # CamelCaseModel inherits from BaseModel with alias_generator=to_camel
        # though ReadFileResult fields are already simple, it's good to verify the
        # mechanism
        dumped = result.model_dump(by_alias=True)

        # Fields like 'content', 'message', 'error' don't change in camelCase
        # but the test ensures the model supports the requested pattern.
        assert dumped["content"] == "content"
        assert dumped["message"] == "msg"
        assert dumped["error"] == "err"

    def test_model_validate_from_dict(self):
        """Test creating a model from a dictionary."""
        data = {"content": "some content", "message": "some message", "error": None}
        result = ReadFileResult.model_validate(data)
        assert result.content == "some content"
        assert result.message == "some message"
        assert result.error is None

    def test_roundtrip_serialization(self):
        """Test that data is preserved through serialization and deserialization."""
        original = ResultFactory.create_read_file_result(
            content="line 1\nline 2", message="Read 2 lines", error=None
        )

        # Serialize to JSON string
        json_str = original.model_dump_json(by_alias=True)

        # Deserialize back
        data = json.loads(json_str)
        restored = ReadFileResult.model_validate(data)

        assert restored.content == original.content
        assert restored.message == original.message
        assert restored.error == original.error
        assert restored == original
