# Actions Layer

## Purpose

Actions represent **single-purpose operations** in the web layer. Each action executes one specific operation (e.g., get session, create session, update reference) and returns a consistent JSON response.

## Responsibilities

1. **Single Operation** - One action, one responsibility
2. **Service Coordination** - Call core services to execute business logic
3. **Request Parsing** - Extract and validate parameters (pre-validated in new pattern)
4. **Error Handling** - Raise HttpException for errors
5. **Data Return** - Return data directly (dispatcher wraps in ApiResponse)

## Characteristics

- ✅ Single responsibility (one operation only)
- ✅ Stateless execution
- ✅ Direct service calls
- ✅ Raise HttpException for errors
- ✅ Return data directly (dict, list, TypedDict, etc.)
- ❌ **NO business logic** - delegate to services
- ❌ **NO orchestration** - one operation only
- ❌ **NO calling other actions** - let controllers orchestrate
- ❌ **NO state** - actions are stateless
- ❌ **NO manual ApiResponse wrapping** - dispatcher handles it

## File Structure

```
actions/
├── __init__.py
├── base_action.py            # Abstract base class
├── session_actions.py        # Session operations
├── reference_actions.py      # Reference operations
├── turn_actions.py           # Turn operations
├── meta_actions.py           # Metadata operations
├── settings_actions.py       # Settings operations
└── session_tree_action.py    # Tree operations
```

## Dependencies

**Allowed:**

- ✅ Core Services (for business logic)
- ✅ Core Models (for type hints)
- ✅ Request Models (for validation)
- ✅ Standard library

**Forbidden:**

- ❌ Other actions (no action-to-action calls)
- ❌ Controllers (actions don't call controllers)
- ❌ Domains directly (use services)
- ❌ Repositories directly (use services)

## Template

### base_action.py - Abstract Base

```python
"""Base Action class for all API actions."""

from abc import ABC, abstractmethod
from typing import Any

from flask import Request
from pipe.web.request_context import RequestContext
from pipe.web.requests.base_request import BaseRequest
from pipe.web.exceptions import (
    BadRequestError,
    NotFoundError,
    UnprocessableEntityError,
    InternalServerError,
)


class BaseAction(ABC):
    """
    Abstract base class for all API actions.

    Supports two patterns:
    1. Legacy pattern (body_model): For backward compatibility
       - Set body_model class variable
       - Access via self.request.get_body()
       - Validation happens lazily

    2. New pattern (request_model): Laravel/Struts style
       - Set request_model to BaseRequest subclass
       - Validation happens BEFORE action execution
       - Access validated data via self.validated_request

    Attributes:
        request: RequestContext for accessing path params and body
        validated_request: Pre-validated BaseRequest (if using request_model)
        params: (Legacy) URL/query parameters
        request_data: (Legacy) Flask Request object
    """

    # Legacy: Pydantic model for request body only
    body_model: type[BaseModel] | None = None

    # New: BaseRequest subclass for unified validation
    request_model: type[BaseRequest] | None = None

    def __init__(
        self,
        params: dict | None = None,
        request_data: Request | None = None,
        request_context: RequestContext | None = None,
        validated_request: BaseRequest | None = None,
    ):
        """
        Initialize the action with parameters and optional request data.

        Args:
            params: Parameters extracted from URL path and query string
            request_data: Optional Flask Request object for accessing body

        Examples:
            # Legacy initialization (still supported)
            action = SessionGetAction(
                params={"session_id": "abc-123"},
                request_data=None,
            )

            # New initialization (automatic in dispatcher)
            action = SessionStartAction(
                request_context=context,
                validated_request=validated_req,
            )
        """
        # Support legacy initialization
        if request_context is None:
            request_context = RequestContext(
                path_params=params or {},
                request_data=request_data,
                body_model=self.body_model,
            )

        self.request = request_context
        self.validated_request = validated_request

        # Keep legacy attributes for backward compatibility
        self.params = params or {}
        self.request_data = request_data

    @abstractmethod
    def execute(self) -> dict[str, Any] | list[Any] | Any:
        """
        Execute the action and return data directly.

        The dispatcher automatically wraps the return value in ApiResponse
        and handles status codes. Actions should raise HttpException for errors.

        This method must be implemented by all action subclasses.

        Legacy pattern:
        1. Extract parameters via self.request.get_path_param()
        2. Get validated body via self.request.get_body()
        3. Call core services
        4. Return data (dict, list, TypedDict, etc.)
        5. Raise HttpException (BadRequestError, NotFoundError, etc.) on errors

        New pattern (Laravel/Struts style):
        1. Access self.validated_request (already validated!)
        2. Call core services
        3. Return data directly
        4. Raise HttpException on errors

        Returns:
            Data (dict, list, TypedDict, or other serializable types)
            Dispatcher wraps this in ApiResponse[T]

        Raises:
            BadRequestError: For 400 errors (invalid input)
            NotFoundError: For 404 errors (resource not found)
            UnprocessableEntityError: For 422 errors (validation failures)
            InternalServerError: For 500 errors (unexpected failures)

        Examples:
            # Legacy pattern
            session_id = self.request.get_path_param("session_id")
            body = self.request.get_body()
            data = service.get_data(session_id)
            return data  # Dispatcher wraps in ApiResponse

            # New pattern
            req = self.validated_request
            session_id = req.session_id  # Type-safe!
            return service.get_data(session_id)

            # Error handling
            if not resource:
                raise NotFoundError("Resource not found")
        """
        pass
```

## Real Examples

### session_actions.py - Session Operations

```python
"""Actions for session operations."""

import subprocess
import sys
from typing import Any

from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.start_session import StartSessionRequest
from pipe.web.requests.sessions.send_instruction import SendInstructionRequest
from pydantic import ValidationError


class SessionStartAction(BaseAction):
    """
    Action to create and start a new session.

    This action:
    1. Validates request data
    2. Creates new session via service
    3. Executes initial instruction via CLI
    4. Returns session ID
    """

    def execute(self) -> tuple[dict[str, Any], int]:
        """
        Create and start new session with initial instruction.

        Returns:
            Success: ({"session_id": str}, 200)
            Validation error: ({"message": str}, 422)
            Execution error: ({"message": str, "details": str}, 500)

        Examples:
            # Request body:
            # {
            #     "purpose": "Build feature",
            #     "background": "Context",
            #     "instruction": "Create API endpoint",
            #     "references": [{"path": "file.py", ...}]
            # }

            action = SessionStartAction(params={}, request_data=request)
            response, status = action.execute()

            if status == 200:
                print(f"Created session: {response['session_id']}")
        """
        from pipe.web.app import session_service

        try:
            # Validate request data
            request_data = StartSessionRequest(**self.request_data.get_json())

            # Create session via service
            session = session_service.create_new_session(
                purpose=request_data.purpose,
                background=request_data.background,
                roles=request_data.roles,
                multi_step_reasoning_enabled=request_data.multi_step_reasoning_enabled,
                hyperparameters=request_data.hyperparameters,
                parent_id=request_data.parent,
                artifacts=request_data.artifacts,
                procedure=request_data.procedure,
            )
            session_id = session.session_id

            # Build CLI command for initial instruction
            command = [
                sys.executable,
                "-m",
                "pipe.cli.takt",
                "--session",
                session_id,
                "--instruction",
                request_data.instruction,
            ]

            # Add optional parameters
            if request_data.references:
                command.extend([
                    "--references",
                    ",".join(r.path for r in request_data.references),
                ])
            if request_data.artifacts:
                command.extend(["--artifacts", ",".join(request_data.artifacts)])
            if request_data.procedure:
                command.extend(["--procedure", request_data.procedure])
            if request_data.multi_step_reasoning_enabled:
                command.append("--multi-step-reasoning")

            # Execute initial instruction
            subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
            )

            return {"session_id": session_id}, 200

        except ValidationError as e:
            return {"message": str(e)}, 422
        except subprocess.CalledProcessError as e:
            return {
                "message": "Conductor script failed during initial instruction processing.",
                "details": e.stderr,
            }, 500
        except Exception as e:
            return {"message": str(e)}, 500


class SessionGetAction(BaseAction):
    """
    Action to retrieve a session by ID.

    Simple retrieval action that gets session from service.
    """

    def execute(self) -> dict[str, Any]:
        """
        Retrieve session by ID.

        Returns:
            SessionData dict directly (dispatcher wraps in ApiResponse)

        Raises:
            BadRequestError: If session_id is missing
            NotFoundError: If session not found
            InternalServerError: For unexpected errors

        Examples:
            action = SessionGetAction(
                params={"session_id": "abc-123"},
                request_data=None,
            )
            data = action.execute()  # Returns SessionData dict
            # Dispatcher wraps: ApiResponse(success=True, data=data)
        """
        from pipe.web.app import session_service
        from pipe.web.exceptions import BadRequestError, NotFoundError

        # Extract parameter
        session_id = self.request.get_path_param("session_id")
        if not session_id:
            raise BadRequestError("session_id is required")

        # Get session from service
        session_data = session_service.get_session(session_id)

        if not session_data:
            raise NotFoundError("Session not found")

        # Return data directly - dispatcher wraps it
        return session_data.to_dict()


class SessionDeleteAction(BaseAction):
    """
    Action to delete a session.

    Deletes session and all related data via service.
    """

    def execute(self) -> dict[str, str]:
        """
        Delete session by ID.

        Returns:
            Success message dict

        Raises:
            BadRequestError: If session_id is missing
            InternalServerError: For unexpected errors
        """
        from pipe.web.app import session_service
        from pipe.web.exceptions import BadRequestError

        session_id = self.request.get_path_param("session_id")
        if not session_id:
            raise BadRequestError("session_id is required")

        session_service.delete_session(session_id)
        return {"message": f"Session {session_id} deleted"}


class SessionInstructionAction(BaseAction):
    """
    Action to send instruction to existing session.

    Executes new instruction via CLI for existing session.
    """

    def execute(self) -> tuple[dict[str, Any], int]:
        """
        Send instruction to session.

        Returns:
            Success: ({"message": str}, 200)
            Validation error: ({"message": str}, 422)
            Execution error: ({"message": str, "details": str}, 500)
        """
        from pipe.web.app import session_service

        session_id = self.params.get("session_id")
        if not session_id:
            return {"message": "session_id is required"}, 400

        try:
            # Validate request
            request_data = SendInstructionRequest(**self.request_data.get_json())

            # Build CLI command
            command = [
                sys.executable,
                "-m",
                "pipe.cli.takt",
                "--session",
                session_id,
                "--instruction",
                request_data.instruction,
            ]

            # Execute instruction
            subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
            )

            return {"message": "Instruction executed successfully."}, 200

        except ValidationError as e:
            return {"message": str(e)}, 422
        except subprocess.CalledProcessError as e:
            return {
                "message": "Instruction execution failed.",
                "details": e.stderr,
            }, 500
        except Exception as e:
            return {"message": str(e)}, 500
```

### reference_actions.py - Reference Operations

```python
"""Actions for reference operations."""

from typing import Any

from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.edit_references import EditReferencesRequest
from pipe.web.requests.sessions.edit_reference_persist import EditReferencePersistRequest
from pipe.web.requests.sessions.edit_reference_ttl import EditReferenceTtlRequest
from pydantic import ValidationError


class ReferencesEditAction(BaseAction):
    """
    Action to update session references.

    Replaces entire reference list for a session.
    """

    def execute(self) -> tuple[dict[str, Any], int]:
        """
        Update session references.

        Returns:
            Success: ({"message": str}, 200)
            Validation error: ({"message": str}, 422)
            Not found: ({"message": str}, 404)
        """
        from pipe.web.app import session_service

        session_id = self.params.get("session_id")
        if not session_id:
            return {"message": "session_id is required"}, 400

        try:
            # Validate request
            request_data = EditReferencesRequest(**self.request_data.get_json())

            # Update via service
            session_service.update_references(
                session_id,
                request_data.references,
            )

            return {"message": f"Session {session_id} references updated."}, 200

        except ValidationError as e:
            return {"message": str(e)}, 422
        except FileNotFoundError:
            return {"message": "Session not found."}, 404
        except Exception as e:
            return {"message": str(e)}, 500


class ReferencePersistEditAction(BaseAction):
    """
    Action to update persist flag for a specific reference.

    Updates whether a reference should persist across turns.
    """

    def execute(self) -> tuple[dict[str, Any], int]:
        """
        Update reference persist flag.

        Returns:
            Success: ({"message": str}, 200)
            Missing param: ({"message": str}, 400)
            Not found: ({"message": str}, 404)
            Out of range: ({"message": str}, 400)
        """
        from pipe.web.app import session_service

        session_id = self.params.get("session_id")
        reference_index = self.params.get("reference_index")

        if not session_id or reference_index is None:
            return {
                "message": "session_id and reference_index are required"
            }, 400

        try:
            reference_index = int(reference_index)
        except ValueError:
            return {"message": "reference_index must be an integer"}, 400

        try:
            # Validate request
            request_data = EditReferencePersistRequest(
                **self.request_data.get_json()
            )
            new_persist_state = request_data.persist

            # Get session to validate index
            session = session_service.get_session(session_id)
            if not session:
                return {"message": "Session not found."}, 404

            if not (0 <= reference_index < len(session.references)):
                return {"message": "Reference index out of range."}, 400

            # Update persist flag
            file_path = session.references[reference_index].path
            session_service.update_reference_persist_in_session(
                session_id,
                file_path,
                new_persist_state,
            )

            return {
                "message": f"Persist state for reference {reference_index} updated."
            }, 200

        except ValidationError as e:
            return {"message": str(e)}, 422
        except Exception as e:
            return {"message": str(e)}, 500
```

## Action Patterns

### Pattern 1: Simple Retrieval

```python
class GetResourceAction(BaseAction):
    def execute(self) -> dict[str, Any]:
        resource_id = self.request.get_path_param("resource_id")

        resource = service.get_resource(resource_id)
        if not resource:
            raise NotFoundError("Resource not found")

        return resource.to_dict()
```

### Pattern 2: Creation with Validation

```python
class CreateResourceAction(BaseAction):
    request_model = CreateResourceRequest  # Pre-validated!

    def execute(self) -> dict[str, str]:
        req = self.validated_request
        resource = service.create_resource(req)
        return {"resource_id": resource.id}
```

### Pattern 3: Update Operation

```python
class UpdateResourceAction(BaseAction):
    request_model = UpdateResourceRequest

    def execute(self) -> dict[str, str]:
        req = self.validated_request
        service.update_resource(req.resource_id, req)
        return {"message": "Updated successfully"}
```

### Pattern 4: Delete Operation

```python
class DeleteResourceAction(BaseAction):
    def execute(self) -> dict[str, str]:
        resource_id = self.request.get_path_param("resource_id")

        service.delete_resource(resource_id)
        return {"message": "Deleted successfully"}
```

## Testing

### Unit Testing Actions

```python
# tests/web/actions/test_session_actions.py
from unittest.mock import Mock, patch
import pytest
from pipe.web.actions import SessionGetAction, SessionDeleteAction
from pipe.web.exceptions import NotFoundError, BadRequestError


def test_session_get_action_success():
    # Mock service
    with patch("pipe.web.app.session_service") as mock_service:
        mock_session = Mock()
        mock_session.to_dict.return_value = {"session_id": "abc-123"}
        mock_service.get_session.return_value = mock_session

        # Execute action
        action = SessionGetAction(
            params={"session_id": "abc-123"},
            request_data=None,
        )
        data = action.execute()

        # Assert - returns data directly
        assert data["session_id"] == "abc-123"
        mock_service.get_session.assert_called_once_with("abc-123")


def test_session_get_action_not_found():
    with patch("pipe.web.app.session_service") as mock_service:
        mock_service.get_session.return_value = None

        action = SessionGetAction(
            params={"session_id": "nonexistent"},
            request_data=None,
        )

        # Should raise NotFoundError
        with pytest.raises(NotFoundError, match="Session not found"):
            action.execute()


def test_session_delete_action_success():
    with patch("pipe.web.app.session_service") as mock_service:
        action = SessionDeleteAction(
            params={"session_id": "abc-123"},
            request_data=None,
        )
        result = action.execute()

        # Returns success message
        assert "deleted" in result["message"].lower()
        mock_service.delete_session.assert_called_once_with("abc-123")
```

````

## Best Practices

### 1. Single Responsibility

```python
# ✅ GOOD: One operation
class SessionGetAction(BaseAction):
    def execute(self):
        session = service.get_session(session_id)
        return session.to_dict()

# ❌ BAD: Multiple operations
class SessionAction(BaseAction):
    def execute(self):
        # Too many responsibilities
        session = service.get_session(session_id)
        tree = service.get_tree()
        settings = service.get_settings()
        return {...}  # Use controller instead
````

### 2. Consistent Error Handling

```python
# ✅ GOOD: Use HttpException hierarchy
def execute(self):
    resource_id = self.request.get_path_param("resource_id")
    if not resource_id:
        raise BadRequestError("resource_id is required")

    result = service.do_something(resource_id)
    if not result:
        raise NotFoundError("Resource not found")

    return result

# ❌ BAD: Generic exceptions or manual error dicts
def execute(self):
    try:
        result = service.do_something()
        return result
    except Exception as e:
        # Loses error context, wrong status code
        return {"error": str(e)}
```

### 3. Use Request Models for Validation

```python
# ✅ GOOD: Unified request model (New pattern)
class UpdateResourceRequest(BaseRequest):
    path_params: ClassVar[list[str]] = ["resource_id"]
    resource_id: str
    name: str

class UpdateResourceAction(BaseAction):
    request_model = UpdateResourceRequest

    def execute(self):
        req = self.validated_request  # Already validated!
        service.update(req.resource_id, req.name)
        return {"message": "Updated"}

# ✅ GOOD: Body-only model (Legacy pattern)
class UpdateResourceBodyModel(BaseModel):
    name: str

class UpdateResourceAction(BaseAction):
    body_model = UpdateResourceBodyModel

    def execute(self):
        resource_id = self.request.get_path_param("resource_id")
        body = self.request.get_body()
        service.update(resource_id, body.name)
        return {"message": "Updated"}

# ❌ BAD: Manual validation
def execute(self):
    data = self.request_data.get_json()
    if not data.get("name"):
        raise BadRequestError("Name required")
    # Lots of manual validation...
```

### 4. New Pattern vs Legacy Pattern

```python
# ✅ NEW PATTERN (Recommended): Laravel/Struts style
# Validation happens BEFORE action execution

class SessionEditRequest(BaseRequest):
    path_params: ClassVar[list[str]] = ["session_id"]
    session_id: str
    purpose: str | None = None

    @field_validator("session_id")
    @classmethod
    def validate_session_exists(cls, v):
        if not session_exists(v):
            raise ValueError(f"Session '{v}' not found")
        return v

class SessionEditAction(BaseAction):
    request_model = SessionEditRequest  # Enables pre-validation

    def execute(self) -> dict[str, str]:
        # Already validated by dispatcher!
        req = self.validated_request

        # Type-safe access
        service.update_session(req.session_id, req.purpose)
        return {"message": "Updated"}  # Dispatcher wraps in ApiResponse

# ✅ LEGACY PATTERN (Still supported)
# Validation happens inside action

class SessionEditBodyModel(BaseModel):
    purpose: str | None = None

class SessionEditAction(BaseAction):
    body_model = SessionEditBodyModel

    def execute(self) -> dict[str, str]:
        # Manual parameter extraction
        session_id = self.request.get_path_param("session_id")
        if not session_id:
            raise BadRequestError("session_id is required")

        # Lazy validation
        body = self.request.get_body()

        service.update_session(session_id, body.purpose)
        return {"message": "Updated"}  # Dispatcher wraps in ApiResponse
```

### 5. Stateless Operations

```python
# ✅ GOOD: Stateless
class GetAction(BaseAction):
    def execute(self):
        # No state stored
        resource_id = self.request.get_path_param("id")
        return service.get(resource_id)

# ❌ BAD: Stateful
class GetAction(BaseAction):
    def __init__(self, params, request_data):
        super().__init__(params, request_data)
        self.cache = {}  # State - BAD!

    def execute(self):
        id = self.request.get_path_param("id")
        if id in self.cache:
            return self.cache[id]
        ...
```

## Summary

Actions are **single-purpose operations**:

- ✅ One action, one operation
- ✅ Stateless execution
- ✅ Return data directly (dict, list, TypedDict, etc.)
- ✅ Raise HttpException for errors
- ✅ Dispatcher wraps responses in ApiResponse
- ❌ No business logic
- ❌ No orchestration
- ❌ No calling other actions
- ❌ No state
- ❌ No manual ApiResponse wrapping

Keep actions simple, focused, and stateless.
