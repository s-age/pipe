# Services Layer

## Purpose

Services provide **workflow orchestration**, coordinating between repositories, domains, and agents to implement high-level business operations. Services manage application state and ensure consistency.

## Responsibilities

1. **Workflow Orchestration** - Coordinate multi-step operations
2. **State Management** - Manage session lifecycle
3. **Component Integration** - Bridge repositories, domains, agents
4. **Transaction Coordination** - Ensure atomicity
5. **Public API** - Provide clean interface for delegates

## Rules

### ✅ DO

- Orchestrate complex workflows
- Manage application state (current session, settings)
- Call repositories for persistence
- Call domains for business logic
- Call agents for external integrations
- Ensure data consistency
- Handle transaction boundaries

### ❌ DON'T

- **NO file I/O** - Use repositories
- **NO business logic** - Use domains
- **NO direct API calls** - Use agents
- **NO complex data transformation** - Use domains
- **NO calling delegates** - Services serve delegates, not vice versa

## File Structure

```
services/
├── session_service.py    # Session lifecycle (deprecated, split into specialized services)
├── session_workflow_service.py   # Start, fork, destroy
├── session_turn_service.py       # Turn management
├── session_meta_service.py       # Metadata editing
├── prompt_service.py             # Prompt construction
└── token_service.py              # Token counting
```

## Dependencies

**Allowed:**
- ✅ repositories/ - Persistence
- ✅ domains/ - Business logic
- ✅ agents/ - External integrations
- ✅ collections/ - Data structures
- ✅ models/ - Type definitions
- ✅ utils/ - Utilities

**Forbidden:**
- ❌ delegates/ - Services serve delegates, not vice versa
- ❌ Direct file operations (use repositories)
- ❌ Direct API calls (use agents)

## Example: Specialized Service

```python
"""Service for session turn management."""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pipe.core.models.session import Session
    from pipe.core.repositories.session_repository import SessionRepository

logger = logging.getLogger(__name__)

class SessionTurnService:
    """
    Manages turn operations within sessions.
    
    Responsibilities:
    - Add turns to session
    - Edit existing turns
    - Delete turns
    - Persist changes
    """
    
    def __init__(self, session_repo: "SessionRepository"):
        self.session_repo = session_repo
    
    def add_turn(self, session: "Session", turn_data: dict) -> None:
        """
        Add new turn to session.
        
        Business Rules:
        - Validated by TurnCollection
        - Session persisted after change
        
        Args:
            session: Target session
            turn_data: Turn data to add
        """
        from pipe.core.models.turn import Turn
        
        # Create and add turn
        turn = Turn(**turn_data)
        session.turns.add(turn)
        
        # Persist change
        self.session_repo.save(session)
        logger.info(f"Added turn to session {session.session_id}")
    
    def edit_turn(self, session: "Session", index: int, data: dict) -> None:
        """
        Edit existing turn.
        
        Args:
            session: Target session
            index: Turn index to edit
            data: New turn data
            
        Raises:
            IndexError: If index out of range
        """
        # Use collection method
        session.turns.edit_by_index(index, data)
        
        # Persist change
        self.session_repo.save(session)
        logger.info(f"Edited turn {index} in session {session.session_id}")
    
    def delete_turn(self, session: "Session", index: int) -> None:
        """
        Delete turn by index.
        
        Args:
            session: Target session
            index: Turn index to delete
            
        Raises:
            IndexError: If index out of range
        """
        # Use collection method
        session.turns.delete_by_index(index)
        
        # Persist change
        self.session_repo.save(session)
        logger.info(f"Deleted turn {index} from session {session.session_id}")
```

## Example: Workflow Orchestration

```python
"""Service for session workflow management."""

from typing import TYPE_CHECKING
from pipe.core.domains.session import fork_session

if TYPE_CHECKING:
    from pipe.core.models.session import Session
    from pipe.core.repositories.session_repository import SessionRepository

class SessionWorkflowService:
    """
    Manages session lifecycle workflows.
    
    Responsibilities:
    - Start new sessions
    - Fork existing sessions
    - Destroy sessions
    """
    
    def __init__(self, session_repo: "SessionRepository", timezone):
        self.session_repo = session_repo
        self.timezone = timezone
    
    def fork_session(self, session_id: str, fork_index: int) -> "Session":
        """
        Fork session at specific turn.
        
        Workflow:
        1. Load original session
        2. Use domain function to create fork
        3. Persist forked session
        4. Return forked session
        
        Args:
            session_id: Original session ID
            fork_index: Turn index to fork from
            
        Returns:
            Forked session
            
        Raises:
            FileNotFoundError: If session not found
            IndexError: If fork_index out of range
            ValueError: If fork point invalid
        """
        # Load original
        original = self.session_repo.load(session_id)
        
        # Use domain logic for fork creation
        forked = fork_session(original, fork_index, self.timezone)
        
        # Persist new session
        self.session_repo.save(forked)
        
        return forked
```

## Common Patterns

### Pattern 1: Load-Modify-Save

```python
def update_entity(self, entity_id: str, updates: dict) -> Entity:
    """Standard update pattern."""
    # Load
    entity = self.repo.load(entity_id)
    
    # Modify (use domain function)
    modified = apply_updates(entity, updates)
    
    # Save
    self.repo.save(modified)
    
    return modified
```

### Pattern 2: Transaction Coordination

```python
def complex_operation(self, id1: str, id2: str) -> None:
    """Coordinate multiple updates atomically."""
    entity1 = self.repo1.load(id1)
    entity2 = self.repo2.load(id2)
    
    # Apply changes
    modified1 = transform1(entity1)
    modified2 = transform2(entity2)
    
    # Validate consistency
    if not are_consistent(modified1, modified2):
        raise ValueError("Inconsistent state")
    
    # Persist both
    self.repo1.save(modified1)
    self.repo2.save(modified2)
```

### Pattern 3: Delegate to Domains

```python
def business_operation(self, entity: Entity, params: dict) -> Entity:
    """Service orchestrates, domain contains logic."""
    # Service just coordinates
    result = domain_function(entity, params)
    self.repo.save(result)
    return result
```

## Testing

```python
# tests/core/services/test_session_turn_service.py

def test_add_turn_persists_session(mock_repo):
    """Test add_turn saves to repository."""
    service = SessionTurnService(mock_repo)
    session = create_test_session()
    turn_data = {"type": "user_input", "content": "test"}
    
    service.add_turn(session, turn_data)
    
    mock_repo.save.assert_called_once_with(session)
    assert len(session.turns) == 1

def test_fork_session_creates_new_id(session_repo):
    """Test fork creates session with new ID."""
    service = SessionWorkflowService(session_repo, timezone)
    original = create_test_session()
    session_repo.save(original)
    
    forked = service.fork_session(original.session_id, 0)
    
    assert forked.session_id != original.session_id
    assert forked.purpose.startswith("Fork of:")
```

## Summary

**Services:**
- ✅ Orchestrate workflows
- ✅ Manage state
- ✅ Coordinate components
- ✅ Ensure consistency
- ❌ No file I/O, business logic, or direct API calls
- ❌ Called by delegates, not vice versa

**Services define workflows, domains define business rules**
