"""Tests for Gemini API stream processor."""

import json
from unittest.mock import MagicMock
from zoneinfo import ZoneInfo

from google.genai import types
from pipe.core.domains.gemini_api_stream_processor import GeminiApiStreamProcessor


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
