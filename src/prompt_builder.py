"""
Builds the final prompt object to be sent to the sub-agent (LLM).
"""
from pathlib import Path
import json

class PromptBuilder:
    """Constructs a structured prompt object for the LLM."""

    def __init__(self, settings: dict, session_data: dict, project_root: Path, multi_step_reasoning_enabled: bool = False):
        self.settings = settings
        self.session_data = session_data
        self.project_root = project_root
        self.multi_step_reasoning_enabled = multi_step_reasoning_enabled

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

        # Load tools.json
        tools_path = self.project_root / 'tools.json'
        tools_json = []
        if tools_path.exists():
            with tools_path.open('r', encoding='utf-8') as f:
                tools_json = json.load(f)

        # Load multi-step reasoning content if enabled
        advanced_reasoning_flow_content = None
        if self.multi_step_reasoning_enabled:
            multi_step_path = self.project_root / 'rules' / 'multi-step-reasoning.md'
            if multi_step_path.is_file():
                advanced_reasoning_flow_content = multi_step_path.read_text(encoding="utf-8")

        prompt_object = {
            "description": "Comprehensive JSON request for an AI sub-agent, clearly separating immutable constraints from dynamic context, with a flexible thinking pipeline.",
            
            # =======================================================
            # 1. IMMUTABLE CONSTRAINTS
            # =======================================================
            "session_goal": {
                "description": "The immutable purpose and background for this entire conversation session.",
                "purpose": self.session_data.get('purpose'),
                "background": self.session_data.get('background'),
            },
            "roles": {
                "description": "A list of personas or role definitions that the AI sub-agent should conform to.",
                "definitions": roles_content
            },
            "constraints": {
                "description": "Constraints the agent must adhere to when generating responses. Tool output should be summarized when returned.",
                "language": self.settings.get('language', 'English'),
                "hyperparameters": {
                    "description": "Contextual instructions to control the AI model's generation process. The model should strive to follow these instructions.",
                    **hyperparams_from_settings
                },
                "processing_config": {
                    "description": "Configuration for the agent's internal processing and reasoning.",
                    "multi_step_reasoning_active": self.multi_step_reasoning_enabled
                }
            },
            
            # =======================================================
            # 2. PROCESSING & REASONING
            # =======================================================
            "main_instruction": {
                "description": "The mandatory, high-level processing sequence for every input. If 'processing_config.multi_step_reasoning_active' is true, Step 4 must invoke the 'advanced_reasoning_flow'.",
                "flowchart": "```mermaid\ngraph TD\n    A[Start] --> B[Step 1: Identify Task from 'current_task'];\n    B --> C[Step 2: Gather Context (History & Constraints)];\n    C --> D[Step 3: Summarize Context & Plan];\n    D --> E[Step 4: Execute Thinking Process (Conditionally Advanced)];\n    E --> F[Step 5: Generate Final Response];\n    F --> G[End];\n```"
            },
            **(
                {"advanced_reasoning_flow": {
                    "description": "The detailed, multi-step internal thinking process for high-quality, verified responses. This is executed when 'processing_config.multi_step_reasoning_active' is true.",
                    "flowchart": '''```mermaid
graph TD
    A(["Start: JSON Input"]) --> B["Step 1: Read 'current_task.instruction' to identify task objective"];
    B --> C["Step 2: Derive general principles behind the task (Step-Back)"];
    C --> D["Step 3: Extract relevant information from the latest turns in 'conversation_history.turns'"];
    D --> E["Step 4: Integrate extracted task instructions, principles, and historical information, then summarize the current context"];
    E --> F["Step 5: Based on the summarized information, think and plan for response generation"];
    F --> G{"Decision: Are there any contradictions or leaps in logic?"};
    G -- NO --> E;
    G -- YES --> H["Step 6: Re-examine the reasoning path from multiple perspectives and confirm the robustness of the conclusion (Self-Consistency)"];
    H --> I["Step 7: Generate the final response based on the plan"];
    I --> J{"Decision: Does it meet the initial requirements (format/purpose)?"};
    J -- NO --> F;
    J -- YES --> K(["End: Output Response"]);
```'''
                }} if advanced_reasoning_flow_content else {}
            ),
            
            # =======================================================
            # 3. DYNAMIC CONTEXT
            # =======================================================
            "conversation_history": {
                "description": "Historical record of past interactions in this session, in chronological order.",
                "turns": history_turns
            },
            "current_task": {
                "description": "The specific task that the AI sub-agent must currently execute.",
                "instruction": current_task_turn.get('instruction')
            },
            "available_tools_schema": {
                "description": "JSON Schema definitions for the tools available to the AI sub-agent.",
                "definitions": tools_json
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

        # Add hyperparameters to the initial context
        hyperparameters_section = self.build().get("constraints", {}).get("hyperparameters", {})
        if hyperparameters_section:
            initial_context.append("\n### Hyperparameters ###")
            for key, value_desc_pair in hyperparameters_section.items():
                if key == "description": # Skip the description of the hyperparameters section
                    continue
                initial_context.append(f"- {key}: {value_desc_pair.get('value')} ({value_desc_pair.get('description')})")

        roles_content = self._load_roles()
        if roles_content:
            initial_context.append("\n### Roles ###")
            initial_context.extend(roles_content)



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