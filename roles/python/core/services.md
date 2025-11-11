# Services Layer

## Purpose

Services are the **application orchestration layer**. They coordinate between multiple components (repositories, domains, agents, collections) to implement high-level business workflows. Services manage application-wide state and enforce business rules.

## Responsibilities

1. **Workflow Orchestration** - Coordinate complex operations across multiple layers
2. **State Management** - Manage session lifecycle and application state
3. **Transaction Coordination** - Ensure operations are atomic and consistent
4. **Business Rule Enforcement** - Apply high-level business logic
5. **Component Integration** - Bridge between repositories, domains, and agents

## Characteristics

- ✅ Orchestrate multi-step workflows
- ✅ Manage application state (current session, settings)
- ✅ Coordinate between repositories, domains, agents
- ✅ Handle transactions and data consistency
- ✅ Provide high-level public API for delegates
- ❌ **NO direct file I/O** - use repositories
- ❌ **NO low-level business logic** - use domains
- ❌ **NO direct API calls** - use agents

## File Structure

```
services/
├── __init__.py
├── session_service.py    # Session lifecycle management
├── prompt_service.py     # Prompt construction and formatting
└── token_service.py      # Token counting and optimization
```

## Dependencies

**Allowed:**

- ✅ `repositories/` - For persistence operations
- ✅ `domains/` - For business logic
- ✅ `agents/` - For AI interactions (limited, prefer via delegates)
- ✅ `collections/` - For data structure manipulation
- ✅ `models/` - For type definitions
- ✅ `utils/` - For utilities

**Forbidden:**

- ❌ `delegates/` - Services are called BY delegates, not vice versa
- ❌ Direct file operations (use repositories)
- ❌ Direct API calls (use agents)

## Template

```python
"""
Service for managing [domain area].
"""

import logging
from typing import TYPE_CHECKING

from pipe.core.models.settings import Settings

if TYPE_CHECKING:
    from pipe.core.repositories.some_repository import SomeRepository

logger = logging.getLogger(__name__)


class SomeService:
    """
    Manages [domain area] operations.

    Responsibilities:
    - [High-level operation 1]
    - [High-level operation 2]
    - [High-level operation 3]
    """

    def __init__(
        self,
        project_root: str,
        settings: Settings,
        repository: "SomeRepository",
    ):
        """
        Initialize service with dependencies.

        Args:
            project_root: Path to project root directory
            settings: Application settings
            repository: Repository for persistence
        """
        self.project_root = project_root
        self.settings = settings
        self.repository = repository

        # Service-level state
        self.current_state: SomeModel | None = None

    def execute_workflow(self, param: str) -> ResultModel:
        """
        Executes a high-level workflow.

        Args:
            param: Input parameter

        Returns:
            Result of the workflow

        Raises:
            ValueError: If param is invalid
            RuntimeError: If workflow fails
        """
        logger.debug(f"Starting workflow with param: {param}")

        # 1. Validate input (might use validators/)
        if not param:
            raise ValueError("Parameter cannot be empty")

        # 2. Load data (via repository)
        data = self.repository.find(param)
        if not data:
            raise ValueError(f"Data not found: {param}")

        # 3. Apply business logic (via domains/)
        processed_data = process_data(data)

        # 4. Save result (via repository)
        self.repository.save(processed_data)

        logger.debug("Workflow completed successfully")
        return processed_data
```

## Real Examples

### SessionService - Session Lifecycle Management

**Key Responsibilities:**

- Load and save sessions
- Create new sessions with proper initialization
- Fork sessions at specific turn indices
- Manage session hierarchy (parent-child relationships)
- Coordinate session mutations via domains

```python
class SessionService:
    """
    Manages the overall session lifecycle, excluding conversation_history.
    """

    def __init__(
        self,
        project_root: str,
        settings: Settings,
        repository: SessionRepository,
    ):
        self.project_root = project_root
        self.settings = settings
        self.repository = repository

        # Application state
        self.current_session: Session | None = None
        self.current_session_id: str | None = None
        self.current_instruction: str | None = None

        # Timezone for timestamps
        self.timezone_obj = self._init_timezone(settings.timezone)

    def start_session(
        self,
        purpose: str,
        background: str,
        roles: list[str] | None = None,
        parent_id: str | None = None,
    ) -> str:
        """
        Creates and initializes a new session.

        This orchestrates:
        1. Session ID generation (via hashing)
        2. Session model creation
        3. Initial references setup
        4. Persistence via repository

        Returns:
            The new session ID
        """
        logger.info("Starting new session")

        # 1. Generate session ID
        session_id = self._generate_session_id(purpose, background)

        # 2. Create session model
        session = Session(
            id=session_id,
            purpose=purpose,
            background=background,
            roles=roles or [],
            parent_id=parent_id,
            created_at=get_current_timestamp(self.timezone_obj),
            turns=[],
            references=ReferenceCollection(),
            todos=[],
        )

        # 3. Save to repository
        self.repository.save(session)

        # 4. Update application state
        self.current_session = session
        self.current_session_id = session_id

        logger.info(f"Session created: {session_id}")
        return session_id

    def load_session(self, session_id: str) -> Session:
        """
        Loads session from repository and sets as current.

        Raises:
            ValueError: If session not found
        """
        logger.debug(f"Loading session: {session_id}")

        session = self.repository.find(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        self.current_session = session
        self.current_session_id = session_id

        return session

    def fork_session(
        self,
        source_session_id: str,
        at_turn_index: int,
    ) -> str:
        """
        Forks a session at a specific turn, creating a new branch.

        This orchestrates:
        1. Load source session
        2. Extract turns up to fork point
        3. Create new session with forked history
        4. Update parent-child relationships

        Returns:
            The new forked session ID
        """
        logger.info(f"Forking session {source_session_id} at turn {at_turn_index}")

        # 1. Load source
        source = self.repository.find(source_session_id)
        if not source:
            raise ValueError(f"Source session not found: {source_session_id}")

        # 2. Validate turn index
        if at_turn_index < 0 or at_turn_index >= len(source.turns):
            raise ValueError(f"Invalid turn index: {at_turn_index}")

        # 3. Create forked session
        forked_turns = source.turns[:at_turn_index + 1]
        forked_id = self._generate_fork_id(source_session_id, at_turn_index)

        forked_session = Session(
            id=forked_id,
            purpose=source.purpose,
            background=source.background,
            roles=source.roles,
            parent_id=source_session_id,
            created_at=get_current_timestamp(self.timezone_obj),
            turns=forked_turns,
            references=source.references.copy(),
            todos=source.todos.copy(),
        )

        # 4. Save forked session
        self.repository.save(forked_session)

        logger.info(f"Session forked: {forked_id}")
        return forked_id

    def add_turn_to_current_session(self, turn: Turn) -> None:
        """
        Adds a turn to the current session and persists.

        This is a workflow coordinator that:
        1. Validates current session exists
        2. Applies domain logic (TTL decay, etc.)
        3. Mutates session
        4. Persists changes
        """
        if not self.current_session:
            raise RuntimeError("No current session")

        # Apply domain logic before adding turn
        decay_references_before_turn(self.current_session)

        # Add turn
        self.current_session.turns.append(turn)

        # Save changes
        self.repository.save(self.current_session)
```

### PromptService - Prompt Construction

**Key Responsibilities:**

- Construct structured prompts for AI agents
- Format conversation history
- Apply filtering rules (via domains/)
- Render Jinja2 templates
- Calculate token budgets

```python
from jinja2 import Environment, FileSystemLoader
from pipe.core.domains.turns import get_turns_for_prompt
from pipe.core.domains.references import get_active_references

class PromptService:
    """
    Constructs and formats prompts for AI agents.

    This service is the **grand architect** of the final prompt,
    coordinating filtering, formatting, and template rendering.
    """

    def __init__(
        self,
        project_root: str,
        settings: Settings,
        session_service: SessionService,
    ):
        self.project_root = project_root
        self.settings = settings
        self.session_service = session_service

        # Initialize Jinja2 environment
        templates_dir = os.path.join(project_root, "templates")
        self.jinja_env = Environment(
            loader=FileSystemLoader(templates_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def build_prompt_for_gemini(self, session_id: str) -> Prompt:
        """
        Builds a complete, structured prompt for Gemini API.

        This orchestrates:
        1. Session loading
        2. Turn filtering (via domains/)
        3. Reference filtering (via domains/)
        4. Template rendering
        5. System instruction formatting

        Returns:
            Structured Prompt object with all components
        """
        logger.debug(f"Building prompt for session: {session_id}")

        # 1. Load session
        session = self.session_service.load_session(session_id)

        # 2. Get filtered turns (via domain logic)
        filtered_turns = list(get_turns_for_prompt(
            session.turns,
            tool_response_limit=3
        ))

        # 3. Get active references (via domain logic)
        active_refs = get_active_references(session.references)

        # 4. Build system instruction
        system_instruction = self._render_system_instruction(
            session=session,
            references=active_refs,
        )

        # 5. Format conversation history
        conversation_history = self._format_turns(filtered_turns)

        # 6. Get current task
        current_task = session.turns[-1] if session.turns else None

        return Prompt(
            system_instruction=system_instruction,
            conversation_history=conversation_history,
            current_task=current_task.message if current_task else "",
            hyperparameters=session.hyperparameters,
            references=active_refs,
            todos=session.todos,
        )

    def _render_system_instruction(
        self,
        session: Session,
        references: list[Reference],
    ) -> str:
        """
        Renders system instruction from template.

        Uses Jinja2 to compose:
        - Session purpose and background
        - Role definitions
        - Active references
        - Current todos
        """
        template = self.jinja_env.get_template("system_instruction.j2")

        # Load role content
        role_contents = []
        for role_path in session.roles:
            with open(os.path.join(self.project_root, role_path)) as f:
                role_contents.append(f.read())

        return template.render(
            purpose=session.purpose,
            background=session.background,
            roles=role_contents,
            references=references,
            todos=session.todos,
        )

    def _format_turns(self, turns: list[Turn]) -> list[dict[str, Any]]:
        """
        Formats turns into API-compatible format.
        """
        formatted = []
        for turn in turns:
            if isinstance(turn, UserTaskTurn):
                formatted.append({
                    "role": "user",
                    "parts": [{"text": turn.message}],
                })
            elif isinstance(turn, ModelResponseTurn):
                formatted.append({
                    "role": "model",
                    "parts": [{"text": turn.message}],
                })
            # ... other turn types
        return formatted
```

### TokenService - Token Management

**Key Responsibilities:**

- Count tokens in text
- Optimize content for token budget
- Provide token usage statistics
- Suggest content truncation

```python
class TokenService:
    """
    Manages token counting and optimization.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.max_tokens = settings.max_context_tokens

    def count_tokens(self, text: str) -> int:
        """
        Counts tokens in text using appropriate tokenizer.

        For now, uses simple approximation.
        TODO: Use actual model tokenizer.
        """
        # Simple approximation: ~4 chars per token
        return len(text) // 4

    def is_within_budget(self, text: str) -> bool:
        """
        Checks if text fits within token budget.
        """
        return self.count_tokens(text) <= self.max_tokens

    def optimize_content(
        self,
        content: str,
        max_tokens: int | None = None,
    ) -> str:
        """
        Truncates content to fit within token budget.
        """
        target_tokens = max_tokens or self.max_tokens
        current_tokens = self.count_tokens(content)

        if current_tokens <= target_tokens:
            return content

        # Truncate to fit budget
        ratio = target_tokens / current_tokens
        target_chars = int(len(content) * ratio)

        return content[:target_chars] + "\n... [truncated]"
```

## Service Coordination Patterns

### Pattern 1: Multi-Step Workflow

```python
class SessionService:
    def complete_task_workflow(self, task: str) -> Session:
        """
        Complete workflow example:
        1. Validate input
        2. Load dependencies
        3. Apply business logic
        4. Persist changes
        5. Return result
        """
        # Step 1: Validation
        if not task:
            raise ValueError("Task cannot be empty")

        # Step 2: Load dependencies
        session = self.load_session(self.current_session_id)

        # Step 3: Business logic (via domains)
        from pipe.core.domains.turns import expire_old_tool_responses
        modified = expire_old_tool_responses(session.turns)

        # Step 4: Persist if modified
        if modified:
            self.repository.save(session)

        # Step 5: Return
        return session
```

### Pattern 2: Transaction Coordination

```python
class SessionService:
    def atomic_operation(self, session_id: str, data: Any) -> None:
        """
        Ensures operation is atomic - either all changes succeed or none.
        """
        try:
            # Load
            session = self.load_session(session_id)
            original_state = session.model_copy()

            # Modify
            session.apply_changes(data)

            # Validate
            if not self._validate_session(session):
                raise ValueError("Invalid session state")

            # Persist
            self.repository.save(session)

        except Exception as e:
            # Rollback on error
            logger.error(f"Operation failed: {e}")
            if original_state:
                self.repository.save(original_state)
            raise
```

### Pattern 3: Lazy Loading

```python
class SessionService:
    def get_session(self, session_id: str) -> Session:
        """
        Lazy loads session only when needed.
        """
        if self.current_session and self.current_session.id == session_id:
            return self.current_session

        return self.load_session(session_id)
```

## Testing

### Unit Testing Services

```python
# tests/core/services/test_session_service.py
from unittest.mock import Mock
import pytest

def test_start_session():
    # Setup mocks
    mock_repo = Mock()
    mock_settings = Mock(timezone="UTC", sessions_path="sessions")

    service = SessionService(
        project_root="/test",
        settings=mock_settings,
        repository=mock_repo,
    )

    # Execute
    session_id = service.start_session(
        purpose="Test purpose",
        background="Test background",
    )

    # Verify
    assert session_id is not None
    mock_repo.save.assert_called_once()
    assert service.current_session is not None


def test_load_session_not_found():
    mock_repo = Mock()
    mock_repo.find.return_value = None

    service = SessionService(
        project_root="/test",
        settings=mock_settings,
        repository=mock_repo,
    )

    with pytest.raises(ValueError, match="Session not found"):
        service.load_session("nonexistent")
```

### Integration Testing

```python
def test_session_workflow_integration(tmp_path):
    """
    Tests full workflow with real repository.
    """
    # Setup with real repository
    settings = Settings(sessions_path=str(tmp_path))
    repo = SessionRepository(str(tmp_path), settings)
    service = SessionService(str(tmp_path), settings, repo)

    # Create session
    session_id = service.start_session("Purpose", "Background")

    # Add turn
    turn = UserTaskTurn(message="Test task", timestamp=get_current_timestamp())
    service.add_turn_to_current_session(turn)

    # Reload and verify
    loaded = service.load_session(session_id)
    assert len(loaded.turns) == 1
    assert loaded.turns[0].message == "Test task"
```

## Best Practices

### 1. Keep Services Focused

Each service should have a clear domain:

```python
# ✅ GOOD: Clear domain separation
class SessionService:  # Manages session lifecycle
class PromptService:   # Constructs prompts
class TokenService:    # Handles tokens

# ❌ BAD: Mixing concerns
class MegaService:     # Does everything
```

### 2. Use Dependency Injection

```python
# ✅ GOOD: Dependencies injected
class SessionService:
    def __init__(self, repository: SessionRepository):
        self.repository = repository

# ❌ BAD: Creating dependencies internally
class SessionService:
    def __init__(self):
        self.repository = SessionRepository()  # Hard to test
```

### 3. Delegate to Domain Layer

```python
# ✅ GOOD: Delegate business logic
from pipe.core.domains.turns import expire_old_tool_responses

class SessionService:
    def cleanup_turns(self, session: Session):
        modified = expire_old_tool_responses(session.turns)
        if modified:
            self.repository.save(session)

# ❌ BAD: Business logic in service
class SessionService:
    def cleanup_turns(self, session: Session):
        # Complex filtering logic here...
```

### 4. Handle Errors Meaningfully

```python
# ✅ GOOD: Clear error messages
def load_session(self, session_id: str) -> Session:
    session = self.repository.find(session_id)
    if not session:
        raise ValueError(f"Session not found: {session_id}")
    return session

# ❌ BAD: Generic errors
def load_session(self, session_id: str) -> Session:
    session = self.repository.find(session_id)
    if not session:
        raise Exception("Error")
```

## Summary

Services are the **application orchestration layer**:

- ✅ Coordinate complex workflows
- ✅ Manage application state
- ✅ Bridge between components
- ✅ Enforce business rules
- ❌ No direct file I/O
- ❌ No low-level business logic
- ❌ No direct API calls

Services are the conductors of the system, orchestrating the symphony of components.
