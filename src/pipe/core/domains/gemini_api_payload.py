"""
Payload builder for Gemini API.

Generates static and dynamic prompts for the Gemini API using Jinja2 templates.
Supports caching by splitting prompts into static (cacheable) and dynamic parts.
Also builds generation configuration with hyperparameters.
"""

import json
import os
from typing import TYPE_CHECKING

from google.genai import types
from jinja2 import Environment, FileSystemLoader
from pipe.core.domains.artifacts import build_artifacts_from_data
from pipe.core.factories.prompt_factory import PromptFactory
from pipe.core.models.gemini_api_payload import (
    GeminiApiDynamicPayload,
    GeminiApiStaticPayload,
)
from pipe.core.models.prompt import Prompt
from pipe.core.repositories.resource_repository import ResourceRepository

if TYPE_CHECKING:
    from pipe.core.models.settings import Settings
    from pipe.core.services.session_service import SessionService


class GeminiApiPayloadBuilder:
    """
    Builds static and dynamic prompts for Gemini API.

    This class renders Prompt objects into static and dynamic content using
    separate Jinja2 templates to support context caching. Also builds
    generation configuration with hyperparameters.
    """

    def __init__(self, project_root: str, settings: "Settings"):
        """
        Initialize the Gemini API payload builder.

        Args:
            project_root: The project root directory
            settings: Settings object for default hyperparameters
        """
        self.project_root = project_root
        self.settings = settings
        self.jinja_env = self._create_jinja_environment()
        self.resource_repository = ResourceRepository(project_root)
        self.prompt_factory = PromptFactory(project_root, self.resource_repository)
        self.last_cached_turn_count: int | None = None

    def _create_jinja_environment(self) -> Environment:
        """
        Create and configure the Jinja2 environment for template rendering.

        Returns:
            Configured Jinja2 Environment
        """
        template_path = os.path.join(self.project_root, "templates", "prompt")
        loader = FileSystemLoader(template_path)
        env = Environment(
            loader=loader,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Configure tojson filter to disable ASCII escaping
        def tojson_filter(value):
            return json.dumps(value, ensure_ascii=False)

        env.filters["tojson"] = tojson_filter

        # Add custom filter to serialize Pydantic models to dict for JSON serialization
        def pydantic_dump(obj):
            """Convert Pydantic model to dict using model_dump()."""
            if hasattr(obj, "model_dump"):
                return obj.model_dump()
            return obj

        env.filters["pydantic_dump"] = pydantic_dump
        return env

    def build_prompt(self, session_service: "SessionService") -> Prompt:
        """
        Build a Prompt object from session data.

        Args:
            session_service: Service containing session data

        Returns:
            A fully constructed Prompt object
        """
        current_session = session_service.current_session
        settings = session_service.settings

        if not current_session:
            raise ValueError("Cannot build prompt without a current session.")

        # Process artifacts (read file contents)
        processed_artifacts = None
        if current_session.artifacts:
            artifacts_with_contents = []
            for artifact_path in current_session.artifacts:
                full_path = os.path.abspath(
                    os.path.join(self.project_root, artifact_path)
                )
                contents = None
                if self.resource_repository.exists(
                    full_path, allowed_root=self.project_root
                ):
                    contents = self.resource_repository.read_text(
                        full_path, allowed_root=self.project_root
                    )
                artifacts_with_contents.append((artifact_path, contents))

            processed_artifacts = build_artifacts_from_data(artifacts_with_contents)

        # Create and return the Prompt object
        return self.prompt_factory.create(
            session=current_session,
            settings=settings,
            artifacts=processed_artifacts,
            current_instruction=session_service.current_instruction,
        )

    def render(
        self, prompt_model: Prompt
    ) -> tuple[GeminiApiStaticPayload, GeminiApiDynamicPayload]:
        """
        Convert Prompt model to complete 4-layer API payload.

        Returns:
            Tuple of (static_payload, dynamic_payload)
            - Static: Cached content + Buffered history (Layers 1-2)
            - Dynamic: Dynamic context + Current instruction (Layers 3-4)
        """
        # Build Static Part (Layers 1-2)
        static = self._render_static_payload(prompt_model)

        # Build Dynamic Part (Layers 3-4)
        dynamic = self._render_dynamic_payload(prompt_model)

        return static, dynamic

    def _render_static_payload(self, prompt_model: Prompt) -> GeminiApiStaticPayload:
        """
        Build static (cacheable) part of payload.

        Returns:
            GeminiApiStaticPayload containing Layer 1 (cached) and Layer 3 (buffered)
        """
        # Layer 1: Render cached content (static system instructions)
        cached_content = self._render_static_template(prompt_model)

        # Layer 3: Convert buffered history with thought_signature restoration
        buffered_history = self._convert_buffered_history(prompt_model.buffered_history)

        return GeminiApiStaticPayload(
            cached_content=cached_content, buffered_history=buffered_history
        )

    def _render_dynamic_payload(self, prompt_model: Prompt) -> GeminiApiDynamicPayload:
        """
        Build dynamic (non-cacheable) part of payload.

        Returns:
            GeminiApiDynamicPayload containing Layer 2 (dynamic) and Layer 4 (instruction)
        """
        # Layer 2: Render dynamic context (JSON)
        dynamic_content = self._render_dynamic_template(prompt_model)

        # Layer 4: Convert current instruction
        current_instruction = self._convert_current_instruction(
            prompt_model.current_task
        )

        return GeminiApiDynamicPayload(
            dynamic_content=dynamic_content, current_instruction=current_instruction
        )

    def _render_static_template(self, prompt_model: Prompt) -> str:
        """Render Layer 1: Cached content (gemini_static_prompt.j2)."""
        context = prompt_model.model_dump()
        try:
            template = self.jinja_env.get_template("gemini_static_prompt.j2")
            return template.render(session=context)
        except Exception:
            # Fallback: use monolithic template (no caching)
            template = self.jinja_env.get_template("gemini_api_prompt.j2")
            return ""

    def _render_dynamic_template(self, prompt_model: Prompt) -> str:
        """Render Layer 2: Dynamic content as JSON."""
        context = prompt_model.model_dump()
        try:
            template = self.jinja_env.get_template("gemini_dynamic_prompt.j2")
            return template.render(session=context)
        except Exception:
            # Fallback: use monolithic template (no caching)
            template = self.jinja_env.get_template("gemini_api_prompt.j2")
            return template.render(session=context)

    def _convert_buffered_history(self, buffered_history) -> list[types.Content]:
        """
        Convert Layer 3: Buffered history to Content objects.
        Restores thought_signature from raw_response.
        """
        if not buffered_history or not buffered_history.turns:
            return []

        return [self.convert_turn_to_content(turn) for turn in buffered_history.turns]

    def _convert_current_instruction(self, current_task) -> types.Content | None:
        """Convert Layer 4: Current instruction to Content object."""
        if not current_task or not current_task.instruction.strip():
            return None

        return types.Content(
            role="user", parts=[types.Part(text=current_task.instruction)]
        )

    def build_payloads_with_tools(
        self,
        session_service: "SessionService",
        loaded_tools: list[dict],
    ) -> tuple[GeminiApiStaticPayload, GeminiApiDynamicPayload, list[types.Tool]]:
        """
        Build complete 4-layer payload with tools.

        This is the primary entry point for Agent layer.

        Returns:
            Tuple of (static_payload, dynamic_payload, converted_tools)
        """
        prompt_model = self.build_prompt(session_service)
        static, dynamic = self.render(prompt_model)
        converted_tools = self.convert_tools(loaded_tools)

        # Track cached turn count for session metadata updates
        if prompt_model.cached_history and prompt_model.cached_history.turns:
            self.last_cached_turn_count = len(prompt_model.cached_history.turns)
        else:
            self.last_cached_turn_count = 0

        return static, dynamic, converted_tools

    def convert_tools(self, loaded_tools_data: list[dict]) -> list[types.Tool]:
        """
        Convert tool definitions to Gemini API types.

        Args:
            loaded_tools_data: List of tool definition dicts

        Returns:
            List of types.Tool objects
        """
        converted_tools = []
        for tool_data in loaded_tools_data:
            parameters_schema = types.Schema(**tool_data.get("parameters", {}))
            converted_tools.append(
                types.Tool(
                    function_declarations=[
                        types.FunctionDeclaration(
                            name=tool_data["name"],
                            description=tool_data.get("description", ""),
                            parameters=parameters_schema,
                        )
                    ]
                )
            )
        return converted_tools

    def build_generation_config(
        self,
        session_data,
        cached_content_name: str | None,
        converted_tools: list[types.Tool],
    ) -> types.GenerateContentConfig:
        """
        Build generation configuration for API call.

        Args:
            session_data: Current session data
            cached_content_name: Cache name if using cache
            converted_tools: Tool definitions

        Returns:
            Generation config object
        """
        # Base parameters from settings
        gen_config_params = {
            "temperature": self.settings.parameters.temperature.value,
            "top_p": self.settings.parameters.top_p.value,
            "top_k": self.settings.parameters.top_k.value,
        }

        # Override with session hyperparameters if present
        if session_params := session_data.hyperparameters:
            if temp_val := session_params.temperature:
                gen_config_params["temperature"] = temp_val
            if top_p_val := session_params.top_p:
                gen_config_params["top_p"] = top_p_val
            if top_k_val := session_params.top_k:
                gen_config_params["top_k"] = top_k_val

        # If using cache, don't pass tools again (they're in the cache)
        return types.GenerateContentConfig(
            tools=None if cached_content_name else converted_tools,  # type: ignore[arg-type]
            temperature=gen_config_params.get("temperature"),
            top_p=gen_config_params.get("top_p"),
            top_k=gen_config_params.get("top_k"),
            cached_content=cached_content_name,
        )

    def convert_turn_to_content(
        self, turn, raw_response: str | None = None
    ) -> types.Content:
        """
        Converts a Turn model to a Gemini Content object.

        Args:
            turn: Turn object to convert
            raw_response: Optional raw response JSON for thought signature restoration

        Returns:
            Gemini Content object
        """
        role = "user"
        parts = []

        # Determine role and basic text content
        if hasattr(turn, "type"):
            # Check for turn-specific raw_response (preferred)
            turn_raw_response = getattr(turn, "raw_response", None)
            target_raw_response = turn_raw_response or raw_response

            if turn.type == "user_task":
                role = "user"
                parts.append(types.Part(text=turn.instruction))
            elif turn.type == "model_response":
                role = "model"
                # If we have a raw response, try to restore signature
                if target_raw_response:
                    restored = self._restore_thought_signature(target_raw_response)
                    if restored:
                        return restored

                parts.append(types.Part(text=turn.content))
            elif turn.type == "function_calling":
                role = "model"
                # If we have a raw response, try to restore signature
                if target_raw_response:
                    restored = self._restore_thought_signature(target_raw_response)
                    if restored:
                        return restored

                # Simplistic text representation for now
                parts.append(types.Part(text=f"Function Call: {turn.response}"))
            elif turn.type == "tool_response":
                role = "user"
                # Simplistic representation
                parts.append(
                    types.Part(text=f"Tool Response ({turn.name}): {turn.response}")
                )

        return types.Content(role=role, parts=parts)

    def _restore_thought_signature(
        self, raw_response_json: str
    ) -> types.Content | None:
        """
        Restores content with thought signature from raw response JSON.

        Args:
            raw_response_json: Raw JSON response from API

        Returns:
            Content object with thought signature, or None if restoration fails
        """
        try:
            parsed = json.loads(raw_response_json)

            # Handle list of chunks (new format)
            if isinstance(parsed, list):
                # Iterate backwards to find the chunk with thought_signature
                for item in reversed(parsed):
                    try:
                        response = types.GenerateContentResponse.model_validate(item)
                        if response.candidates and response.candidates[0].content:
                            content = response.candidates[0].content
                            if content.parts:
                                for part in content.parts:
                                    if getattr(part, "thought_signature", None):
                                        return content
                    except Exception:
                        continue
                return None

            # Handle single object (old format)
            elif isinstance(parsed, dict):
                response = types.GenerateContentResponse.model_validate(parsed)
                if response.candidates and response.candidates[0].content:
                    return response.candidates[0].content
                return None

            return None

        except Exception:
            return None
