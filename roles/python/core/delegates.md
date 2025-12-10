# Delegates Layer

## Purpose

Delegates provide **high-level workflows** for CLI/Web interfaces. They orchestrate services to implement complete user operations (start session, send instruction, compress history).

## Responsibilities

1. **Workflow Orchestration** - Coordinate multiple services
2. **User Interface** - Provide clean API for CLI/Web
3. **State Management** - Manage current session state
4. **Error Translation** - Convert internal errors to user-friendly messages
5. **Transaction Boundaries** - Define operation atomicity

## Rules

### ✅ DO

- Orchestrate multiple services
- Manage workflow state
- Provide clean public API
- Handle cross-service transactions
- Convert technical errors to user messages

### ❌ DON'T

- **NO business logic** - Use services/domains
- **NO file I/O** - Use repositories via services
- **NO API calls** - Use agents via services
- **NO direct model manipulation** - Use services

## File Structure

```
delegates/
├── session_delegate.py    # Session workflows
└── ...
```

## Dependencies

**Allowed:**
- ✅ Services (orchestrate them)
- ✅ Models (for types)
- ✅ Standard library

**Forbidden:**
- ❌ Repositories directly
- ❌ Domains directly
- ❌ Agents directly
- ❌ Tools directly

## Example

```python
"""Session workflow delegate."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pipe.core.services.session_workflow_service import SessionWorkflowService
    from pipe.core.services.session_turn_service import SessionTurnService
    from pipe.core.models.session import Session

class SessionDelegate:
    """
    High-level session workflows.
    
    Orchestrates multiple services to provide complete
    user-facing operations.
    """
    
    def __init__(
        self,
        workflow_service: "SessionWorkflowService",
        turn_service: "SessionTurnService",
        current_session: "Session | None" = None
    ):
        self.workflow_service = workflow_service
        self.turn_service = turn_service
        self.current_session = current_session
    
    def start_new_session(self, purpose: str) -> "Session":
        """
        Start new session workflow.
        
        Workflow:
        1. Create session via workflow service
        2. Set as current session
        3. Return session
        
        Args:
            purpose: Session purpose
            
        Returns:
            New session
        """
        # Create via service
        session = self.workflow_service.create_session(purpose)
        
        # Set as current
        self.current_session = session
        
        return session
    
    def send_instruction(self, instruction: str) -> "Session":
        """
        Send instruction to current session.
        
        Workflow:
        1. Validate current session exists
        2. Add user turn
        3. Get model response
        4. Update current session
        5. Return updated session
        
        Args:
            instruction: User instruction
            
        Returns:
            Updated session
            
        Raises:
            ValueError: If no current session
        """
        if not self.current_session:
            raise ValueError("No active session")
        
        # Add user turn
        self.turn_service.add_turn(
            self.current_session,
            {"type": "user_input", "content": instruction}
        )
        
        # Get model response (via another service)
        # ... orchestration logic ...
        
        return self.current_session
    
    def fork_current_session(self, fork_index: int) -> "Session":
        """
        Fork current session.
        
        Workflow:
        1. Validate current session exists
        2. Fork via workflow service
        3. Set fork as current
        4. Return forked session
        
        Args:
            fork_index: Turn index to fork from
            
        Returns:
            Forked session
            
        Raises:
            ValueError: If no current session
        """
        if not self.current_session:
            raise ValueError("No active session")
        
        # Fork via service
        forked = self.workflow_service.fork_session(
            self.current_session.session_id,
            fork_index
        )
        
        # Set as current
        self.current_session = forked
        
        return forked
```

## Common Patterns

### Pattern 1: State Management

```python
def ensure_current_session(self) -> Session:
    """Ensure session exists, raise clear error."""
    if not self.current_session:
        raise ValueError("No active session. Start one with start_session()")
    return self.current_session
```

### Pattern 2: Multi-Service Orchestration

```python
def complex_workflow(self, param: str) -> Result:
    """Orchestrate multiple services."""
    # Service 1
    result1 = self.service1.operation(param)
    
    # Service 2 using result1
    result2 = self.service2.operation(result1.data)
    
    # Update state
    self.current_state = result2
    
    return result2
```

### Pattern 3: Error Translation

```python
def user_operation(self, param: str) -> Result:
    """Translate technical errors to user messages."""
    try:
        return self.service.operation(param)
    except FileNotFoundError:
        raise ValueError("Session not found. Please check the ID.")
    except PermissionError:
        raise ValueError("Cannot access session. Check permissions.")
```

## Testing

```python
# tests/core/delegates/test_session_delegate.py

def test_start_new_session_sets_current(mock_workflow_service):
    """Test start_new_session sets current session."""
    delegate = SessionDelegate(mock_workflow_service, mock_turn_service)
    
    session = delegate.start_new_session("Test purpose")
    
    assert delegate.current_session == session
    assert session.purpose == "Test purpose"

def test_send_instruction_requires_session():
    """Test send_instruction validates session exists."""
    delegate = SessionDelegate(mock_workflow_service, mock_turn_service)
    
    with pytest.raises(ValueError, match="No active session"):
        delegate.send_instruction("test")

def test_fork_current_session_updates_current(mock_workflow_service):
    """Test fork updates current session."""
    delegate = SessionDelegate(mock_workflow_service, mock_turn_service)
    delegate.current_session = create_test_session()
    
    forked = delegate.fork_current_session(0)
    
    assert delegate.current_session == forked
    assert forked.session_id != delegate.current_session.session_id
```

## Summary

**Delegates:**
- ✅ High-level workflow orchestration
- ✅ Multi-service coordination
- ✅ User-facing API
- ✅ State management
- ❌ No business logic, I/O, or direct layer access

**Delegates orchestrate services, services implement operations**
