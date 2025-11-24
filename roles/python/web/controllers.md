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
└── session_detail_controller.py    # Multi-view controller
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

## Real Example

### session_detail_controller.py - Session Detail Orchestration

**Purpose**: Provide complete session view with tree context

**Orchestration**:

1. Get session tree (all sessions)
2. Get specific session details
3. Combine with settings

```python
"""
Controller for session detail operations.

Orchestrates session and tree actions to provide a complete
session detail view with navigation context.
"""

from typing import Any

from flask import Request
from pipe.web.actions import SessionGetAction, SessionTreeAction


class SessionDetailController:
    """
    Controller for session detail view.

    Provides a composite view that combines:
    - Session tree (for navigation)
    - Current session details
    - Application settings

    This is a frontend-specific view that requires data from
    multiple sources.

    Attributes:
        session_service: Service for session operations
        settings: Application settings
    """

    def __init__(self, session_service, settings):
        """
        Initialize controller with dependencies.

        Args:
            session_service: SessionService instance
            settings: Settings model instance
        """
        self.session_service = session_service
        self.settings = settings

    def get_session_with_tree(
        self,
        session_id: str,
        request_data: Request | None = None,
    ) -> tuple[dict[str, Any], int]:
        """
        Get session details with tree context.

        This orchestrates multiple actions to provide a complete
        view for the session detail page:
        1. Gets the full session tree (for sidebar navigation)
        2. Gets the specific session details
        3. Includes application settings

        Args:
            session_id: ID of the session to retrieve
            request_data: Optional Flask request data

        Returns:
            Tuple of (response_dict, status_code)

            Response format:
            {
                "session_tree": [...],      # All sessions for navigation
                "current_session": {...},   # Selected session details
                "settings": {...}           # Application settings
            }

        Examples:
            controller = SessionDetailController(service, settings)
            response, status = controller.get_session_with_tree("abc-123")

            if status == 200:
                tree = response["session_tree"]
                session = response["current_session"]
                print(f"Session {session['session_id']} in tree of {len(tree)}")
        """
        # Step 1: Get session tree
        session_tree_action = SessionTreeAction(
            params={},
            request_data=request_data,
        )
        tree_response, tree_status = session_tree_action.execute()

        # Check for tree errors
        if tree_status != 200:
            return tree_response, tree_status

        # Step 2: Get specific session
        session_action = SessionGetAction(
            params={"session_id": session_id},
            request_data=request_data,
        )
        session_response, session_status = session_action.execute()

        # Check for session errors
        if session_status != 200:
            return session_response, session_status

        # Step 3: Combine into composite response
        return {
            "session_tree": tree_response.get("sessions", []),
            "current_session": session_response.get("session", {}),
            "settings": self.settings.model_dump(),
        }, 200
```

## Controller Patterns

### Pattern 1: Sequential Action Orchestration

```python
def orchestrate_operations(self, resource_id: str):
    # Execute actions sequentially
    response1, status1 = Action1(...).execute()
    if status1 != 200:
        return response1, status1

    response2, status2 = Action2(...).execute()
    if status2 != 200:
        return response2, status2

    # Combine results
    return {
        "data1": response1["data"],
        "data2": response2["data"],
    }, 200
```

### Pattern 2: Conditional Action Execution

```python
def conditional_orchestration(self, resource_id: str, include_extra: bool):
    # Always get base data
    base_response, status = BaseAction(...).execute()
    if status != 200:
        return base_response, status

    result = {"base": base_response["data"]}

    # Conditionally get extra data
    if include_extra:
        extra_response, status = ExtraAction(...).execute()
        if status == 200:
            result["extra"] = extra_response["data"]

    return result, 200
```

### Pattern 3: Error Aggregation

```python
def aggregate_with_errors(self, resource_id: str):
    errors = []
    result = {}

    # Try to get multiple resources
    response1, status1 = Action1(...).execute()
    if status1 == 200:
        result["data1"] = response1["data"]
    else:
        errors.append(f"Action1 failed: {response1.get('message')}")

    response2, status2 = Action2(...).execute()
    if status2 == 200:
        result["data2"] = response2["data"]
    else:
        errors.append(f"Action2 failed: {response2.get('message')}")

    # Return partial results with errors
    if errors:
        result["errors"] = errors

    return result, 200 if not errors else 207  # 207 = Multi-Status
```

## Testing

### Unit Testing Controllers

```python
# tests/web/controllers/test_session_detail_controller.py
from unittest.mock import Mock, patch
from pipe.web.controllers import SessionDetailController


def test_get_session_with_tree_success():
    # Mock dependencies
    mock_service = Mock()
    mock_settings = Mock()
    mock_settings.model_dump.return_value = {"key": "value"}

    controller = SessionDetailController(mock_service, mock_settings)

    # Mock action responses
    with patch("pipe.web.actions.SessionTreeAction") as MockTreeAction, \
         patch("pipe.web.actions.SessionGetAction") as MockGetAction:

        # Mock tree action
        tree_instance = MockTreeAction.return_value
        tree_instance.execute.return_value = (
            {"sessions": [{"id": "1"}, {"id": "2"}]},
            200,
        )

        # Mock session action
        get_instance = MockGetAction.return_value
        get_instance.execute.return_value = (
            {"session": {"session_id": "abc-123"}},
            200,
        )

        # Execute
        response, status = controller.get_session_with_tree("abc-123")

        # Assert
        assert status == 200
        assert "session_tree" in response
        assert "current_session" in response
        assert "settings" in response
        assert len(response["session_tree"]) == 2


def test_get_session_with_tree_tree_error():
    controller = SessionDetailController(Mock(), Mock())

    with patch("pipe.web.actions.SessionTreeAction") as MockTreeAction:
        # Tree action fails
        tree_instance = MockTreeAction.return_value
        tree_instance.execute.return_value = (
            {"message": "Tree failed"},
            500,
        )

        # Execute
        response, status = controller.get_session_with_tree("abc-123")

        # Should return tree error immediately
        assert status == 500
        assert response["message"] == "Tree failed"


def test_get_session_with_tree_session_error():
    controller = SessionDetailController(Mock(), Mock())

    with patch("pipe.web.actions.SessionTreeAction") as MockTreeAction, \
         patch("pipe.web.actions.SessionGetAction") as MockGetAction:

        # Tree succeeds
        tree_instance = MockTreeAction.return_value
        tree_instance.execute.return_value = (
            {"sessions": []},
            200,
        )

        # Session fails
        get_instance = MockGetAction.return_value
        get_instance.execute.return_value = (
            {"message": "Session not found"},
            404,
        )

        # Execute
        response, status = controller.get_session_with_tree("nonexistent")

        # Should return session error
        assert status == 404
        assert response["message"] == "Session not found"
```

## Integration with Actions

### Controllers Use Actions

```python
# ✅ GOOD: Controller orchestrates actions
class DashboardController:
    def get_dashboard(self):
        # Use actions for operations
        sessions_response, _ = SessionListAction(...).execute()
        stats_response, _ = StatsAction(...).execute()

        return {
            "sessions": sessions_response["sessions"],
            "stats": stats_response["stats"],
        }, 200

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
        data1 = Action1().execute()
        data2 = Action2().execute()
        data3 = Action3().execute()
        return combine(data1, data2, data3)

# ❌ BAD: Single action - no controller needed
class ReportController:
    def get_simple_data(self):
        # Just use the action directly in routes
        return Action1().execute()
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
# ✅ GOOD: Check each action's status
def orchestrate(self):
    response1, status1 = Action1().execute()
    if status1 != 200:
        return response1, status1  # Early return on error

    response2, status2 = Action2().execute()
    if status2 != 200:
        return response2, status2

    return combine(response1, response2), 200

# ❌ BAD: Ignore action errors
def orchestrate(self):
    response1, _ = Action1().execute()  # Ignoring status
    response2, _ = Action2().execute()
    return combine(response1, response2), 200
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
