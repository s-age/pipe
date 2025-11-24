# Actions Layer

## Purpose

Actions represent **single-purpose operations** in the web layer. Each action executes one specific operation (e.g., get session, create session, update reference) and returns a consistent JSON response.

## Responsibilities

1. **Single Operation** - One action, one responsibility
2. **Service Coordination** - Call core services to execute business logic
3. **Request Parsing** - Extract and validate parameters
4. **Error Handling** - Catch and format errors consistently
5. **Response Formatting** - Return `(dict, status_code)` tuples

## Characteristics

- ✅ Single responsibility (one operation only)
- ✅ Stateless execution
- ✅ Direct service calls
- ✅ Consistent error handling
- ✅ Return `tuple[dict[str, Any], int]`
- ❌ **NO business logic** - delegate to services
- ❌ **NO orchestration** - one operation only
- ❌ **NO calling other actions** - let controllers orchestrate
- ❌ **NO state** - actions are stateless

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


class BaseAction(ABC):
    """
    Abstract base class for all API actions.

    All actions inherit from this base and implement execute().
    Actions receive parameters and request data, then return
    a tuple of (response_dict, status_code).

    Attributes:
        params: URL/query parameters
        request_data: Flask Request object
    """

    def __init__(self, params: dict, request_data: Request | None = None):
        """
        Initialize the action with parameters and optional request data.

        Args:
            params: Parameters extracted from URL path and query string
            request_data: Optional Flask Request object for accessing body

        Examples:
            # Action with URL params only
            action = SessionGetAction(
                params={"session_id": "abc-123"},
                request_data=None,
            )

            # Action with request body
            action = SessionStartAction(
                params={},
                request_data=request,  # Flask request with JSON body
            )
        """
        self.params = params
        self.request_data = request_data

    @abstractmethod
    def execute(self) -> tuple[dict[str, Any], int]:
        """
        Execute the action and return a JSON response with status code.

        This method must be implemented by all action subclasses.
        It should:
        1. Extract parameters from self.params and self.request_data
        2. Validate inputs (or use request models)
        3. Call core services to execute business logic
        4. Handle errors appropriately
        5. Return (response_dict, status_code)

        Returns:
            Tuple of (response_dict, status_code)

        Examples:
            response, status = action.execute()

            if status == 200:
                print("Success:", response)
            else:
                print("Error:", response.get("message"))
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

    def execute(self) -> tuple[dict[str, Any], int]:
        """
        Retrieve session by ID.

        Returns:
            Success: ({"session": dict}, 200)
            Missing param: ({"message": str}, 400)
            Not found: ({"message": str}, 404)
            Error: ({"message": str}, 500)

        Examples:
            action = SessionGetAction(
                params={"session_id": "abc-123"},
                request_data=None,
            )
            response, status = action.execute()

            if status == 200:
                session = response["session"]
                print(f"Session: {session['session_id']}")
        """
        from pipe.web.app import session_service

        # Extract parameter
        session_id = self.params.get("session_id")
        if not session_id:
            return {"message": "session_id is required"}, 400

        try:
            # Get session from service
            session_data = session_service.get_session(session_id)

            if not session_data:
                return {"message": "Session not found."}, 404

            return {"session": session_data.to_dict()}, 200

        except Exception as e:
            return {"message": str(e)}, 500


class SessionDeleteAction(BaseAction):
    """
    Action to delete a session.

    Deletes session and all related data via service.
    """

    def execute(self) -> tuple[dict[str, Any], int]:
        """
        Delete session by ID.

        Returns:
            Success: ({"message": str}, 200)
            Missing param: ({"message": str}, 400)
            Error: ({"message": str}, 500)
        """
        from pipe.web.app import session_service

        session_id = self.params.get("session_id")
        if not session_id:
            return {"message": "session_id is required"}, 400

        try:
            session_service.delete_session(session_id)
            return {"message": f"Session {session_id} deleted."}, 200

        except Exception as e:
            return {"message": str(e)}, 500


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
    def execute(self) -> tuple[dict[str, Any], int]:
        resource_id = self.params.get("resource_id")

        try:
            resource = service.get_resource(resource_id)
            return {"resource": resource.to_dict()}, 200
        except NotFoundError:
            return {"message": "Not found"}, 404
```

### Pattern 2: Creation with Validation

```python
class CreateResourceAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        try:
            request_data = CreateResourceRequest(**self.request_data.get_json())
            resource = service.create_resource(request_data)
            return {"resource_id": resource.id}, 201
        except ValidationError as e:
            return {"message": str(e)}, 422
```

### Pattern 3: Update Operation

```python
class UpdateResourceAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        resource_id = self.params.get("resource_id")

        try:
            request_data = UpdateResourceRequest(**self.request_data.get_json())
            service.update_resource(resource_id, request_data)
            return {"message": "Updated successfully"}, 200
        except NotFoundError:
            return {"message": "Not found"}, 404
        except ValidationError as e:
            return {"message": str(e)}, 422
```

### Pattern 4: Delete Operation

```python
class DeleteResourceAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        resource_id = self.params.get("resource_id")

        try:
            service.delete_resource(resource_id)
            return {"message": "Deleted successfully"}, 200
        except NotFoundError:
            return {"message": "Not found"}, 404
```

## Testing

### Unit Testing Actions

```python
# tests/web/actions/test_session_actions.py
from unittest.mock import Mock, patch
from pipe.web.actions import SessionGetAction, SessionDeleteAction


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
        response, status = action.execute()

        # Assert
        assert status == 200
        assert response["session"]["session_id"] == "abc-123"
        mock_service.get_session.assert_called_once_with("abc-123")


def test_session_get_action_not_found():
    with patch("pipe.web.app.session_service") as mock_service:
        mock_service.get_session.return_value = None

        action = SessionGetAction(
            params={"session_id": "nonexistent"},
            request_data=None,
        )
        response, status = action.execute()

        assert status == 404
        assert "not found" in response["message"].lower()


def test_session_delete_action_success():
    with patch("pipe.web.app.session_service") as mock_service:
        action = SessionDeleteAction(
            params={"session_id": "abc-123"},
            request_data=None,
        )
        response, status = action.execute()

        assert status == 200
        assert "deleted" in response["message"].lower()
        mock_service.delete_session.assert_called_once_with("abc-123")
```

## Best Practices

### 1. Single Responsibility

```python
# ✅ GOOD: One operation
class SessionGetAction(BaseAction):
    def execute(self):
        session = service.get_session(session_id)
        return {"session": session.to_dict()}, 200

# ❌ BAD: Multiple operations
class SessionAction(BaseAction):
    def execute(self):
        # Too many responsibilities
        session = service.get_session(session_id)
        tree = service.get_tree()
        settings = service.get_settings()
        return {...}, 200  # Use controller instead
```

### 2. Consistent Error Handling

```python
# ✅ GOOD: Consistent error responses
def execute(self):
    try:
        result = service.do_something()
        return {"result": result}, 200
    except ValidationError as e:
        return {"message": str(e)}, 422
    except NotFoundError:
        return {"message": "Not found"}, 404
    except Exception as e:
        return {"message": str(e)}, 500

# ❌ BAD: Inconsistent error handling
def execute(self):
    result = service.do_something()  # No error handling
    return result, 200  # Might crash
```

### 3. Use Request Models for Validation

```python
# ✅ GOOD: Request model validates
def execute(self):
    request_data = CreateResourceRequest(**self.request_data.get_json())
    # All validation done by model
    return service.create(request_data), 201

# ❌ BAD: Manual validation
def execute(self):
    data = self.request_data.get_json()
    if not data.get("name"):
        return {"message": "Name required"}, 400
    # Lots of manual validation...
```

### 4. Stateless Operations

```python
# ✅ GOOD: Stateless
class GetAction(BaseAction):
    def execute(self):
        # No state stored
        return service.get(self.params["id"]), 200

# ❌ BAD: Stateful
class GetAction(BaseAction):
    def __init__(self, params, request_data):
        super().__init__(params, request_data)
        self.cache = {}  # State - BAD!

    def execute(self):
        if id in self.cache:
            return self.cache[id], 200
        ...
```

## Summary

Actions are **single-purpose operations**:

- ✅ One action, one operation
- ✅ Stateless execution
- ✅ Consistent response format
- ✅ Clear error handling
- ❌ No business logic
- ❌ No orchestration
- ❌ No calling other actions
- ❌ No state

Keep actions simple, focused, and stateless.
