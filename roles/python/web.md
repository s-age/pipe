# Web Layer Guidelines (BFF)

## Overview

The `src/pipe/web` directory implements a **Backend for Frontend (BFF)** architecture that provides a clean HTTP API interface for the application. This layer acts as an adapter between HTTP requests and the core business logic.

## Architecture Pattern

```
┌──────────────────────────────────────────────┐
│ HTTP Request                                 │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│ Controllers (Orchestration)                  │  ← Combine multiple actions
├──────────────────────────────────────────────┤
│ Actions (Single Responsibility)              │  ← Execute one operation
├──────────────────────────────────────────────┤
│ Request Models (Validation)                  │  ← Validate input
├──────────────────────────────────────────────┤
│ Validators (Custom Rules)                    │  ← Business rule validation
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│ Core Layer (Services, Domains, Repos)       │
└──────────────────────────────────────────────┘
```

## Directory Structure

```
web/
├── app.py                    # Flask application setup
├── controllers/              # Multi-action orchestration
│   └── session_detail_controller.py
├── actions/                  # Single-purpose actions
│   ├── base_action.py
│   ├── session_actions.py
│   ├── reference_actions.py
│   ├── turn_actions.py
│   └── ...
├── requests/                 # Request validation models
│   └── sessions/
│       ├── start_session.py
│       ├── edit_references.py
│       └── ...
└── validators/               # Custom validation rules
    └── rules/
        └── file_exists.py
```

## Core Principles

### 1. BFF Pattern

- **Backend for Frontend** - Tailored API for specific frontend needs
- **Thin layer** - Business logic stays in core layer
- **HTTP adapter** - Transforms HTTP to domain calls
- **Client-specific** - Responses shaped for frontend consumption

### 2. Separation of Concerns

- **Controllers** - Orchestrate multiple actions
- **Actions** - Execute single operations
- **Requests** - Validate and parse input
- **Validators** - Enforce custom rules

### 3. Single Responsibility

Each action performs **one** operation:

- `SessionStartAction` - Create and start session
- `SessionGetAction` - Retrieve session
- `ReferencesEditAction` - Update references

### 4. Type Safety

- All request data validated with Pydantic
- Type hints on all functions
- Clear response structures

## Layer Responsibilities

### Controllers

**Purpose**: Orchestrate multiple actions to fulfill complex requests

**Characteristics**:

- ✅ Combine multiple actions
- ✅ Coordinate related operations
- ✅ Return composite responses
- ❌ **NO business logic** - delegate to core
- ❌ **NO direct database access** - use services
- ❌ **NO complex validation** - use request models

### Actions

**Purpose**: Execute single operations with clear boundaries

**Characteristics**:

- ✅ Single responsibility
- ✅ Direct service calls
- ✅ Simple error handling
- ✅ Return `(dict, status_code)` tuple
- ❌ **NO orchestration** - one operation only
- ❌ **NO business logic** - delegate to core
- ❌ **NO state** - stateless operations

### Request Models

**Purpose**: Validate and parse HTTP request data

**Characteristics**:

- ✅ Pydantic models
- ✅ Field validation
- ✅ Custom validators
- ✅ Type coercion
- ❌ **NO business logic** - only validation
- ❌ **NO persistence** - just data structures

### Validators

**Purpose**: Custom validation rules for request data

**Characteristics**:

- ✅ Reusable validation functions
- ✅ Clear error messages
- ✅ Independent of request models
- ❌ **NO business logic** - only validation
- ❌ **NO side effects** - pure validation

## Dependency Rules

**Allowed**:

- Controllers → Actions, Core Services
- Actions → Core Services, Request Models
- Request Models → Validators, Core Models
- Validators → No dependencies (pure functions)

**Forbidden**:

- ❌ Web layer must NOT import Core domains directly
- ❌ Actions must NOT call other actions
- ❌ Request models must NOT import services
- ❌ Direct file I/O in web layer

## Forbidden Patterns

1. **Business Logic in Web Layer** - Use core layer
2. **Direct Database/File Access** - Use repositories via services
3. **Complex Orchestration in Actions** - Use controllers
4. **Stateful Actions** - Actions must be stateless
5. **print() for Logging** - Use logging module

## Best Practices

### 1. Keep Actions Simple

```python
# ✅ GOOD: Single responsibility
class SessionGetAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        session_id = self.params.get("session_id")
        session = session_service.get_session(session_id)
        return {"session": session.to_dict()}, 200

# ❌ BAD: Multiple responsibilities
class SessionGetAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        # Getting session AND tree AND settings - too much!
        session = session_service.get_session(session_id)
        tree = session_service.get_tree()
        settings = settings_service.get_settings()
        return {...}, 200
```

### 2. Use Controllers for Orchestration

```python
# ✅ GOOD: Controller orchestrates multiple actions
class SessionDetailController:
    def get_session_with_tree(self, session_id: str):
        tree_response, _ = SessionTreeAction(...).execute()
        session_response, _ = SessionGetAction(...).execute()

        return {
            "session_tree": tree_response["sessions"],
            "current_session": session_response["session"],
        }, 200

# ❌ BAD: Action doing orchestration
class SessionGetAction(BaseAction):
    def execute(self):
        # Actions shouldn't orchestrate other actions
        tree = SessionTreeAction(...).execute()
        ...
```

### 3. Validate in Request Models

```python
# ✅ GOOD: Validation in request model
class StartSessionRequest(BaseModel):
    purpose: str
    instruction: str

    @field_validator("purpose")
    @classmethod
    def check_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("purpose must not be empty")
        return v

# ❌ BAD: Validation in action
class SessionStartAction(BaseAction):
    def execute(self):
        data = self.request_data.get_json()
        if not data["purpose"].strip():  # Manual validation
            return {"message": "Invalid"}, 400
```

### 4. Return Consistent Responses

```python
# ✅ GOOD: Consistent response format
def execute(self) -> tuple[dict[str, Any], int]:
    return {"session": session.to_dict()}, 200

# ❌ BAD: Inconsistent format
def execute(self):
    return session, 200  # Not a dict!
```

## Error Handling

### Standard Error Response

```python
# Validation error
return {"message": "Validation failed: ...", "errors": [...]}, 422

# Not found
return {"message": "Session not found"}, 404

# Server error
return {"message": "Internal error", "details": str(e)}, 500

# Success
return {"session": session.to_dict()}, 200
```

### Exception Handling Pattern

```python
def execute(self) -> tuple[dict[str, Any], int]:
    try:
        # Validate request
        request_data = RequestModel(**self.request_data.get_json())

        # Call service
        result = service.do_something(request_data.field)

        return {"result": result}, 200

    except ValidationError as e:
        return {"message": str(e)}, 422
    except FileNotFoundError:
        return {"message": "Resource not found"}, 404
    except Exception as e:
        return {"message": str(e)}, 500
```

## Testing

### Testing Actions

```python
# tests/web/actions/test_session_actions.py
def test_session_get_action_success():
    action = SessionGetAction(
        params={"session_id": "test-123"},
        request_data=None,
    )

    response, status = action.execute()

    assert status == 200
    assert "session" in response


def test_session_get_action_not_found():
    action = SessionGetAction(
        params={"session_id": "nonexistent"},
        request_data=None,
    )

    response, status = action.execute()

    assert status == 404
    assert "message" in response
```

### Testing Request Models

```python
# tests/web/requests/test_start_session.py
def test_start_session_request_validation():
    # Valid request
    request = StartSessionRequest(
        purpose="Test",
        background="Background",
        instruction="Do something",
    )
    assert request.purpose == "Test"

    # Invalid request
    with pytest.raises(ValidationError):
        StartSessionRequest(
            purpose="",  # Empty - should fail
            background="Background",
            instruction="Do something",
        )
```

## Summary

The web layer is a **thin BFF** that:

- ✅ Adapts HTTP requests to core layer calls
- ✅ Validates input with Pydantic
- ✅ Returns consistent JSON responses
- ✅ Separates concerns (controllers, actions, requests)
- ❌ Contains NO business logic
- ❌ Does NO direct data access
- ❌ Has NO state

Keep it thin, keep it clean, keep it focused on HTTP adaptation.
