# Controllers Layer

## Purpose

Controllers handle **HTTP routing and orchestration**. They map URLs to actions, handle authentication, and coordinate multiple operations.

## Responsibilities

1. **Route Handling** - Map URLs to actions
2. **Auth/Validation** - Check permissions
3. **Multi-Action Orchestration** - Coordinate actions
4. **Response Building** - Build HTTP responses
5. **Error Handling** - Convert exceptions to HTTP errors

## Rules

### ✅ DO

- Handle routing
- Orchestrate multiple actions when needed
- Convert exceptions to HTTP responses
- Keep thin (delegate to actions)
- Handle CORS and headers

### ❌ DON'T

- **NO business logic** - Use actions/services
- **NO direct service calls** - Use actions
- **NO complex validation** - Use request models
- **NO persistence** - Use actions/services

## File Structure

```
controllers/
├── session_controller.py    # Session routes
├── reference_controller.py  # Reference routes
└── ...
```

## Dependencies

**Allowed:**
- ✅ Actions
- ✅ Request models
- ✅ Flask
- ✅ Standard library

**Forbidden:**
- ❌ Services directly (use actions)
- ❌ Repositories
- ❌ Domains

## Example

```python
"""Session controller."""

from flask import Blueprint, request
from pipe.web.actions.session_actions import (
    GetSessionAction,
    StartSessionAction,
    ForkSessionAction
)
from pipe.web.dispatcher import dispatch

bp = Blueprint('sessions', __name__, url_prefix='/sessions')

@bp.route('/<session_id>', methods=['GET'])
def get_session(session_id: str):
    """Get session by ID."""
    return dispatch(GetSessionAction, request, session_id=session_id)

@bp.route('/', methods=['POST'])
def start_session():
    """Start new session."""
    return dispatch(StartSessionAction, request)

@bp.route('/<session_id>/fork', methods=['POST'])
def fork_session(session_id: str):
    """Fork session."""
    return dispatch(ForkSessionAction, request, session_id=session_id)
```

## Common Patterns

### Pattern 1: Simple Route

```python
@bp.route('/<id>', methods=['GET'])
def get(id: str):
    """Get entity."""
    return dispatch(GetAction, request, entity_id=id)
```

### Pattern 2: Multi-Action Orchestration

```python
@bp.route('/complex', methods=['POST'])
def complex_operation():
    """Orchestrate multiple actions."""
    # Action 1
    result1 = dispatch(Action1, request)
    # Action 2 using result1
    result2 = dispatch(Action2, request, data=result1.data)
    return result2
```

## Testing

```python
# tests/web/controllers/test_session_controller.py

def test_get_session_returns_session(client):
    """Test GET /sessions/<id> returns session."""
    response = client.get('/sessions/test123')
    
    assert response.status_code == 200
    assert response.json['session_id'] == 'test123'

def test_start_session_creates_session(client):
    """Test POST /sessions creates session."""
    response = client.post('/sessions', json={
        'purpose': 'Test session'
    })
    
    assert response.status_code == 200
    assert 'session_id' in response.json
```

## Summary

**Controllers:**
- ✅ HTTP routing
- ✅ Action orchestration
- ✅ Response building
- ❌ No business logic
- ❌ Delegate to actions

**Controllers route requests, actions execute operations**
