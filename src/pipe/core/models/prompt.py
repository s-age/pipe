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
    pass


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
    buffered_history: PromptConversationHistory | None = None
    file_references: list[PromptFileReference] | None = None
    artifacts: list[Artifact] | None = None  # Changed type to list[Artifact]
    procedure: str | None = None
    procedure_content: str | None = None
    raw_response: str | None = None
