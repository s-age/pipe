"""
Factory for creating Prompt objects from Session data.

Encapsulates the logic for building a Prompt from a Session,
keeping the Prompt model itself as a pure data structure.
"""

import os
import sys
import zoneinfo

from pipe.core.models.artifact import Artifact
from pipe.core.models.prompt import Prompt
from pipe.core.models.session import Session
from pipe.core.models.settings import Settings
from pipe.core.models.turn import UserTaskTurn
from pipe.core.repositories.resource_repository import ResourceRepository


class PromptFactory:
    """
    Builds Prompt objects from Session data.

    This factory encapsulates all the complex logic for creating a Prompt,
    including gathering references, resolving procedures, and merging
    hyperparameters. This keeps the Prompt model clean and focused on
    representing prompt data.
    """

    def __init__(self, project_root: str, resource_repository: ResourceRepository):
        """
        Initialize the PromptFactory.

        Args:
            project_root: The project root directory
            resource_repository: Repository for reading external resources
        """
        self.project_root = project_root
        self.resource_repository = resource_repository

    def create(
        self,
        session: Session,
        settings: Settings,
        artifacts: list[Artifact] | None = None,
        current_instruction: str | None = None,
    ) -> Prompt:
        """
        Create a Prompt object from a Session.

        Args:
            session: The Session to build a prompt from
            settings: Application settings
            artifacts: Optional list of artifacts to include
            current_instruction: Optional current instruction text

        Returns:
            A fully constructed Prompt object
        """
        from pipe.core.domains.references import get_references_for_prompt
        from pipe.core.domains.todos import get_todos_for_prompt
        from pipe.core.models.hyperparameters import Hyperparameters
        from pipe.core.models.prompts.constraints import PromptConstraints
        from pipe.core.models.prompts.conversation_history import (
            PromptConversationHistory,
        )
        from pipe.core.models.prompts.current_task import PromptCurrentTask
        from pipe.core.models.prompts.file_reference import PromptFileReference
        from pipe.core.models.prompts.roles import PromptRoles
        from pipe.core.models.prompts.session_goal import PromptSessionGoal
        from pipe.core.models.prompts.todo import PromptTodo
        from pipe.core.utils.datetime import get_current_timestamp

        # 1. Merge hyperparameters from settings defaults and session overrides
        merged_hyperparameters: Hyperparameters | None = None
        if session.hyperparameters:
            # Session has custom hyperparameters, use them
            merged_hyperparameters = session.hyperparameters
        else:
            # Use default values from settings
            merged_hyperparameters = Hyperparameters(
                temperature=settings.parameters.temperature.value,
                top_p=settings.parameters.top_p.value,
                top_k=settings.parameters.top_k.value,
            )

        # 2. Build Constraints
        constraints = PromptConstraints.build(
            settings, merged_hyperparameters, session.multi_step_reasoning_enabled
        )

        # 3. Build Roles
        roles = PromptRoles.build(session.roles, self.project_root)

        # 4. Build File References
        references_with_content = list(
            get_references_for_prompt(session.references, self.project_root)
        )
        prompt_references = [
            PromptFileReference(**ref) for ref in references_with_content
        ]

        # 5. Build Todos
        prompt_todos = [
            PromptTodo(**todo) for todo in get_todos_for_prompt(session.todos)
        ]

        # 6. Determine current task instruction and conversation history
        history_turns_for_prompt = session.turns

        current_task_instruction_content = ""
        if current_instruction is not None and current_instruction.strip() != "":
            # If current_instruction is provided, it's the current task.
            # Check if the last turn is a UserTaskTurn with matching instruction
            if session.turns and isinstance(session.turns[-1], UserTaskTurn):
                if session.turns[-1].instruction == current_instruction:
                    # Last turn matches current_instruction, exclude it from history
                    history_turns_for_prompt = session.turns[:-1]
            current_task_instruction_content = current_instruction
        elif session.turns:
            # If no current_instruction, but session has turns,
            # the last turn might be the current task if it's a UserTaskTurn.
            last_turn = session.turns[-1]
            if isinstance(last_turn, UserTaskTurn):
                current_task_instruction_content = last_turn.instruction
                history_turns_for_prompt = session.turns[:-1]  # Exclude from history

        # 7. Build conversation history (both full and split for caching)
        conversation_history = PromptConversationHistory.build(
            history_turns_for_prompt, settings.tool_response_expiration
        )

        # 7.1. Split history for Gemini caching strategy
        from pipe.core.domains.gemini_cache import GeminiCache

        gemini_cache = GeminiCache(
            tool_response_limit=settings.tool_response_expiration
        )
        cached_history, buffered_history = gemini_cache.split_history(
            history_turns_for_prompt,
            cached_content_token_count=session.cached_content_token_count,
            prompt_token_count=session.token_count,
        )

        # 8. Build current task
        current_task_turn = UserTaskTurn(
            type="user_task",
            instruction=current_task_instruction_content or "",
            timestamp=get_current_timestamp(zoneinfo.ZoneInfo(settings.timezone)),
        )
        current_task = PromptCurrentTask(**current_task_turn.model_dump())

        # 9. Resolve procedure content
        procedure_content = self._resolve_procedure_content(
            session.procedure, settings.timezone
        )

        # 10. Assemble the final Prompt object
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
            "cached_history": cached_history,
            "buffered_history": buffered_history,
            "current_task": current_task,
            "todos": prompt_todos if prompt_todos else None,
            "file_references": prompt_references if prompt_references else None,
            "artifacts": artifacts if artifacts else None,
            "procedure": session.procedure if session.procedure else None,
            "procedure_content": procedure_content,
            "reasoning_process": (
                {"description": "Think step-by-step to achieve the goal."}
                if session.multi_step_reasoning_enabled
                else None
            ),
        }

        return Prompt(**prompt_data)

    def _resolve_procedure_content(
        self, procedure_path: str | None, timezone: str
    ) -> str | None:
        """
        Resolve the content of a procedure file.

        Args:
            procedure_path: Path to the procedure file
            timezone: Timezone for error messages

        Returns:
            The procedure file content, or an error message if not found
        """
        if not procedure_path:
            return None

        try:
            full_path = os.path.join(self.project_root, procedure_path)
            return self.resource_repository.read_text(full_path, self.project_root)
        except (FileNotFoundError, ValueError):
            print(
                f"Warning: Procedure file not found: {procedure_path}",
                file=sys.stderr,
            )
            return f"Error: Procedure file not found at {procedure_path}"
