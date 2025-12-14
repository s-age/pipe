# Request Models Layer

## Purpose

Request Models provide **strict, type-safe input validation** for HTTP requests. They decouple validation rules from business logic and Actions.

## Responsibilities

1.  **Validation**: specific rules (min/max length, regex, etc.) for both Body and Path parameters.
2.  **Normalization**: Ensure input data is in the expected format (e.g., snake_case).
3.  **Type Safety**: Provide Python types for the Action layer.

## Rules

### ✅ DO

-   Inherit from `pipe.web.requests.base_request.BaseRequest`.
-   Define `path_params` list to map URL parameters to fields.
-   Use standard Pydantic `Field` for constraints.
-   Use `@field_validator` for complex logic.
-   Type-hint all fields.

### ❌ DON'T

-   **NO Business Logic**: Do not query the database or call services.
-   **NO Side Effects**: Validation should be pure.

## File Structure

```text
src/pipe/web/requests/
├── base_request.py
├── sessions/
│   ├── fork_session_request.py
│   └── start_session_request.py
└── ...
```

## The Unified Pattern (BaseRequest)

This pattern validates **Path Parameters** and **Body Data** in a single model.

```python
from pydantic import Field, field_validator
from pipe.web.requests.base_request import BaseRequest

class ForkSessionRequest(BaseRequest):
    # 1. Define which fields come from the URL path
    path_params = ["session_id"]

    # 2. Define fields (Path + Body)
    session_id: str = Field(..., description="The ID of the session")
    fork_index: int = Field(..., ge=0, description="The turn index to fork from")
    new_title: str | None = Field(None, max_length=100)

    # 3. Custom Validators
    @field_validator("session_id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("Session ID must be alphanumeric")
        return v
```

### Usages in Action

When attached to an Action via `request_model`, the dispatcher:
1.  Extracts path parameters from the URL.
2.  Extracts JSON body.
3.  Merges them (snake_cased).
4.  Validates against this model.
5.  Injects the instance into `action.validated_request`.

## Handling Legacy/Simple Requests

If you do not create a Request Model, the Action receives a raw `dict` in `self.validated_request`. This is acceptable for very simple read operations (e.g., `GET /items`) where validation is minimal, but **Request Models are strongly preferred** for any mutation or complex query.

## Testing Requests

Test Request Models to ensure validation rules work as expected.

```python
def test_fork_request_validation():
    # Valid
    req = ForkSessionRequest(session_id="abc", fork_index=1)
    assert req.fork_index == 1

    # Invalid (Negative index)
    with pytest.raises(ValidationError):
        ForkSessionRequest(session_id="abc", fork_index=-1)
```