import json

from pipe.core.models.results.web_fetch_result import WebFetchResult

from tests.factories.models.results.results_factory import ResultFactory


class TestWebFetchResultModel:
    """Tests for WebFetchResult model validation and serialization."""

    def test_default_values(self):
        """Test that default values are correctly set to None."""
        result = WebFetchResult()
        assert result.message is None
        assert result.error is None

    def test_valid_creation(self):
        """Test creating a WebFetchResult with all fields."""
        result = ResultFactory.create_web_fetch_result(
            message="fetched content", error=None
        )
        assert result.message == "fetched content"
        assert result.error is None

    def test_creation_with_error(self):
        """Test creating a WebFetchResult representing an error."""
        result = ResultFactory.create_web_fetch_result(
            message=None, error="Failed to fetch URL"
        )
        assert result.message is None
        assert result.error == "Failed to fetch URL"

    def test_model_dump_with_aliases(self):
        """Test serialization with by_alias=True for camelCase conversion."""
        result = ResultFactory.create_web_fetch_result(
            message="some content", error="some error"
        )
        # CamelCaseModel inherits from BaseModel with alias_generator=to_camel
        dumped = result.model_dump(by_alias=True)

        # Fields like 'message', 'error' don't change in camelCase
        assert dumped["message"] == "some content"
        assert dumped["error"] == "some error"

    def test_model_validate_from_dict(self):
        """Test creating a model from a dictionary."""
        data = {"message": "content", "error": None}
        result = WebFetchResult.model_validate(data)
        assert result.message == "content"
        assert result.error is None

    def test_roundtrip_serialization(self):
        """Test that data is preserved through serialization and deserialization."""
        original = ResultFactory.create_web_fetch_result(
            message="<html><body>Hello</body></html>", error=None
        )

        # Serialize to JSON string
        json_str = original.model_dump_json(by_alias=True)

        # Deserialize back
        data = json.loads(json_str)
        restored = WebFetchResult.model_validate(data)

        assert restored.message == original.message
        assert restored.error == original.error
        assert restored == original
