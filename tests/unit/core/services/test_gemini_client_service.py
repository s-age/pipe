from unittest.mock import MagicMock

import pytest
from google.genai import types
from pipe.core.models.unified_chunk import TextChunk
from pipe.core.services.gemini_client_service import GeminiClientService


@pytest.fixture
def gemini_client_service():
    session_service = MagicMock()
    session_service.settings.timezone = "UTC"
    return GeminiClientService(session_service)


def test_convert_chunk_with_empty_text(gemini_client_service):
    """
    Verifies that a chunk with an empty string as text is correctly converted
    to a TextChunk and not ignored.
    """
    # Create a mock chunk with empty text
    mock_part = MagicMock(spec=types.Part)
    mock_part.text = ""
    mock_part.function_call = None

    mock_candidate = MagicMock()
    mock_candidate.content.parts = [mock_part]

    mock_chunk = MagicMock(spec=types.GenerateContentResponse)
    mock_chunk.candidates = [mock_candidate]
    mock_chunk.usage_metadata = None

    # Call the method
    unified_chunks = gemini_client_service._convert_chunk_to_unified_format(mock_chunk)

    # Verify
    assert len(unified_chunks) == 1
    assert isinstance(unified_chunks[0], TextChunk)
    assert unified_chunks[0].content == ""


def test_convert_chunk_with_none_text(gemini_client_service):
    """
    Verifies that a chunk with None as text is ignored and does not produce a TextChunk.
    """
    # Create a mock chunk with None text (should be ignored)
    mock_part = MagicMock(spec=types.Part)
    mock_part.text = None
    mock_part.function_call = None

    mock_candidate = MagicMock()
    mock_candidate.content.parts = [mock_part]

    mock_chunk = MagicMock(spec=types.GenerateContentResponse)
    mock_chunk.candidates = [mock_candidate]
    mock_chunk.usage_metadata = None

    # Call the method
    unified_chunks = gemini_client_service._convert_chunk_to_unified_format(mock_chunk)

    # Verify
    assert len(unified_chunks) == 0
