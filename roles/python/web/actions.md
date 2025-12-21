# Actions Layer

## Purpose

Actions execute **single-purpose web operations**. Each action handles one specific operation (get session, create session, update reference) and returns data directly. They serve as the entry point for business logic from the HTTP layer.

## Responsibilities

1.  **Single Operation** - One action, one responsibility.
2.  **Service Coordination** - Call core services to perform business logic.
3.  **Error Handling** - Raise `HttpException` (or subclasses) for expected errors.
4.  **Data Return** - Return Pydantic models, dicts, lists, or primitives directly.
5.  **Request Access** - Access validated request data via `self.validated_request`.

## Rules

### ✅ DO

-   **Single Responsibility**: Focus on one specific task (e.g., `CreateSessionAction` vs `GetSessionAction`).
-   **Use Services**: Delegate actual business logic to Core Services (`self.session_service.create(...)`).
-   **Dependency Injection**: Declare dependencies in `__init__` (type-hinted). The `GenericActionFactory` will auto-wire them.
-   **Use Request Models**: Define `request_model` for type-safe, pre-validated input.
-   **Return Raw Data**: Return the result directly. The `ActionDispatcher` wraps it in an `ApiResponse`.
-   **Stateless**: Actions are instantiated per request; do not store state between requests.

### ❌ DON'T

-   **NO Business Logic**: Do not implement complex logic in the Action. Use Services.
-   **NO Orchestration**: Do not call other Actions. Use Services or Controllers if orchestration is needed.
-   **NO Direct Response Creation**: Do not return `Flask.Response` manually unless necessary (e.g., streaming). Let the dispatcher handle standard JSON responses.
-   **NO "Bag of State"**: Avoid `**kwargs` unless absolutely necessary. Be explicit about dependencies.

## File Structure

```text
src/pipe/web/actions/
├── base_action.py            # Abstract base class
├── session_actions.py        # Grouped by domain (small)
├── sessions/                 # Grouped by domain (large)
│   ├── create_action.py
│   ├── get_action.py
│   └── ...
└── fs/
    ├── search_l2_action.py
    └── ...
```

## Dependency Injection (Auto-Wiring)

The system uses `GenericActionFactory` to inject dependencies defined in the `__init__` method.

```python
class MyAction(BaseAction):
    def __init__(
        self,
        session_service: SessionService,  # Auto-injected from container
        settings: Settings,               # Auto-injected from container
        **kwargs
    ):
        super().__init__(**kwargs)
        self.session_service = session_service
        self.settings = settings
```

## Patterns

### 1. The Unified Pattern (Recommended)

Use a `request_model` (subclass of `BaseRequest`) to handle both path parameters and body data.

```python
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.fork_session import ForkSessionRequest

class ForkSessionAction(BaseAction):
    # Validation happens BEFORE execute()
    request_model = ForkSessionRequest 

    def __init__(self, session_service: SessionService, **kwargs):
        super().__init__(**kwargs)
        self.session_service = session_service

    def execute(self) -> dict:
        # self.validated_request is an instance of ForkSessionRequest
        req = self.validated_request
        
        result = self.session_service.fork(
            session_id=req.session_id,
            index=req.fork_index
        )
        return result.model_dump()
```

### 2. The Legacy/Simple Pattern (Dict-based)

If `request_model` is not defined, `self.validated_request` is a dictionary (snake_cased).

```python
class SimpleAction(BaseAction):
    def execute(self) -> dict:
        # self.validated_request is a dict
        query = self.validated_request.get("query")
        # self.params contains path parameters
        session_id = self.params.get("session_id")
        
        return {"result": "ok"}
```

## Error Handling

Raise exceptions from `pipe.web.exceptions`. The dispatcher catches them and formats the error response.

```python
from pipe.web.exceptions import NotFoundError, BadRequestError

def execute(self):
    if not found:
        raise NotFoundError("Resource not found")
    if invalid:
        raise BadRequestError("Invalid input")
```

## Testing

Test Actions by instantiating them directly and mocking dependencies.

```python
def test_fork_action():
    mock_service = MagicMock()
    action = ForkSessionAction(session_service=mock_service)
    
    # Mock the validated request
    action.validated_request = ForkSessionRequest(session_id="123", fork_index=1)
    
    action.execute()
    
    mock_service.fork.assert_called_with(session_id="123", index=1)
```