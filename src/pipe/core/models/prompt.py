from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from .prompts.file_reference import PromptFileReference
from .prompts.session_goal import PromptSessionGoal
from .prompts.roles import PromptRoles
from .prompts.conversation_history import PromptConversationHistory
from .prompts.current_task import PromptCurrentTask
from .prompts.constraints import PromptConstraints
from .prompts.todo import PromptTodo

# Top-level model corresponding to gemini_api_prompt.j2
class Prompt(BaseModel):
    # Core instructions and immediate task
    description: str
    main_instruction: str
    reasoning_process: Optional[Dict[str, Any]] = None
    current_task: PromptCurrentTask
    todos: Optional[List[PromptTodo]] = None
    
    # Contextual information
    current_datetime: str
    session_goal: PromptSessionGoal
    roles: PromptRoles
    constraints: PromptConstraints
    conversation_history: PromptConversationHistory
    file_references: Optional[List[PromptFileReference]] = None
