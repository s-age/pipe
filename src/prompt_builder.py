"""
Builds the final prompt object to be sent to the sub-agent (LLM).
"""
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

class PromptBuilder:
    """Constructs a structured prompt object for the LLM."""

    def __init__(self, settings: dict, session_data: dict, project_root: Path, api_mode: str, multi_step_reasoning_enabled: bool = False):
        self.settings = settings
        self.session_data = session_data
        self.project_root = project_root
        self.api_mode = api_mode
        self.multi_step_reasoning_enabled = multi_step_reasoning_enabled

        # Initialize Jinja2 environment
        self.template_env = Environment(
            loader=FileSystemLoader(self.project_root / 'templates' / 'prompt'),
            trim_blocks=True, # Remove leading whitespace from lines that contain Jinja2 blocks
            lstrip_blocks=True # Remove trailing whitespace from the end of a block
        )

    def _load_roles(self) -> list[str]:
        """Loads content from role definition files."""
        content = []
        for rel_path in self.session_data.get('roles', []):
            path = self.project_root / rel_path.strip()
            if path.is_file():
                content.append(path.read_text(encoding="utf-8"))
        return content

    def build(self) -> str:
        """Builds the complete prompt object as a JSON string."""
        
        all_turns = self.session_data.get('turns', [])
        history_turns = all_turns[:-1]
        current_task_turn = all_turns[-1] if all_turns else {}

        roles_content = self._load_roles()

        prompt_object = {
            "description": "JSON object representing the entire request to the AI sub-agent. The agent's goal is to accomplish the 'current_task' based on all provided context.",
            "main_instruction": self.settings.get('main_instruction'),
            "hyperparameters": self._build_hyperparameters_section(),
            "session_goal": {
                "description": "The immutable purpose and background for this entire conversation session.",
                "purpose": self.session_data.get('purpose'),
                "background": self.session_data.get('background'),
            },
            "response_constraints": {
                "description": "Constraints that the AI sub-agent should adhere to when generating responses. The entire response, including all content, must be generated in the specified language.",
                "language": self.settings.get('language', 'Japanese'),
            },
            "roles": {
                "description": "A list of personas or role definitions that the AI sub-agent should conform to.",
                "definitions": roles_content
            },
            "conversation_history": {
                "description": "Historical record of past interactions in this session, in chronological order.",
                "turns": history_turns
            },
            "current_task": {
                "description": "The specific task that the AI sub-agent must currently execute.",
                "instruction": current_task_turn.get('instruction')
            },
            "reasoning_process": self.settings.get('reasoning_process')
        }
        
        return json.dumps(prompt_object, ensure_ascii=False, indent=2)



    def _build_hyperparameters_section(self) -> dict:
        """Builds the hyperparameters section from settings."""
        params = {}
        for key, value_desc_pair in self.settings.get('parameters', {}).items():
            params[key] = {
                "type": "number",
                "value": value_desc_pair.get('value'),
                "description": value_desc_pair.get('description')
            }
        return params
