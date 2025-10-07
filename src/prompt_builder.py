"""
Builds the final prompt object to be sent to the sub-agent (LLM).
"""
from pathlib import Path

class PromptBuilder:
    """Constructs a structured prompt object for the LLM."""

    def __init__(self, settings: dict, session_data: dict, project_root: Path):
        self.settings = settings
        self.session_data = session_data
        self.project_root = project_root

    def _load_roles(self) -> list[str]:
        """Loads content from role definition files."""
        content = []
        for rel_path in self.session_data.get('roles', []):
            path = self.project_root / rel_path.strip()
            if path.is_file():
                content.append(path.read_text(encoding="utf-8"))
        return content

    def build(self) -> dict:
        """Builds the complete prompt object from all session components."""
        
        all_turns = self.session_data.get('turns', [])
        history_turns = all_turns[:-1]
        current_task_turn = all_turns[-1] if all_turns else {}

        roles_content = self._load_roles()
        hyperparams_from_settings = self._build_hyperparameters_section()

        prompt_object = {
            "description": "JSON object representing the entire request to the AI sub-agent. The agent's goal is to accomplish the 'current_task' based on all provided context.",
            "main_instruction": "When you receive JSON data, process your thoughts according to the following flowchart:\n\n```mermaid\ngraph TD\n    A[\"Start: JSON Input\"] --> B[\"Step 1: Read 'current_task.instruction' to identify task objective\"];\n    B --> C[\"Step 2: Extract relevant information from the latest turns in 'conversation_history.turns'\"];\n    C --> D[\"Step 3: Integrate extracted task instructions and historical information, then summarize the current context\"];\n    D --> E[\"Step 4: Based on the summarized information, think and plan for response generation\"];\n    E --> F[\"Step 5: Generate final response based on the plan\"];\n    F --> G[\"End: Output Response\"];\n```",
            "hyperparameters": {
                "description": "Contextual instructions to control the AI model's generation process. The model should strive to follow these instructions.",
                **hyperparams_from_settings
            },
            "session_goal": {
                "description": "The immutable purpose and background for this entire conversation session.",
                "purpose": self.session_data.get('purpose'),
                "background": self.session_data.get('background'),
            },
            "response_constraints": {
                "description": "Constraints that the AI sub-agent should adhere to when generating responses. The entire response, including all content, must be generated in the specified language.",
                "language": self.settings.get('language', 'English') # Ensure language is explicitly a constraint
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
            }
        }

        return prompt_object

    def build_contents_for_api(self) -> list[dict]:
        """Builds a simple content list for the google-generativeai API."""
        contents = []
        
        # 1. Combine all meta-information into a single system-like prompt.
        # Since Gemini doesn't have a dedicated system role, we prepend this
        # to the first user message.
        initial_context = []
        initial_context.append("## SYSTEM CONTEXT & ROLES ##")
        initial_context.append(f"Purpose: {self.session_data.get('purpose', 'Not set')}")
        initial_context.append(f"Background: {self.session_data.get('background', 'Not set')}")

        roles_content = self._load_roles()
        if roles_content:
            initial_context.append("\n### Roles ###")
            initial_context.extend(roles_content)

        # Add multi-step reasoning if enabled
        if self.session_data.get('multi_step_reasoning_enabled', False):
            multi_step_path = self.project_root / 'rules' / 'multi-step-reasoning.md'
            if multi_step_path.is_file():
                initial_context.append("\n### Reasoning Process ###")
                initial_context.append(multi_step_path.read_text(encoding="utf-8"))

        # The combined context is the first user message.
        contents.append({'role': 'user', 'parts': [{'text': "\n".join(initial_context)}]})
        # Acknowledge the context as the model.
        contents.append({'role': 'model', 'parts': [{'text': "Understood. I will follow all instructions and context provided."}]})

        # 2. Add the actual conversation turns
        all_turns = self.session_data.get('turns', [])
        for turn in all_turns:
            role = ''
            text = ''
            if turn.get('type') == 'user_task':
                role = 'user'
                text = turn.get('instruction', '')
            elif turn.get('type') == 'model_response':
                role = 'model'
                text = turn.get('content', '')
            
            if role and text:
                contents.append({'role': role, 'parts': [{'text': text}]})

        return contents

    def _build_hyperparameters_section(self) -> dict:
        """Builds the hyperparameters section from settings."""
        params = {}
        for key, value_desc_pair in self.settings.get('parameters', {}).items():
            params[key] = {
                "type": "number", # Assuming number for now
                "value": value_desc_pair.get('value'),
                "description": value_desc_pair.get('description')
            }
        return params