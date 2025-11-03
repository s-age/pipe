import os
import sys
import zoneinfo
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from ..models.artifact import Artifact  # Import Artifact model
from .prompts.constraints import PromptConstraints
from .prompts.conversation_history import PromptConversationHistory
from .prompts.current_task import PromptCurrentTask
from .prompts.file_reference import PromptFileReference
from .prompts.roles import PromptRoles
from .prompts.session_goal import PromptSessionGoal
from .prompts.todo import PromptTodo

if TYPE_CHECKING:
    from pipe.core.models.session import Session
    from pipe.core.models.settings import Settings


# Top-level model corresponding to gemini_api_prompt.j2
class Prompt(BaseModel):
    # Core instructions and immediate task
    description: str
    main_instruction: str
    reasoning_process: dict[str, Any] | None = None
    current_task: PromptCurrentTask
    todos: list[PromptTodo] | None = None

    # Contextual information
    current_datetime: str
    session_goal: PromptSessionGoal
    roles: PromptRoles
    constraints: PromptConstraints
    conversation_history: PromptConversationHistory
    file_references: list[PromptFileReference] | None = None
    artifacts: list[Artifact] | None = None  # Changed type to list[Artifact]
    procedure: str | None = None
    procedure_content: str | None = None

    @classmethod
    def from_session(
        cls,
        session: "Session",
        settings: "Settings",
        project_root: str,
        artifacts: list[Artifact] | None = None,
    ) -> "Prompt":
        """Builds and returns a Prompt object from a session's data."""
        from pipe.core.domains.references import get_references_for_prompt
        from pipe.core.domains.todos import get_todos_for_prompt
        from pipe.core.models.prompts.constraints import PromptHyperparameters
        from pipe.core.utils.datetime import get_current_timestamp
        from pipe.core.utils.file import read_text_file

        # 1. Build Hyperparameters
        merged_params = settings.parameters.model_dump()
        if session.hyperparameters:
            if session.hyperparameters.temperature is not None:
                merged_params["temperature"]["value"] = (
                    session.hyperparameters.temperature
                )
            if session.hyperparameters.top_p is not None:
                merged_params["top_p"]["value"] = session.hyperparameters.top_p
            if session.hyperparameters.top_k is not None:
                merged_params["top_k"]["value"] = session.hyperparameters.top_k

        hyperparameters = PromptHyperparameters.from_merged_params(merged_params)

        # 2. Build Constraints
        constraints = PromptConstraints.build(
            settings, hyperparameters, session.multi_step_reasoning_enabled
        )

        # 3. Build other prompt components
        roles = PromptRoles.build(session.roles, project_root)

        references_with_content = list(
            get_references_for_prompt(session.references, project_root)
        )
        prompt_references = [
            PromptFileReference(**ref) for ref in references_with_content
        ]

        prompt_todos = [
            PromptTodo(**todo) for todo in get_todos_for_prompt(session.todos)
        ]

        conversation_history = PromptConversationHistory.build(
            session.turns, settings.tool_response_expiration
        )

        current_task_turn_data = session.turns[-1].model_dump()
        current_task = PromptCurrentTask(**current_task_turn_data)

        procedure_content = None
        if session.procedure:
            try:
                procedure_content = read_text_file(
                    os.path.join(project_root, session.procedure)
                )
            except FileNotFoundError:
                print(
                    f"Warning: Procedure file not found: {session.procedure}",
                    file=sys.stderr,
                )
                procedure_content = (
                    f"Error: Procedure file not found at {session.procedure}"
                )

        # 4. Assemble the final Prompt object
        prompt_data = {
            "current_datetime": get_current_timestamp(
                zoneinfo.ZoneInfo(settings.timezone)
            ),
            "description": (
                "This structured prompt guides your response. First, understand the "
                "core instructions: `main_instruction` defines your thinking "
                "process. Next, identify the immediate objective from `current_task` "
                "and `todos`. Then, gather all context required to execute the task "
                "by processing `session_goal`, `roles`, `constraints`, "
                "`conversation_history`, and `file_references` in that order. "
                "Finally, execute the `current_task` by synthesizing all gathered "
                "information."
            ),
            "session_goal": PromptSessionGoal.build(
                purpose=session.purpose, background=session.background
            ),
            "roles": roles,
            "constraints": constraints,
            "main_instruction": (
                "Your main instruction is to be helpful and follow all previous "
                "instructions."
            ),
            "conversation_history": conversation_history,
            "current_task": current_task,
            "todos": prompt_todos if prompt_todos else None,
            "file_references": prompt_references if prompt_references else None,
            "artifacts": artifacts if artifacts else None,
            "procedure": session.procedure if session.procedure else None,
            "procedure_content": procedure_content if procedure_content else None,
            "reasoning_process": {
                "description": "Think step-by-step to achieve the goal."
            }
            if session.multi_step_reasoning_enabled
            else None,
        }

        return cls(**prompt_data)
