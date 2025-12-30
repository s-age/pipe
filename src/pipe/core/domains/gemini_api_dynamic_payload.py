"""
Data Generation Layer 2, 3, 4: API request content list construction.

Generates the "Request Payload" (Dynamic Context + Recent History + Current Task)
for the actual API inference call. Handles Thought Signature restoration.
"""

import json
import os
from typing import Any

from google.genai import types
from jinja2 import Environment, FileSystemLoader
from pipe.core.models.prompt import Prompt
from pipe.core.models.turn import (
    FunctionCallingTurn,
    ModelResponseTurn,
    ToolResponseTurn,
    Turn,
    UserTaskTurn,
)


class GeminiApiDynamicPayload:
    """
    Builds dynamic payload for Gemini API inference requests.

    Handles:
    - Layer 2: Dynamic context (file_references, current_datetime, todos, artifacts)
    - Layer 3: Buffered history with Thought Signature restoration
    - Layer 4: Current task trigger
    """

    def __init__(self, project_root: str):
        """
        Initialize the dynamic payload builder.

        Args:
            project_root: Path to project root (for template loading).
        """
        self.project_root = project_root

    def build(self, prompt: Prompt) -> list[types.Content]:
        """
        Construct the payload for models.generate_content.

        Args:
            prompt: Prompt object containing all dynamic context.

        Returns:
            List of Content objects for API request.

        Internal Logic:
            1. Dynamic Context (Layer 2): Render gemini_dynamic_prompt.j2
            2. Buffered History (Layer 3): Restore thought signatures
            3. Trigger (Layer 4): Add current task if exists
        """
        contents: list[types.Content] = []

        # Layer 2: Dynamic Context
        dynamic_content = self._build_dynamic_context(prompt)
        if dynamic_content:
            contents.append(dynamic_content)

        # Layer 3: Buffered History
        if prompt.buffered_history:
            # Handle both PromptConversationHistory and list[Turn]
            buffered_turns = (
                prompt.buffered_history.turns
                if hasattr(prompt.buffered_history, "turns")
                else prompt.buffered_history
            )
            history_contents = self._build_buffered_history(buffered_turns)  # type: ignore[arg-type]
            contents.extend(history_contents)

        # Layer 4: Current Task Trigger
        if prompt.current_task:
            trigger_content = types.Content(
                role="user",
                parts=[types.Part(text=prompt.current_task.instruction)],
            )
            contents.append(trigger_content)

        return contents

    def _build_dynamic_context(self, prompt: Prompt) -> types.Content | None:
        """
        Build dynamic context from prompt using gemini_dynamic_prompt.j2.

        Args:
            prompt: Prompt object with dynamic context fields.

        Returns:
            Content object with rendered dynamic context, or None if empty.
        """
        template_path = os.path.join(self.project_root, "templates", "prompt")
        jinja_env = Environment(
            loader=FileSystemLoader(template_path),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        template = jinja_env.get_template("gemini_dynamic_prompt.j2")

        # Build rendering context
        rendering_context = {
            "file_references": prompt.file_references,
            "current_datetime": prompt.current_datetime,
            "todos": prompt.todos,
            "artifacts": prompt.artifacts,
        }

        rendered_text = template.render(session=rendering_context)

        # Only return content if there's actual text
        if rendered_text.strip():
            return types.Content(
                role="user",
                parts=[types.Part(text=rendered_text)],
            )

        return None

    def _build_buffered_history(
        self, buffered_history: list[Turn]
    ) -> list[types.Content]:
        """
        Build history contents with thought signature restoration.

        Args:
            buffered_history: List of Turn objects from prompt.

        Returns:
            List of Content objects representing the buffered history.
        """
        contents: list[types.Content] = []

        for turn in buffered_history:
            if isinstance(turn, UserTaskTurn):
                # User task turns
                contents.append(
                    types.Content(
                        role="user",
                        parts=[types.Part(text=turn.instruction)],
                    )
                )
            elif isinstance(turn, ModelResponseTurn):
                # Try to restore thought signature, fallback to simple text
                restored_content = self._restore_thought_signature(turn)
                if restored_content:
                    contents.append(restored_content)
                else:
                    # Fallback to simple text content
                    contents.append(
                        types.Content(
                            role="model",
                            parts=[types.Part(text=turn.content)],
                        )
                    )
            elif isinstance(turn, FunctionCallingTurn):
                # Function calling turns - restore from raw_response
                restored_content = self._restore_function_call(turn)
                if restored_content:
                    contents.append(restored_content)
            elif isinstance(turn, ToolResponseTurn):
                # Tool response turns - convert to function_response
                tool_response_content = self._build_tool_response(turn)
                if tool_response_content:
                    contents.append(tool_response_content)

        return contents

    def _restore_thought_signature(
        self, turn: ModelResponseTurn
    ) -> types.Content | None:
        """
        Reconstruct Content with thought parts from raw_response.

        Args:
            turn: ModelResponseTurn with potential raw_response.

        Returns:
            Fully reconstructed Content with thought/text parts, or None if restoration fails.
        """
        if not turn.raw_response:
            return None

        try:
            # Parse raw_response JSON
            chunks_data = json.loads(turn.raw_response)

            # Extract parts from the last chunk's candidate
            # raw_response is a list of GenerateContentResponse chunks
            if not chunks_data or not isinstance(chunks_data, list):
                return None

            # Look for the last chunk with actual content
            for chunk_data in reversed(chunks_data):
                if not isinstance(chunk_data, dict):
                    continue

                candidates = chunk_data.get("candidates", [])
                if not candidates:
                    continue

                for candidate in candidates:
                    content_data = candidate.get("content")
                    if not content_data:
                        continue

                    parts_data = content_data.get("parts", [])
                    if not parts_data:
                        continue

                    # Reconstruct parts with thought signature
                    parts = self._reconstruct_parts(parts_data)
                    if parts:
                        return types.Content(
                            role="model",
                            parts=parts,
                        )

            return None

        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def _reconstruct_parts(self, parts_data: list[dict[str, Any]]) -> list[types.Part]:
        """
        Reconstruct Part objects from raw parts data.

        Args:
            parts_data: List of part dictionaries from raw_response.

        Returns:
            List of reconstructed Part objects.
        """
        parts: list[types.Part] = []

        for part_data in parts_data:
            # Check for thought_signature
            if "thought_signature" in part_data:
                thought_sig = part_data["thought_signature"]
                if isinstance(thought_sig, dict):
                    chunks = thought_sig.get("chunks", [])
                    for chunk in chunks:
                        if isinstance(chunk, dict):
                            # Reconstruct thought or text part
                            if "thought" in chunk:
                                parts.append(
                                    types.Part(
                                        thought=True,
                                        text=chunk.get("thought", ""),
                                    )
                                )
                            elif "text" in chunk:
                                parts.append(
                                    types.Part(
                                        text=chunk.get("text", ""),
                                    )
                                )
            # Check for regular thought part
            elif part_data.get("thought") is True and "text" in part_data:
                parts.append(
                    types.Part(
                        thought=True,
                        text=part_data.get("text", ""),
                    )
                )
            # Check for regular text part
            elif "text" in part_data:
                parts.append(
                    types.Part(
                        text=part_data.get("text", ""),
                    )
                )
            # Check for function_call
            elif "function_call" in part_data:
                func_call_data = part_data["function_call"]
                if isinstance(func_call_data, dict):
                    parts.append(
                        types.Part(
                            function_call=types.FunctionCall(
                                name=func_call_data.get("name", ""),
                                args=func_call_data.get("args", {}),
                            )
                        )
                    )

        return parts

    def _restore_function_call(self, turn: FunctionCallingTurn) -> types.Content | None:
        """
        Reconstruct Content with function call from raw_response.

        Args:
            turn: FunctionCallingTurn with raw_response.

        Returns:
            Reconstructed Content with function_call parts, or None if restoration fails.
        """
        if not turn.raw_response:
            return None

        try:
            chunks_data = json.loads(turn.raw_response)

            if not chunks_data or not isinstance(chunks_data, list):
                return None

            # Look for the last chunk with function call
            for chunk_data in reversed(chunks_data):
                if not isinstance(chunk_data, dict):
                    continue

                candidates = chunk_data.get("candidates", [])
                if not candidates:
                    continue

                for candidate in candidates:
                    content_data = candidate.get("content")
                    if not content_data:
                        continue

                    parts_data = content_data.get("parts", [])
                    if not parts_data:
                        continue

                    parts = self._reconstruct_parts(parts_data)
                    if parts:
                        return types.Content(
                            role="model",
                            parts=parts,
                        )

            return None

        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def _build_tool_response(self, turn: ToolResponseTurn) -> types.Content | None:
        """
        Build Content with function_response from ToolResponseTurn.

        Args:
            turn: ToolResponseTurn containing tool execution result.

        Returns:
            Content object with function_response part, or None if data is invalid.
        """
        if not turn.response:
            return None

        # Build response dictionary from TurnResponse
        response_dict = {
            "status": turn.response.status,
        }

        # Include message if present
        if turn.response.message:
            response_dict["message"] = turn.response.message

        # Include any extra fields from TurnResponse
        if hasattr(turn.response, "model_extra") and turn.response.model_extra:
            response_dict.update(turn.response.model_extra)

        # Build FunctionResponse part
        function_response_part = types.Part(
            function_response=types.FunctionResponse(
                name=turn.name,
                response=response_dict,
            )
        )

        return types.Content(
            role="user",
            parts=[function_response_part],
        )
