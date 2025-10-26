"""
Service responsible for constructing the prompt object from session data.
"""
import json
from typing import Dict, Any

from pipe.core.models.session import Session
from pipe.core.models.settings import Settings
from pipe.core.services.session_service import SessionService
from pipe.core.models.prompt import Prompt
from pipe.core.models.prompts.constraints import PromptConstraints, PromptHyperparameters, PromptHyperparameter, PromptProcessingConfig
from pipe.core.models.prompts.conversation_history import PromptConversationHistory
from pipe.core.models.prompts.current_task import PromptCurrentTask
from pipe.core.models.prompts.file_reference import PromptFileReference
from pipe.core.models.prompts.roles import PromptRoles
from pipe.core.models.prompts.session_goal import PromptSessionGoal
from pipe.core.models.prompts.todo import PromptTodo
from pipe.core.collections.roles import RoleCollection
from pipe.core.collections.references import ReferenceCollection
from pipe.core.collections.todos import TodoCollection
from pipe.core.collections.turns import TurnCollection
from pipe.core.collections.prompts.reference_collection import PromptReferenceCollection
from pipe.core.collections.prompts.turn_collection import PromptTurnCollection
from pipe.core.utils.datetime import get_current_timestamp
import zoneinfo

class PromptService:
    """Constructs a structured Prompt object for the LLM."""

    def __init__(self, project_root: str):
        self.project_root = project_root

    def build_prompt(self, session_service: SessionService) -> Prompt:
        """
        Builds and returns a validated Prompt object based on the current session and settings.
        """
        session_data = session_service.current_session
        settings = session_service.settings
        multi_step_reasoning_enabled = session_data.multi_step_reasoning_enabled
        current_instruction = session_service.current_instruction

        # 1. Build Hyperparameters
        merged_params = settings.parameters.model_dump()
        if session_data.hyperparameters:
            session_params = session_data.hyperparameters.model_dump()
            for key, value_desc_pair in session_params.items():
                if key in merged_params and value_desc_pair and 'value' in value_desc_pair:
                    merged_params[key]['value'] = value_desc_pair['value']
        
        hyperparameters = PromptHyperparameters(
            description="Hyperparameter settings for the model.",
            temperature=PromptHyperparameter(type="number", **merged_params['temperature']),
            top_p=PromptHyperparameter(type="number", **merged_params['top_p']),
            top_k=PromptHyperparameter(type="number", **merged_params['top_k'])
        )

        # 2. Build Constraints
        constraints = PromptConstraints(
            description="Constraints for the model.",
            language=settings.language,
            processing_config=PromptProcessingConfig(
                description="Configuration for processing.",
                multi_step_reasoning_active=multi_step_reasoning_enabled
            ),
            hyperparameters=hyperparameters
        )

        # 3. Build other prompt components using Collections
        roles = PromptRoles(
            description="The following are the roles for this session.",
            definitions=RoleCollection(session_data.roles).get_for_prompt(self.project_root)
        )

        # The `get_for_prompt` from the original ReferenceCollection reads files
        references_with_content = list(ReferenceCollection(session_data.references).get_for_prompt(self.project_root))
        prompt_references = [PromptFileReference(**ref) for ref in references_with_content]
        
        # The `get_for_prompt` from the original TodoCollection formats the data
        todos_for_prompt = TodoCollection(session_data.todos).get_for_prompt()
        prompt_todos = [PromptTodo(**todo) for todo in todos_for_prompt]

        history_turns = list(reversed(list(session_data.turns.get_for_prompt())))
        
        conversation_history = PromptConversationHistory(
            description="Historical record of past interactions in this session, in chronological order.",
            turns=PromptTurnCollection(history_turns).get_turns()
        )

        current_task_turn_data = session_data.turns[-1].model_dump()
        current_task = PromptCurrentTask(**current_task_turn_data)
        
        # 4. Assemble the final Prompt object
        prompt_data = {
            "current_datetime": get_current_timestamp(zoneinfo.ZoneInfo(settings.timezone)),
            "description": current_instruction,
            "session_goal": PromptSessionGoal(
                description="This section outlines the goal of the current session.",
                purpose=session_data.purpose,
                background=session_data.background
            ),
            "roles": roles,
            "constraints": constraints,
            "main_instruction": "Your main instruction is to be helpful and follow all previous instructions.",
            "conversation_history": conversation_history,
            "current_task": current_task,
            "todos": prompt_todos if prompt_todos else None,
            "file_references": prompt_references if prompt_references else None,
            "reasoning_process": {"description": "Think step-by-step to achieve the goal."} if multi_step_reasoning_enabled else None
        }

        return Prompt(**prompt_data)
