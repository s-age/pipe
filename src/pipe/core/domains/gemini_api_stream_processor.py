"""
Stream processor for Gemini API output.

Handles streaming chunk processing, logging, and conversion to unified format.
"""

import json
from collections.abc import Generator
from typing import TYPE_CHECKING

from google.genai import types
from pipe.core.models.unified_chunk import (
    MetadataChunk,
    TextChunk,
    ToolCallChunk,
    UnifiedChunk,
    UsageMetadata,
)
from pipe.core.utils.datetime import get_current_datetime

if TYPE_CHECKING:
    import zoneinfo

    from pipe.core.repositories.streaming_log_repository import StreamingLogRepository


class GeminiApiStreamProcessor:
    """
    Processes streaming chunks from Gemini API.

    This class handles:
    - Raw chunk logging with metadata extraction
    - Conversion to unified chunk format (TextChunk, ToolCallChunk, MetadataChunk)
    - Collecting raw responses for thought signature preservation
    """

    def __init__(
        self,
        streaming_log_repo: "StreamingLogRepository",
        timezone: "zoneinfo.ZoneInfo",
    ):
        """
        Initialize the stream processor.

        Args:
            streaming_log_repo: Repository for logging stream chunks
            timezone: Timezone for timestamp formatting
        """
        self.streaming_log_repo = streaming_log_repo
        self.timezone = timezone
        self.collected_chunks: list[types.GenerateContentResponse] = []
        self.last_raw_response: str | None = None

    def process_stream(
        self,
        stream: Generator[types.GenerateContentResponse, None, None],
    ) -> Generator[UnifiedChunk, None, None]:
        """
        Process streaming API response chunks.

        Args:
            stream: Generator of Gemini API response chunks

        Yields:
            Unified Pydantic chunk models (TextChunk | ToolCallChunk | MetadataChunk)
        """
        for chunk in stream:
            self.collected_chunks.append(chunk)

            # Log raw chunk (extract text and usage, skip binary fields)
            self._log_raw_chunk(chunk)

            # Convert Gemini chunk to unified format
            unified_chunks = self._convert_chunk_to_unified_format(chunk)
            yield from unified_chunks

        # After stream completes, save the collected chunks as raw_response
        self._save_raw_response()

    def _log_raw_chunk(self, chunk: types.GenerateContentResponse) -> None:
        """
        Log the complete raw chunk from API as-is.

        Args:
            chunk: Gemini API response chunk
        """
        try:
            # Log the entire API response as-is
            chunk_data = chunk.model_dump()
            self.streaming_log_repo.write_log_line(
                "RAW_CHUNK",
                json.dumps(chunk_data, ensure_ascii=False),
                get_current_datetime(self.timezone),
            )
        except Exception:
            pass

    def _convert_chunk_to_unified_format(
        self, chunk: types.GenerateContentResponse
    ) -> list[UnifiedChunk]:
        """
        Convert Gemini API chunk to unified Pydantic format.

        Args:
            chunk: Raw Gemini API response chunk

        Returns:
            List of unified Pydantic chunk models
        """
        unified_chunks: list[UnifiedChunk] = []

        # Extract candidates if present
        if chunk.candidates and len(chunk.candidates) > 0:
            candidate = chunk.candidates[0]
            if candidate.content and candidate.content.parts:
                # Extract text content and tool calls
                for part in candidate.content.parts:
                    if part.text is not None:
                        is_thought = bool(getattr(part, "thought", False))
                        unified_chunks.append(
                            TextChunk(content=part.text, is_thought=is_thought)
                        )
                    elif hasattr(part, "function_call") and part.function_call:
                        unified_chunks.append(
                            ToolCallChunk(
                                name=part.function_call.name,
                                args=dict(part.function_call.args or {}),
                            )
                        )

        # Extract usage metadata (typically on final chunk)
        if chunk.usage_metadata:
            unified_chunks.append(
                MetadataChunk(
                    usage=UsageMetadata(
                        prompt_token_count=chunk.usage_metadata.prompt_token_count,
                        candidates_token_count=chunk.usage_metadata.candidates_token_count,
                        total_token_count=chunk.usage_metadata.total_token_count,
                        cached_content_token_count=chunk.usage_metadata.cached_content_token_count,
                    )
                )
            )

        return unified_chunks

    def _save_raw_response(self) -> None:
        """
        Save the collected chunks as raw_response JSON if special content exists.

        This preserves:
        - thought_signature (for thinking models)
        - thought=True parts (thinking process)
        - function_call (tool invocations)

        If none of these are found, raw_response is set to None to save space.
        Note: function_response (tool results) is not saved as it's external data.
        """
        if not self.collected_chunks:
            return

        should_save = False
        for chunk in self.collected_chunks:
            if chunk.candidates:
                for candidate in chunk.candidates:
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            # Check for thought_signature
                            if getattr(part, "thought_signature", None):
                                should_save = True
                                break
                            # Check for thought=True
                            if getattr(part, "thought", False):
                                should_save = True
                                break
                            # Check for function_call (tool invocation)
                            if getattr(part, "function_call", None):
                                should_save = True
                                break
                    if should_save:
                        break
            if should_save:
                break

        if should_save:
            try:
                # Dump all chunks to a list of dicts
                chunks_data = [chunk.model_dump() for chunk in self.collected_chunks]
                self.last_raw_response = json.dumps(chunks_data, ensure_ascii=False)
            except Exception:
                # Fallback or error handling if needed, currently just keeping None
                self.last_raw_response = None
        else:
            self.last_raw_response = None

    def get_last_raw_response(self) -> str | None:
        """
        Get the last raw response JSON.

        Returns:
            JSON string of the last response chunk, or None
        """
        return self.last_raw_response
