"""Tests for Gemini API stream processor."""

import json
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

from google.genai import types
from pipe.core.domains.gemini_api_stream_processor import GeminiApiStreamProcessor
from pipe.core.models.unified_chunk import TextChunk, ToolCallChunk


class TestSaveRawResponse:
    """Tests for _save_raw_response method."""

    def test_save_raw_response_with_thought_signature(self):
        """Test that raw response is saved when thought_signature exists."""
        # Create mock streaming log repository
        mock_log_repo = MagicMock()
        mock_log_repo.write_log_line = MagicMock()

        timezone = ZoneInfo("UTC")
        processor = GeminiApiStreamProcessor(mock_log_repo, timezone)

        # Create mock chunk with thought_signature
        mock_part = MagicMock()
        mock_part.thought_signature = "test_signature"
        mock_part.text = "test text"
        mock_part.thought = False

        mock_content = MagicMock()
        mock_content.parts = [mock_part]

        mock_candidate = MagicMock()
        mock_candidate.content = mock_content

        mock_chunk = MagicMock(spec=types.GenerateContentResponse)
        mock_chunk.candidates = [mock_candidate]
        mock_chunk.model_dump.return_value = {"test": "data"}

        processor.collected_chunks = [mock_chunk]

        # Call the method
        processor._save_raw_response()

        # Verify raw response was saved
        assert processor.last_raw_response is not None
        saved_data = json.loads(processor.last_raw_response)
        assert len(saved_data) == 1
        assert saved_data[0] == {"test": "data"}

    def test_save_raw_response_with_thought_true(self):
        """Test that raw response is saved when thought=True."""
        mock_log_repo = MagicMock()
        timezone = ZoneInfo("UTC")
        processor = GeminiApiStreamProcessor(mock_log_repo, timezone)

        # Create mock chunk with thought=True
        mock_part = MagicMock()
        mock_part.thought_signature = None
        mock_part.text = "thinking process"
        mock_part.thought = True

        mock_content = MagicMock()
        mock_content.parts = [mock_part]

        mock_candidate = MagicMock()
        mock_candidate.content = mock_content

        mock_chunk = MagicMock(spec=types.GenerateContentResponse)
        mock_chunk.candidates = [mock_candidate]
        mock_chunk.model_dump.return_value = {"thought_chunk": "data"}

        processor.collected_chunks = [mock_chunk]

        # Call the method
        processor._save_raw_response()

        # Verify raw response was saved
        assert processor.last_raw_response is not None
        saved_data = json.loads(processor.last_raw_response)
        assert len(saved_data) == 1

    def test_save_raw_response_with_function_call(self):
        """Test that raw response is saved when function_call exists."""
        mock_log_repo = MagicMock()
        timezone = ZoneInfo("UTC")
        processor = GeminiApiStreamProcessor(mock_log_repo, timezone)

        # Create mock chunk with function_call
        mock_function_call = MagicMock()
        mock_function_call.name = "test_function"
        mock_function_call.args = {"arg1": "value1"}

        mock_part = MagicMock()
        mock_part.thought_signature = None
        mock_part.thought = False
        mock_part.function_call = mock_function_call

        mock_content = MagicMock()
        mock_content.parts = [mock_part]

        mock_candidate = MagicMock()
        mock_candidate.content = mock_content

        mock_chunk = MagicMock(spec=types.GenerateContentResponse)
        mock_chunk.candidates = [mock_candidate]
        mock_chunk.model_dump.return_value = {"function_call_chunk": "data"}

        processor.collected_chunks = [mock_chunk]

        # Call the method
        processor._save_raw_response()

        # Verify raw response was saved
        assert processor.last_raw_response is not None
        saved_data = json.loads(processor.last_raw_response)
        assert len(saved_data) == 1

    def test_save_raw_response_without_special_content(self):
        """Test that raw response is None when no special content exists."""
        mock_log_repo = MagicMock()
        timezone = ZoneInfo("UTC")
        processor = GeminiApiStreamProcessor(mock_log_repo, timezone)

        # Create mock chunk with only regular text (no thought_signature, thought=False, no function_call)
        mock_part = MagicMock()
        mock_part.thought_signature = None
        mock_part.thought = False
        mock_part.function_call = None
        mock_part.text = "regular text"

        mock_content = MagicMock()
        mock_content.parts = [mock_part]

        mock_candidate = MagicMock()
        mock_candidate.content = mock_content

        mock_chunk = MagicMock(spec=types.GenerateContentResponse)
        mock_chunk.candidates = [mock_candidate]

        processor.collected_chunks = [mock_chunk]

        # Call the method
        processor._save_raw_response()

        # Verify raw response is None
        assert processor.last_raw_response is None

    def test_save_raw_response_with_multiple_chunks(self):
        """Test that all chunks are saved when special content exists."""
        mock_log_repo = MagicMock()
        timezone = ZoneInfo("UTC")
        processor = GeminiApiStreamProcessor(mock_log_repo, timezone)

        # Create first chunk with thought=True
        mock_part1 = MagicMock()
        mock_part1.thought_signature = None
        mock_part1.thought = True
        mock_part1.text = "thinking"

        mock_content1 = MagicMock()
        mock_content1.parts = [mock_part1]

        mock_candidate1 = MagicMock()
        mock_candidate1.content = mock_content1

        mock_chunk1 = MagicMock(spec=types.GenerateContentResponse)
        mock_chunk1.candidates = [mock_candidate1]
        mock_chunk1.model_dump.return_value = {"chunk": "1"}

        # Create second chunk with regular text
        mock_part2 = MagicMock()
        mock_part2.thought_signature = None
        mock_part2.thought = False
        mock_part2.function_call = None
        mock_part2.text = "output"

        mock_content2 = MagicMock()
        mock_content2.parts = [mock_part2]

        mock_candidate2 = MagicMock()
        mock_candidate2.content = mock_content2

        mock_chunk2 = MagicMock(spec=types.GenerateContentResponse)
        mock_chunk2.candidates = [mock_candidate2]
        mock_chunk2.model_dump.return_value = {"chunk": "2"}

        processor.collected_chunks = [mock_chunk1, mock_chunk2]

        # Call the method
        processor._save_raw_response()

        # Verify all chunks were saved
        assert processor.last_raw_response is not None
        saved_data = json.loads(processor.last_raw_response)
        assert len(saved_data) == 2
        assert saved_data[0] == {"chunk": "1"}
        assert saved_data[1] == {"chunk": "2"}

    def test_save_raw_response_with_empty_chunks(self):
        """Test that method handles empty chunks list gracefully."""
        mock_log_repo = MagicMock()
        timezone = ZoneInfo("UTC")
        processor = GeminiApiStreamProcessor(mock_log_repo, timezone)

        processor.collected_chunks = []

        # Call the method
        processor._save_raw_response()

        # Verify raw response is None
        assert processor.last_raw_response is None


class TestGetLastUsageMetadata:
    """Tests for get_last_usage_metadata method."""

    def test_get_last_usage_metadata_with_single_chunk(self):
        """Test that last usage metadata is returned from a single chunk."""
        from pipe.core.models.unified_chunk import UsageMetadata

        mock_log_repo = MagicMock()
        timezone = ZoneInfo("UTC")
        processor = GeminiApiStreamProcessor(mock_log_repo, timezone)

        # Create mock chunk with usage metadata
        mock_usage = MagicMock()
        mock_usage.prompt_token_count = 100
        mock_usage.candidates_token_count = 50
        mock_usage.total_token_count = 150
        mock_usage.cached_content_token_count = 3950

        mock_chunk = MagicMock(spec=types.GenerateContentResponse)
        mock_chunk.candidates = []
        mock_chunk.usage_metadata = mock_usage
        mock_chunk.model_dump.return_value = {"test": "data"}

        # Process the chunk
        list(processor._convert_chunk_to_unified_format(mock_chunk))

        # Verify last usage metadata
        last_usage = processor.get_last_usage_metadata()
        assert last_usage is not None
        assert isinstance(last_usage, UsageMetadata)
        assert last_usage.prompt_token_count == 100
        assert last_usage.candidates_token_count == 50
        assert last_usage.total_token_count == 150
        assert last_usage.cached_content_token_count == 3950

    def test_get_last_usage_metadata_with_multiple_chunks(self):
        """Test that last usage metadata is from the final chunk."""
        from pipe.core.models.unified_chunk import UsageMetadata

        mock_log_repo = MagicMock()
        timezone = ZoneInfo("UTC")
        processor = GeminiApiStreamProcessor(mock_log_repo, timezone)

        # Create first chunk with usage metadata
        mock_usage1 = MagicMock()
        mock_usage1.prompt_token_count = 100
        mock_usage1.candidates_token_count = 50
        mock_usage1.total_token_count = 150
        mock_usage1.cached_content_token_count = None

        mock_chunk1 = MagicMock(spec=types.GenerateContentResponse)
        mock_chunk1.candidates = []
        mock_chunk1.usage_metadata = mock_usage1
        mock_chunk1.model_dump.return_value = {"chunk": "1"}

        # Create second chunk with different usage metadata
        mock_usage2 = MagicMock()
        mock_usage2.prompt_token_count = 200
        mock_usage2.candidates_token_count = 75
        mock_usage2.total_token_count = 275
        mock_usage2.cached_content_token_count = 3950

        mock_chunk2 = MagicMock(spec=types.GenerateContentResponse)
        mock_chunk2.candidates = []
        mock_chunk2.usage_metadata = mock_usage2
        mock_chunk2.model_dump.return_value = {"chunk": "2"}

        # Process both chunks
        list(processor._convert_chunk_to_unified_format(mock_chunk1))
        list(processor._convert_chunk_to_unified_format(mock_chunk2))

        # Verify last usage metadata is from the second chunk
        last_usage = processor.get_last_usage_metadata()
        assert last_usage is not None
        assert isinstance(last_usage, UsageMetadata)
        assert last_usage.prompt_token_count == 200
        assert last_usage.candidates_token_count == 75
        assert last_usage.total_token_count == 275
        assert last_usage.cached_content_token_count == 3950

    def test_get_last_usage_metadata_with_no_usage(self):
        """Test that None is returned when no usage metadata exists."""
        mock_log_repo = MagicMock()
        timezone = ZoneInfo("UTC")
        processor = GeminiApiStreamProcessor(mock_log_repo, timezone)

        # Create chunk without usage metadata
        mock_chunk = MagicMock(spec=types.GenerateContentResponse)
        mock_chunk.candidates = []
        mock_chunk.usage_metadata = None
        mock_chunk.model_dump.return_value = {"chunk": "1"}

        # Process the chunk
        list(processor._convert_chunk_to_unified_format(mock_chunk))

        # Verify no usage metadata
        last_usage = processor.get_last_usage_metadata()
        assert last_usage is None

    def test_get_last_usage_metadata_with_null_cached_count(self):
        """Test that cached_content_token_count=None is properly stored."""
        from pipe.core.models.unified_chunk import UsageMetadata

        mock_log_repo = MagicMock()
        timezone = ZoneInfo("UTC")
        processor = GeminiApiStreamProcessor(mock_log_repo, timezone)

        # Create mock chunk with cached_content_token_count=None
        mock_usage = MagicMock()
        mock_usage.prompt_token_count = 100
        mock_usage.candidates_token_count = 50
        mock_usage.total_token_count = 150
        mock_usage.cached_content_token_count = None

        mock_chunk = MagicMock(spec=types.GenerateContentResponse)
        mock_chunk.candidates = []
        mock_chunk.usage_metadata = mock_usage
        mock_chunk.model_dump.return_value = {"test": "data"}

        # Process the chunk
        list(processor._convert_chunk_to_unified_format(mock_chunk))

        # Verify last usage metadata with None cached count
        last_usage = processor.get_last_usage_metadata()
        assert last_usage is not None
        assert isinstance(last_usage, UsageMetadata)
        assert last_usage.cached_content_token_count is None


class TestLogRawChunk:
    """Tests for _log_raw_chunk method."""

    @patch("pipe.core.domains.gemini_api_stream_processor.get_current_datetime")
    def test_log_raw_chunk_success(self, mock_datetime):
        """Test that raw chunk is successfully logged."""
        mock_log_repo = MagicMock()
        timezone = ZoneInfo("UTC")
        processor = GeminiApiStreamProcessor(mock_log_repo, timezone)

        mock_datetime.return_value = "2025-01-01T00:00:00+00:00"

        # Create mock chunk
        mock_chunk = MagicMock(spec=types.GenerateContentResponse)
        mock_chunk.model_dump.return_value = {"chunk_data": "test"}

        # Call the method
        processor._log_raw_chunk(mock_chunk)

        # Verify write_log_line was called correctly
        mock_log_repo.write_log_line.assert_called_once_with(
            "RAW_CHUNK",
            json.dumps({"chunk_data": "test"}, ensure_ascii=False),
            "2025-01-01T00:00:00+00:00",
        )

    def test_log_raw_chunk_exception_handling(self):
        """Test that exceptions in _log_raw_chunk are silently handled."""
        mock_log_repo = MagicMock()
        timezone = ZoneInfo("UTC")
        processor = GeminiApiStreamProcessor(mock_log_repo, timezone)

        # Create mock chunk that raises exception on model_dump
        mock_chunk = MagicMock(spec=types.GenerateContentResponse)
        mock_chunk.model_dump.side_effect = Exception("Test exception")

        # Call the method - should not raise exception
        processor._log_raw_chunk(mock_chunk)

        # Verify no log was written
        mock_log_repo.write_log_line.assert_not_called()


class TestConvertChunkToUnifiedFormat:
    """Tests for _convert_chunk_to_unified_format method."""

    def test_convert_text_chunk_with_thought_false(self):
        """Test conversion of text chunk with thought=False."""
        mock_log_repo = MagicMock()
        timezone = ZoneInfo("UTC")
        processor = GeminiApiStreamProcessor(mock_log_repo, timezone)

        # Create mock chunk with text part
        mock_part = MagicMock()
        mock_part.text = "Regular text content"
        mock_part.thought = False

        mock_content = MagicMock()
        mock_content.parts = [mock_part]

        mock_candidate = MagicMock()
        mock_candidate.content = mock_content

        mock_chunk = MagicMock(spec=types.GenerateContentResponse)
        mock_chunk.candidates = [mock_candidate]
        mock_chunk.usage_metadata = None

        # Convert chunk
        unified_chunks = processor._convert_chunk_to_unified_format(mock_chunk)

        # Verify TextChunk was created correctly
        assert len(unified_chunks) == 1
        assert isinstance(unified_chunks[0], TextChunk)
        assert unified_chunks[0].content == "Regular text content"
        assert unified_chunks[0].is_thought is False

    def test_convert_text_chunk_with_thought_true(self):
        """Test conversion of text chunk with thought=True."""
        mock_log_repo = MagicMock()
        timezone = ZoneInfo("UTC")
        processor = GeminiApiStreamProcessor(mock_log_repo, timezone)

        # Create mock chunk with thought text
        mock_part = MagicMock()
        mock_part.text = "Thinking process"
        mock_part.thought = True

        mock_content = MagicMock()
        mock_content.parts = [mock_part]

        mock_candidate = MagicMock()
        mock_candidate.content = mock_content

        mock_chunk = MagicMock(spec=types.GenerateContentResponse)
        mock_chunk.candidates = [mock_candidate]
        mock_chunk.usage_metadata = None

        # Convert chunk
        unified_chunks = processor._convert_chunk_to_unified_format(mock_chunk)

        # Verify TextChunk was created with is_thought=True
        assert len(unified_chunks) == 1
        assert isinstance(unified_chunks[0], TextChunk)
        assert unified_chunks[0].content == "Thinking process"
        assert unified_chunks[0].is_thought is True

    def test_convert_tool_call_chunk(self):
        """Test conversion of tool call chunk."""
        mock_log_repo = MagicMock()
        timezone = ZoneInfo("UTC")
        processor = GeminiApiStreamProcessor(mock_log_repo, timezone)

        # Create mock function_call
        mock_function_call = MagicMock()
        mock_function_call.name = "search_database"
        mock_function_call.args = {"query": "test", "limit": 10}

        # Create mock part with function_call
        mock_part = MagicMock()
        mock_part.text = None
        mock_part.function_call = mock_function_call

        mock_content = MagicMock()
        mock_content.parts = [mock_part]

        mock_candidate = MagicMock()
        mock_candidate.content = mock_content

        mock_chunk = MagicMock(spec=types.GenerateContentResponse)
        mock_chunk.candidates = [mock_candidate]
        mock_chunk.usage_metadata = None

        # Convert chunk
        unified_chunks = processor._convert_chunk_to_unified_format(mock_chunk)

        # Verify ToolCallChunk was created correctly
        assert len(unified_chunks) == 1
        assert isinstance(unified_chunks[0], ToolCallChunk)
        assert unified_chunks[0].name == "search_database"
        assert unified_chunks[0].args == {"query": "test", "limit": 10}

    def test_convert_tool_call_chunk_with_none_args(self):
        """Test conversion of tool call chunk with None args."""
        mock_log_repo = MagicMock()
        timezone = ZoneInfo("UTC")
        processor = GeminiApiStreamProcessor(mock_log_repo, timezone)

        # Create mock function_call with None args
        mock_function_call = MagicMock()
        mock_function_call.name = "no_args_function"
        mock_function_call.args = None

        # Create mock part with function_call
        mock_part = MagicMock()
        mock_part.text = None
        mock_part.function_call = mock_function_call

        mock_content = MagicMock()
        mock_content.parts = [mock_part]

        mock_candidate = MagicMock()
        mock_candidate.content = mock_content

        mock_chunk = MagicMock(spec=types.GenerateContentResponse)
        mock_chunk.candidates = [mock_candidate]
        mock_chunk.usage_metadata = None

        # Convert chunk
        unified_chunks = processor._convert_chunk_to_unified_format(mock_chunk)

        # Verify ToolCallChunk was created with empty args dict
        assert len(unified_chunks) == 1
        assert isinstance(unified_chunks[0], ToolCallChunk)
        assert unified_chunks[0].name == "no_args_function"
        assert unified_chunks[0].args == {}

    def test_convert_chunk_with_mixed_parts(self):
        """Test conversion of chunk with both text and tool call parts."""
        mock_log_repo = MagicMock()
        timezone = ZoneInfo("UTC")
        processor = GeminiApiStreamProcessor(mock_log_repo, timezone)

        # Create text part
        mock_text_part = MagicMock()
        mock_text_part.text = "Calling a tool"
        mock_text_part.thought = False

        # Create function_call part
        mock_function_call = MagicMock()
        mock_function_call.name = "execute_query"
        mock_function_call.args = {"sql": "SELECT * FROM users"}

        mock_tool_part = MagicMock()
        mock_tool_part.text = None
        mock_tool_part.function_call = mock_function_call

        mock_content = MagicMock()
        mock_content.parts = [mock_text_part, mock_tool_part]

        mock_candidate = MagicMock()
        mock_candidate.content = mock_content

        mock_chunk = MagicMock(spec=types.GenerateContentResponse)
        mock_chunk.candidates = [mock_candidate]
        mock_chunk.usage_metadata = None

        # Convert chunk
        unified_chunks = processor._convert_chunk_to_unified_format(mock_chunk)

        # Verify both chunks were created
        assert len(unified_chunks) == 2
        assert isinstance(unified_chunks[0], TextChunk)
        assert unified_chunks[0].content == "Calling a tool"
        assert isinstance(unified_chunks[1], ToolCallChunk)
        assert unified_chunks[1].name == "execute_query"


class TestSaveRawResponseExceptionHandling:
    """Tests for exception handling in _save_raw_response method."""

    def test_save_raw_response_with_model_dump_exception(self):
        """Test that exception in model_dump is handled gracefully."""
        mock_log_repo = MagicMock()
        timezone = ZoneInfo("UTC")
        processor = GeminiApiStreamProcessor(mock_log_repo, timezone)

        # Create mock chunk with thought=True (should save)
        mock_part = MagicMock()
        mock_part.thought_signature = None
        mock_part.thought = True
        mock_part.text = "thinking"

        mock_content = MagicMock()
        mock_content.parts = [mock_part]

        mock_candidate = MagicMock()
        mock_candidate.content = mock_content

        # Make model_dump raise exception
        mock_chunk = MagicMock(spec=types.GenerateContentResponse)
        mock_chunk.candidates = [mock_candidate]
        mock_chunk.model_dump.side_effect = Exception("Serialization error")

        processor.collected_chunks = [mock_chunk]

        # Call the method - should handle exception gracefully
        processor._save_raw_response()

        # Verify raw response is None due to exception
        assert processor.last_raw_response is None


class TestGetLastRawResponse:
    """Tests for get_last_raw_response method."""

    def test_get_last_raw_response_with_saved_response(self):
        """Test getting raw response when it exists."""
        mock_log_repo = MagicMock()
        timezone = ZoneInfo("UTC")
        processor = GeminiApiStreamProcessor(mock_log_repo, timezone)

        # Create mock chunk with thought=True
        mock_part = MagicMock()
        mock_part.thought_signature = None
        mock_part.thought = True
        mock_part.text = "thinking"

        mock_content = MagicMock()
        mock_content.parts = [mock_part]

        mock_candidate = MagicMock()
        mock_candidate.content = mock_content

        mock_chunk = MagicMock(spec=types.GenerateContentResponse)
        mock_chunk.candidates = [mock_candidate]
        mock_chunk.model_dump.return_value = {"test": "data"}

        processor.collected_chunks = [mock_chunk]

        # Save raw response
        processor._save_raw_response()

        # Get last raw response
        raw_response = processor.get_last_raw_response()

        # Verify raw response is returned correctly
        assert raw_response is not None
        saved_data = json.loads(raw_response)
        assert len(saved_data) == 1
        assert saved_data[0] == {"test": "data"}

    def test_get_last_raw_response_with_no_response(self):
        """Test getting raw response when it doesn't exist."""
        mock_log_repo = MagicMock()
        timezone = ZoneInfo("UTC")
        processor = GeminiApiStreamProcessor(mock_log_repo, timezone)

        # Get last raw response without saving any
        raw_response = processor.get_last_raw_response()

        # Verify raw response is None
        assert raw_response is None

    def test_get_last_raw_response_with_non_special_content(self):
        """Test getting raw response when no special content exists."""
        mock_log_repo = MagicMock()
        timezone = ZoneInfo("UTC")
        processor = GeminiApiStreamProcessor(mock_log_repo, timezone)

        # Create mock chunk with regular text (no special content)
        mock_part = MagicMock()
        mock_part.thought_signature = None
        mock_part.thought = False
        mock_part.function_call = None
        mock_part.text = "regular text"

        mock_content = MagicMock()
        mock_content.parts = [mock_part]

        mock_candidate = MagicMock()
        mock_candidate.content = mock_content

        mock_chunk = MagicMock(spec=types.GenerateContentResponse)
        mock_chunk.candidates = [mock_candidate]

        processor.collected_chunks = [mock_chunk]

        # Save raw response
        processor._save_raw_response()

        # Get last raw response
        raw_response = processor.get_last_raw_response()

        # Verify raw response is None because no special content exists
        assert raw_response is None
