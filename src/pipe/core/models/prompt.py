from typing import TYPE_CHECKING, NotRequired, TypedDict

from pipe.core.models.base import CamelCaseModel

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


class ReasoningProcess(TypedDict):
    """Structure for multi-step reasoning process configuration."""

    description: str
    flowchart: NotRequired[str]


# Top-level model corresponding to gemini_api_prompt.j2
class Prompt(CamelCaseModel):
    # Core instructions and immediate task
    description: str
    main_instruction: str
    reasoning_process: ReasoningProcess | None = None
    current_task: PromptCurrentTask
    todos: list[PromptTodo] | None = None

    # Contextual information
    current_datetime: str
    session_goal: PromptSessionGoal
    roles: PromptRoles
    constraints: PromptConstraints
    conversation_history: PromptConversationHistory
    cached_history: PromptConversationHistory | None = None
    buffered_history: PromptConversationHistory | None = None
    file_references: list[PromptFileReference] | None = None
    artifacts: list[Artifact] | None = None  # Changed type to list[Artifact]
    procedure: str | None = None
    procedure_content: str | None = None
    raw_response: str | None = None

    @classmethod
    def from_session(
        cls,
        session: "Session",
        settings: "Settings",
        project_root: str,
        artifacts: list[Artifact] | None = None,
        current_instruction: str | None = None,
    ) -> "Prompt":
        """
        Builds and returns a Prompt object from a session's data.

        Delegates to PromptFactory for the actual prompt construction.
        This method is maintained for backward compatibility.
        """
        from pipe.core.factories.prompt_factory import PromptFactory
        from pipe.core.repositories.resource_repository import ResourceRepository

        resource_repo = ResourceRepository(project_root)
        factory = PromptFactory(project_root, resource_repo)

        return factory.create(
            session=session,
            settings=settings,
            artifacts=artifacts,
            current_instruction=current_instruction,
        )
