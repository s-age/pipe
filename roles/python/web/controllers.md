# Controllers Layer

## Purpose

Controllers orchestrate **multiple actions** to fulfill complex requests. They combine the results of several actions into composite responses tailored for specific frontend needs.

## Responsibilities

1. **Multi-Action Orchestration** - Coordinate multiple action executions
2. **Composite Responses** - Combine results from multiple sources
3. **Frontend-Specific Views** - Shape data for specific UI needs
4. **Request Delegation** - Pass request context to actions
5. **Error Aggregation** - Handle errors from multiple actions

## Characteristics

- ✅ Orchestrate multiple actions
- ✅ Combine action results
- ✅ Frontend-specific response shaping
- ✅ Stateless coordination
- ❌ **NO business logic** - delegate to services
- ❌ **NO direct service calls for simple operations** - use actions
- ❌ **NO data persistence** - use services/repositories

## File Structure

```
controllers/
├── __init__.py
├── start_session_controller.py      # Session initialization
├── session_chat_controller.py       # Chat interface context
└── session_management_controller.py # Session management dashboard
```

## Dependencies

**Allowed:**

- ✅ Actions (to execute operations)
- ✅ Core Services (for complex coordination only)
- ✅ Core Models (for type hints)
- ✅ Settings (for configuration)

**Forbidden:**

- ❌ Domains (use services, not domains directly)
- ❌ Repositories (use services, not repositories directly)
- ❌ Other controllers (no controller-to-controller calls)

## Template

```python
"""
Controller for [feature] operations.

Orchestrates multiple actions to provide composite views.
"""

from typing import Any

from flask import Request
from pipe.web.actions import Action1, Action2, Action3


class FeatureController:
    """
    Controller for [feature] operations.

    Orchestrates multiple actions to provide complex,
    frontend-specific responses.

    Attributes:
        service: Core service for business logic
        settings: Application settings
    """

    def __init__(self, service, settings):
        """
        Initialize controller with dependencies.

        Args:
            service: Core service instance
            settings: Application settings
        """
        self.service = service
        self.settings = settings

    def get_composite_view(
        self,
        resource_id: str,
        request_data: Request | None = None,
    ) -> tuple[dict[str, Any], int]:
        """
        Get composite view by orchestrating multiple actions.

        This combines data from multiple sources to provide
        a complete view for the frontend.

        Args:
            resource_id: ID of the resource
            request_data: Optional Flask request data

        Returns:
            Tuple of (response_dict, status_code)

        Examples:
            controller = FeatureController(service, settings)
            response, status = controller.get_composite_view("123")

            if status == 200:
                print(response["resource"])
                print(response["related_data"])
        """
        # Execute first action
        action1 = Action1(params={}, request_data=request_data)
        response1, status1 = action1.execute()

        # Check for errors
        if status1 != 200:
            return response1, status1

        # Execute second action
        action2 = Action2(
            params={"id": resource_id},
            request_data=request_data,
        )
        response2, status2 = action2.execute()

        # Check for errors
        if status2 != 200:
            return response2, status2

        # Combine results
        return {
            "resource": response2.get("resource", {}),
            "related_data": response1.get("data", []),
            "settings": self.settings.model_dump(),
        }, 200
```

## Real Examples

### 1. start_session_controller.py - Session Initialization

**Purpose**: Initialize new sessions and load initial session data with all required context

**Orchestration**:

1. Get session tree (for navigation sidebar)
2. Get specific session details
3. Get available roles
4. Get application settings

```python
"""Controller for initializing new sessions and loading initial session data."""

from typing import Any
from flask import Request
from pipe.web.actions import (
    GetRolesAction,
    SessionGetAction,
    SessionTreeAction,
    SettingsGetAction,
)
from pipe.web.exceptions import HttpException


class StartSessionController:
    """Controller for session initialization operations."""

    def __init__(self, session_service, settings):
        self.session_service = session_service
        self.settings = settings

    def get_session_with_tree(
        self, session_id: str, request_data: Request | None = None
    ) -> tuple[dict[str, Any], int]:
        """
        Get complete session initialization context.

        Returns:
            {
                "session_tree": [...],
                "current_session": {...},
                "settings": {...},
                "role_options": [...]
            }
        """
        try:
            # Actions return data directly or raise HttpException
            tree_data = SessionTreeAction(params={}, request_data=request_data).execute()
            session_data = SessionGetAction(
                params={"session_id": session_id}, request_data=request_data
            ).execute()
            roles_data = GetRolesAction(params={}, request_data=request_data).execute()
            settings_data = SettingsGetAction(params={}, request_data=request_data).execute()

            return {
                "session_tree": tree_data.get(
                    "session_tree", tree_data.get("sessions", [])
                ),
                "current_session": session_data,
                "settings": settings_data.get("settings", {}),
                "role_options": roles_data,
            }, 200
        except HttpException as e:
            return {"success": False, "message": e.message}, e.status_code
```

### 2. session_chat_controller.py - Chat Interface Context

**Purpose**: Provide chat interface with session context and history

**Orchestration**:

1. Get session tree (all sessions)
2. Get settings
3. Optionally get specific session if session_id provided

```python
"""Controller for chat interface, providing session history and current session context."""

from typing import Any
from flask import Request
from pipe.web.actions import SessionGetAction, SessionTreeAction, SettingsGetAction
from pipe.web.exceptions import HttpException


class SessionChatController:
    """Controller for chat interface operations."""

    def __init__(self, session_service, settings):
        self.session_service = session_service
        self.settings = settings

    def get_chat_context(
        self, session_id: str | None, request_data: Request | None = None
    ) -> tuple[dict[str, Any], int]:
        """
        Get chat interface context.

        Returns:
            {
                "sessions": [...],
                "session_tree": [...],
                "settings": {...},
                "current_session": {...}  # if session_id provided
            }
        """
        try:
            tree_data = SessionTreeAction(params={}, request_data=request_data).execute()
            settings_data = SettingsGetAction(params={}, request_data=request_data).execute()

            response = {
                "sessions": tree_data.get("sessions", []),
                "session_tree": tree_data.get(
                    "session_tree", tree_data.get("sessions", [])
                ),
                "settings": settings_data.get("settings", {}),
            }

            if session_id:
                session_data = SessionGetAction(
                    params={"session_id": session_id}, request_data=request_data
                ).execute()
                response["current_session"] = session_data

            return response, 200
        except HttpException as e:
            return {"success": False, "message": e.message}, e.status_code
```

### 3. session_management_controller.py - Management Dashboard

**Purpose**: Provide session management dashboard with archives

**Orchestration**:

1. Get session tree (active sessions)
2. Get archived sessions
3. Transform archive data for UI consumption

```python
"""Controller for session management dashboard, including archives and bulk operations."""

from typing import Any
from flask import Request
from pipe.web.actions import SessionTreeAction
from pipe.web.actions.session_management_actions import SessionsListBackupAction
from pipe.web.exceptions import HttpException


class SessionManagementController:
    """Controller for session management operations."""

    def __init__(self, session_service, settings):
        self.session_service = session_service
        self.settings = settings

    def get_dashboard(
        self, request_data: Request | None = None
    ) -> tuple[dict[str, Any], int]:
        """
        Get session management dashboard data.

        Returns:
            {
                "session_tree": [...],
                "archives": [...]
            }
        """
        try:
            tree_data = SessionTreeAction(params={}, request_data=request_data).execute()
            archives_raw = SessionsListBackupAction(params={}, request_data=request_data).execute()

            archives = []
            for item in archives_raw:
                session_data = item.get("session_data", {})
                archives.append({
                    "session_id": item.get("session_id", ""),
                    "purpose": session_data.get("purpose", ""),
                    "background": session_data.get("background", ""),
                    # ... transform data for UI
                })

            return {
                "session_tree": tree_data.get(
                    "session_tree", tree_data.get("sessions", [])
                ),
                "archives": archives,
            }, 200
        except HttpException as e:
            return {"success": False, "message": e.message}, e.status_code
```

## Key Differences Between Controllers

| Controller                  | Primary Use Case       | Actions Used                                | Unique Feature           |
| --------------------------- | ---------------------- | ------------------------------------------- | ------------------------ |
| StartSessionController      | Session initialization | SessionTree, SessionGet, GetRoles, Settings | Includes role_options    |
| SessionChatController       | Chat interface         | SessionTree, SessionGet, Settings           | Optional session loading |
| SessionManagementController | Admin dashboard        | SessionTree, SessionsListBackup             | Archive transformation   |

## Controller Patterns

### Pattern 1: Sequential Action Orchestration

```python
def orchestrate_operations(self, resource_id: str):
    """Execute actions sequentially with error handling."""
    try:
        # Actions return data directly, raise HttpException on error
        data1 = Action1(...).execute()
        data2 = Action2(...).execute()

        # Combine results
        return {
            "data1": data1,
            "data2": data2,
        }, 200
    except HttpException as e:
        return {"success": False, "message": e.message}, e.status_code
```

### Pattern 2: Conditional Action Execution

```python
def conditional_orchestration(self, resource_id: str, include_extra: bool):
    """Conditionally execute additional actions."""
    try:
        # Always get base data
        base_data = BaseAction(...).execute()
        result = {"base": base_data}

        # Conditionally get extra data
        if include_extra:
            extra_data = ExtraAction(...).execute()
            result["extra"] = extra_data

        return result, 200
    except HttpException as e:
        return {"success": False, "message": e.message}, e.status_code
```

### Pattern 3: Partial Success with Error Tracking

```python
def aggregate_with_errors(self, resource_id: str):
    """Handle multiple actions with partial success support."""
    errors = []
    result = {}

    # Try to get multiple resources
    try:
        data1 = Action1(...).execute()
        result["data1"] = data1
    except HttpException as e:
        errors.append(f"Action1 failed: {e.message}")

    try:
        data2 = Action2(...).execute()
        result["data2"] = data2
    except HttpException as e:
        errors.append(f"Action2 failed: {e.message}")

    # Return partial results with errors
    if errors:
        result["errors"] = errors
        result["success"] = False

    return result, 200 if not errors else 207  # 207 = Multi-Status
```

## Testing

### Unit Testing Controllers

```python
# tests/web/controllers/test_start_session_controller.py
from unittest.mock import Mock, patch
from pipe.web.controllers import StartSessionController
from pipe.web.exceptions import NotFoundError


def test_get_session_with_tree_success():
    # Mock dependencies
    mock_service = Mock()
    mock_settings = Mock()

    controller = StartSessionController(mock_service, mock_settings)

    # Mock action responses (actions return data directly)
    with patch("pipe.web.actions.SessionTreeAction") as MockTreeAction, \
         patch("pipe.web.actions.SessionGetAction") as MockGetAction, \
         patch("pipe.web.actions.GetRolesAction") as MockRolesAction, \
         patch("pipe.web.actions.SettingsGetAction") as MockSettingsAction:

        # Mock successful data returns
        tree_instance = MockTreeAction.return_value
        tree_instance.execute.return_value = {
            "session_tree": [{"id": "1"}, {"id": "2"}]
        }

        get_instance = MockGetAction.return_value
        get_instance.execute.return_value = {"session_id": "abc-123"}

        roles_instance = MockRolesAction.return_value
        roles_instance.execute.return_value = ["role1", "role2"]

        settings_instance = MockSettingsAction.return_value
        settings_instance.execute.return_value = {"settings": {"key": "value"}}

        # Execute
        response, status = controller.get_session_with_tree("abc-123")

        # Assert
        assert status == 200
        assert "session_tree" in response
        assert "current_session" in response
        assert "settings" in response
        assert "role_options" in response


def test_get_session_with_tree_not_found():
    controller = StartSessionController(Mock(), Mock())

    with patch("pipe.web.actions.SessionTreeAction") as MockTreeAction, \
         patch("pipe.web.actions.SessionGetAction") as MockGetAction:

        # Tree succeeds
        tree_instance = MockTreeAction.return_value
        tree_instance.execute.return_value = {"session_tree": []}

        # Session raises NotFoundError
        get_instance = MockGetAction.return_value
        get_instance.execute.side_effect = NotFoundError("Session not found")

        # Execute
        response, status = controller.get_session_with_tree("nonexistent")

        # Should return error response
        assert status == 404
        assert response["success"] is False
        assert "not found" in response["message"].lower()
```

## Integration with Actions

### Controllers Use Actions

```python
# ✅ GOOD: Controller orchestrates actions
class DashboardController:
    def get_dashboard(self):
        try:
            # Use actions for operations
            sessions_data = SessionListAction(...).execute()
            stats_data = StatsAction(...).execute()

            return {
                "sessions": sessions_data,
                "stats": stats_data,
            }, 200
        except HttpException as e:
            return {"success": False, "message": e.message}, e.status_code

# ❌ BAD: Controller calls services directly for simple operations
class DashboardController:
    def get_dashboard(self):
        # Should use SessionListAction instead
        sessions = self.session_service.list_sessions()
        ...
```

### Actions Don't Call Controllers

```python
# ❌ BAD: Action calling controller
class SessionAction(BaseAction):
    def execute(self):
        # Actions should never call controllers
        controller = DashboardController(...)
        dashboard = controller.get_dashboard()
        ...
```

## Best Practices

### 1. Use for Multi-Action Orchestration

```python
# ✅ GOOD: Multiple actions need coordination
class ReportController:
    def get_full_report(self):
        try:
            data1 = Action1().execute()
            data2 = Action2().execute()
            data3 = Action3().execute()
            return self.combine(data1, data2, data3), 200
        except HttpException as e:
            return {"success": False, "message": e.message}, e.status_code

    def combine(self, d1, d2, d3):
        return {"report": {"data1": d1, "data2": d2, "data3": d3}}

# ❌ BAD: Single action - no controller needed
class ReportController:
    def get_simple_data(self):
        # Just use the action directly in routes
        return Action1().execute(), 200
```

### 2. Keep Business Logic in Core

```python
# ✅ GOOD: Delegate to services
class AnalyticsController:
    def get_analytics(self):
        # Service handles business logic
        analytics = self.service.calculate_analytics()
        return {"analytics": analytics}, 200

# ❌ BAD: Business logic in controller
class AnalyticsController:
    def get_analytics(self):
        # Controller shouldn't calculate
        total = sum(session.turns for session in sessions)
        avg = total / len(sessions)
        ...
```

### 3. Handle Errors Gracefully

```python
# ✅ GOOD: Use try/except with HttpException
def orchestrate(self):
    try:
        data1 = Action1().execute()
        data2 = Action2().execute()
        return self.combine(data1, data2), 200
    except HttpException as e:
        return {"success": False, "message": e.message}, e.status_code

# ❌ BAD: No error handling
def orchestrate(self):
    data1 = Action1().execute()  # May raise exception
    data2 = Action2().execute()
    return self.combine(data1, data2), 200
```

### 4. Frontend-Specific Shaping

```python
# ✅ GOOD: Shape for frontend needs
def get_session_page_data(self):
    return {
        "session_tree": [...],      # For navigation
        "current_session": {...},   # For main content
        "settings": {...},          # For UI config
    }, 200

# ❌ BAD: Return raw service data
def get_session_page_data(self):
    # Frontend has to do too much work
    return self.service.get_all_data(), 200
```

## Summary

Controllers are **action orchestrators**:

- ✅ Combine multiple actions
- ✅ Shape frontend-specific responses
- ✅ Handle complex coordination
- ✅ Aggregate errors from multiple sources
- ❌ No business logic
- ❌ No direct service calls for simple ops
- ❌ No controller-to-controller calls

Use controllers when you need to **combine multiple actions** into a single, cohesive response.
