"""
Builds the final prompt object to be sent to the sub-agent (LLM).
"""
import json
import json5
import sys
import os

from jinja2 import Environment, FileSystemLoader
from pipe.core.utils.file import read_text_file
from pipe.core.utils.datetime import get_current_timestamp

class PromptBuilder:
    """Constructs a structured prompt object for the LLM."""

    def __init__(self, settings: dict, session_data: dict, project_root: str, api_mode: str, multi_step_reasoning_enabled: bool = False):
        self.settings = settings
        self.session_data = session_data
        self.project_root = project_root
        self.api_mode = api_mode
        self.multi_step_reasoning_enabled = multi_step_reasoning_enabled

        # Initialize Jinja2 environment
        self.template_env = Environment(
            loader=FileSystemLoader(os.path.join(self.project_root, 'templates', 'prompt')),
            trim_blocks=True,
            lstrip_blocks=True
        )
        # Add tojson filter for convenience in templates
        self.template_env.filters['tojson'] = json.dumps

    def _load_roles(self) -> list[str]:
        """Loads content from role definition files."""
        content = []
        for rel_path in self.session_data.get('roles', []):
            path = os.path.join(self.project_root, rel_path.strip())
            if os.path.isfile(path):
                content.append(read_text_file(path))
        return content

    def _build_hyperparameters_section(self) -> dict:
        """Builds the hyperparameters section from settings and session data."""
        import copy

        # 1. Start with a deep copy of the default parameters from settings
        merged_params = copy.deepcopy(self.settings.get('parameters', {}))

        # 2. Override with session-specific hyperparameters
        if session_params := self.session_data.get('hyperparameters'):
            for key, value_desc_pair in session_params.items():
                if key in merged_params:
                    # Ensure 'value' exists in the session data before overriding
                    if 'value' in value_desc_pair:
                        merged_params[key]['value'] = value_desc_pair['value']

        # 3. Build the final structure for the prompt using the merged parameters
        params = {
            "description": merged_params.get('description', "Hyperparameter settings for the model.")
        }
        for key, value_desc_pair in merged_params.items():
            if key != 'description':
                params[key] = {
                    "type": "number",
                    "value": value_desc_pair.get('value'),
                    "description": value_desc_pair.get('description')
                }
        return params

    def build(self) -> str:
        """Builds the complete prompt object as a JSON string using Jinja2 templates."""
        
        if self.api_mode == 'gemini-api':
            template = self.template_env.get_template('gemini_api_prompt.j2')
        elif self.api_mode == 'gemini-cli':
            template = self.template_env.get_template('gemini_cli_prompt.j2')
        else:
            raise ValueError(f"Unknown api_mode: {self.api_mode}")

        all_turns = self.session_data.get('turns', [])
        history_turns = all_turns[:-1]
        current_task_turn = all_turns[-1] if all_turns else {}
        current_task_turn = current_task_turn.copy() # Create a shallow copy to avoid mutating the original session data

        # If the current turn (e.g., a tool response) doesn't have an instruction,
        # find the last user instruction to keep the main task context.
        # Do not inject instruction into tool-related turns to avoid confusion.
        if not current_task_turn.get('instruction') and current_task_turn.get('type') not in ['tool_response', 'function_calling']:
            last_user_instruction = ''
            for turn in reversed(all_turns):
                if turn.get('type') == 'user_task' and turn.get('instruction'):
                    last_user_instruction = turn.get('instruction')
                    break
            current_task_turn['instruction'] = last_user_instruction

        current_instruction = current_task_turn.get('instruction', '')

        roles_content = self._load_roles()
        roles_data = {
            "description": "The following are the roles for this session.",
            "definitions": roles_content
        }

        file_references_content = []
        references = self.session_data.get('references', [])
        for ref in references:
            if not ref.get('disabled', False):
                file_path = ref.get('path')
                if os.path.isfile(file_path):
                    try:
                        content = read_text_file(file_path)
                        file_references_content.append({
                            "path": os.path.relpath(file_path, self.project_root),
                            "content": content
                        })
                    except Exception as e:
                        print(f"Warning: Could not read referenced file {file_path}: {e}", file=sys.stderr)

        # Build the complex constraints object required by the template
        constraints_settings = self.settings.get('constraints', {})
        processing_config_settings = constraints_settings.get('processing_config', {})
        hyperparameters_data = self._build_hyperparameters_section()

        constraints_data = {
            "description": constraints_settings.get('description'),
            "language": self.settings.get('language', 'Japanese'),
            "processing_config": {
                "description": processing_config_settings.get('description'),
                "multi_step_reasoning_active": self.multi_step_reasoning_enabled
            },
            "hyperparameters": hyperparameters_data
        }

        context = {
            "current_datetime": get_current_timestamp(self.template_env.globals.get('local_tz')),
            "session": {
                "description": current_instruction,
                "session_goal": {
                    "description": "This section outlines the goal of the current session.",
                    "purpose": self.session_data.get('purpose'),
                    "background": self.session_data.get('background')
                },
                "roles": roles_data,
                "file_references": file_references_content,
                "conversation_history": {
                    "description": "Historical record of past interactions in this session, in chronological order.",
                    "turns": history_turns
                },
                "current_task": current_task_turn,
                "constraints": constraints_data,
                "todos": self.session_data.get('todos', []),
                "settings": self.settings
            }
        }
        
        rendered_string = template.render(context)
        try:
            # trailing commas are ignored by `json5`.
            parsed_json = json5.loads(rendered_string)
            return json.dumps(parsed_json, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error: Generated prompt is not valid JSON. {e}", file=sys.stderr)
            print(f"--- Invalid JSON String ---\n{rendered_string}\n--- End of Invalid JSON String ---", file=sys.stderr)
            raise