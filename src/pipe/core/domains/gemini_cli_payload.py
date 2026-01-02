"""
Payload builder for Gemini CLI.

Generates JSON-formatted prompts for the gemini-cli tool using Jinja2 templates.
"""

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

from jinja2 import Environment, FileSystemLoader
from pipe.core.models.prompt import Prompt

if TYPE_CHECKING:
    from pipe.core.services.session_service import SessionService


class GeminiCliPayloadBuilder:
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
        self.project_root = project_root
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
            """Convert Pydantic model to dict using model_dump().

            Uses mode='json' to ensure proper JSON serialization and prevent
            circular reference errors by converting nested models to dicts.
            """
            if hasattr(obj, "model_dump"):
                return obj.model_dump(mode="json", exclude_none=True)
            return obj

        env.filters["pydantic_dump"] = pydantic_dump
        return env

    def build_prompt_model(self, session_service: "SessionService") -> Prompt:
        """
        Build a Prompt object from session data.

        This method replicates the core functionality of PromptService.build_prompt()
        without requiring PromptService dependency.

        Args:
            session_service: Service containing session data

        Returns:
            A fully constructed Prompt object
        """
        from pipe.core.domains.artifacts import build_artifacts_from_data
        from pipe.core.factories.prompt_factory import PromptFactory
        from pipe.core.repositories.resource_repository import ResourceRepository

        current_session = session_service.current_session
        settings = session_service.settings

        if not current_session:
            raise ValueError("Cannot build prompt without a current session.")

        # Initialize repositories and factories
        resource_repository = ResourceRepository(self.project_root)
        prompt_factory = PromptFactory(self.project_root, resource_repository)

        # Process artifacts (read file contents)
        processed_artifacts = None
        if current_session.artifacts:
            artifacts_with_contents = []
            for artifact_path in current_session.artifacts:
                full_path = os.path.abspath(
                    os.path.join(self.project_root, artifact_path)
                )
                contents = None
                if resource_repository.exists(
                    full_path, allowed_root=self.project_root
                ):
                    contents = resource_repository.read_text(
                        full_path, allowed_root=self.project_root
                    )
                artifacts_with_contents.append((artifact_path, contents))

            processed_artifacts = build_artifacts_from_data(artifacts_with_contents)

        # Create and return the Prompt object
        return prompt_factory.create(
            session=current_session,
            settings=settings,
            artifacts=processed_artifacts,
            current_instruction=session_service.current_instruction,
        )

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
        rendered_prompt = template.render(prompt=prompt_model)

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
