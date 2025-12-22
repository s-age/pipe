import pytest
from pipe.core.models.unified_chunk import (
    MetadataChunk,
    TextChunk,
    ToolCallChunk,
    UsageMetadata,
)
from pydantic import ValidationError


class TestTextChunk:
    """Tests for TextChunk model."""

    def test_valid_text_chunk(self):
        """Test creating a valid TextChunk."""
        chunk = TextChunk(content="Hello world")
        assert chunk.type == "text"
        assert chunk.content == "Hello world"
        assert chunk.is_thought is False

    def test_text_chunk_with_thought(self):
        """Test TextChunk with is_thought set to True."""
        chunk = TextChunk(content="Thinking...", is_thought=True)
        assert chunk.is_thought is True

    def test_text_chunk_serialization_aliases(self):
        """Test serialization uses camelCase for aliases."""
        chunk = TextChunk(content="thought content", is_thought=True)
        dumped = chunk.model_dump(by_alias=True)
        assert dumped["content"] == "thought content"
        assert dumped["isThought"] is True
        assert dumped["type"] == "text"

    def test_text_chunk_deserialization(self):
        """Test deserialization from both snake_case and camelCase."""
        # From camelCase
        data = {"content": "test", "isThought": True}
        chunk = TextChunk.model_validate(data)
        assert chunk.is_thought is True

        # From snake_case (thanks to populate_by_name=True)
        data_snake = {"content": "test", "is_thought": True}
        chunk_snake = TextChunk.model_validate(data_snake)
        assert chunk_snake.is_thought is True


class TestToolCallChunk:
    """Tests for ToolCallChunk model."""

    def test_valid_tool_call_chunk(self):
        """Test creating a valid ToolCallChunk."""
        chunk = ToolCallChunk(name="get_weather", args={"location": "Tokyo"})
        assert chunk.type == "tool_call"
        assert chunk.name == "get_weather"
        assert chunk.args == {"location": "Tokyo"}

    def test_tool_call_chunk_default_args(self):
        """Test ToolCallChunk provides empty dict as default args."""
        chunk = ToolCallChunk(name="search")
        assert chunk.args == {}

    def test_tool_call_chunk_missing_name(self):
        """Test ToolCallChunk raises error if name is missing."""
        with pytest.raises(ValidationError):
            ToolCallChunk()

    def test_tool_call_chunk_serialization(self):
        """Test serialization of ToolCallChunk."""
        chunk = ToolCallChunk(name="test_tool", args={"key": "value"})
        dumped = chunk.model_dump(by_alias=True)
        assert dumped["name"] == "test_tool"
        assert dumped["args"] == {"key": "value"}
        assert dumped["type"] == "tool_call"


class TestUsageMetadata:
    """Tests for UsageMetadata model."""

    def test_valid_usage_metadata(self):
        """Test creating a valid UsageMetadata."""
        usage = UsageMetadata(
            prompt_token_count=10,
            candidates_token_count=20,
            total_token_count=30,
            cached_content_token_count=5,
        )
        assert usage.prompt_token_count == 10
        assert usage.candidates_token_count == 20
        assert usage.total_token_count == 30
        assert usage.cached_content_token_count == 5

    def test_usage_metadata_optional_fields(self):
        """Test UsageMetadata with only some fields."""
        usage = UsageMetadata(total_token_count=100)
        assert usage.total_token_count == 100
        assert usage.prompt_token_count is None

    def test_usage_metadata_no_aliases(self):
        """Test UsageMetadata does not use aliases as it inherits from BaseModel."""
        usage = UsageMetadata(prompt_token_count=10)
        dumped = usage.model_dump(by_alias=True)
        # Inherits from BaseModel directly, not CamelCaseModel, so no auto-aliasing
        assert "prompt_token_count" in dumped
        assert "promptTokenCount" not in dumped


class TestMetadataChunk:
    """Tests for MetadataChunk model."""

    def test_valid_metadata_chunk(self):
        """Test creating a valid MetadataChunk."""
        usage = UsageMetadata(total_token_count=100)
        chunk = MetadataChunk(usage=usage)
        assert chunk.type == "metadata"
        assert chunk.usage.total_token_count == 100

    def test_metadata_chunk_deserialization(self):
        """Test deserialization of MetadataChunk."""
        data = {
            "type": "metadata",
            "usage": {"prompt_token_count": 50, "total_token_count": 150},
        }
        chunk = MetadataChunk.model_validate(data)
        assert chunk.usage.prompt_token_count == 50
        assert chunk.usage.total_token_count == 150


def test_unified_chunk_union():
    """Test that UnifiedChunk correctly handles different types."""
    from pipe.core.models.unified_chunk import UnifiedChunk
    from pydantic import TypeAdapter

    adapter = TypeAdapter(UnifiedChunk)

    # Test TextChunk
    text_data = {"type": "text", "content": "hello"}
    text_chunk = adapter.validate_python(text_data)
    assert isinstance(text_chunk, TextChunk)

    # Test ToolCallChunk
    tool_data = {"type": "tool_call", "name": "test"}
    tool_chunk = adapter.validate_python(tool_data)
    assert isinstance(tool_chunk, ToolCallChunk)

    # Test MetadataChunk
    meta_data = {"type": "metadata", "usage": {"total_token_count": 10}}
    meta_chunk = adapter.validate_python(meta_data)
    assert isinstance(meta_chunk, MetadataChunk)
