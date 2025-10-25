"""
Builds the final prompt object to be sent to the sub-agent (LLM).
"""
import json
import json5
import sys
import os
from jinja2 import Environment, FileSystemLoader
from pipe.core.models.session import Session
from pipe.core.models.settings import Settings
from pipe.core.utils.file import read_text_file
from pipe.core.utils.datetime import get_current_timestamp

class PromptBuilder:
    """Constructs a structured prompt object for the LLM."""

    def __init__(self, settings: Settings, session_data: Session, project_root: str, api_mode: str, multi_step_reasoning_enabled: bool = False):
        self.settings = settings
        self.session_data = session_data
        self.project_root = project_root
        self.api_mode = api_mode
        self.multi_step_reasoning_enabled = multi_step_reasoning_enabled

        self.template_env = Environment(
            loader=FileSystemLoader(os.path.join(self.project_root, 'templates', 'prompt')),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.template_env.filters['tojson'] = json.dumps

    def _load_roles(self) -> list[str]:
        content = []
        for rel_path in self.session_data.roles:
            path = os.path.join(self.project_root, rel_path.strip())
            if os.path.isfile(path):
                content.append(read_text_file(path))
        return content

    def _build_hyperparameters_section(self) -> dict:
        import copy
        merged_params = self.settings.parameters.model_dump()

        if self.session_data.hyperparameters:
            session_params = self.session_data.hyperparameters.model_dump()
            for key, value_desc_pair in session_params.items():
                if key in merged_params and value_desc_pair and 'value' in value_desc_pair:
                    merged_params[key]['value'] = value_desc_pair['value']

        params = {"description": "Hyperparameter settings for the model."}
        for key, value_desc_pair in merged_params.items():
            params[key] = {
                "type": "number",
                "value": value_desc_pair.get('value'),
                "description": value_desc_pair.get('description')
            }
        return params

    def build(self) -> str:
        if self.api_mode == 'gemini-api':
            template = self.template_env.get_template('gemini_api_prompt.j2')
        elif self.api_mode == 'gemini-cli':
            template = self.template_env.get_template('gemini_cli_prompt.j2')
        else:
            raise ValueError(f"Unknown api_mode: {self.api_mode}")

        history_turns_iterable = self.session_data.turns.get_for_prompt()
        history_turns = list(reversed(list(history_turns_iterable))) # Reverse the reversed iterator to get chronological order
        
        # The last turn is the current task, which is not part of the history.
        # The collection filtering logic applies to history, so we handle the current task separately.
        current_task_turn = self.session_data.turns[-1] if self.session_data.turns else None
        
        current_instruction = ""
        if current_task_turn:
            if hasattr(current_task_turn, 'instruction') and current_task_turn.instruction:
                current_instruction = current_task_turn.instruction
            else:
                # Search backwards for the most recent instruction if the last turn doesn't have one
                for turn in reversed(self.session_data.turns):
                    if hasattr(turn, 'instruction') and turn.instruction:
                        current_instruction = turn.instruction
                        break
        
        roles_data = {
            "description": "The following are the roles for this session.",
            "definitions": self._load_roles()
        }

        file_references_content = list(self.session_data.references.get_for_prompt(self.project_root))

        context = {
            "current_datetime": get_current_timestamp(self.template_env.globals.get('local_tz')),
            "session": {
                "description": current_instruction,
                "session_goal": {
                    "description": "This section outlines the goal of the current session.",
                    "purpose": self.session_data.purpose,
                    "background": self.session_data.background
                },
                "roles": roles_data,
                "file_references": file_references_content,
                "conversation_history": {
                    "description": "Historical record of past interactions in this session, in chronological order.",
                    "turns": [turn.model_dump() for turn in history_turns]
                },
                "current_task": current_task_turn.model_dump() if current_task_turn else {},
                "constraints": {
                    "description": "Constraints for the model.",
                    "language": self.settings.language,
                    "processing_config": {
                        "description": "Configuration for processing.",
                        "multi_step_reasoning_active": self.multi_step_reasoning_enabled
                    },
                    "hyperparameters": self._build_hyperparameters_section()
                },
                "todos": [todo.model_dump() for todo in self.session_data.todos] if self.session_data.todos else [],
                "settings": self.settings.model_dump()
            }
        }
        
        rendered_string = template.render(context)
        try:
            parsed_json = json5.loads(rendered_string)
            return json.dumps(parsed_json, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error: Generated prompt is not valid JSON. {e}", file=sys.stderr)
            print(f"--- Invalid JSON String ---\n{rendered_string}\n--- End of Invalid JSON String ---", file=sys.stderr)
            raise