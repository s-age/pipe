import pytest
from pipe.core.models.results.search_file_content_result import (
    FileMatchItem,
    SearchFileContentResult,
)
from pydantic import ValidationError

from tests.factories.models.results.results_factory import ResultFactory


class TestSearchFileContentResultModel:
    """Tests for SearchFileContentResult and FileMatchItem models."""

    def test_valid_file_match_item_creation(self):
        """Test creating a valid FileMatchItem with all fields."""
        item = ResultFactory.create_file_match_item(
            file_path="src/app.py",
            line_number=42,
            line_content="print('hello')",
            error=None,
        )
        assert item.file_path == "src/app.py"
        assert item.line_number == 42
        assert item.line_content == "print('hello')"
        assert item.error is None

    def test_file_match_item_default_values(self):
        """Test FileMatchItem default values."""
        item = FileMatchItem()
        assert item.file_path is None
        assert item.line_number is None
        assert item.line_content is None
        assert item.error is None

    def test_valid_search_file_content_result_with_list(self):
        """Test SearchFileContentResult with a list of matches."""
        items = [
            ResultFactory.create_file_match_item(file_path="a.py"),
            ResultFactory.create_file_match_item(file_path="b.py"),
        ]
        result = ResultFactory.create_search_file_content_result(content=items)
        assert isinstance(result.content, list)
        assert len(result.content) == 2
        assert result.content[0].file_path == "a.py"

    def test_valid_search_file_content_result_with_string(self):
        """Test SearchFileContentResult with a string message (e.g. error)."""
        result = ResultFactory.create_search_file_content_result(
            content="No matches found"
        )
        assert result.content == "No matches found"

    def test_search_file_content_result_missing_content(self):
        """Test that missing content raises ValidationError."""
        with pytest.raises(ValidationError):
            SearchFileContentResult()  # content is required

    def test_model_dump_with_aliases(self):
        """Test serialization with by_alias=True for camelCase conversion."""
        item = ResultFactory.create_file_match_item(
            file_path="src/test.py", line_number=1, line_content="test"
        )
        result = ResultFactory.create_search_file_content_result(content=[item])

        dumped = result.model_dump(by_alias=True)

        # Check top level
        assert "content" in dumped

        # Check item level (camelCase aliases)
        item_dump = dumped["content"][0]
        assert "filePath" in item_dump
        assert "lineNumber" in item_dump
        assert "lineContent" in item_dump
        assert item_dump["filePath"] == "src/test.py"
        assert item_dump["lineNumber"] == 1
        assert item_dump["lineContent"] == "test"

    def test_model_validate_with_aliases(self):
        """Test deserialization from camelCase data."""
        data = {
            "content": [
                {
                    "filePath": "src/app.py",
                    "lineNumber": 10,
                    "lineContent": "def foo():",
                    "error": None,
                }
            ]
        }
        result = SearchFileContentResult.model_validate(data)
        assert len(result.content) == 1
        assert result.content[0].file_path == "src/app.py"
        assert result.content[0].line_number == 10
        assert result.content[0].line_content == "def foo():"

    def test_roundtrip_serialization(self):
        """Test that serialization and deserialization preserve data."""
        original = ResultFactory.create_search_file_content_result(
            content=[
                ResultFactory.create_file_match_item(file_path="test.py", line_number=5)
            ]
        )

        # Serialize to JSON string
        json_str = original.model_dump_json(by_alias=True)

        # Deserialize back
        restored = SearchFileContentResult.model_validate_json(json_str)

        assert restored.content[0].file_path == original.content[0].file_path
        assert restored.content[0].line_number == original.content[0].line_number
        assert restored.content[0].line_content == original.content[0].line_content
