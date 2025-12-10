# Actions Layer

## Purpose

Actions execute **single-purpose web operations**. Each action handles one specific operation (get session, create session, update reference) and returns data directly.

## Responsibilities

1. **Single Operation** - One action, one responsibility
2. **Service Coordination** - Call core services
3. **Error Handling** - Raise HttpException for errors
4. **Data Return** - Return data (dict/list/TypedDict)
5. **Request Access** - Access validated request data

## Rules

### ✅ DO

- Single responsibility (one operation)
- Call services for business logic
- Raise HttpException for errors
- Return data directly (dispatcher wraps in ApiResponse)
- Access validated data via self.validated_request (new pattern)
- Keep stateless

### ❌ DON'T

- **NO business logic** - Use services
- **NO orchestration** - One operation only
- **NO calling other actions** - Let controllers orchestrate
- **NO state** - Actions are stateless
- **NO manual ApiResponse wrapping** - Dispatcher handles it

## File Structure

```
actions/
├── base_action.py            # Abstract base
├── session_actions.py        # Session operations
├── reference_actions.py      # Reference operations
├── turn_actions.py           # Turn operations
└── ...
```

## Dependencies

**Allowed:**
- ✅ Core Services
- ✅ Core Models (type hints)
- ✅ Request Models (validation)
- ✅ Standard library

**Forbidden:**
- ❌ Other actions
- ❌ Controllers
- ❌ Domains directly (use services)
- ❌ Repositories directly (use services)

## Example: Legacy Pattern (body_model)

```python
"""Get session action."""

from pipe.web.actions.base_action import BaseAction
from pipe.web.exceptions import NotFoundError

class GetSessionAction(BaseAction):
    """
    Get session by ID.
    
    Legacy pattern using body_model (no request validation).
    Path params accessed via self.request.
    """
    
    def execute(self) -> dict:
        """
        Get session.
        
        Returns:
            Session data as dict
            
        Raises:
            NotFoundError: If session not found
        """
        # Access path params from request
        session_id = self.request.get_path_param("session_id")
        
        # Call service
        try:
            session = self.session_service.load_session(session_id)
        except FileNotFoundError:
            raise NotFoundError(f"Session {session_id} not found")
        
        # Return data (dispatcher wraps in ApiResponse)
        return session.model_dump()
```

## Example: New Pattern (request_model)

```python
"""Fork session action."""

from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.fork_session import ForkSessionRequest
from pipe.web.exceptions import BadRequestError

class ForkSessionAction(BaseAction):
    """
    Fork session at turn index.
    
    New pattern using request_model (Laravel/Struts style).
    Validation happens BEFORE execute().
    """
    
    request_model = ForkSessionRequest  # Pre-validated
    
    def execute(self) -> dict:
        """
        Fork session.
        
        Returns:
            Forked session data
            
        Raises:
            BadRequestError: If validation fails
        """
        # Access validated data
        session_id = self.validated_request.session_id
        fork_index = self.validated_request.fork_index
        
        # Call service
        try:
            forked = self.session_service.fork_session(session_id, fork_index)
        except ValueError as e:
            raise BadRequestError(str(e))
        
        return forked.model_dump()
```

## Common Patterns

### Pattern 1: Simple Get

```python
def execute(self) -> dict:
    """Get entity by ID."""
    entity_id = self.request.get_path_param("entity_id")
    entity = self.service.get(entity_id)
    return entity.model_dump()
```

### Pattern 2: Create with Validation

```python
request_model = CreateEntityRequest

def execute(self) -> dict:
    """Create entity."""
    data = self.validated_request.model_dump()
    entity = self.service.create(data)
    return entity.model_dump()
```

### Pattern 3: Update

```python
request_model = UpdateEntityRequest

def execute(self) -> dict:
    """Update entity."""
    entity_id = self.validated_request.entity_id
    updates = self.validated_request.get_updates()
    entity = self.service.update(entity_id, updates)
    return entity.model_dump()
```

## Testing

```python
# tests/web/actions/test_session_actions.py

def test_get_session_returns_session_data(mock_service):
    """Test get session returns data."""
    action = GetSessionAction(mock_service)
    action.request = MockRequest(path_params={"session_id": "test123"})
    
    result = action.execute()
    
    assert result["session_id"] == "test123"
    mock_service.load_session.assert_called_once_with("test123")

def test_fork_session_validates_request():
    """Test fork validates via request_model."""
    action = ForkSessionAction(mock_service)
    action.validated_request = ForkSessionRequest(
        session_id="test123",
        fork_index=5
    )
    
    result = action.execute()
    
    assert result["purpose"].startswith("Fork of:")
```

## Summary

**Actions:**
- ✅ Single-purpose operations
- ✅ Call services for logic
- ✅ Raise HttpException for errors
- ✅ Return data directly
- ❌ No business logic or orchestration
- ❌ Stateless

**Actions execute one operation, services contain workflows**
