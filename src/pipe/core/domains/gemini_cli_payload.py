"""
Payload builder for Gemini CLI.

Generates JSON-formatted prompts for the gemini-cli tool using Jinja2 templates.
"""

import json
from pathlib import Path
from typing import TYPE_CHECKING

from jinja2 import Environment, FileSystemLoader
from pipe.core.domains.payload import BasePayloadBuilder
from pipe.core.models.prompt import Prompt

if TYPE_CHECKING:
    from pipe.core.services.session_service import SessionService


class GeminiCliPayloadBuilder(BasePayloadBuilder):
    """
    Builds JSON payloads for Gemini CLI tool.

    This class renders Prompt objects into JSON format using the
    gemini_cli_prompt.j2 or gemini_api_prompt.j2 template, depending
    on the API mode setting.
    """

    def __init__(self, project_root: str, api_mode: str = "gemini-cli"):
        """
        Initialize the Gemini CLI payload builder.

        Args:
            project_root: The project root directory
            api_mode: API mode ('gemini-cli' or 'gemini-api')
        """
        super().__init__(project_root)
        self.api_mode = api_mode
        self.jinja_env = self._create_jinja_environment()

    def _create_jinja_environment(self) -> Environment:
        """
        Create and configure the Jinja2 environment for template rendering.

        Returns:
            Configured Jinja2 Environment
        """
        template_path = str(Path(self.project_root) / "templates" / "prompt")
        loader = FileSystemLoader(template_path)
        env = Environment(loader=loader, autoescape=False)

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

    def render(self, prompt_model: Prompt) -> str:
        """
        Render the Prompt model into a JSON string for Gemini CLI.

        Args:
            prompt_model: The Prompt object to render

        Returns:
            Pretty-printed JSON string ready for gemini-cli
        """
        # Select template based on API mode
        template_name = (
            "gemini_api_prompt.j2"
            if self.api_mode == "gemini-api"
            else "gemini_cli_prompt.j2"
        )

        template = self.jinja_env.get_template(template_name)
        rendered_prompt = template.render(session=prompt_model)

        # Ensure the rendered prompt is valid JSON and pretty-print it
        json_output = json.dumps(
            json.loads(rendered_prompt), indent=2, ensure_ascii=False
        )

        # Escape @ to prevent gemini-cli from treating it as a file path
        return json_output.replace("@", "\\@")

    def build(self, session_service: "SessionService") -> str:
        """
        Build and render the complete JSON payload for Gemini CLI.

        Args:
            session_service: Service containing session data

        Returns:
            Pretty-printed JSON string ready to send to gemini-cli
        """
        prompt_model = self.build_prompt_model(session_service)
        return self.render(prompt_model)
